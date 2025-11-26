import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Sparkles,
  ArrowRight,
  Target,
  TrendingUp,
  Users,
  Zap,
  CheckCircle2,
  MessageSquare,
  Award,
  Megaphone,
  Plus
} from 'lucide-react'

const strategyTools = [
  {
    title: 'Positioning Workshop',
    description: 'Define your strategic positioning and message architecture',
    icon: Award,
    url: '/strategy/positioning',
    color: 'purple',
    status: 'ready',
  },
  {
    title: 'Strategic Cohorts',
    description: 'Deep customer intelligence with buying triggers and decision criteria',
    icon: Users,
    url: '/strategy/cohorts',
    color: 'blue',
    status: 'ready',
  },
  {
    title: 'Campaign Builder',
    description: 'Orchestrate coordinated campaigns that ladder up to strategic intent',
    icon: Megaphone,
    url: '/strategy/campaigns/new',
    color: 'green',
    status: 'ready',
  },
  {
    title: 'Message Architecture',
    description: 'Build your message hierarchy and proof points',
    icon: MessageSquare,
    url: '/strategy/positioning',
    color: 'amber',
    status: 'coming-soon',
  },
]

const strategySections = [
  {
    title: 'Target Market',
    description: 'Enterprise SaaS companies with 100-500 employees',
    icon: Users,
    status: 'complete',
  },
  {
    title: 'Value Proposition',
    description: 'AI-powered strategy execution platform',
    icon: Zap,
    status: 'complete',
  },
  {
    title: 'Key Moves',
    description: '12 strategic moves identified',
    icon: Target,
    status: 'complete',
  },
  {
    title: 'Success Metrics',
    description: 'KPIs and tracking mechanisms defined',
    icon: TrendingUp,
    status: 'in-progress',
  },
]

export default function Strategy() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-white via-neutral-50 to-white" />
        <div className="relative z-10 flex items-center gap-6">
          <div className="w-16 h-16 rounded-full border border-neutral-200 bg-white flex items-center justify-center">
            <Sparkles className="w-7 h-7 text-neutral-900" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="micro-label tracking-[0.5em]">Strategy Atelier</span>
              <span className="h-px w-16 bg-neutral-200" />
            </div>
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Strategic Command Center
            </h1>
            <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
              Positioning, Cohorts, and Campaign Orchestration
            </p>
          </div>
        </div>
      </motion.div>

      {/* Strategy Tools - NEW */}
      <div className="runway-card p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="micro-label mb-2">Strategic Arsenal</p>
            <h2 className="font-serif text-3xl md:text-4xl text-neutral-900 leading-tight">Marketing Warfare Tools</h2>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategyTools.map((tool, index) => {
            const Icon = tool.icon
            const isReady = tool.status === 'ready'

            return (
              <motion.div
                key={tool.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {isReady ? (
                  <Link
                    to={tool.url}
                    className="block p-6 border-2 border-neutral-200 hover:border-neutral-900 hover:bg-neutral-50 transition-all group h-full"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 border-2 border-neutral-200 bg-white text-neutral-900 flex items-center justify-center group-hover:border-neutral-900 transition-colors">
                        <Icon className="w-6 h-6" />
                      </div>
                      <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-neutral-900 group-hover:translate-x-1 transition-all" />
                    </div>
                    <h3 className="text-lg font-bold text-neutral-900 mb-2">{tool.title}</h3>
                    <p className="text-sm text-neutral-600">{tool.description}</p>
                    <div className="mt-4 flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      <span className="text-xs text-neutral-500">Ready to use</span>
                    </div>
                  </Link>
                ) : (
                  <div className="p-6 border-2 border-dashed border-neutral-200 bg-neutral-50 h-full opacity-60">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 border-2 border-neutral-200 bg-white text-neutral-400 flex items-center justify-center">
                        <Icon className="w-6 h-6" />
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-neutral-600 mb-2">{tool.title}</h3>
                    <p className="text-sm text-neutral-500">{tool.description}</p>
                    <div className="mt-4 flex items-center gap-2">
                      <div className="w-2 h-2 bg-amber-500 rounded-full" />
                      <span className="text-xs text-neutral-400">Coming soon</span>
                    </div>
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/strategy/positioning"
          className="runway-card p-6 hover:shadow-lg transition-shadow group"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Award className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="font-semibold text-neutral-900">Define Positioning</h3>
          </div>
          <p className="text-sm text-neutral-600 mb-4">
            Create your strategic positioning statement and message architecture
          </p>
          <div className="flex items-center gap-2 text-sm text-neutral-500 group-hover:text-neutral-900">
            Start Workshop
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        <Link
          to="/strategy/cohorts"
          className="runway-card p-6 hover:shadow-lg transition-shadow group"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-neutral-900">Manage Cohorts</h3>
          </div>
          <p className="text-sm text-neutral-600 mb-4">
            View and enhance your customer cohorts with strategic intelligence
          </p>
          <div className="flex items-center gap-2 text-sm text-neutral-500 group-hover:text-neutral-900">
            View Cohorts
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        <Link
          to="/strategy/campaigns/new"
          className="runway-card p-6 hover:shadow-lg transition-shadow group bg-gradient-to-br from-neutral-900 to-neutral-800 text-white"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
              <Plus className="w-5 h-5 text-white" />
            </div>
            <h3 className="font-semibold text-white">New Campaign</h3>
          </div>
          <p className="text-sm text-white/70 mb-4">
            Launch a coordinated campaign with strategic intent
          </p>
          <div className="flex items-center gap-2 text-sm text-white/90 group-hover:text-white">
            Create Campaign
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>
      </div>

      {/* Strategy Overview */}
      <div className="runway-card p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="micro-label mb-2">Playbook Spread</p>
            <h2 className="font-serif text-3xl md:text-4xl text-neutral-900 leading-tight">Strategic Capsules</h2>
          </div>
          <Link
            to="/strategy/wizard"
            className="flex items-center gap-2 border border-neutral-900 px-5 py-2 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            Begin Fresh Edit
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {strategySections.map((section, index) => {
            const Icon = section.icon
            return (
              <motion.div
                key={section.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-8 border-2 border-neutral-200 hover:bg-neutral-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 border-2 border-neutral-200 bg-white text-neutral-900 flex items-center justify-center">
                    <Icon className="w-6 h-6" />
                  </div>
                  {section.status === 'complete' && (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  )}
                </div>
                <h3 className="text-xl font-bold text-neutral-900 mb-2">{section.title}</h3>
                <p className="text-neutral-600">{section.description}</p>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Strategy Score */}
      <div className="runway-card p-8">
        <p className="micro-label mb-2">Pulse</p>
        <h2 className="font-serif text-3xl md:text-4xl text-neutral-900 leading-tight mb-6">Strategy Score</h2>
        <div className="flex items-center gap-8">
          <div className="text-6xl font-bold text-neutral-900">92</div>
          <div className="flex-1">
            <div className="w-full h-4 bg-neutral-200 rounded-full overflow-hidden mb-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: '92%' }}
                transition={{ duration: 1 }}
                className="h-full bg-gradient-to-r from-neutral-700 to-neutral-900 rounded-full"
              />
            </div>
            <p className="text-sm text-neutral-600">
              Your strategy is well-defined and actionable
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
