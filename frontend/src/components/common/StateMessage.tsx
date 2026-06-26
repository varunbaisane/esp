import { Card } from "./Card";
import { Button } from "./Button";

interface StateMessageProps {
  title: string;
  message: string;
  type?: "empty" | "error";
  onRetry?: () => void;
  retryText?: string;
}

export const StateMessage = ({
  title,
  message,
  type = "empty",
  onRetry,
  retryText = "Retry",
}: StateMessageProps) => {
  return (
    <Card className="flex flex-col items-center justify-center p-12 text-center w-full min-h-[300px]">
      <div className={`mb-4 ${type === "error" ? "text-red-500" : "text-gray-400"}`}>
        {type === "error" ? (
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        ) : (
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        )}
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 max-w-sm mb-6">{message}</p>
      
      {onRetry && (
        <Button variant={type === "error" ? "danger" : "secondary"} onClick={onRetry}>
          {retryText}
        </Button>
      )}
    </Card>
  );
};
