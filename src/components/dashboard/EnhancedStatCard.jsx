import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';

export default function EnhancedStatCard({ 
  icon: Icon, 
  title, 
  value, 
  change, 
  changeType = 'increase',
  loading = false,
  chart: Chart,
  delay = 0
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 flex flex-col h-full"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400">
          {React.createElement(Icon, { className: 'w-5 h-5' })}
        </div>
        {Chart && (
          <div className="h-10 w-20">
            <Chart />
          </div>
        )}
      </div>

      {loading ? (
        <>
          <div className="h-6 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2"></div>
          <div className="h-4 w-1/2 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        </>
      ) : (
        <>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {value}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {title}
          </p>
          {change !== undefined && (
            <div className={`mt-auto inline-flex items-center text-sm font-medium ${
              changeType === 'increase' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`}>
              {changeType === 'increase' ? (
                <TrendingUp className="w-4 h-4 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 mr-1" />
              )}
              {change}% from last month
            </div>
          )}
        </>
      )}
    </motion.div>
  );
}
