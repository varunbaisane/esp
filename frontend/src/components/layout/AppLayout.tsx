import type { ReactNode } from "react";
import { Header } from "./Header";
import { Container } from "./Container";

interface AppLayoutProps {
  children: ReactNode;
}

export const AppLayout = ({ children }: AppLayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <main className="flex-grow py-8">
        <Container>{children}</Container>
      </main>
    </div>
  );
};
