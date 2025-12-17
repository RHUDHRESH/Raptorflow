import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import {
  Target,
  Users,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Radio,
  Rocket
} from 'lucide-react'
import { BRAND_ICONS } from '@/components/brand/BrandSystem'

import { EmptyState } from '@/components/EmptyState'

// Editorial Stat Card
const StatCard = ({ icon: Icon, label, value, change, changeType, delay, loading }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    className="card-editorial p-6"
  >
    <div className="flex items-start justify-between">
      <div className="w-10 h-10 bg-paper-200 rounded-editorial flex items-center justify-center">
        <Icon className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
      </div>
      {change && (
        <span className={`pill-editorial ${changeType === 'up' ? 'pill-success' : 'pill-error'
          }`}>
          {changeType === 'up' ? '+' : ''}{change}%
        </span>
      )}
    </div>
    <div className="mt-5">
      {loading ? (
        <div className="h-9 w-16 skeleton" />
      ) : (
        <p className="font-serif text-3xl text-ink">{value}</p>
      )}
      <p className="text-body-sm text-ink-400 mt-1">{label}</p>
    </div>
  </motion.div>
)

// Editorial Quick Action Card
const QuickAction = ({ icon: Icon, title, description, onClick, delay, highlight }) => (
  <motion.button
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    onClick={onClick}
    className={`group p-6 border rounded-card text-left transition-editorial w-full ${highlight
      ? 'bg-signal-muted border-primary/20 hover:border-primary/40'
      : 'bg-white border-border-light hover:border-border hover:shadow-editorial'
      }`}
  >
    <div className={`w-10 h-10 rounded-editorial flex items-center justify-center transition-editorial ${highlight ? 'bg-signal-muted' : 'bg-paper-200 group-hover:bg-paper-300'
      }`}>
      <Icon className={`w-5 h-5 transition-editorial ${highlight ? 'text-primary' : 'text-ink-400 group-hover:text-ink'
        }`} strokeWidth={1.5} />
    </div>
    <h3 className="mt-4 text-ink font-medium">{title}</h3>
    <p className="mt-1 text-body-sm text-ink-400">{description}</p>
    <div className="mt-4 flex items-center gap-2 text-primary text-body-sm opacity-0 group-hover:opacity-100 transition-opacity">
      <span>Get started</span>
      <ArrowRight className="w-4 h-4" />
    </div>
  </motion.button>
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

  useEffect(() => {
    // Simulate loading - in real app, fetch from API
    const timer = setTimeout(() => {
      setLoading(false)
      // Stats start at 0 - user needs to create data
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="max-w-6xl mx-auto">
      {/* Editorial Header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
        className="mb-10"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-serif text-headline-lg text-ink">
              Welcome back{userName !== 'there' ? `, ${userName}` : ''}
            </h1>
            <p className="text-body-md text-ink-400 mt-2">
              Your strategic command center
            </p>
          </div>

          {/* Plan badge */}
        </div>
      </motion.div>

      {/* Plan warning if expiring soon */}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
        <StatCard
          icon={BRAND_ICONS.speed}
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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick actions */}
        <div className="lg:col-span-2">
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="font-serif text-headline-xs text-ink mb-5"
          >
            Quick Actions
          </motion.h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
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
            className="font-serif text-headline-xs text-ink mb-5"
          >
            Recent Moves
          </motion.h2>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.4 }}
            className="card-editorial p-5"
          >
            {recentMoves.length > 0 ? (
              <div className="space-y-2">
                {recentMoves.map((move, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 hover:bg-paper-200 rounded-editorial transition-editorial cursor-pointer">
                    <div className={`w-2 h-2 rounded-full ${move.status === 'active' ? 'bg-primary' :
                      move.status === 'pending' ? 'bg-ink-300' : 'bg-ink-200'
                      }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-ink text-body-sm font-medium truncate">{move.name}</p>
                      <p className="text-body-xs text-ink-400">{move.campaign}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={BRAND_ICONS.speed}
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-10">
        {/* Getting started checklist */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.4 }}
          className="card-editorial p-6"
        >
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-serif text-headline-xs text-ink">Getting Started</h3>
            <span className="pill-editorial pill-neutral">
              {[stats.cohorts > 0, stats.campaigns > 0, stats.activeMoves > 0].filter(Boolean).length}/3 completed
            </span>
          </div>
          <div className="space-y-2">
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
                className={`w-full flex items-center gap-4 p-4 rounded-editorial transition-editorial text-left ${item.done ? 'bg-signal-muted' : 'hover:bg-paper-200'
                  }`}
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${item.done ? 'bg-primary' : 'border border-border-dark'
                  }`}>
                  {item.done && <CheckCircle2 className="w-4 h-4 text-primary-foreground" />}
                </div>
                <div className="flex-1">
                  <span className={`text-body-sm font-medium ${item.done ? 'text-ink-400 line-through' : 'text-ink'}`}>
                    {item.title}
                  </span>
                  <p className="text-body-xs text-ink-400">{item.description}</p>
                </div>
                {!item.done && <ArrowRight className="w-4 h-4 text-ink-300" />}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Radar preview */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.65, duration: 0.4 }}
          className="card-editorial p-6"
        >
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-serif text-headline-xs text-ink flex items-center gap-2">
              <Radio className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
              Radar
            </h3>
            <button
              onClick={() => navigate('/app/radar')}
              className="text-body-sm text-primary hover:text-primary/80 transition-editorial"
            >
              View all
            </button>
          </div>

          {stats.cohorts > 0 ? (
            <div className="space-y-3">
              <p className="text-ink-400 text-body-sm text-center py-10">
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
