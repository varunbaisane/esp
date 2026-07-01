import { Link, useLocation } from "react-router-dom";
import { COLORS } from "../../styles/design-tokens";
import { useAuth } from "../../hooks/useAuth";
import { UserAvatar } from "../common/UserAvatar";

interface SidebarProps {
  state: 'full' | 'icon' | 'closed';
  setState: (state: 'full' | 'icon' | 'closed') => void;
}

export const Sidebar = ({ state, setState }: SidebarProps) => {
  const location = useLocation();
  const { currentUser } = useAuth();
  
  const isManagerOrAdmin = currentUser?.roles?.some(role => role === "ADMIN" || role === "ENGINEERING_MANAGER");

  const formatRole = (role: string) => {
    return role.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ');
  };

  const handleLinkClick = () => {
    // Only close the sidebar automatically on mobile
    if (window.innerWidth < 768) {
      setState('closed');
    }
  };

  const isActive = (path: string) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  const navLinkClass = (path: string) => `
    flex items-center p-3 rounded-md text-sm font-medium transition-colors overflow-hidden whitespace-nowrap
    ${isActive(path) 
      ? `bg-cyan-50 ${COLORS.primary.text["700"]}` 
      : "text-gray-600 hover:text-cyan-600 hover:bg-gray-50"}
  `;

  const widthClasses = state === 'full' 
    ? "w-full md:w-56" 
    : (state === 'icon' ? "w-16" : "w-full");
    
  const transformClasses = state === 'closed'
    ? "-translate-x-full"
    : "translate-x-0";

  const textClasses = state === 'full' ? "ml-3 block" : "hidden";

  return (
    <>
      {/* Mobile Backdrop */}
      {state === 'full' && (
        <div 
          className="fixed inset-0 z-20 bg-gray-900/50 md:hidden"
          onClick={() => setState('closed')}
        />
      )}
      
      {/* Sidebar Content */}
      <aside className={`
        fixed inset-y-0 top-[73px] left-0 z-30 bg-white border-r border-gray-200 transform transition-all duration-300 ease-in-out md:static overflow-hidden flex flex-col
        ${widthClasses}
        ${transformClasses}
      `}>
        <nav className="flex-1 px-2 py-4 flex flex-col gap-2 overflow-y-auto">
          <Link to="/workspace" className={navLinkClass("/workspace")} onClick={handleLinkClick}>
            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            <span className={textClasses}>My Workspace</span>
          </Link>
          {isManagerOrAdmin && (
            <>
              <Link to="/team-operations" className={navLinkClass("/team-operations")} onClick={handleLinkClick}>
                <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                <span className={textClasses}>Team Operations</span>
              </Link>
              <Link to="/analytics" className={navLinkClass("/analytics")} onClick={handleLinkClick}>
                <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                <span className={textClasses}>Analytics</span>
              </Link>
              <Link to="/admin" className={navLinkClass("/admin")} onClick={handleLinkClick}>
                <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                <span className={textClasses}>Administration</span>
              </Link>
            </>
          )}
          <Link to="/dashboard" className={navLinkClass("/dashboard")} onClick={handleLinkClick}>
            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
            <span className={textClasses}>Global Operations</span>
          </Link>
          <Link to="/tickets" className={navLinkClass("/tickets")} onClick={handleLinkClick}>
            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
            <span className={textClasses}>Tickets</span>
          </Link>
          <Link to="/activity" className={navLinkClass("/activity")} onClick={handleLinkClick}>
            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span className={textClasses}>Activity</span>
          </Link>
        </nav>
        
        {/* User Card */}
        {currentUser && (
          <div className="mt-auto p-4 border-t border-gray-200 bg-gray-50 flex-shrink-0">
            <div className="flex items-center gap-3">
              <UserAvatar name={currentUser.full_name} size="md" />
              <div className={`${textClasses} overflow-hidden`}>
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {currentUser.full_name}
                </p>
                <p className="text-xs font-medium text-gray-500 truncate">
                  {currentUser.roles && currentUser.roles.length > 0 
                    ? formatRole(currentUser.roles[0]) 
                    : "User"}
                </p>
              </div>
            </div>
          </div>
        )}
      </aside>
    </>
  );
};
