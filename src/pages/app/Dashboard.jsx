import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
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
  Sparkles,
  Crown,
  Radio,
  Rocket,
  Plus,
  AlertCircle
} from 'lucide-react'

// Stat card component
const StatCard = ({ icon: Icon, label, value, change, changeType, delay, loading }) => (
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
      {loading ? (
        <div className="h-8 w-16 bg-white/5 rounded animate-pulse" />
      ) : (
        <p className="text-2xl font-light text-white">{value}</p>
      )}
      <p className="text-sm text-white/40 mt-1">{label}</p>
    </div>
  </motion.div>
)

// Quick action card
const QuickAction = ({ icon: Icon, title, description, onClick, delay, highlight }) => (
  <motion.button
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    onClick={onClick}
    className={`group p-5 border rounded-xl text-left transition-all ${
      highlight 
        ? 'bg-amber-500/10 border-amber-500/30 hover:bg-amber-500/20' 
        : 'bg-zinc-900/50 border-white/5 hover:border-amber-500/30 hover:bg-zinc-900'
    }`}
  >
    <div className={`p-2 rounded-lg w-fit transition-colors ${
      highlight ? 'bg-amber-500/20' : 'bg-white/5 group-hover:bg-amber-500/10'
    }`}>
      <Icon className={`w-5 h-5 transition-colors ${
        highlight ? 'text-amber-400' : 'text-white/60 group-hover:text-amber-400'
      }`} strokeWidth={1.5} />
    </div>
    <h3 className="mt-4 text-white font-medium">{title}</h3>
    <p className="mt-1 text-sm text-white/40">{description}</p>
    <div className="mt-4 flex items-center gap-2 text-amber-400 text-sm opacity-0 group-hover:opacity-100 transition-opacity">
      <span>Get started</span>
      <ArrowRight className="w-4 h-4" />
    </div>
  </motion.button>
)

// Empty state component
const EmptyState = ({ icon: Icon, title, description, action, onAction }) => (
  <div className="text-center py-8">
    <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center mx-auto mb-4">
      <Icon className="w-6 h-6 text-white/30" />
    </div>
    <h3 className="text-white/60 font-medium mb-1">{title}</h3>
    <p className="text-white/30 text-sm mb-4">{description}</p>
    {action && (
      <button
        onClick={onAction}
        className="text-amber-400 text-sm hover:text-amber-300 flex items-center gap-2 mx-auto"
      >
        <Plus className="w-4 h-4" />
        {action}
      </button>
    )}
  </div>
)

const Dashboard = () => {
  const navigate = useNavigate()
  const { user, profile } = useAuth()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    activeMoves: 0,
    campaigns: 0,
    cohorts: 0,
    radarAlerts: 0
  })
  const [recentMoves, setRecentMoves] = useState([])
  const [upcomingTasks, setUpcomingTasks] = useState([])

  const userName = profile?.full_name || user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'there'
  
  // Calculate days remaining in plan
  const daysRemaining = profile?.plan_expires_at 
    ? Math.max(0, Math.ceil((new Date(profile.plan_expires_at) - new Date()) / (1000 * 60 * 60 * 24)))
    : 0

  useEffect(() => {
    // Simulate loading - in real app, fetch from API
    const timer = setTimeout(() => {
      setLoading(false)
      // Stats start at 0 - user needs to create data
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-light text-white">
              Welcome back{userName !== 'there' ? `, ${userName}` : ''}
            </h1>
            <p className="text-white/40 mt-1">
              Here's your strategic command center
            </p>
          </div>
          
          {/* Plan badge */}
          {profile?.plan && profile.plan !== 'none' && profile.plan !== 'free' && (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-xs text-white/40">Plan expires</p>
                <p className="text-sm text-amber-400">{daysRemaining} days left</p>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                <Crown className="w-4 h-4 text-amber-400" />
                <span className="text-amber-400 text-sm font-medium capitalize">{profile.plan}</span>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Plan warning if expiring soon */}
      {daysRemaining > 0 && daysRemaining <= 7 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center gap-4"
        >
          <AlertCircle className="w-5 h-5 text-amber-400" />
          <div className="flex-1">
            <p className="text-amber-400 font-medium">Plan expiring soon</p>
            <p className="text-amber-400/60 text-sm">
              Your {profile?.plan} plan expires in {daysRemaining} days. Renew to keep access.
            </p>
          </div>
          <button 
            onClick={() => navigate('/onboarding/plan')}
            className="px-4 py-2 bg-amber-500 text-black rounded-lg text-sm font-medium"
          >
            Renew Plan
          </button>
        </motion.div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          icon={Zap} 
          label="Active Moves" 
          value={stats.activeMoves}
          loading={loading}
          delay={0.1} 
        />
        <StatCard 
          icon={Target} 
          label="Campaigns" 
          value={stats.campaigns}
          loading={loading}
          delay={0.15} 
        />
        <StatCard 
          icon={Users} 
          label="Cohorts" 
          value={stats.cohorts}
          loading={loading}
          delay={0.2} 
        />
        <StatCard 
          icon={Radio} 
          label="Radar Alerts" 
          value={stats.radarAlerts}
          loading={loading}
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
              icon={Users}
              title="Create Your First Cohort"
              description="Define your ideal customer profile"
              onClick={() => navigate('/app/cohorts')}
              delay={0.35}
              highlight={stats.cohorts === 0}
            />
            <QuickAction
              icon={Rocket}
              title="Start a Spike"
              description="Launch a focused 30-day GTM sprint"
              onClick={() => navigate('/app/spikes/new')}
              delay={0.4}
            />
            <QuickAction
              icon={Radio}
              title="Check Radar"
              description="See trending topics for your cohorts"
              onClick={() => navigate('/app/radar')}
              delay={0.45}
            />
            <QuickAction
              icon={Sparkles}
              title="Ask Muse"
              description="Get AI-powered marketing assets"
              onClick={() => navigate('/app/muse')}
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
            className="bg-zinc-900/50 border border-white/5 rounded-xl p-4"
          >
            {recentMoves.length > 0 ? (
              <div className="space-y-3">
                {recentMoves.map((move, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 hover:bg-white/5 rounded-lg transition-colors cursor-pointer">
                    <div className={`w-2 h-2 rounded-full ${
                      move.status === 'active' ? 'bg-emerald-400' : 
                      move.status === 'pending' ? 'bg-amber-400' : 'bg-white/20'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm font-medium truncate">{move.name}</p>
                      <p className="text-xs text-white/40">{move.campaign}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Zap}
                title="No moves yet"
                description="Create your first move to start executing"
                action="Create Move"
                onAction={() => navigate('/app/moves')}
              />
            )}
          </motion.div>
        </div>
      </div>

      {/* Bottom section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Getting started checklist */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-zinc-900/50 border border-white/5 rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-medium">Getting Started</h3>
            <span className="text-xs text-white/40">
              {[stats.cohorts > 0, stats.campaigns > 0, stats.activeMoves > 0].filter(Boolean).length}/3 completed
            </span>
          </div>
          <div className="space-y-3">
            {[
              { 
                title: 'Create your first cohort', 
                done: stats.cohorts > 0, 
                action: () => navigate('/app/cohorts'),
                description: 'Define who you\'re targeting'
              },
              { 
                title: 'Launch a campaign', 
                done: stats.campaigns > 0, 
                action: () => navigate('/app/campaigns'),
                description: 'Organize your GTM efforts'
              },
              { 
                title: 'Execute your first move', 
                done: stats.activeMoves > 0, 
                action: () => navigate('/app/moves'),
                description: 'Take action with precision'
              },
            ].map((item, i) => (
              <button 
                key={i} 
                onClick={item.action}
                className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors text-left ${
                  item.done ? 'bg-emerald-500/10' : 'hover:bg-white/5'
                }`}
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  item.done ? 'bg-emerald-500' : 'border border-white/20'
                }`}>
                  {item.done && <CheckCircle2 className="w-4 h-4 text-black" />}
                </div>
                <div className="flex-1">
                  <span className={`text-sm ${item.done ? 'text-emerald-400 line-through' : 'text-white'}`}>
                    {item.title}
                  </span>
                  <p className="text-xs text-white/40">{item.description}</p>
                </div>
                {!item.done && <ArrowRight className="w-4 h-4 text-white/20" />}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Radar preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.65 }}
          className="bg-zinc-900/50 border border-white/5 rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-medium flex items-center gap-2">
              <Radio className="w-4 h-4 text-emerald-400" />
              Radar
            </h3>
            <button 
              onClick={() => navigate('/app/radar')}
              className="text-xs text-amber-400 hover:text-amber-300"
            >
              View all
            </button>
          </div>
          
          {stats.cohorts > 0 ? (
            <div className="space-y-3">
              {/* Radar would show trending matches here */}
              <p className="text-white/40 text-sm text-center py-8">
                Radar is scanning for opportunities based on your cohort interests...
              </p>
            </div>
          ) : (
            <EmptyState
              icon={Radio}
              title="Radar needs cohorts"
              description="Create cohorts to enable trend matching"
              action="Create Cohort"
              onAction={() => navigate('/app/cohorts')}
            />
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard
