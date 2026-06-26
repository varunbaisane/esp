import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthFormActions } from "./AuthFormActions";
import type { RegisterRequest } from "../../types/auth";
import { authService } from "../../services/authService";
import { COLORS } from "../../styles/design-tokens";
import axios from "axios";

export const RegisterForm = () => {
  const navigate = useNavigate();
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
      // Redirect to login page on success
      navigate("/login");
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setError("Email already registered");
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
            type="password"
            required
            disabled={isLoading}
            className={`appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm disabled:opacity-50 disabled:bg-gray-50`}
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            onFocus={() => setIsPasswordFocused(true)}
            onBlur={() => setIsPasswordFocused(false)}
          />
          
          {/* Password Requirements Tooltip */}
          <div 
            className={`absolute z-10 left-0 top-full mt-2 w-full bg-white border border-slate-200 rounded-xl shadow-sm p-4 transition-all duration-200 ease-in-out ${
              isPasswordFocused ? 'opacity-100 translate-y-0 visible' : 'opacity-0 -translate-y-1 invisible'
            }`}
          >
            <p className="text-xs font-semibold text-gray-700 mb-2">Password Requirements</p>
            <ul className="text-xs text-gray-500 space-y-1.5">
              <li className="flex items-center gap-2">
                <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                Minimum 12 characters
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                Uppercase letter
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                Lowercase letter
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                Number
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                Special character
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
        <div className="mt-1">
          <input
            type="password"
            required
            disabled={isLoading}
            className={`appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm disabled:opacity-50 disabled:bg-gray-50`}
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
          />
        </div>
      </div>

      <AuthFormActions submitText="Create Account" isLoading={isLoading} />
    </form>
  );
};
