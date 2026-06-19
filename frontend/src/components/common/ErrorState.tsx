import { Card } from "./Card";

interface ErrorStateProps {
  message: string;
}

export const ErrorState = ({ message }: ErrorStateProps) => {
  return (
    <Card className="bg-red-50/50 border-red-500 text-center py-8">
      <div className="flex flex-col items-center justify-center gap-2">
        <h3 className="text-base font-bold text-red-900 flex items-center gap-2">
          <span className="text-lg">⚠</span> Unable to load data
        </h3>
        <p className="text-sm text-red-700">{message}</p>
      </div>
    </Card>
  );
};
