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
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-b from-white via-neutral-50 to-white" />
        <div className="relative z-10 flex items-center gap-6">
          <div className="w-16 h-16 rounded-full border border-neutral-200 bg-white flex items-center justify-center">
            <TrendingUp className="w-7 h-7 text-neutral-900" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="micro-label tracking-[0.5em]">Insights Studio</span>
              <span className="h-px w-16 bg-neutral-200" />
            </div>
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Read the Pulse
            </h1>
            <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
              Couture analytics for every move and ritual
            </p>
          </div>
        </div>
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
              className="runway-card p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-neutral-100 text-neutral-900 flex items-center justify-center">
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
      <div className="runway-card p-8">
        <div className="flex items-center gap-3 mb-2">
          <Zap className="w-6 h-6 text-neutral-900" />
          <div>
            <p className="micro-label mb-1">Editor’s Picks</p>
            <h2 className="text-2xl font-display font-bold">AI Recommendations</h2>
          </div>
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
                  ? "border-neutral-900 bg-neutral-50"
                  : "border-neutral-200 hover:border-neutral-400 hover:bg-neutral-50"
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
                  <button className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors">
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
        <div className="runway-card p-8">
          <h3 className="text-xl font-bold mb-4">Move Progress Over Time</h3>
          <div className="h-64 flex items-center justify-center text-neutral-400">
            Chart visualization would go here
          </div>
        </div>
        <div className="runway-card p-8">
          <h3 className="text-xl font-bold mb-4">Completion Rate by Category</h3>
          <div className="h-64 flex items-center justify-center text-neutral-400">
            Chart visualization would go here
          </div>
        </div>
      </div>
    </div>
  )
}

