import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { login as loginApi } from '@/api/auth';
import { toast } from "sonner";
import { InputField } from '@/components/common/InputField';

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    // const [error, setError] = useState('');

    const { login, isLoggedIn } = useAuth();
    const navigate = useNavigate();

    // [추가] 로그인 상태가 true가 되면 자동으로 홈으로 이동
    useEffect(() => {
        if (isLoggedIn) {
            navigate('/', { replace: true });
        }
    }, [isLoggedIn, navigate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault(); // 폴 제출 시 새로고침 방지
        setLoading(true);
        //setError('');

        try {
            await loginApi(email, password);
            // AuthContext의 상태 갱신 트리거
            login();
            toast.success("로그인되었습니다."); // 성공 알림
            //navigate('/'); // 홈으로 이동
        } catch (err) {
            toast.error("로그인 실패: 이메일과 비밀번호를 확인해주세요."); // 실패 알림
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen w-full items-center justify-center bg-white p-6 dark:bg-background-dark">
            <div className="flex w-full max-w-2xl flex-col items-center gap-8 text-center">
                {/* 일러스트 플레이스홀더 */}
                {/* Vite 환경에서 public 폴더의 파일은 루트 경로(/)로 접근 가능 */}
                <img
                    src="/LoginImg.png" 
                    alt="로그인 일러스트"
                    className="aspect-video w-full max-w-[360px] object-contain"
                />
                <div className="flex max-w-[480px] flex-col items-center gap-2">
                    <h2 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                        로그인하여 일정을 관리하세요
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        앱의 핵심 기능을 활용하여 당신의 하루를 체계적으로 계획하고 관리할 수 있습니다.
                    </p>
                </div>
                {/* 로그인 폼 컨테이너 */}
                <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 text-left">
                    <InputField
                        id="login-email"
                        label="이메일 주소"
                        type="email"
                        placeholder="example@email.com"
                        value={email}
                        onChange={(e: any) => setEmail(e.target.value)}
                    />
                    <InputField
                        id="login-password"
                        label="비밀번호"
                        type={showPassword ? "text" : "password"}
                        placeholder="********"
                        icon={true}
                        value={password}
                        onChange={(e: any) => setPassword(e.target.value)}
                        onIconClick={() => setShowPassword(!showPassword)}
                    />
                    <button
                        type='submit'
                        disabled={loading}
                        className="flex h-12 w-full cursor-pointer items-center justify-center rounded-lg bg-primary px-5 text-base font-bold text-white transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-70"
                    >
                        {loading ? '로그인 중...' : '로그인'}
                    </button>
                    <div className="flex justify-center gap-4 text-sm text-gray-500">
                        <Link to="/signup" className="hover:text-primary">회원가입</Link>
                        <span>|</span>
                        <button type="button" onClick={() => toast.info("준비 중인 기능입니다.")} className="hover:text-primary">비밀번호 찾기</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;