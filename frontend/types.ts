
export interface ChartData {
  type: 'bar' | 'line' | 'pie' | null;
  labels: string[];
  values: number[];
  title: string;
  x_axis: string;
  y_axis: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  chartData?: ChartData | null;
  query_executed?: string;
  error?: boolean;
}

export type Theme = 'light' | 'dark';
