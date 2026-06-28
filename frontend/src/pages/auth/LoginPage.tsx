import { Link } from "react-router-dom";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { LoginForm } from "../../components/auth/LoginForm";
import { COLORS } from "../../styles/design-tokens";

export const LoginPage = () => {
  return (
    <AuthLayout
      title="Sign in to your account"
      subtitle="Enter your email and password to access your dashboard"
    >
      <LoginForm />

      <div className="mt-6 text-center text-sm text-gray-600">
        Don't have an account?{" "}
        <Link to="/register" className={`font-semibold ${COLORS.primary.text["600"]} ${COLORS.primary.hover.text["700"]}`}>
          Create Account
        </Link>
      </div>
    </AuthLayout>
  );
};
