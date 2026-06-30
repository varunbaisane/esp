import { Link } from "react-router-dom";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { RegisterForm } from "../../components/auth/RegisterForm";
import { COLORS } from "../../styles/design-tokens";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";

export const RegisterPage = () => {
  useDocumentTitle("Register");
  return (
    <AuthLayout
      title="Create your account"
      subtitle="Join ESP to manage your engineering support requests"
    >
      <RegisterForm />

      <div className="mt-6 text-center text-sm text-gray-600">
        Already have an account?{" "}
        <Link to="/login" className={`font-semibold ${COLORS.primary.text["600"]} ${COLORS.primary.hover.text["700"]}`}>
          Sign In
        </Link>
      </div>
    </AuthLayout>
  );
};
