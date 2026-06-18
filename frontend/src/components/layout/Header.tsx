import { Link } from "react-router-dom";
import { Container } from "./Container";

export const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <Container>
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-semibold text-gray-900 tracking-tight">
              Engineering Support Platform
            </h1>
            <nav className="hidden md:flex space-x-6">
              <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Dashboard
              </Link>
              <Link to="/tickets" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Tickets
              </Link>
            </nav>
          </div>
        </div>
      </Container>
    </header>
  );
};
