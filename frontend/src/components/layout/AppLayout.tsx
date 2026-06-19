import { useState, useEffect, type ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface AppLayoutProps {
  children: ReactNode;
}

type SidebarState = 'full' | 'icon' | 'closed';

export const AppLayout = ({ children }: AppLayoutProps) => {
  const [sidebarState, setSidebarState] = useState<SidebarState>('closed');

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      setSidebarState(prev => {
        if (width >= 1024) {
          return prev === 'closed' ? 'full' : prev;
        } else if (width >= 768) {
          return prev === 'closed' ? 'icon' : prev;
        } else {
          return 'closed';
        }
      });
    };

    // Set initial state
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSidebar = () => {
    setSidebarState(prev => {
      if (window.innerWidth >= 768) {
        return prev === 'full' ? 'icon' : 'full';
      } else {
        return prev === 'closed' ? 'full' : 'closed';
      }
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header spans full width */}
      <Header onMenuClick={toggleSidebar} />

      <div className="flex-1 flex min-h-0 relative">
        <Sidebar state={sidebarState} setState={setSidebarState} />

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
