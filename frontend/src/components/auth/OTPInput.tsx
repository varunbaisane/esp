import { useRef, useEffect } from "react";
import { COLORS } from "../../styles/design-tokens";

interface OTPInputProps {
  value: string;
  onChange: (value: string) => void;
  onComplete?: () => void;
  length?: number;
  disabled?: boolean;
}

export const OTPInput = ({ value, onChange, onComplete, length = 6, disabled = false }: OTPInputProps) => {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    inputRefs.current = inputRefs.current.slice(0, length);
  }, [length]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
    const val = e.target.value;
    if (/[^0-9]/.test(val)) return; // Only numbers allowed

    const newValue = value.split("");
    // If the user typed a number
    if (val !== "") {
      newValue[index] = val.slice(-1); // Take the last character in case they type fast
      onChange(newValue.join(""));
      
      // Auto-focus next input
      if (index < length - 1) {
        inputRefs.current[index + 1]?.focus();
      } else {
        inputRefs.current[index]?.blur(); // Blur if it's the last one
        onComplete?.();
      }
    } else {
      // If the user deleted the number
      newValue[index] = "";
      onChange(newValue.join(""));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === "Backspace") {
      if (!value[index] && index > 0) {
        // If the box is empty and they press backspace, go to previous and delete it
        const newValue = value.split("");
        newValue[index - 1] = "";
        onChange(newValue.join(""));
        inputRefs.current[index - 1]?.focus();
      }
    } else if (e.key === "ArrowLeft" && index > 0) {
      e.preventDefault();
      inputRefs.current[index - 1]?.focus();
      inputRefs.current[index - 1]?.select();
    } else if (e.key === "ArrowRight" && index < length - 1) {
      e.preventDefault();
      inputRefs.current[index + 1]?.focus();
      inputRefs.current[index + 1]?.select();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text/plain");
    // Ignore spaces and hyphens, keep only digits
    const cleanedData = pastedData.replace(/[\s-]/g, "").replace(/\D/g, "");
    
    if (cleanedData) {
      const sliced = cleanedData.slice(0, length);
      onChange(sliced);
      
      // Auto focus the appropriate input
      if (sliced.length === length) {
        inputRefs.current[length - 1]?.focus();
        onComplete?.();
      } else {
        inputRefs.current[sliced.length]?.focus();
      }
    }
  };

  return (
    <div className="flex justify-between gap-2">
      {Array.from({ length }).map((_, index) => (
        <input
          key={index}
          ref={(el) => { inputRefs.current[index] = el; }}
          type="text"
          inputMode="numeric"
          disabled={disabled}
          value={value[index] || ""}
          onChange={(e) => handleChange(e, index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          onPaste={handlePaste}
          className={`w-10 h-12 sm:w-12 sm:h-14 text-center text-2xl font-semibold rounded-lg border border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 disabled:bg-gray-50 disabled:text-gray-500 transition-colors ${COLORS.primary.ring["500"]} ${COLORS.primary.border["500"]}`}
        />
      ))}
    </div>
  );
};
