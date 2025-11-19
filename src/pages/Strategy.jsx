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
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 p-12 text-white"
      >
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
              <Sparkles className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-4xl font-display font-bold mb-2">Strategy</h1>
              <p className="text-primary-100 text-lg">
                Your comprehensive strategy blueprint
              </p>
            </div>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-accent-500/20 rounded-full blur-3xl" />
      </motion.div>

      {/* Strategy Overview */}
      <div className="glass rounded-2xl p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-display font-bold">Strategy Overview</h2>
          <Link
            to="/strategy/wizard"
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            Run Strategy Wizard
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
                className="p-6 rounded-xl border border-neutral-200 hover:bg-neutral-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary-600 flex items-center justify-center">
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
      <div className="glass rounded-2xl p-8">
        <h2 className="text-2xl font-display font-bold mb-6">Strategy Score</h2>
        <div className="flex items-center gap-8">
          <div className="text-6xl font-bold text-primary-600">92</div>
          <div className="flex-1">
            <div className="w-full h-4 bg-neutral-200 rounded-full overflow-hidden mb-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: '92%' }}
                transition={{ duration: 1 }}
                className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
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

