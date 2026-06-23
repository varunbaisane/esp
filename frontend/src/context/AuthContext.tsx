import React, { createContext, useState, useEffect, type ReactNode } from "react";
import { type AuthContextType, type CurrentUser, ACCESS_TOKEN_KEY } from "../types/auth";
import { authService } from "../services/authService";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize auth state from local storage on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      if (storedToken) {
        setToken(storedToken);
        try {
          const user = await authService.me();
          setCurrentUser(user);
          setIsAuthenticated(true);
        } catch (error) {
          console.error("Failed to fetch user", error);
          localStorage.removeItem(ACCESS_TOKEN_KEY);
        }
      }
      setIsLoading(false);
    };
    initializeAuth();
  }, []);

  const login = async (newToken: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, newToken);
    setToken(newToken);
    try {
      const user = await authService.me();
      setCurrentUser(user);
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Failed to fetch user", error);
    }
  };

  const logout = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    setToken(null);
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ token, currentUser, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
