import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signup as signupApi } from '@/api/auth';
import { toast } from "sonner";
import { InputField } from '@/components/common/InputField';

interface ErrResponse {
    response?: {
        status: number,
        data: {
            detail: string
        }
    }
}

const SignupPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // 비밀번호 표시 상태 관리
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password || !confirmPassword) {
        toast.error("모든 필드를 입력해주세요.");
        return;
    }
    if (password !== confirmPassword) {
        toast.error('비밀번호가 일치하지 않습니다.');
        return;
    }
    if (password.length < 8) {
        toast.error('비밀번호는 8자 이상이어야 합니다.');
        return;
    }

    // 1. 숫자 포함 여부 확인
    if (!/\d/.test(password)) {
        toast.error('비밀번호에 숫자가 포함되어야 합니다.');
        return;
    }
    // 2. 영문자 포함 여부 확인
    if (!/[A-Za-z]/.test(password)) {
        toast.error('비밀번호에 영문자가 포함되어야 합니다.');
        return;
    }
    // 3. 특수문자 포함 여부 확인
    if (!/[!@#$%^&*]/.test(password)) {
        toast.error('비밀번호에 특수문자가 포함되어야 합니다.');
        return;
    }

    setLoading(true);

    try {
      await signupApi(email, password);
      toast.success('회원가입 성공! 로그인해주세요.');
      navigate('/login');

    } catch (error: unknown) {
      console.error(error);
      const err = error as ErrResponse;
      toast.error(err.response?.data.detail);
      
    } finally {
      setLoading(false);
    }
  };

  return (
        <div className="relative flex min-h-screen w-full flex-col items-center justify-center bg-[#f6f7f8] p-4 dark:bg-background-dark">
            {/* 배경 블러 효과 오버레이 */}
            <div className="absolute inset-0 bg-slate-900/30 backdrop-blur-sm dark:bg-background-dark/60"></div>
            {/* 회원가입 카드 */}
            <div className="relative w-full max-w-md rounded-xl bg-white p-8 shadow-2xl dark:bg-[#101922] md:p-10">
                <h1 className="text-center text-3xl font-bold tracking-tight text-[#1E1E1E] dark:text-white">
                    회원가입
                </h1>
                <form className="mt-8 flex flex-col gap-6" onSubmit={handleSubmit}>
                    <InputField
                        id="signup-email"
                        label="이메일 주소"
                        type="email"
                        placeholder="example@email.com"
                        value={email}
                        onChange={(e: any) => setEmail(e.target.value)}
                    />
                    <InputField
                        id="signup-password"
                        label="비밀번호"
                        type={showPassword ? "text" : "password"}
                        placeholder="8자 이상 입력해주세요"
                        icon={true}
                        value={password}
                        onChange={(e: any) => setPassword(e.target.value)}
                        onIconClick={() => setShowPassword(!showPassword)}
                    />
                    <InputField
                        id="signup-confirm"
                        label="비밀번호 확인"
                        type={showConfirmPassword ? "text" : "password"}
                        placeholder="비밀번호를 다시 입력해주세요"
                        icon={true}
                        value={confirmPassword}
                        onChange={(e: any) => setConfirmPassword(e.target.value)}
                        onIconClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    />
                    <div className="mt-2">
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex h-12 w-full cursor-pointer items-center justify-center rounded-lg bg-primary px-5 text-base font-bold text-white transition-colors hover:bg-primary/90       
       focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-70"
                        >
                            {loading ? '가입 중...' : '회원가입'}
                        </button>
                    </div>
                </form>
                <div className="mt-6 text-center">
                    <p className="text-sm text-[#6B7280] dark:text-gray-400">
                        이미 계정이 있으신가요?{' '}
                        <Link to="/login" className="font-bold text-primary hover:underline">
                            로그인
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};
export default SignupPage;