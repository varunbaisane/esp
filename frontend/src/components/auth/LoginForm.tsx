import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthFormActions } from "./AuthFormActions";
import type { LoginRequest } from "../../types/auth";
import { authService } from "../../services/authService";
import { useAuth } from "../../hooks/useAuth";
import { COLORS } from "../../styles/design-tokens";
import axios from "axios";

export const LoginForm = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<LoginRequest>({
    email: "",
    password: "",
    remember_me: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await authService.login(formData);
      await login(response.access_token, formData.remember_me);
      navigate("/dashboard");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setError(err.response?.data?.detail || "Invalid email or password");
        } else if (err.response?.status === 403) {
          navigate("/verify-email", { state: { email: formData.email } });
        } else if (err.response?.status === 422) {
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

      <div>
        <label className="block text-sm font-medium text-gray-700">Password</label>
        <div className="mt-1 relative">
          <input
            type={showPassword ? "text" : "password"}
            required
            disabled={isLoading}
            className={`appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm disabled:opacity-50 disabled:bg-gray-50`}
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
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
        </div>
      </div>

      <div className="flex items-center justify-between">
        <label className="flex items-center group cursor-pointer select-none">
          <div className="relative flex items-center justify-center">
            <input
              type="checkbox"
              className="peer sr-only"
              checked={formData.remember_me}
              onChange={(e) => setFormData({ ...formData, remember_me: e.target.checked })}
            />
            <div className={`w-5 h-5 border-2 rounded transition-all duration-200 ease-in-out ${
              formData.remember_me 
                ? 'bg-cyan-600 border-cyan-600' 
                : 'bg-white border-gray-300 group-hover:border-cyan-500'
            }`}></div>
            <svg 
              className={`absolute w-3.5 h-3.5 text-white pointer-events-none transition-transform duration-200 ease-in-out ${
                formData.remember_me ? 'scale-100 opacity-100' : 'scale-50 opacity-0'
              }`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <span className="ml-2.5 text-sm font-medium text-gray-700 group-hover:text-gray-900">
            Remember me
          </span>
        </label>

        <div className="text-sm">
          <Link to="/forgot-password" className={`font-medium ${COLORS.primary.text["600"]} ${COLORS.primary.hover.text["700"]}`}>
            Forgot your password?
          </Link>
        </div>
      </div>

      <AuthFormActions submitText="Sign in" isLoading={isLoading} />
    </form>
  );
};
