import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card } from "../common/Card";

interface StatusDistributionChartProps {
  data: Record<string, number>;
}

const COLORS = ['#0ea5e9', '#f59e0b', '#10b981', '#64748b'];

export const StatusDistributionChart = ({ data }: StatusDistributionChartProps) => {
  const chartData = Object.entries(data).map(([name, value]) => ({ name, value }));

  return (
    <Card className="h-96 flex flex-col">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Status Distribution</h3>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
