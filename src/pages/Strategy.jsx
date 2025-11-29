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
  Plus,
  Building2,
  Brain,
  Briefcase,
  BarChart3,
  Eye,
  Scale,
  Bell
} from 'lucide-react'
import { LuxeHeading, LuxeButton, LuxeCard, LuxeBadge, HeroSection } from '../components/ui/PremiumUI'
import { pageTransition, fadeInUp, staggerContainer } from '../utils/animations'

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
    url: '/cohorts',
    color: 'blue',
    status: 'ready',
  },
  {
    title: 'Campaign Builder',
    description: 'Orchestrate coordinated campaigns that ladder up to strategic intent',
    icon: Megaphone,
    url: '/campaigns/new',
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

const councilOfLords = [
  {
    title: 'Architect Lord',
    description: 'Strategic planning & architecture optimization',
    icon: Building2,
    url: '/strategy/architect',
    color: 'purple',
    status: 'ready',
    emoji: '🏗️',
  },
  {
    title: 'Cognition Lord',
    description: 'Learning, knowledge synthesis & decision support',
    icon: Brain,
    url: '/strategy/cognition',
    color: 'blue',
    status: 'ready',
    emoji: '🧠',
  },
  {
    title: 'Strategos Lord',
    description: 'Execution planning & resource allocation',
    icon: Briefcase,
    url: '/strategy/strategos',
    color: 'teal',
    status: 'ready',
    emoji: '⚔️',
  },
  {
    title: 'Aesthete Lord',
    description: 'Quality assurance & brand compliance',
    icon: Award,
    url: '/strategy/aesthete',
    color: 'pink',
    status: 'ready',
    emoji: '✨',
  },
  {
    title: 'Seer Lord',
    description: 'Trend prediction & market intelligence',
    icon: Eye,
    url: '/strategy/seer',
    color: 'indigo',
    status: 'ready',
    emoji: '🔮',
  },
  {
    title: 'Arbiter Lord',
    description: 'Conflict resolution & fair arbitration',
    icon: Scale,
    url: '/strategy/arbiter',
    color: 'orange',
    status: 'ready',
    emoji: '⚖️',
  },
  {
    title: 'Herald Lord',
    description: 'Communications & message delivery',
    icon: Bell,
    url: '/strategy/herald',
    color: 'cyan',
    status: 'ready',
    emoji: '📢',
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
    <motion.div
      className="space-y-8 animate-fade-in p-6 max-w-7xl mx-auto"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageTransition}
    >
      {/* Hero */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Strategic Command Center"
          subtitle="Positioning, Cohorts, and Campaign Orchestration"
          metrics={[
            { label: 'Strategy Score', value: '92' },
            { label: 'Active Moves', value: '12' },
            { label: 'Campaigns', value: '3' }
          ]}
        />
      </motion.div>

      {/* Strategy Tools - NEW */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-mono font-medium uppercase tracking-[0.5em] text-neutral-400 mb-2">Strategic Arsenal</p>
              <LuxeHeading level={2}>Marketing Warfare Tools</LuxeHeading>
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
                      className="block p-6 border border-neutral-200 rounded-xl hover:border-neutral-900 hover:bg-neutral-50 transition-all group h-full"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 border border-neutral-200 rounded-lg bg-white text-neutral-900 flex items-center justify-center group-hover:border-neutral-900 transition-colors">
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
                    <div className="p-6 border border-dashed border-neutral-200 rounded-xl bg-neutral-50 h-full opacity-60">
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 border border-neutral-200 rounded-lg bg-white text-neutral-400 flex items-center justify-center">
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
        </LuxeCard>
      </motion.div>

      {/* Council of Lords - Phase 2A */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border border-slate-700">
          <div className="mb-6">
            <div>
              <p className="text-xs font-mono font-medium uppercase tracking-[0.5em] text-slate-400 mb-2">Strategic Oversight</p>
              <LuxeHeading level={2} className="text-white">Council of Lords</LuxeHeading>
              <p className="text-slate-400 mt-2">Seven powerful agents guiding strategic execution across all domains</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {councilOfLords.map((lord, index) => {
              const Icon = lord.icon
              return (
                <motion.div
                  key={lord.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link
                    to={lord.url}
                    className="block p-5 border border-slate-700 rounded-lg hover:border-slate-500 hover:bg-slate-700/50 transition-all group h-full bg-slate-800/50"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="text-2xl">{lord.emoji}</div>
                      <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300 group-hover:translate-x-1 transition-all" />
                    </div>
                    <h3 className="text-sm font-bold text-white mb-1">{lord.title}</h3>
                    <p className="text-xs text-slate-400">{lord.description}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                      <span className="text-xs text-slate-500">Active</span>
                    </div>
                  </Link>
                </motion.div>
              )
            })}
          </div>
        </LuxeCard>
      </motion.div>

      {/* Quick Actions */}
      <motion.div className="grid grid-cols-1 md:grid-cols-3 gap-6" variants={staggerContainer}>
        <motion.div variants={fadeInUp}>
          <Link to="/strategy/positioning">
            <LuxeCard className="p-6 hover:shadow-lg transition-shadow group h-full">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Award className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="font-semibold text-neutral-900">Define Positioning</h3>
              </div>
              <p className="text-sm text-neutral-600 mb-4">
                Create your strategic positioning statement and message architecture
              </p>
              <div className="flex items-center gap-2 text-sm text-neutral-500 group-hover:text-neutral-900 mt-auto">
                Start Workshop
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </LuxeCard>
          </Link>
        </motion.div>

        <motion.div variants={fadeInUp}>
          <Link to="/cohorts">
            <LuxeCard className="p-6 hover:shadow-lg transition-shadow group h-full">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-neutral-900">Manage Cohorts</h3>
              </div>
              <p className="text-sm text-neutral-600 mb-4">
                View and enhance your customer cohorts with strategic intelligence
              </p>
              <div className="flex items-center gap-2 text-sm text-neutral-500 group-hover:text-neutral-900 mt-auto">
                View Cohorts
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </LuxeCard>
          </Link>
        </motion.div>

        <motion.div variants={fadeInUp}>
          <Link to="/campaigns/new">
            <LuxeCard className="p-6 hover:shadow-lg transition-shadow group bg-gradient-to-br from-neutral-900 to-neutral-800 text-white h-full">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
                  <Plus className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-white">New Campaign</h3>
              </div>
              <p className="text-sm text-white/70 mb-4">
                Launch a coordinated campaign with strategic intent
              </p>
              <div className="flex items-center gap-2 text-sm text-white/90 group-hover:text-white mt-auto">
                Create Campaign
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </LuxeCard>
          </Link>
        </motion.div>
      </motion.div>

      {/* Strategy Overview */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-mono font-medium uppercase tracking-[0.5em] text-neutral-400 mb-2">Playbook Spread</p>
              <LuxeHeading level={2}>Strategic Capsules</LuxeHeading>
            </div>
            <Link
              to="/strategy/wizard"
              className="flex items-center gap-2 border border-neutral-900 px-5 py-2 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-colors rounded-lg"
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
                  className="p-8 border border-neutral-200 rounded-xl hover:bg-neutral-50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 border border-neutral-200 rounded-lg bg-white text-neutral-900 flex items-center justify-center">
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
        </LuxeCard>
      </motion.div>

      {/* Strategy Score */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8">
          <p className="text-xs font-mono font-medium uppercase tracking-[0.5em] text-neutral-400 mb-2">Pulse</p>
          <LuxeHeading level={2} className="mb-6">Strategy Score</LuxeHeading>
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
        </LuxeCard>
      </motion.div>
    </motion.div>
  )
}
