import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import apiClient, { registerUser } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { motion } from "motion/react";

export function LoginPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [isFindPassword, setIsFindPassword] = useState(false);
  const [findPasswordStep, setFindPasswordStep] = useState(1); // 1: 이메일, 2: 인증번호, 3: 새 비밀번호
  const [confirmPassword, setConfirmPassword] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [sentCode, setSentCode] = useState(""); // 데모용 발송된 인증번호
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null); // 에러 메세지 상태
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();

  const resetForm = () => {
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setVerificationCode("");
    setSentCode("");
    setFindPasswordStep(1);
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setError(null); // 이전 에러 메세지 초기화

    // 이메일 유효성 검사
    // if (!email.includes("@")) {
    //   alert("올바른 이메일 형식을 입력해주세요.");
    //   return;
    // }
    
    // 비밀번호 길이 검사
    if (password.length < 8 || password.length >= 16) {
      alert("비밀번호는 8자 이상 16자 미만이어야 합니다.");
      return;
    }
    
    // 비밀번호 특수문자 검사
    const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;
    if (!specialCharRegex.test(password)) {
      alert("비밀번호에는 특수문자가 최소 1개 이상 포함되어야 합니다.");
      return;
    }

    try {
      // await apiClient.post('/auth/login', {email, password});
      // login();
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      setIsLoading(true);
      await apiClient.post('/auth/login', formData, {
        // headers: { 'Content-Type': 'application/x-www-form-urlencoded'}
      });
      setIsLoading(false);
      login();

    } catch (err: any) {
        console.error("로그인 실패: ", err);
        setIsLoading(false);
        if (err.response && err.response.data && err.response.detail) {
          setError(err.response.data.detail);
        } else {
          setError("로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.")
        }
    }
  }
  
  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // 이메일 유효성 검사
    // if (!email.includes("@")) {
    //   alert("올바른 이메일 형식을 입력해주세요.");
    //   return;
    // }
    
    // 비밀번호 길이 검사
    if (password.length < 8 || password.length >= 16) {
      alert("비밀번호는 8자 이상 16자 미만이어야 합니다.");
      return;
    }
    
    // 비밀번호 특수문자 검사
    const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;
    if (!specialCharRegex.test(password)) {
      alert("비밀번호에는 특수문자가 최소 1개 이상 포함되어야 합니다.");
      return;
    }
    
    // 비밀번호 확인 검증
    if (password !== confirmPassword) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }

    setIsLoading(true)
    try {
      await registerUser(email, password);
      alert("회원가입이 완료되었습니다!");
      setIsSignup(false);
      resetForm();
    } catch (err: any) {
      console.error("회원가입 실패: ", err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("회원가입에 실패했습니다. 다시 시도해주세요.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailVerification = (e: React.FormEvent) => {
    e.preventDefault();
    // 실제로는 서버에서 이메일 존재 여부 확인
    // 데모 목적으로 모든 이메일을 유효한 것으로 처리
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    setSentCode(code);
    alert(`인증번호가 이메일로 발송되었습니다. (데모용 코드: ${code})`);
    setFindPasswordStep(2);
  };

  const handleVerificationCodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (verificationCode !== sentCode) {
      alert("인증번호가 일치하지 않습니다.");
      return;
    }
    setFindPasswordStep(3);
  };

  const handlePasswordReset = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }
    // 실제 비밀번호 재설정 로직은 여기에 구현
    alert("비밀번호가 성공적으로 변경되었습니다!");
    setIsFindPassword(false);
    resetForm();
  };

  const getCardDescription = () => {
    if (isSignup) return "새 계정을 만들어보세요";
    if (isFindPassword) {
      if (findPasswordStep === 1) return "가입하신 이메일을 입력해주세요";
      if (findPasswordStep === 2) return "이메일로 발송된 인증번호를 입력해주세요";
      if (findPasswordStep === 3) return "새로운 비밀번호를 설정해주세요";
    }
    return "일정관리 시스템에 로그인하세요";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md relative">
        {isLoading && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-lg">
            <motion.div
              className="text-2xl text-gray-700 bg-white/80 px-6 py-3 rounded-full backdrop-blur-sm"
              animate={{
                scale: [1, 1.05, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              Loading...
            </motion.div>
          </div>
        )}
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center">Jeiary</CardTitle>
          <CardDescription className="text-center">
            {getCardDescription()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!isSignup && !isFindPassword ? (
            // 로그인 폼
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="example@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-red-500 text-sm text-center">{error}</p>}
              <Button type="submit" className="w-full">
                로그인
              </Button>
            </form>
          ) : isSignup ? (
            // 회원가입 폼
            <form onSubmit={handleSignupSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="signup-email">이메일</Label>
                <Input
                  id="signup-email"
                  type="email"
                  placeholder="example@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-password">비밀번호</Label>
                <Input
                  id="signup-password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm-password">비밀번호 확인</Label>
                <Input
                  id="confirm-password"
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-red-500 text-sm text-center">{error}</p>}
              <Button type="submit" className="w-full">
                회원가입
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                className="w-full"
                onClick={() => {
                  setIsSignup(false);
                  resetForm();
                }}
              >
                로그인으로 돌아가기
              </Button>
            </form>
          ) : (
            // 비밀번호 찾기 폼
            <>
              {findPasswordStep === 1 && (
                <form onSubmit={handleEmailVerification} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="find-email">이메일</Label>
                    <Input
                      id="find-email"
                      type="email"
                      placeholder="example@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full">
                    인증번호 발송
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="w-full"
                    onClick={() => {
                      setIsFindPassword(false);
                      resetForm();
                    }}
                  >
                    로그인으로 돌아가기
                  </Button>
                </form>
              )}

              {findPasswordStep === 2 && (
                <form onSubmit={handleVerificationCodeSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="verification-code">인증번호</Label>
                    <Input
                      id="verification-code"
                      type="text"
                      placeholder="6자리 인증번호"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      maxLength={6}
                      required
                    />
                    <p className="text-xs text-gray-500">
                      {email}로 인증번호가 발송되었습니다.
                    </p>
                  </div>
                  <Button type="submit" className="w-full">
                    인증번호 확인
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="w-full"
                    onClick={() => {
                      setFindPasswordStep(1);
                      setVerificationCode("");
                    }}
                  >
                    이전 단계로
                  </Button>
                </form>
              )}

              {findPasswordStep === 3 && (
                <form onSubmit={handlePasswordReset} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="new-password">새 비밀번호</Label>
                    <Input
                      id="new-password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new-confirm-password">새 비밀번호 확인</Label>
                    <Input
                      id="new-confirm-password"
                      type="password"
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full">
                    비밀번호 변경
                  </Button>
                </form>
              )}
            </>
          )}
          
          {!isSignup && !isFindPassword && (
            <div className="mt-4 text-center text-sm text-gray-600">
              <div className="flex gap-2 justify-center">
                <Button 
                  variant="link" 
                  size="sm" 
                  className="text-xs"
                  onClick={() => {
                    setIsSignup(true);
                    resetForm();
                  }}
                >
                  회원가입
                </Button>
                <span className="text-gray-300">|</span>
                <Button variant="link" size="sm" className="text-xs">
                  아이디 찾기
                </Button>
                <span className="text-gray-300">|</span>
                <Button 
                  variant="link" 
                  size="sm" 
                  className="text-xs"
                  onClick={() => {
                    setIsFindPassword(true);
                    resetForm();
                  }}
                >
                  비밀번호 찾기
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
