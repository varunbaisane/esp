import { Button } from "../common/Button";
import { ButtonLoader } from "../common/ButtonLoader";

interface TicketFormActionsProps {
  loading: boolean;
}

export const TicketFormActions = ({ loading }: TicketFormActionsProps) => {
  return (
    <div className="pt-4 flex items-center justify-end space-x-4 border-t border-gray-200 mt-6">
      <Button 
        to="/tickets" 
        variant="ghost"
        aria-disabled={loading}
      >
        Cancel
      </Button>
      <Button
        type="submit"
        variant="primary"
        disabled={loading}
      >
        {loading ? <ButtonLoader text="Creating..." /> : "Create Ticket"}
      </Button>
    </div>
  );
};
