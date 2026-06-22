import { Link } from "react-router-dom";

interface HeaderProps {
  onMenuClick: () => void;
  onLogout: () => void;
}

export const Header = ({ onMenuClick, onLogout }: HeaderProps) => {
  return (
    <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={onMenuClick}
              className="p-2 text-gray-500 hover:text-gray-900 focus:outline-none bg-gray-100 rounded-md"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <Link to="/" className="flex items-center gap-3">
              <span className="font-bold text-gray-900 text-xl tracking-tight">ESP</span>
              <span className="hidden sm:block text-sm font-medium text-gray-500 tracking-wider uppercase border-l border-gray-300 pl-3">Engineering Support Platform</span>
            </Link>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={onLogout}
              className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors flex items-center gap-1.5"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
            <div className="w-8 h-8 rounded-full bg-cyan-100 text-cyan-800 flex items-center justify-center font-bold text-sm ring-2 ring-offset-2 ring-cyan-500/30">
              V
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
