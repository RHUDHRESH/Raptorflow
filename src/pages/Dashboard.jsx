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
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <span className="micro-label tracking-[0.5em]">Runway Dispatch</span>
            <span className="h-px w-16 bg-neutral-200" />
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-400">Issue 10</span>
          </div>
          <div className="space-y-6">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Today's edit is ready.
            </h1>
            <p className="font-sans text-base text-neutral-600 max-w-2xl leading-relaxed">
              Curated signals from every move, ritual, and review. Glide into the session with the
              confidence of a cover story.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/strategy/wizard"
              className="inline-flex items-center gap-3 border border-neutral-900 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-all"
            >
              <Sparkles className="w-4 h-4" />
              Begin Strategy Edit
            </Link>
            <Link
              to="/review"
              className="inline-flex items-center gap-3 border border-neutral-200 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-600 hover:border-neutral-900 hover:text-neutral-900 transition-all"
            >
              <Clock className="w-4 h-4" />
              Editorial Recap
            </Link>
          </div>
        </div>
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
              className="runway-card p-6 transition-shadow hover:shadow-xl"
            >
              <div className="flex items-center justify-between mb-5">
                <div className="w-12 h-12 border-2 border-neutral-200 bg-white flex items-center justify-center text-neutral-900">
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-xs uppercase tracking-[0.3em] text-green-600">{stat.change}</span>
              </div>
              <div className="text-3xl font-display text-neutral-900 mb-1">{stat.value}</div>
              <div className="text-xs uppercase tracking-[0.3em] text-neutral-500">{stat.label}</div>
            </motion.div>
          )
        })}
      </div>

      {/* Recent Moves */}
      <div className="runway-card p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="micro-label mb-2">Movement Log</p>
            <h2 className="font-serif text-3xl md:text-4xl text-neutral-900 leading-tight">Recent Moves</h2>
          </div>
          <Link
            to="/moves"
            className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-neutral-600 hover:text-neutral-900"
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
              className="flex items-center justify-between border-b-2 border-neutral-200 p-6 hover:bg-neutral-50 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-neutral-900">{move.name}</h3>
                  <span className={cn(
                    "px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border",
                    move.status === 'on-track' 
                      ? "bg-green-50 text-green-900 border-green-200" 
                      : "bg-yellow-50 text-yellow-900 border-yellow-200"
                  )}>
                    {move.status === 'on-track' ? 'On Track' : 'At Risk'}
                  </span>
                </div>
                <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${move.progress}%` }}
                    transition={{ duration: 1, delay: index * 0.2 }}
                    className="h-full bg-gradient-to-r from-neutral-700 to-neutral-900 rounded-full"
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

