import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Zap, 
  CheckCircle2, 
  Clock, 
  Target,
  TrendingUp,
  ArrowRight,
  Sparkles,
  AlertCircle,
  PlayCircle
} from 'lucide-react'
import { cn } from '../utils/cn'

// Mock quick wins data
const mockQuickWins = [
  {
    id: 'qw-1',
    type: 'anomaly',
    title: 'Tone Clash Detected',
    description: 'Email draft for Authority Sprint violates Safety Seeker profile',
    action: 'Review and adjust copy',
    priority: 'high',
    moveId: 'move-1',
    moveName: 'Authority Sprint – Enterprise CTOs',
    estimatedTime: '5 min'
  },
  {
    id: 'qw-2',
    type: 'capacity',
    title: 'Sprint Capacity Warning',
    description: 'Adding Scarcity Flank will exceed Sprint budget by 6 points',
    action: 'Reschedule or reduce intensity',
    priority: 'medium',
    moveId: 'move-2',
    moveName: 'Scarcity Flank',
    estimatedTime: '10 min'
  },
  {
    id: 'qw-3',
    type: 'unlock',
    title: 'Capability Unlocked',
    description: 'Lead Magnet v1 completed – new maneuvers available',
    action: 'View unlocked maneuvers',
    priority: 'low',
    moveId: null,
    moveName: null,
    estimatedTime: '2 min'
  },
  {
    id: 'qw-4',
    type: 'task',
    title: 'Approve LinkedIn Post',
    description: 'Draft ready for Authority Sprint Day 3',
    action: 'Review and approve',
    priority: 'high',
    moveId: 'move-1',
    moveName: 'Authority Sprint – Enterprise CTOs',
    estimatedTime: '3 min'
  },
  {
    id: 'qw-5',
    type: 'metric',
    title: 'Performance Drift',
    description: 'Garrison Move CTR dropped 2% below baseline',
    action: 'Review metrics and adjust',
    priority: 'medium',
    moveId: 'move-3',
    moveName: 'Garrison – High-Value Accounts',
    estimatedTime: '15 min'
  }
]

const getQuickWinIcon = (type) => {
  const icons = {
    anomaly: AlertCircle,
    capacity: Target,
    unlock: Sparkles,
    task: CheckCircle2,
    metric: TrendingUp
  }
  return icons[type] || Zap
}

const getQuickWinColor = (type, priority) => {
  if (priority === 'high') {
    return {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-900',
      badge: 'bg-red-100 text-red-900'
    }
  }
  if (priority === 'medium') {
    return {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-900',
      badge: 'bg-yellow-100 text-yellow-900'
    }
  }
  return {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-900',
    badge: 'bg-blue-100 text-blue-900'
  }
}

export default function DailySweep() {
  const [quickWins, setQuickWins] = useState(mockQuickWins)
  const [filter, setFilter] = useState('all')
  const [completed, setCompleted] = useState(new Set())

  const filteredWins = quickWins.filter(win => {
    if (filter === 'all') return true
    if (filter === 'completed') return completed.has(win.id)
    if (filter === 'pending') return !completed.has(win.id)
    return win.priority === filter
  })

  const handleComplete = (id) => {
    setCompleted(prev => new Set([...prev, id]))
    // In production, this would update the backend
  }

  const handleDismiss = (id) => {
    setQuickWins(prev => prev.filter(win => win.id !== id))
  }

  const pendingWins = quickWins.filter(win => !completed.has(win.id))
  const highPriorityWins = pendingWins.filter(win => win.priority === 'high')

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <span className="micro-label tracking-[0.5em]">Daily Sweep</span>
            <span className="h-px w-16 bg-neutral-200" />
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-400">Quick Wins</span>
          </div>
          <div className="space-y-4">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Rapid Response
            </h1>
            <p className="font-sans text-base text-neutral-600 max-w-2xl leading-relaxed">
              AI-detected anomalies, capacity warnings, and time-boxed actions. Clear these to keep operations smooth.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.3 }}
          className="runway-card p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
              <Zap className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-neutral-900">{highPriorityWins.length}</div>
              <div className="text-xs text-neutral-600">High Priority</div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.3 }}
          className="runway-card p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
              <Target className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-neutral-900">{pendingWins.length}</div>
              <div className="text-xs text-neutral-600">Pending</div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
          className="runway-card p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-neutral-900">{completed.size}</div>
              <div className="text-xs text-neutral-600">Completed</div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.3 }}
          className="runway-card p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-neutral-900">
                {pendingWins.reduce((sum, win) => {
                  const time = parseInt(win.estimatedTime) || 0
                  return sum + time
                }, 0)} min
              </div>
              <div className="text-xs text-neutral-600">Total Time</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        {['all', 'high', 'medium', 'low', 'pending', 'completed'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "px-4 py-2 text-sm font-medium rounded-lg border transition-all duration-180",
              filter === f
                ? "border-neutral-900 bg-neutral-900 text-white"
                : "border-neutral-200 bg-white text-neutral-700 hover:border-neutral-900"
            )}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Quick Wins List */}
      <div className="space-y-3">
        <AnimatePresence>
          {filteredWins.map((win, index) => {
            const Icon = getQuickWinIcon(win.type)
            const colors = getQuickWinColor(win.type, win.priority)
            const isCompleted = completed.has(win.id)

            return (
              <motion.div
                key={win.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05, duration: 0.18 }}
                className={cn(
                  "runway-card p-5 border-2 transition-all duration-180",
                  isCompleted 
                    ? "bg-green-50 border-green-200 opacity-60" 
                    : colors.border,
                  "hover:shadow-lg"
                )}
              >
                <div className="flex items-start gap-4">
                  <div className={cn(
                    "w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0",
                    isCompleted ? "bg-green-200" : colors.bg
                  )}>
                    <Icon className={cn(
                      "w-6 h-6",
                      isCompleted ? "text-green-700" : colors.text
                    )} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className={cn(
                            "font-bold text-lg",
                            isCompleted ? "text-green-900 line-through" : "text-neutral-900"
                          )}>
                            {win.title}
                          </h3>
                          <span className={cn(
                            "px-2 py-0.5 text-[10px] font-mono uppercase tracking-[0.1em] rounded",
                            colors.badge
                          )}>
                            {win.priority}
                          </span>
                        </div>
                        <p className={cn(
                          "text-sm mb-2",
                          isCompleted ? "text-green-700" : "text-neutral-600"
                        )}>
                          {win.description}
                        </p>
                        {win.moveName && (
                          <Link
                            to={`/moves/${win.moveId}`}
                            className="text-xs text-neutral-500 hover:text-neutral-900 transition-colors duration-180"
                          >
                            Move: {win.moveName} →
                          </Link>
                        )}
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <div className="flex items-center gap-1 text-xs text-neutral-500">
                          <Clock className="w-3 h-3" />
                          {win.estimatedTime}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 mt-3">
                      {!isCompleted ? (
                        <>
                          <button
                            onClick={() => handleComplete(win.id)}
                            className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-all duration-180 text-sm font-medium"
                          >
                            <CheckCircle2 className="w-4 h-4" />
                            {win.action}
                          </button>
                          <button
                            onClick={() => handleDismiss(win.id)}
                            className="px-4 py-2 border border-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-all duration-180 text-sm font-medium"
                          >
                            Dismiss
                          </button>
                        </>
                      ) : (
                        <div className="flex items-center gap-2 text-sm text-green-700">
                          <CheckCircle2 className="w-4 h-4" />
                          Completed
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {filteredWins.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="runway-card p-12 text-center"
        >
          <Zap className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-neutral-900 mb-2">All Clear!</h3>
          <p className="text-sm text-neutral-600">
            No quick wins match your current filter. Check back later or adjust filters.
          </p>
        </motion.div>
      )}
    </div>
  )
}

