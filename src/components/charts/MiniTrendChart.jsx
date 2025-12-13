import React from 'react';
import {
  LineChart,
  Line,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  Label,
} from 'recharts';

// Generate random data for the mini chart
const generateData = (count = 7) => {
  return Array.from({ length: count }, (_, i) => ({
    name: `${i + 1}`,
    value: Math.floor(Math.random() * 100) + 50,
  }));
};

export default function MiniTrendChart({ data = null, color = '#6366f1', height = 40, width = 80, type = 'line' }) {
  const chartData = data || generateData(7);
  const isPositive = chartData[chartData.length - 1].value >= chartData[0].value;
  
  // Common props for both line and area charts
  const commonProps = {
    data: chartData,
    margin: { top: 0, right: 0, left: 0, bottom: 0 },
  };

  return (
    <div className="relative" style={{ width, height }}>
      <ResponsiveContainer width="100%" height="100%">
        {type === 'area' ? (
          <AreaChart {...commonProps}>
            <defs>
              <linearGradient id={`colorValue-${color}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.2} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              fillOpacity={1}
              fill={`url(#colorValue-${color})`}
              strokeWidth={2}
              dot={false}
              activeDot={false}
            />
          </AreaChart>
        ) : (
          <LineChart {...commonProps}>
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={false}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
      
      {/* Small indicator dot */}
      <div 
        className={`absolute -right-1 -top-1 w-2 h-2 rounded-full ${
          isPositive ? 'bg-green-500' : 'bg-red-500'
        }`}
      />
    </div>
  );
}
