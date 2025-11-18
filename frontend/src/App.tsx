import { Routes, Route } from 'react-router-dom';
import { LoginPage } from './components/LoginPage';
import { Mainlayout } from './components/MainLayout';
import PrivateRoute from './components/PrivateRoute';
import PublicRoute from './components/PublicRoute';

export default function App() {
  return (
    <Routes>
      {/* 인증이 필요한 라우트 그룹 */}
      {/* element : 이 라우트 내부에 있는 모든 자식 라우트들은 PrivateRoute 컴포넌트의 보호를 받게 됩니다. 즉, isLoggedIn이 true일 때만 접근 가능합니다. */}
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<Mainlayout />} />
      </Route>

      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>
    </Routes>
  )
}