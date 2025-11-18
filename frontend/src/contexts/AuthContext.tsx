import { createContext, useState, useContext, type ReactNode, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from '../api/client'; // API 클라이언트 임포트
import { motion } from "motion/react";


// AuthContext가 제공할 값의 타입을 정의
interface AuthContextType {
    isLoggedIn: boolean;
    login: () => void;
    logout: () => void;
    // httpOnly 쿠키 방식에서는 accessToken을 직접 프론트엔드에서 관리하지 않습니다.
    // 필요하다면 백엔드에 인증 상태를 확인하는 API를 호출하여 isLoggedIn을 업데이트합니다.
}

// 기본 컨텍스트 값 (초기 상태)
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider 컴포넌트의 props 타입을 정의합니다.
interface AuthProviderProps {
    children: ReactNode;
}

// AuthProvider 컴포넌트 : 인증 상태를 관리하고 하위 컴포넌트에 제공
export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(true);
    const navigate = useNavigate();

    // 앱 로드 시 로그인 상태를 확인하는 함수
    const checkLoginStatus = async() => {
        try {
            // 백엔드에 로그인 상태를 확인하는 API 호출 (예: /auth/me)
            // 이 API는 유효한 access_token 쿠키가 있으면 200 OK를 반환해야 합니다.
            await apiClient.get('/auth/me');
            setIsLoggedIn(true)
        } catch(error) {
            setIsLoggedIn(false);
        } finally {
            setLoading(false);
        }
    };

    // 컴포넌트 마운트 시 로그인 상태 확인
    useEffect(() => {
        checkLoginStatus();
    }, []);

    // 로그인 함수 : 로그인 성공 시 호출
    const login = () => {
        setIsLoggedIn(true);
    }

    // 로그아웃 함수
    // logout 함수를 useCallback으로 감싸지 않으면, 
    // AuthProvider 컴포넌트가 리렌더링될 때마다 이름만 같고 실제로는 새로운 `logout` 함수가 계속 만들어집니다
    // useEffect 비서는 logout 함수도 감시 대상([isLoggedIn, logout])으로 두고 있는데, logout 함수가 계속 새로운 것으로 바뀌니 "어? 감시 대상이 바뀌었네!"라고 착각하여, 
    // 멀쩡한 감청 장치를 떼고 새로 설치하는 불필요한 일을 반복하게 됩니다.
    const logout = useCallback(async () => {
        try {
            await apiClient.post('/auth/logout');
        } catch(error) {
            console.error("로그아웃 실패: ", error);
            // 에러가 발생해도 클라이언트 측에서는 로그아웃 상태로 전환
        } finally {
            setIsLoggedIn(false);
            navigate('/login')
        }
    },[navigate]);

    useEffect(() => {
        const handleLogoutEvent = () => {
            console.log("AuthContext: 'auth:logout' event received. Logging out.");
            // 이미 로그아웃 상태가 아니라면 로그아웃 처리
            //if (isLoggedIn) {
            logout();
            //}
        }

        window.addEventListener('auth:logout', handleLogoutEvent);

        return () => {
            window.removeEventListener('auth:logout', handleLogoutEvent);
        };
    }, [isLoggedIn, logout]);

    // 로딩 중일 때는 아무것도 렌더링하지 않거나 로딩 스피너를 보여줄 수 있습니다.
    if(loading) {
        return (
            <div className="absolute inset-0 flex items-center justify-center">
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
        );
    }

    return (
        <AuthContext.Provider value={{isLoggedIn, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
};

// AuthContext를 쉽게 사용할 수 있도록 커스텀 훅으로 제공
export const useAuth = () => {
    const context = useContext(AuthContext);
    if(context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};






/**
 * AuthContext 구현 이유
 * 1. 로그인 상테를 전역에서 관리
 * 2. HttpOnly 쿠키 인증 방식을 사용하므로 로그인 여부만 서버를 통해 확인
 * 3. login, logout 과 같은 코드 중복 제거 및 유지보수 단순화
 * 
 =======================================================================================
 * 핵심 정리

    AuthContext: 저장소 생성
    AuthProvider: 상태 관리 + 함수 제공 + Context에 값 주입
    useState: 상태 저장 (isLoggedIn, loading)
    useEffect: 자동 초기화 (checkLoginStatus 실행)
    checkLoginStatus: API로 로그인 상태 확인
    login/logout: 상태 변경 함수
    Context.Provider: 하위 컴포넌트에 값 전달
    useAuth: 간편하게 Context 값 사용

    모든 요소가 상태 관리 → 함수 제공 → 전역 공유 → 간편 사용의 흐름으로 연결됩니다!

=======================================================================================

## 전체 연결 구조도
```
┌─────────────────────────────────────────┐
│         App.tsx (최상위)                 │
│  <AuthProvider>                         │
│    <Routes>...</Routes>                 │
│  </AuthProvider>                        │
└─────────────────────────────────────────┘
            ↓ children prop
┌─────────────────────────────────────────┐
│      AuthProvider 컴포넌트               │
│                                          │
│  ┌────────────────────────────────┐    │
│  │ 상태 관리                       │    │
│  │ - isLoggedIn (boolean)         │    │
│  │ - loading (boolean)            │    │
│  └────────────────────────────────┘    │
│            ↓                             │
│  ┌────────────────────────────────┐    │
│  │ 함수들                          │    │
│  │ - checkLoginStatus()           │─────┼─→ apiClient.get('/auth/me')
│  │ - login()                      │    │
│  │ - logout()                     │─────┼─→ apiClient.post('/auth/logout')
│  └────────────────────────────────┘    │
│            ↓                             │
│  ┌────────────────────────────────┐    │
│  │ Context.Provider               │    │
│  │ value={{isLoggedIn,login,logout}}  │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
            ↓ Context 값 제공
┌─────────────────────────────────────────┐
│      하위 컴포넌트들                     │
│                                          │
│  const { isLoggedIn } = useAuth();     │
│    ↓                                     │
│  useContext(AuthContext) 호출           │
│    ↓                                     │
│  Provider의 value 사용                  │
└─────────────────────────────────────────┘
 */