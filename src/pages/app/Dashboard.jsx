import React from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  TrendingUp, 
  Zap, 
  Target, 
  Users, 
  ArrowRight,
  BarChart3,
  Calendar,
  CheckCircle2,
  Clock,
  Sparkles
} from 'lucide-react'

// Stat card component
const StatCard = ({ icon: Icon, label, value, change, changeType, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    className="bg-zinc-900/50 border border-white/5 rounded-xl p-5 hover:border-white/10 transition-colors"
  >
    <div className="flex items-start justify-between">
      <div className="p-2 bg-amber-500/10 rounded-lg">
        <Icon className="w-5 h-5 text-amber-400" strokeWidth={1.5} />
      </div>
      {change && (
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
          changeType === 'up' 
            ? 'bg-emerald-500/10 text-emerald-400' 
            : 'bg-red-500/10 text-red-400'
        }`}>
          {changeType === 'up' ? '+' : ''}{change}%
        </span>
      )}
    </div>
    <div className="mt-4">
      <p className="text-2xl font-light text-white">{value}</p>
      <p className="text-sm text-white/40 mt-1">{label}</p>
    </div>
  </motion.div>
)

// Quick action card
const QuickAction = ({ icon: Icon, title, description, onClick, delay }) => (
  <motion.button
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    onClick={onClick}
    className="group p-5 bg-zinc-900/50 border border-white/5 rounded-xl text-left hover:border-amber-500/30 hover:bg-zinc-900 transition-all"
  >
    <div className="p-2 bg-white/5 rounded-lg w-fit group-hover:bg-amber-500/10 transition-colors">
      <Icon className="w-5 h-5 text-white/60 group-hover:text-amber-400 transition-colors" strokeWidth={1.5} />
    </div>
    <h3 className="mt-4 text-white font-medium">{title}</h3>
    <p className="mt-1 text-sm text-white/40">{description}</p>
    <div className="mt-4 flex items-center gap-2 text-amber-400 text-sm opacity-0 group-hover:opacity-100 transition-opacity">
      <span>Get started</span>
      <ArrowRight className="w-4 h-4" />
    </div>
  </motion.button>
)

// Recent move item
const RecentMove = ({ title, campaign, status, date, delay }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay }}
    className="flex items-center gap-4 p-4 hover:bg-white/5 rounded-lg transition-colors cursor-pointer"
  >
    <div className={`w-2 h-2 rounded-full ${
      status === 'active' ? 'bg-emerald-400' : 
      status === 'pending' ? 'bg-amber-400' : 'bg-white/20'
    }`} />
    <div className="flex-1 min-w-0">
      <p className="text-white font-medium truncate">{title}</p>
      <p className="text-sm text-white/40">{campaign}</p>
    </div>
    <div className="text-right">
      <p className="text-xs text-white/40">{date}</p>
      <p className={`text-xs capitalize ${
        status === 'active' ? 'text-emerald-400' : 
        status === 'pending' ? 'text-amber-400' : 'text-white/40'
      }`}>{status}</p>
    </div>
  </motion.div>
)

const Dashboard = () => {
  const navigate = useNavigate()

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-light text-white">
          Welcome back
        </h1>
        <p className="text-white/40 mt-1">
          Here's what's happening with your strategy
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          icon={Zap} 
          label="Active Moves" 
          value="12" 
          change="8" 
          changeType="up" 
          delay={0.1} 
        />
        <StatCard 
          icon={Target} 
          label="Campaign Progress" 
          value="67%" 
          change="12" 
          changeType="up" 
          delay={0.15} 
        />
        <StatCard 
          icon={Users} 
          label="Cohorts Tracked" 
          value="5" 
          delay={0.2} 
        />
        <StatCard 
          icon={TrendingUp} 
          label="GTM Velocity" 
          value="4.2x" 
          change="23" 
          changeType="up" 
          delay={0.25} 
        />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick actions */}
        <div className="lg:col-span-2">
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-lg font-medium text-white mb-4"
          >
            Quick Actions
          </motion.h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <QuickAction
              icon={Zap}
              title="Create a Move"
              description="Launch a new tactical sprint"
              onClick={() => navigate('/app/moves')}
              delay={0.35}
            />
            <QuickAction
              icon={Sparkles}
              title="Ask Muse"
              description="Get AI-powered strategy insights"
              onClick={() => navigate('/app/muse')}
              delay={0.4}
            />
            <QuickAction
              icon={Target}
              title="Define Position"
              description="Refine your market positioning"
              onClick={() => navigate('/app/position')}
              delay={0.45}
            />
            <QuickAction
              icon={Users}
              title="Analyze Cohorts"
              description="Deep dive into your audiences"
              onClick={() => navigate('/app/cohorts')}
              delay={0.5}
            />
          </div>
        </div>

        {/* Recent moves */}
        <div>
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-lg font-medium text-white mb-4"
          >
            Recent Moves
          </motion.h2>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="bg-zinc-900/50 border border-white/5 rounded-xl overflow-hidden"
          >
            <RecentMove
              title="LinkedIn Thought Leadership"
              campaign="Q1 Awareness"
              status="active"
              date="2 hours ago"
              delay={0.4}
            />
            <RecentMove
              title="Product Hunt Launch"
              campaign="Launch Campaign"
              status="pending"
              date="Yesterday"
              delay={0.45}
            />
            <RecentMove
              title="Email Nurture Sequence"
              campaign="Q1 Awareness"
              status="active"
              date="2 days ago"
              delay={0.5}
            />
            <RecentMove
              title="Community Outreach"
              campaign="Growth"
              status="completed"
              date="1 week ago"
              delay={0.55}
            />
          </motion.div>
        </div>
      </div>

      {/* Bottom section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Upcoming */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-zinc-900/50 border border-white/5 rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-medium">Upcoming</h3>
            <Calendar className="w-5 h-5 text-white/40" />
          </div>
          <div className="space-y-3">
            {[
              { title: 'Strategy Review', time: 'Tomorrow, 2:00 PM' },
              { title: 'Content Calendar Planning', time: 'Wed, 10:00 AM' },
              { title: 'Cohort Analysis', time: 'Fri, 3:00 PM' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <Clock className="w-4 h-4 text-amber-400" />
                <span className="text-white">{item.title}</span>
                <span className="text-white/40 ml-auto">{item.time}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Progress */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.65 }}
          className="bg-zinc-900/50 border border-white/5 rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-medium">90-Day War Map</h3>
            <BarChart3 className="w-5 h-5 text-white/40" />
          </div>
          <div className="space-y-4">
            {[
              { phase: 'Phase 1: Foundation', progress: 100 },
              { phase: 'Phase 2: Traction', progress: 67 },
              { phase: 'Phase 3: Scale', progress: 12 },
            ].map((item, i) => (
              <div key={i}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-white/60">{item.phase}</span>
                  <span className="text-white/40">{item.progress}%</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard

