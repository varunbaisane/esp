import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthFormActions } from "./AuthFormActions";
import type { RegisterRequest } from "../../types/auth";
import { authService } from "../../services/authService";
import { useAuth } from "../../hooks/useAuth";
import { COLORS } from "../../styles/design-tokens";
import axios from "axios";
import { GoogleLogin } from "@react-oauth/google";
import type { CredentialResponse } from "@react-oauth/google";

const RequirementItem = ({ fulfilled, text }: { fulfilled: boolean, text: string }) => (
  <li className={`flex items-center gap-2 transition-colors duration-200 ${fulfilled ? 'text-green-600' : ''}`}>
    <div className="w-4 flex justify-center items-center shrink-0">
      {fulfilled ? (
        <svg className="w-3.5 h-3.5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <span className="w-1 h-1 rounded-full bg-gray-400"></span>
      )}
    </div>
    {text}
  </li>
);

export const RegisterForm = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [formData, setFormData] = useState<RegisterRequest & { confirmPassword: string }>({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);
    try {
      await authService.register({
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
      });
      navigate("/registration-success");
    } catch (err: any) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 409) {
          setError(err.response?.data?.detail || "Email already registered");
        } else if (err.response?.status === 422) {
          // Validation error might have multiple detail items, we should format them nicely
          const detail = err.response?.data?.detail;
          if (Array.isArray(detail)) {
            setError(detail.map((d: any) => {
              const field = d.loc[d.loc.length - 1];
              let cleanMsg = d.msg.replace(/^Value error,\s*/i, '');
              
              if (typeof field === 'string') {
                const fieldName = field.charAt(0).toUpperCase() + field.slice(1);
                if (cleanMsg.toLowerCase().startsWith(field.toLowerCase())) {
                  cleanMsg = cleanMsg.charAt(0).toUpperCase() + cleanMsg.slice(1);
                  return cleanMsg;
                }
                cleanMsg = cleanMsg.charAt(0).toUpperCase() + cleanMsg.slice(1);
                return `${fieldName}: ${cleanMsg}`;
              }
              return cleanMsg;
            }).join(' | '));
          } else {
            setError(detail || "Validation Error");
          }
        } else if (err.response?.status === 500) {
          setError("Internal Server Error");
        } else {
          setError(err.response?.data?.detail || "Unable to connect to server");
        }
      } else {
        setError("Unable to connect to server");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
          {error}
        </div>
      )}

      <div className="flex justify-center w-full">
        <GoogleLogin
          onSuccess={async (credentialResponse: CredentialResponse) => {
            if (!credentialResponse.credential) return;
            setError(null);
            setIsLoading(true);
            try {
              const response = await authService.loginWithGoogle(credentialResponse.credential);
              await login(response.access_token, false);
              navigate("/dashboard");
            } catch (err) {
               if (axios.isAxiosError(err) && err.response?.data?.detail) {
                  setError(err.response.data.detail);
               } else {
                  setError("Google signup failed");
               }
            } finally {
              setIsLoading(false);
            }
          }}
          onError={() => {
            setError("Google signup failed");
          }}
          useOneTap={false}
          theme="outline"
          size="large"
          text="continue_with"
          shape="rectangular"
          width="100%"
        />
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">Or continue with</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Full Name</label>
        <div className="mt-1">
          <input
            type="text"
            required
            disabled={isLoading}
            className={`appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm disabled:opacity-50 disabled:bg-gray-50`}
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Email address</label>
        <div className="mt-1">
          <input
            type="email"
            required
            disabled={isLoading}
            className={`appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm disabled:opacity-50 disabled:bg-gray-50`}
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>
      </div>

      <div className="relative">
        <label className="block text-sm font-medium text-gray-700">Password</label>
        <div className="mt-1 relative">
          <input
            type={showPassword ? "text" : "password"}
            required
            disabled={isLoading}
            className={`appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm disabled:opacity-50 disabled:bg-gray-50`}
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            onFocus={() => setIsPasswordFocused(true)}
            onBlur={() => setIsPasswordFocused(false)}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
            onClick={() => setShowPassword(!showPassword)}
            tabIndex={-1}
          >
            {showPassword ? (
              <svg className="w-5 h-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            )}
          </button>
          
          {/* Password Requirements Tooltip */}
          <div 
            className={`absolute z-20 left-0 top-full mt-3 md:left-full md:top-0 md:mt-0 md:ml-4 w-full md:w-64 bg-white border border-slate-200 rounded-xl shadow-lg p-4 transition-all duration-200 ease-in-out ${
              isPasswordFocused ? 'opacity-100 translate-y-0 md:translate-x-0 visible' : 'opacity-0 -translate-y-1 md:translate-y-0 md:-translate-x-2 invisible'
            }`}
          >
            {/* Tooltip Arrow */}
            <div className="absolute w-3 h-3 bg-white rotate-45 
              -top-1.5 left-6 border-l border-t border-slate-200
              md:top-4 md:-left-1.5 md:border-t-0 md:border-b md:border-slate-200
            "></div>
            
            <p className="text-xs font-semibold text-gray-700 mb-2 relative z-10">Password Requirements</p>
            <ul className="text-xs text-gray-500 space-y-1.5 relative z-10">
              <RequirementItem fulfilled={formData.password.length >= 8} text="Minimum 8 characters" />
              <RequirementItem fulfilled={/[A-Z]/.test(formData.password)} text="Uppercase letter" />
              <RequirementItem fulfilled={/[a-z]/.test(formData.password)} text="Lowercase letter" />
              <RequirementItem fulfilled={/\d/.test(formData.password)} text="Number" />
              <RequirementItem fulfilled={/[!@#$%^&*(),.?":{}|<>]/.test(formData.password)} text="Special character" />
            </ul>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
        <div className="mt-1 relative">
          <input
            type={showConfirmPassword ? "text" : "password"}
            required
            disabled={isLoading}
            className={`appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm disabled:opacity-50 disabled:bg-gray-50`}
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            tabIndex={-1}
          >
            {showConfirmPassword ? (
              <svg className="w-5 h-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            )}
          </button>
        </div>
      </div>

      <AuthFormActions submitText="Create Account" isLoading={isLoading} />
    </form>
  );
};
