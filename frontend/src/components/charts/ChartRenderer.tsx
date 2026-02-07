import {
    BarChart,
    Bar,
    LineChart,
    Line,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

// Color palette for charts
const CHART_COLORS = [
    '#6366f1', // indigo
    '#8b5cf6', // violet
    '#ec4899', // pink
    '#f43f5e', // rose
    '#f97316', // orange
    '#eab308', // yellow
    '#22c55e', // green
    '#14b8a6', // teal
];

interface ChartData {
    type: 'value' | 'table' | 'bar' | 'line' | 'pie';
    value?: number | string;
    columns?: string[];
    rows?: (string | number)[][];
}

interface ChartRendererProps {
    chartData: ChartData;
}

export default function ChartRenderer({ chartData }: ChartRendererProps) {
    // Value display
    if (chartData.type === 'value' && chartData.value !== undefined) {
        return (
            <div className="p-6 bg-[rgb(var(--bg-tertiary))] rounded-lg text-center">
                <p className="text-4xl font-bold text-[rgb(var(--accent))]">
                    {chartData.value}
                </p>
            </div>
        );
    }

    // Table display
    if (chartData.type === 'table' && chartData.columns && chartData.rows) {
        return (
            <div className="overflow-x-auto rounded-lg border border-[rgb(var(--border))]">
                <table className="w-full text-sm">
                    <thead className="bg-[rgb(var(--bg-tertiary))]">
                        <tr>
                            {chartData.columns.map((col, i) => (
                                <th key={i} className="px-4 py-3 text-left font-medium">
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {chartData.rows.map((row, rowIdx) => (
                            <tr
                                key={rowIdx}
                                className="border-t border-[rgb(var(--border))] hover:bg-[rgb(var(--bg-secondary))]"
                            >
                                {row.map((cell, cellIdx) => (
                                    <td key={cellIdx} className="px-4 py-3">
                                        {cell}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    }

    // Transform table data for charts
    if (!chartData.columns || !chartData.rows || chartData.rows.length === 0) {
        return (
            <div className="p-4 bg-[rgb(var(--bg-tertiary))] rounded-lg text-center text-[rgb(var(--text-secondary))]">
                No chart data available
            </div>
        );
    }

    const [, ...valueColumns] = chartData.columns;
    const data = chartData.rows.map((row) => {
        const obj: Record<string, string | number> = { name: String(row[0]) };
        valueColumns.forEach((col, i) => {
            obj[col] = row[i + 1];
        });
        return obj;
    });

    // Bar Chart
    if (chartData.type === 'bar') {
        return (
            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--border), 0.3)" />
                        <XAxis dataKey="name" tick={{ fill: 'rgb(var(--text-secondary))' }} />
                        <YAxis tick={{ fill: 'rgb(var(--text-secondary))' }} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgb(var(--bg-secondary))',
                                border: '1px solid rgb(var(--border))',
                                borderRadius: '8px',
                            }}
                        />
                        <Legend />
                        {valueColumns.map((col, i) => (
                            <Bar
                                key={col}
                                dataKey={col}
                                fill={CHART_COLORS[i % CHART_COLORS.length]}
                                radius={[4, 4, 0, 0]}
                            />
                        ))}
                    </BarChart>
                </ResponsiveContainer>
            </div>
        );
    }

    // Line Chart
    if (chartData.type === 'line') {
        return (
            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--border), 0.3)" />
                        <XAxis dataKey="name" tick={{ fill: 'rgb(var(--text-secondary))' }} />
                        <YAxis tick={{ fill: 'rgb(var(--text-secondary))' }} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgb(var(--bg-secondary))',
                                border: '1px solid rgb(var(--border))',
                                borderRadius: '8px',
                            }}
                        />
                        <Legend />
                        {valueColumns.map((col, i) => (
                            <Line
                                key={col}
                                type="monotone"
                                dataKey={col}
                                stroke={CHART_COLORS[i % CHART_COLORS.length]}
                                strokeWidth={2}
                                dot={{ fill: CHART_COLORS[i % CHART_COLORS.length] }}
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </div>
        );
    }

    // Pie Chart
    if (chartData.type === 'pie') {
        const pieData = data.map((d) => ({
            name: d.name,
            value: Number(Object.values(d)[1]) || 0,
        }));

        return (
            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) =>
                                `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`
                            }
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {pieData.map((_, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={CHART_COLORS[index % CHART_COLORS.length]}
                                />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgb(var(--bg-secondary))',
                                border: '1px solid rgb(var(--border))',
                                borderRadius: '8px',
                            }}
                        />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        );
    }

    // Fallback
    return (
        <div className="p-4 bg-[rgb(var(--bg-tertiary))] rounded-lg text-center text-[rgb(var(--text-secondary))]">
            Unsupported chart type: {chartData.type}
        </div>
    );
}
