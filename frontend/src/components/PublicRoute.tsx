import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const PublicRoute = () => {
    const { isLoggedIn } = useAuth();

    return isLoggedIn ? <Navigate to="/" replace /> : <Outlet />;
};

export default PublicRoute