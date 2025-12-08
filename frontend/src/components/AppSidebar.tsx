import { useLocation, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { ThemeToggle } from './ThemeToggle';

// 내부 NavItem 컴포넌트 정의
const NavItem = ({ url, icon, label, isActive }: { url: string; icon: string; label: string; isActive: boolean }) => {
    return (
      <Link
        to={url}
        className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 transition-colors ${
          isActive
            ? 'bg-primary/10 text-primary'
            : 'text-gray-600 hover:bg-gray-200/60 dark:text-gray-400 dark:hover:bg-gray-800'
        }`}
      >
        <span className={`material-symbols-outlined ${isActive ? 'filled' : ''}`}>{icon}</span>
        <p className="text-sm font-medium leading-normal">{label}</p>
      </Link>
    );
};
export function AppSidebar() {
    const { user, logout } = useAuth();
    const location = useLocation();

    const items = [
        { title: "홈", url: "/", icon: "home" },
        { title: "일정", url: "/calendar", icon: "calendar_month" },
    ];

    return (
        <aside className="flex w-64 flex-col border-r border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-[#161f29]">
            <div className="flex h-full flex-col justify-between">
                <div className="flex flex-col gap-6">
                    {/* User Profile */}
                    {user && (
                        <div className="flex items-center gap-3">
                            {/* 아바타 이미지: user.avatarUrl이 있으면 배경이미지로, 없으면 기본 회색 원 */}
                            <div
                                className="size-10 rounded-full bg-cover bg-center bg-no-repeat bg-gray-200 dark:bg-gray-700"
                                style={user.avatarUrl ? { backgroundImage: `url("${user.avatarUrl}")` } : {}}
                                aria-label="User profile picture"
                            >
                                {!user.avatarUrl && (
                                    <div className="flex h-full w-full items-center justify-center text-sm font-medium text-gray-500">
                                        {user.name?.[0] || user.email[0].toUpperCase()}
                                    </div>
                                )}
                            </div>
                            <div className="flex flex-col overflow-hidden">
                                <h1 className="truncate text-base font-medium leading-normal text-gray-900 dark:text-white">
                                    {user.name || user.email.split('@')[0]}
                                </h1>
                                <p className="truncate text-sm font-normal leading-normal text-gray-500 dark:text-gray-400">
                                    {user.email}
                                </p>
                            </div>
                        </div>
                    )}
                    {/* Navigation */}
                    <nav className="flex flex-col gap-2">
                        {items.map((item) => (
                            <NavItem
                                key={item.url}
                                url={item.url}
                                icon={item.icon}
                                label={item.title}
                                isActive={location.pathname === item.url}
                            />
                        ))}
                    </nav>
                </div>
                {/* Footer (Logout & Theme) */}
                <div className="flex gap-2 border-t border-gray-200 pt-6 dark:border-gray-700">
                    <button
                        onClick={logout}
                        className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-gray-600 hover:bg-gray-200/60 dark:text-gray-400 dark:hover:bg-gray-800"
                    >
                        <span className="material-symbols-outlined">logout</span>
                        <p className="text-sm font-medium leading-normal">로그아웃</p>
                    </button>
                    {/* 테마 토글 버튼 배치 (선택 사항: 디자인에 맞춰 위치 조정 가능) */}
                    <div className="px-3">
                         <ThemeToggle />
                    </div>
                </div>
            </div>
        </aside>
    );
}