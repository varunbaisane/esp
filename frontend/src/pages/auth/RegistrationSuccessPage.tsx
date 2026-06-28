import { Link } from "react-router-dom";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { Button } from "../../components/common/Button";


export const RegistrationSuccessPage = () => {
  return (
    <AuthLayout
      title="Registration Successful"
      subtitle="We've sent a verification code to your email."
    >
      <div className="flex flex-col items-center justify-center py-6">
        <svg className="w-16 h-16 text-emerald-500 mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        
        <p className="text-center text-gray-600 mb-8 px-4">
          Please check your inbox (and spam folder) for a 6-digit OTP to verify your account.
        </p>

        <Link to="/verify-email" className="w-full">
          <Button type="button" className="w-full">
            Continue to Verification
          </Button>
        </Link>
      </div>
    </AuthLayout>
  );
};
