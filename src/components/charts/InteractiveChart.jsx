import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { RefreshCw, BarChart2, LineChart, ChevronDown } from 'lucide-react';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const timeRanges = [
  { label: '24H', value: '24h' },
  { label: '7D', value: '7d' },
  { label: '30D', value: '30d' },
  { label: '3M', value: '3m' },
  { label: '1Y', value: '1y' },
  { label: 'All', value: 'all' },
];

const chartTypes = [
  { label: 'Line', value: 'line', icon: LineChart },
  { label: 'Bar', value: 'bar', icon: BarChart2 },
];

const generateData = (range) => {
  const now = new Date();
  let labels = [];
  let values = [];
  
  switch(range) {
    case '24h':
      labels = Array.from({ length: 24 }, (_, i) => {
        const date = new Date(now);
        date.setHours(now.getHours() - 23 + i);
        return date.toLocaleTimeString([], { hour: '2-digit' });
      });
      values = Array.from({ length: 24 }, () => Math.floor(Math.random() * 1000) + 500);
      break;
      
    case '7d':
      labels = Array.from({ length: 7 }, (_, i) => {
        const date = new Date(now);
        date.setDate(now.getDate() - 6 + i);
        return date.toLocaleDateString([], { weekday: 'short' });
      });
      values = Array.from({ length: 7 }, () => Math.floor(Math.random() * 2000) + 1000);
      break;
      
    case '30d':
      labels = Array.from({ length: 30 }, (_, i) => (i + 1).toString());
      values = Array.from({ length: 30 }, () => Math.floor(Math.random() * 3000) + 1500);
      break;
      
    case '3m':
      labels = ['Jan', 'Feb', 'Mar'];
      values = Array.from({ length: 3 }, () => Math.floor(Math.random() * 5000) + 3000);
      break;
      
    case '1y':
      labels = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      values = Array.from({ length: 12 }, () => Math.floor(Math.random() * 10000) + 5000);
      break;
      
    default:
      labels = ['Q1', 'Q2', 'Q3', 'Q4'];
      values = [10000, 15000, 8000, 12000];
  }
  
  return { labels, values };
};

export default function InteractiveChart({
  title = 'Performance',
  subtitle = 'Track your metrics over time',
  height = 300,
  className = '',
  onRefresh,
  loading = false,
}) {
  const [timeRange, setTimeRange] = useState('7d');
  const [chartType, setChartType] = useState('line');
  const [isTimeRangeOpen, setIsTimeRangeOpen] = useState(false);
  const [isChartTypeOpen, setIsChartTypeOpen] = useState(false);
  const dropdownRef = useRef(null);
  
  const { labels, values } = generateData(timeRange);
  
  const data = {
    labels,
    datasets: [
      {
        label: 'Value',
        data: values,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#6366f1',
        pointBorderColor: '#fff',
        pointHoverRadius: 5,
        pointHoverBackgroundColor: '#6366f1',
        pointHoverBorderColor: '#fff',
        pointHitRadius: 10,
        pointBorderWidth: 2,
      },
    ],
  };
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'white',
        titleColor: '#1f2937',
        bodyColor: '#4b5563',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        padding: 10,
        displayColors: false,
        callbacks: {
          label: function(context) {
            return `Value: ${context.parsed.y.toLocaleString()}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
        },
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
          callback: function(value) {
            if (value >= 1000) {
              return `$${(value / 1000).toFixed(1)}k`;
            }
            return `$${value}`;
          },
        },
      },
    },
  };
  
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsTimeRangeOpen(false);
        setIsChartTypeOpen(false);
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    }
  };
  
  const ChartComponent = chartType === 'bar' ? Bar : Line;
  const ChartTypeIcon = chartTypes.find(t => t.value === chartType)?.icon || LineChart;
  
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden ${className}`}>
      <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => {
                  setIsChartTypeOpen(!isChartTypeOpen);
                  setIsTimeRangeOpen(false);
                }}
                className="inline-flex items-center px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                <ChartTypeIcon className="w-4 h-4 mr-1.5" />
                {chartType === 'line' ? 'Line' : 'Bar'}
                <ChevronDown className="w-4 h-4 ml-1.5 -mr-1" />
              </button>
              
              {isChartTypeOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute right-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                >
                  <div className="py-1">
                    {chartTypes.map((type) => (
                      <button
                        key={type.value}
                        onClick={() => {
                          setChartType(type.value);
                          setIsChartTypeOpen(false);
                        }}
                        className={`w-full text-left px-4 py-2 text-sm flex items-center ${
                          chartType === type.value
                            ? 'bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300'
                            : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        <type.icon className="w-4 h-4 mr-2" />
                        {type.label}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
            
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => {
                  setIsTimeRangeOpen(!isTimeRangeOpen);
                  setIsChartTypeOpen(false);
                }}
                className="inline-flex items-center px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                {timeRanges.find(r => r.value === timeRange)?.label || '7D'}
                <ChevronDown className="w-4 h-4 ml-1.5 -mr-1" />
              </button>
              
              {isTimeRangeOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute right-0 z-10 mt-2 w-24 origin-top-right rounded-md bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                >
                  <div className="py-1">
                    {timeRanges.map((range) => (
                      <button
                        key={range.value}
                        onClick={() => {
                          setTimeRange(range.value);
                          setIsTimeRangeOpen(false);
                        }}
                        className={`w-full text-left px-4 py-2 text-sm ${
                          timeRange === range.value
                            ? 'bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300'
                            : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        {range.label}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
            
            <button
              type="button"
              onClick={handleRefresh}
              disabled={loading}
              className="p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 rounded-lg"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        <div style={{ height }}>
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-pulse flex flex-col items-center">
                <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div className="h-64 w-full bg-gray-100 dark:bg-gray-700/50 rounded"></div>
              </div>
            </div>
          ) : (
            <ChartComponent options={options} data={data} />
          )}
        </div>
      </div>
    </div>
  );
}
