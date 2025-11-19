import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Target, 
  TrendingUp, 
  Clock, 
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  PlayCircle
} from 'lucide-react'
import { cn } from '../utils/cn'

const stats = [
  { label: 'Active Moves', value: 12, change: '+3', icon: Target, color: 'primary' },
  { label: 'Completion Rate', value: '87%', change: '+5%', icon: CheckCircle2, color: 'accent' },
  { label: 'Weekly Reviews', value: 8, change: '+2', icon: Clock, color: 'primary' },
  { label: 'Strategy Score', value: 92, change: '+7', icon: TrendingUp, color: 'accent' },
]

const recentMoves = [
  { id: 1, name: 'Launch Product Beta', status: 'on-track', progress: 75 },
  { id: 2, name: 'Acquire 100 Customers', status: 'at-risk', progress: 45 },
  { id: 3, name: 'Build ICP Database', status: 'on-track', progress: 90 },
]

export default function Dashboard() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900 p-12 text-white"
      >
        <div className="relative z-10">
          <h1 className="text-5xl font-display font-bold mb-4">Welcome Back</h1>
          <p className="text-xl text-neutral-300 mb-8 max-w-2xl">
            Your strategy execution platform. Track moves, review progress, and optimize your path to success.
          </p>
          <div className="flex gap-4">
            <Link
              to="/strategy/wizard"
              className="flex items-center gap-2 px-6 py-3 bg-white text-neutral-900 rounded-xl font-medium hover:bg-neutral-100 transition-colors"
            >
              <Sparkles className="w-5 h-5" />
              Start Strategy Wizard
            </Link>
            <Link
              to="/review"
              className="flex items-center gap-2 px-6 py-3 bg-white/10 backdrop-blur-xl border border-white/20 text-white rounded-xl font-medium hover:bg-white/20 transition-colors"
            >
              <Clock className="w-5 h-5" />
              Weekly Review
            </Link>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-accent-500/20 rounded-full blur-3xl" />
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center",
                  stat.color === 'primary' ? "bg-primary-100 text-primary-600" : "bg-accent-100 text-accent-600"
                )}>
                  <Icon className="w-6 h-6" />
                </div>
                <span className="text-sm font-medium text-green-600">{stat.change}</span>
              </div>
              <div className="text-3xl font-bold text-neutral-900 mb-1">{stat.value}</div>
              <div className="text-sm text-neutral-600">{stat.label}</div>
            </motion.div>
          )
        })}
      </div>

      {/* Recent Moves */}
      <div className="glass rounded-2xl p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-display font-bold">Recent Moves</h2>
          <Link
            to="/moves"
            className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
          >
            View All
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="space-y-4">
          {recentMoves.map((move, index) => (
            <motion.div
              key={move.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-4 rounded-xl border border-neutral-200 hover:bg-neutral-50 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-neutral-900">{move.name}</h3>
                  <span className={cn(
                    "px-2 py-1 text-xs font-medium rounded-lg",
                    move.status === 'on-track' 
                      ? "bg-green-100 text-green-700" 
                      : "bg-yellow-100 text-yellow-700"
                  )}>
                    {move.status === 'on-track' ? 'On Track' : 'At Risk'}
                  </span>
                </div>
                <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${move.progress}%` }}
                    transition={{ duration: 1, delay: index * 0.2 }}
                    className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
                  />
                </div>
              </div>
              <div className="ml-4 text-right">
                <div className="text-2xl font-bold text-neutral-900">{move.progress}%</div>
                <div className="text-xs text-neutral-500">Complete</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

