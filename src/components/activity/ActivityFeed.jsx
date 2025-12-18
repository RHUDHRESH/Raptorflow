import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  Info, 
  Zap, 
  UserPlus, 
  CreditCard, 
  Settings,
  ArrowRight
} from 'lucide-react';

const activityIcons = {
  success: CheckCircle2,
  warning: AlertTriangle,
  info: Info,
  primary: Zap,
  user: UserPlus,
  payment: CreditCard,
  system: Settings,
};

const activityColors = {
  success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  info: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  primary: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  user: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  payment: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  system: 'bg-gray-100 text-gray-700 dark:bg-gray-700/30 dark:text-gray-400',
};

const ActivityItem = ({ activity, index }) => {
  const Icon = activityIcons[activity.type] || activityIcons.info;
  
  return (
    <motion.li 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.05 }}
      className="relative pb-6 pl-8 last:pb-0 group"
    >
      {/* Timeline dot */}
      <div className="absolute left-0 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/50 ring-4 ring-white dark:ring-gray-800">
        <div className={`h-2 w-2 rounded-full ${
          activity.type === 'success' ? 'bg-green-500' :
          activity.type === 'warning' ? 'bg-yellow-500' :
          activity.type === 'info' ? 'bg-orange-500' : 'bg-orange-500'
        }`} />
      </div>
      
      <div className="flex items-start">
        <div className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full ${activityColors[activity.type] || activityColors.info} mr-3`}>
          <Icon className="h-4 w-4" />
        </div>
        
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {activity.title}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {activity.description}
          </p>
          
          {activity.meta && (
            <div className="mt-1.5 flex items-center text-xs text-gray-500 dark:text-gray-400">
              <Clock className="w-3.5 h-3.5 mr-1" />
              <span>{activity.meta}</span>
              
              {activity.action && (
                <button 
                  type="button"
                  className="ml-2 inline-flex items-center text-xs font-medium text-orange-600 hover:text-orange-800 dark:text-orange-400 dark:hover:text-orange-300"
                  onClick={activity.onAction}
                >
                  {activity.action}
                  <ArrowRight className="ml-0.5 h-3.5 w-3.5" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.li>
  );
};

export default function ActivityFeed({ 
  activities = [], 
  title = 'Recent Activity', 
  emptyText = 'No recent activity',
  loading = false,
  className = ''
}) {
  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden ${className}`}>
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
        </div>
        <div className="p-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="mb-4 last:mb-0">
              <div className="flex">
                <div className="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse mr-3"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2 animate-pulse"></div>
                  <div className="h-3 bg-gray-100 dark:bg-gray-600 rounded w-1/2 animate-pulse"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden ${className}`}>
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
        </div>
        <div className="p-6 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-50 dark:bg-gray-700/50 text-gray-400 mb-3">
            <Clock className="h-6 w-6" />
          </div>
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">No activity yet</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{emptyText}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden ${className}`}>
      <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
      </div>
      
      <div className="p-6">
        <div className="flow-root">
          <ul role="list" className="-mb-8">
            <AnimatePresence>
              {activities.map((activity, index) => (
                <ActivityItem 
                  key={activity.id || index} 
                  activity={activity} 
                  index={index} 
                />
              ))}
            </AnimatePresence>
          </ul>
        </div>
        
        <div className="mt-6">
          <a
            href="#"
            className="flex w-full items-center justify-center rounded-md bg-white dark:bg-gray-700/50 px-3 py-2 text-sm font-medium text-orange-600 hover:bg-gray-50 dark:text-orange-400 dark:hover:bg-gray-700"
          >
            View all activity
            <ArrowRight className="ml-2 h-4 w-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
