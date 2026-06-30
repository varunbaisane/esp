import { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { authService } from "../../services/authService";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { OTPInput } from "../../components/auth/OTPInput";
import { Button } from "../../components/common/Button";
import { COLORS } from "../../styles/design-tokens";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";

export const VerifyEmailPage = () => {
  useDocumentTitle("Verify Email");
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [countdown, setCountdown] = useState(60);
  const [canResend, setCanResend] = useState(true);

  useEffect(() => {
    if (countdown > 0 && !canResend) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0) {
      setCanResend(true);
    }
  }, [countdown, canResend]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !otp) {
      setError("Email and OTP are required.");
      return;
    }
    if (otp.length !== 6) {
      setError("OTP must be 6 digits.");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      await authService.verifyEmail(email, otp);
      navigate("/login", { state: { message: "Email verified successfully! You can now log in." } });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to verify email. The OTP may be invalid or expired.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (!email) {
      setError("Please enter your email to resend OTP.");
      return;
    }
    
    setError(null);
    setCanResend(false);
    setCountdown(60);
    
    try {
      await authService.sendVerificationOtp(email);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to resend OTP. Please try again later.");
      setCanResend(true);
      setCountdown(0);
    }
  };

  return (
    <AuthLayout
      title="Verify Email"
      subtitle="Enter the 6-digit code sent to your email"
    >
      <form onSubmit={handleVerify} className="space-y-6">
        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm flex items-center gap-2">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <div className="mt-1">
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm`}
            />
          </div>
        </div>

        <div>
          <label htmlFor="otp" className="block text-sm font-medium text-gray-700">
            Verification Code
          </label>
          <div className="mt-2">
            <OTPInput
              value={otp}
              onChange={setOtp}
              disabled={isLoading}
            />
          </div>
        </div>

        <div>
          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? "Verifying..." : "Verify Email"}
          </Button>
        </div>
        
        <div className="text-center text-sm text-gray-600 mt-4">
          Didn't receive the code?{" "}
          <button 
            type="button" 
            onClick={handleResend}
            disabled={!canResend}
            className={`font-semibold ${!canResend ? 'text-gray-400 cursor-not-allowed' : COLORS.primary.text["600"] + ' ' + COLORS.primary.hover.text["700"]}`}
          >
            {canResend ? 'Resend Code' : `Resend in ${countdown}s`}
          </button>
        </div>
        
        <div className="text-center mt-6 text-sm text-gray-600">
          <Link to="/login" className={`font-semibold ${COLORS.primary.text["600"]} ${COLORS.primary.hover.text["700"]}`}>
            Back to login
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
};
