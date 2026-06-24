import { Link, useLocation } from "react-router-dom";
import { COLORS } from "../../styles/design-tokens";

interface SidebarProps {
  state: 'full' | 'icon' | 'closed';
  setState: (state: 'full' | 'icon' | 'closed') => void;
}

export const Sidebar = ({ state, setState }: SidebarProps) => {
  const location = useLocation();

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
        fixed inset-y-0 top-[73px] left-0 z-30 bg-white border-r border-gray-200 transform transition-all duration-300 ease-in-out md:static overflow-hidden
        ${widthClasses}
        ${transformClasses}
      `}>
        <nav className="px-2 py-4 flex flex-col gap-2">
          <Link to="/" className={navLinkClass("/")} onClick={handleLinkClick}>
            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
            <span className={textClasses}>Dashboard</span>
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
      </aside>
    </>
  );
};
