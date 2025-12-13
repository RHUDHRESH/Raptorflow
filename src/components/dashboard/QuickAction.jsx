import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

// Individual quick action button
export function QuickActionItem({ icon: Icon, title, description, onClick, highlight = false, delay = 0 }) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      onClick={onClick}
      className={`group relative p-5 text-left rounded-xl transition-all duration-200 flex flex-col h-full ${
        highlight 
          ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white' 
          : 'bg-white dark:bg-gray-800 hover:shadow-md border border-gray-100 dark:border-gray-700 hover:border-indigo-100 dark:hover:border-indigo-900/50'
      }`}
    >
      <div className={`p-2.5 rounded-lg inline-flex mb-3 ${
        highlight 
          ? 'bg-white/20 text-white' 
          : 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400'
      }`}>
        {React.createElement(Icon, { className: 'w-5 h-5' })}
      </div>
      <h3 className={`font-medium mb-1 ${
        highlight ? 'text-white' : 'text-gray-900 dark:text-white'
      }`}>
        {title}
      </h3>
      <p className={`text-sm ${
        highlight ? 'text-indigo-100' : 'text-gray-500 dark:text-gray-400'
      }`}>
        {description}
      </p>
      <div className={`mt-3 inline-flex items-center text-sm font-medium ${
        highlight ? 'text-white/90' : 'text-indigo-600 dark:text-indigo-400'
      }`}>
        Get started
        <ArrowRight className="w-4 h-4 ml-1 transition-transform group-hover:translate-x-1" />
      </div>
    </motion.button>
  );
}

// Quick actions grid
export default function QuickActions({ actions = [], loading = false }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-full bg-gray-100 dark:bg-gray-800 rounded-xl p-5 animate-pulse">
            <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4"></div>
            <div className="h-5 w-3/4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 w-1/2 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((action, index) => (
        <QuickActionItem
          key={action.id || index}
          {...action}
          delay={index * 0.1}
        />
      ))}
    </div>
  );
}
