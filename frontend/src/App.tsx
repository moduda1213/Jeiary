import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from "./contexts/ThemeContext";
import { Toaster } from "@/components/ui/sonner";

// 페이지 컴포넌트
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ChatDashboard from './pages/ChatDashboard';
import CalendarView from './pages/CalendarView';

// 레이아웃 컴포넌트 (실제 구현된 파일 사용)
import { MainLayout } from './components/MainLayout';

// 인증 보호 라우트 (실제 로직 적용)
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const { isLoggedIn, loading } = useAuth(); // AuthContext에서 상태 가져옴
    console.log("isLoggedIn: ", isLoggedIn)
    if (loading) {
        return <div>Loading...</div>; // 로딩 중 처리
    }

    if (!isLoggedIn) {
        return <Navigate to="/login" replace />;
    }
    
    // 인증된 경우 MainLayout 적용
    return <MainLayout>{children}</MainLayout>;
};

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <Router>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <ChatDashboard />
              </ProtectedRoute>
            } />
            <Route path="/calendar" element={
              <ProtectedRoute>
                <CalendarView />
              </ProtectedRoute>
            } />
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster />
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}
export default App;