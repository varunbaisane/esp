export const ACCESS_TOKEN_KEY = "access_token";

export const Roles = {
  ADMIN: "ADMIN",
  ENGINEERING_MANAGER: "ENGINEERING_MANAGER",
  SUPPORT_L1: "SUPPORT_L1",
  SUPPORT_L2: "SUPPORT_L2",
  SUPPORT_L3: "SUPPORT_L3",
} as const;

export type RoleName = typeof Roles[keyof typeof Roles];

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: number;
  email: string;
  full_name: string;
  roles: string[];
}

export interface AuthState {
  token: string | null;
  currentUser: CurrentUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthContextType extends AuthState {
  login: (token: string, rememberMe?: boolean) => Promise<void>;
  logout: () => void;
}

export interface ResetPasswordRequest {
  email: string;
  otp: string;
  new_password: string;
}
