import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authService } from "../../services/authService";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { OTPInput } from "../../components/auth/OTPInput";
import { Button } from "../../components/common/Button";
import { COLORS } from "../../styles/design-tokens";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";

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

export const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const [step, setStep] = useState<"request" | "reset">("request");
  useDocumentTitle(step === "reset" ? "Reset Password" : "Forgot Password");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);

  const [countdown, setCountdown] = useState(60);
  const [canResend, setCanResend] = useState(true);

  useEffect(() => {
    if (countdown > 0 && !canResend && step === "reset") {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0) {
      setCanResend(true);
    }
  }, [countdown, canResend, step]);

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError("Please enter your email.");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      await authService.forgotPassword(email);
      setStep("reset");
      setCanResend(false);
      setCountdown(60);
    } catch (err: any) {
      // For security reasons, the backend returns 200 even if email doesn't exist,
      // but if there's an actual error we display it.
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
        setError(detail || "Something went wrong.");
      }
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
      await authService.forgotPassword(email);
    } catch (err: any) {
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
        setError(detail || "Failed to resend OTP. Please try again later.");
      }
      setCanResend(true);
      setCountdown(0);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp || !newPassword) {
      setError("OTP and new password are required.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      await authService.resetPassword({ email, otp, new_password: newPassword });
      navigate("/login", { state: { message: "Password reset successful! You can now log in." } });
    } catch (err: any) {
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
        setError(detail || "Failed to reset password. The OTP may be invalid or expired.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title={step === "request" ? "Forgot Password" : "Reset Password"}
      subtitle={step === "request" ? "Enter your email to receive a password reset code" : "Enter the verification code and your new password"}
    >
      <form onSubmit={step === "request" ? handleRequestOtp : handleResetPassword} className="space-y-6">
        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm flex items-center gap-2">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {step === "reset" && (
          <div className="p-3 bg-green-50 text-green-700 rounded-md text-sm flex items-center gap-2">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Code sent! Please check your email.</span>
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
              disabled={step === "reset"}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-500`}
            />
          </div>
        </div>

        {step === "reset" && (
          <>
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
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700">
                New Password
              </label>
              <div className="mt-1 relative">
                <input
                  id="new_password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  onFocus={() => setIsPasswordFocused(true)}
                  onBlur={() => setIsPasswordFocused(false)}
                  className={`block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 pr-10 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm`}
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
                    <RequirementItem fulfilled={newPassword.length >= 8} text="Minimum 8 characters" />
                    <RequirementItem fulfilled={/[A-Z]/.test(newPassword)} text="Uppercase letter" />
                    <RequirementItem fulfilled={/[a-z]/.test(newPassword)} text="Lowercase letter" />
                    <RequirementItem fulfilled={/\d/.test(newPassword)} text="Number" />
                    <RequirementItem fulfilled={/[!@#$%^&*(),.?":{}|<>]/.test(newPassword)} text="Special character" />
                  </ul>
                </div>
              </div>
            </div>
          </>
        )}

        <div>
          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? "Processing..." : (step === "request" ? "Send Reset Code" : "Reset Password")}
          </Button>
        </div>

        {step === "reset" && (
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
        )}

        <div className="text-center mt-6 text-sm text-gray-600">
          <Link to="/login" className={`font-semibold ${COLORS.primary.text["600"]} ${COLORS.primary.hover.text["700"]}`}>
            Back to login
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
};
