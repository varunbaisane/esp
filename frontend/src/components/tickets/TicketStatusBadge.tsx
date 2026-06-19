import type { TicketStatus } from "../../types/ticket";
import { COLORS } from "../../styles/design-tokens";

interface TicketStatusBadgeProps {
  status: TicketStatus;
}

export const TicketStatusBadge = ({ status }: TicketStatusBadgeProps) => {
  const styles = COLORS.status[status] || COLORS.status.CLOSED;
  const formattedStatus = status.replace("_", " ");
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles.bg} ${styles.text} ${styles.border}`}>
      {formattedStatus}
    </span>
  );
};
