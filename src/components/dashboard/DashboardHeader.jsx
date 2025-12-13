import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Zap } from 'lucide-react';

export default function DashboardHeader({ user, loading = false }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col md:flex-row md:items-center md:justify-between mb-8"
    >
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
          {loading ? (
            <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
          ) : (
            `Welcome back, ${user?.name || 'User'}`
          )}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1 flex items-center">
          <Clock className="w-4 h-4 mr-1.5" />
          {new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </div>
      
      <div className="mt-4 md:mt-0">
        <div className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-yellow-50 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500">
          <Zap className="w-4 h-4 mr-2" />
          <span>Pro Plan • Expires in 14 days</span>
        </div>
      </div>
    </motion.div>
  );
}
