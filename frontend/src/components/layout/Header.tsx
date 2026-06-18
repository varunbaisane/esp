import { Container } from "./Container";

export const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <Container>
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900 tracking-tight">
              Engineering Support Platform
            </h1>
          </div>
        </div>
      </Container>
    </header>
  );
};
