import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const PrivateRoute = () => {
    const { isLoggedIn } = useAuth();

    // Outlet : 부모 라우트의 자식 라우트들을 렌더링하는 위치를 지정  -> 즉, 인증된 사용자가 보게 될 페이지 컴포넌트들이 여기에 렌더링됩니다.
    // replace 옵션은 브라우저 히스토리에 현재 경로를 남기지 않아, 사용자가 뒤로 가기 버튼을 눌렀을 때 이전 페이지로 돌아가는 것을 방지
    return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace />;
};
export default PrivateRoute;