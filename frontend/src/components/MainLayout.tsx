import React from 'react';
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from './AppSidebar';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
    return (
      <SidebarProvider>
        <AppSidebar />
        <main className="flex-1 flex flex-col min-h-0 w-full">
          <div className="p-4 border-b flex items-center gap-2 md:hidden">
              <SidebarTrigger />
              <span className="font-semibold">Jeiary</span>
          </div>
          <div className="flex-1 overflow-auto bg-white dark:bg-[#101922] relative">
              {children}
          </div>
        </main>
      </SidebarProvider>
    );
  };