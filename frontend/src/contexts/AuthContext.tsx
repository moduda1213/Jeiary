import { createContext, useState, useContext, type ReactNode, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { getMe, logout as logoutApi } from '@/api/auth'; 
import type { User, AuthContextType } from "@/types";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const navigate = useNavigate();

    // 로그인 상태 확인 (내 정보 조회)
    const checkLoginStatus = async () => {
        try {
            const userData = await getMe();
            setUser(userData);
            console.log("Login Status Checked: User found", userData);
        } catch (error) {
            console.error("Login Status Check Failed", error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    // 앱 시작 시 로그인 상태 확인
    useEffect(() => {
        checkLoginStatus();
    }, []);

    // 로그인 함수: 실제 API 호출은 LoginPage에서 하고, 여기서는 상태 갱신만 트리거
    const login = () => {
        checkLoginStatus();
    };
    // 로그아웃 함수
    const logout = useCallback(async () => {
        try {
            await logoutApi();
        } catch (error) {
            console.error("로그아웃 실패:", error);
        } finally {
            setUser(null);
            navigate('/login');
        }
    }, [navigate]);
    // 로딩 중일 때 (선택 사항: 전역 로딩 스피너)
    if (loading) {
        return <div className="flex h-screen items-center justify-center">Loading...</div>;
    }

    return (
        <AuthContext.Provider value={{ user, isLoggedIn: !!user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) throw new Error('useAuth must be used within an AuthProvider');
    return context;
};