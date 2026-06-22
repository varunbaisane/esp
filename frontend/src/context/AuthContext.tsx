import React, { createContext, useState, useEffect, type ReactNode } from "react";
import { type AuthContextType, ACCESS_TOKEN_KEY } from "../types/auth";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize auth state from local storage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (storedToken) {
      setToken(storedToken);
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const login = (newToken: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, newToken);
    setToken(newToken);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    setToken(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ token, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
