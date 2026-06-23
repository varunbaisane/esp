import { Card } from "../common/Card";

interface StatCardProps {
  title: string;
  value: number;
  theme: { accent: string, dot: string };
  subtitle?: string;
}

export const StatCard = ({ title, value, theme, subtitle = "Tickets" }: StatCardProps) => {

  return (
    <Card className="flex flex-col relative overflow-hidden group rounded-2xl">
      <div className={`absolute top-0 left-0 w-1 h-full ${theme.accent}`} />
      <div className="flex items-center gap-2 mb-4 pl-2">
        <div className={`w-3 h-3 rounded-full ${theme.dot}`} />
        <h3 className="text-sm font-bold text-gray-700 tracking-widest uppercase">
          {title}
        </h3>
      </div>
      <div className="flex flex-col pl-2 mt-2">
        <span className="text-5xl font-black text-gray-900 tracking-tight">{value}</span>
        <span className="text-sm font-semibold text-gray-400 mt-1 uppercase tracking-wider">{subtitle}</span>
      </div>
    </Card>
  );
};
