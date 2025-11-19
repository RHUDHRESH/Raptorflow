import { useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Target, CheckCircle2, AlertCircle, Zap, ArrowRight } from 'lucide-react'
import { cn } from '../utils/cn'

const insights = [
  {
    id: 1,
    title: 'Increase Move Completion Rate',
    description: 'Your completion rate is 15% below target. Consider breaking down larger moves into smaller tasks.',
    type: 'optimization',
    action: 'Apply Recommendation',
    impact: 'high',
  },
  {
    id: 2,
    title: 'Optimize Weekly Review Frequency',
    description: 'Moves reviewed weekly show 30% better outcomes. Consider increasing review frequency.',
    type: 'suggestion',
    action: 'View Details',
    impact: 'medium',
  },
  {
    id: 3,
    title: 'Focus on High-Impact Moves',
    description: '3 moves account for 60% of your progress. Consider prioritizing similar moves.',
    type: 'insight',
    action: 'See Analysis',
    impact: 'high',
  },
]

export default function Analytics() {
  const [selectedInsight, setSelectedInsight] = useState(null)

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-accent-600 via-accent-700 to-primary-600 p-12 text-white"
      >
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
              <TrendingUp className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-4xl font-display font-bold mb-2">Analytics</h1>
              <p className="text-accent-100 text-lg">
                Data-driven insights and actionable optimizations
              </p>
            </div>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-primary-500/20 rounded-full blur-3xl" />
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total Moves', value: 12, change: '+3', icon: Target },
          { label: 'Completion Rate', value: '87%', change: '+5%', icon: CheckCircle2 },
          { label: 'Avg Velocity', value: '8.5', change: '+1.2', icon: TrendingUp },
          { label: 'Active Reviews', value: 8, change: '+2', icon: AlertCircle },
        ].map((metric, index) => {
          const Icon = metric.icon
          return (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-accent-100 text-accent-600 flex items-center justify-center">
                  <Icon className="w-6 h-6" />
                </div>
                <span className="text-sm font-medium text-green-600">{metric.change}</span>
              </div>
              <div className="text-3xl font-bold text-neutral-900 mb-1">{metric.value}</div>
              <div className="text-sm text-neutral-600">{metric.label}</div>
            </motion.div>
          )
        })}
      </div>

      {/* AI Recommendations */}
      <div className="glass rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <Zap className="w-6 h-6 text-accent-600" />
          <h2 className="text-2xl font-display font-bold">AI Recommendations</h2>
        </div>
        <div className="space-y-4">
          {insights.map((insight, index) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "p-6 rounded-xl border-2 transition-all cursor-pointer",
                selectedInsight === insight.id
                  ? "border-primary-500 bg-primary-50"
                  : "border-neutral-200 hover:border-primary-300 hover:bg-neutral-50"
              )}
              onClick={() => setSelectedInsight(selectedInsight === insight.id ? null : insight.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-bold text-neutral-900">{insight.title}</h3>
                    <span className={cn(
                      "px-2 py-1 text-xs font-medium rounded-lg",
                      insight.impact === 'high' 
                        ? "bg-red-100 text-red-700"
                        : "bg-yellow-100 text-yellow-700"
                    )}>
                      {insight.impact === 'high' ? 'High Impact' : 'Medium Impact'}
                    </span>
                  </div>
                  <p className="text-neutral-600">{insight.description}</p>
                </div>
              </div>
              {selectedInsight === insight.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 pt-4 border-t border-neutral-200"
                >
                  <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
                    {insight.action}
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass rounded-2xl p-8">
          <h3 className="text-xl font-bold mb-4">Move Progress Over Time</h3>
          <div className="h-64 flex items-center justify-center text-neutral-400">
            Chart visualization would go here
          </div>
        </div>
        <div className="glass rounded-2xl p-8">
          <h3 className="text-xl font-bold mb-4">Completion Rate by Category</h3>
          <div className="h-64 flex items-center justify-center text-neutral-400">
            Chart visualization would go here
          </div>
        </div>
      </div>
    </div>
  )
}

