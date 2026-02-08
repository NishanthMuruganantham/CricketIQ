import React from 'react';
import { 
  LineChart as ReLineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { ChartData } from '../../types.ts';

interface LineChartProps {
  data: ChartData;
}

const LineChart: React.FC<LineChartProps> = ({ data }) => {
  const chartData = data.labels.map((label, index) => ({
    name: label,
    value: data.values[index],
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ReLineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis 
          dataKey="name" 
          stroke="#94a3b8" 
          fontSize={10} 
          tickLine={false} 
          axisLine={false}
          label={{ value: data.x_axis, position: 'insideBottom', offset: -5, fontSize: 10, fill: '#94a3b8' }}
        />
        <YAxis 
          stroke="#94a3b8" 
          fontSize={10} 
          tickLine={false} 
          axisLine={false}
          label={{ value: data.y_axis, angle: -90, position: 'insideLeft', fontSize: 10, fill: '#94a3b8' }}
        />
        <Tooltip 
          contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
          itemStyle={{ color: '#818cf8' }}
        />
        <Line 
          type="monotone" 
          dataKey="value" 
          stroke="#6366f1" 
          strokeWidth={3} 
          dot={{ fill: '#6366f1', strokeWidth: 2, r: 4, stroke: '#fff' }} 
          activeDot={{ r: 6, strokeWidth: 0 }}
        />
      </ReLineChart>
    </ResponsiveContainer>
  );
};

export default LineChart;