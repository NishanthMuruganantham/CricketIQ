import React from 'react';
import { 
  BarChart as ReBarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { ChartData } from '../../types.ts';

interface BarChartProps {
  data: ChartData;
}

const BarChart: React.FC<BarChartProps> = ({ data }) => {
  const chartData = data.labels.map((label, index) => ({
    name: label,
    value: data.values[index],
  }));

  const brandColor = '#6366f1';

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ReBarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
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
          cursor={{ fill: 'rgba(99, 102, 241, 0.05)' }}
        />
        <Bar dataKey="value" fill={brandColor} radius={[4, 4, 0, 0]} barSize={40}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={brandColor} fillOpacity={1 - (index * 0.15)} />
          ))}
        </Bar>
      </ReBarChart>
    </ResponsiveContainer>
  );
};

export default BarChart;