import { useState } from "react";
import { AuthFormActions } from "./AuthFormActions";
import type { LoginRequest } from "../../types/auth";
import { COLORS } from "../../styles/design-tokens";

export const LoginForm = () => {
  const [formData, setFormData] = useState<LoginRequest>({
    email: "",
    password: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Phase 5.8: No logic, just UI structure
    console.log("Login submitted:", formData);
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <label className="block text-sm font-medium text-gray-700">Email address</label>
        <div className="mt-1">
          <input
            type="email"
            required
            className={`appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm`}
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Password</label>
        <div className="mt-1">
          <input
            type="password"
            required
            className={`appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]} sm:text-sm`}
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <input
            id="remember-me"
            name="remember-me"
            type="checkbox"
            className={`h-4 w-4 ${COLORS.primary.text["600"]} focus:ring-cyan-500 border-gray-300 rounded`}
          />
          <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
            Remember me
          </label>
        </div>

        <div className="text-sm">
          <a href="#" className={`font-medium ${COLORS.primary.text["600"]} ${COLORS.primary.hover.text["700"]}`}>
            Forgot your password?
          </a>
        </div>
      </div>

      <AuthFormActions submitText="Sign in" />
    </form>
  );
};
