import React from 'react';
import { User, ViewState } from '../types';

interface SidebarProps {
  user: User;
  currentView: ViewState;
  onNavigate: (view: ViewState) => void;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, currentView, onNavigate, onLogout }) => {
  const NavItem = ({ view, icon, label }: { view: ViewState; icon: string; label: string }) => {
    const isActive = currentView === view;
    return (
      <button
        onClick={() => onNavigate(view)}
        className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 transition-colors ${
          isActive
            ? 'bg-primary/10 text-primary'
            : 'text-gray-600 hover:bg-gray-200/60 dark:text-gray-400 dark:hover:bg-gray-800'
        }`}
      >
        <span className={`material-symbols-outlined ${isActive ? 'filled' : ''}`}>{icon}</span>
        <p className="text-sm font-medium leading-normal">{label}</p>
      </button>
    );
  };

  return (
    <aside className="flex h-full w-64 flex-col border-r border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-[#161f29]">
      <div className="flex h-full flex-col justify-between">
        <div className="flex flex-col gap-6">
          {/* User Profile */}
          <div className="flex items-center gap-3">
            <div
              className="size-10 rounded-full bg-cover bg-center bg-no-repeat"
              style={{ backgroundImage: `url("${user.avatarUrl}")` }}
              aria-label="User profile picture"
            ></div>
            <div className="flex flex-col overflow-hidden">
              <h1 className="truncate text-base font-medium leading-normal text-gray-900 dark:text-white">
                {user.name}
              </h1>
              <p className="truncate text-sm font-normal leading-normal text-gray-500 dark:text-gray-400">
                {user.email}
              </p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex flex-col gap-2">
            <NavItem view={ViewState.HOME} icon="home" label="홈" />
            <NavItem view={ViewState.CALENDAR} icon="calendar_month" label="일정" />
          </nav>
        </div>

        {/* Logout */}
        <div className="flex flex-col gap-1">
          <button
            onClick={onLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-gray-600 hover:bg-gray-200/60 dark:text-gray-400 dark:hover:bg-gray-800"
          >
            <span className="material-symbols-outlined">logout</span>
            <p className="text-sm font-medium leading-normal">로그아웃</p>
          </button>
        </div>
      </div>
    </aside>
  );
};
