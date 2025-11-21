import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sparkles, ArrowRight, Target, TrendingUp, Users, Zap, CheckCircle2 } from 'lucide-react'

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
              Blueprint the Collection
            </h1>
            <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
              Narrative, value, and metrics in one editorial spread
            </p>
          </div>
        </div>
      </motion.div>

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

