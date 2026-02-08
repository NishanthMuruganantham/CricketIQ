import React from 'react';
import { ChartData } from '../../types.ts';
import BarChart from './BarChart.tsx';
import LineChart from './LineChart.tsx';

interface ChartRendererProps {
  chartData: ChartData;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ chartData }) => {
  if (!chartData || !chartData.type) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden w-full">
      <h3 className="text-sm font-semibold mb-4 text-slate-700 dark:text-slate-200 text-center">
        {chartData.title}
      </h3>
      <div className="h-[250px] w-full">
        {chartData.type === 'bar' && <BarChart data={chartData} />}
        {chartData.type === 'line' && <LineChart data={chartData} />}
        {chartData.type === 'pie' && (
          <div className="h-full flex items-center justify-center text-slate-400 text-sm italic">
            Pie chart rendering coming soon...
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartRenderer;