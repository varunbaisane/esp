import { Card } from "./Card";

interface LoadingStateProps {
  message?: string;
}

export const LoadingState = ({ message = "Loading..." }: LoadingStateProps) => {
  return (
    <Card className="flex flex-col items-center justify-center p-12 text-center">
      <div className="text-4xl text-gray-400 mb-4 animate-pulse">○</div>
      <p className="text-sm font-medium text-gray-500">{message}</p>
    </Card>
  );
};
