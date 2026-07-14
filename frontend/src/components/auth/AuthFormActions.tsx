import { Button } from "../common/Button";
import { ButtonLoader } from "../common/ButtonLoader";

interface AuthFormActionsProps {
  submitText: string;
  isLoading?: boolean;
}

export const AuthFormActions = ({ submitText, isLoading }: AuthFormActionsProps) => {
  return (
    <div className="space-y-4">
      <Button type="submit" variant="primary" className="w-full" disabled={isLoading}>
        {isLoading ? <ButtonLoader text={submitText} /> : submitText}
      </Button>
    </div>
  );
};
