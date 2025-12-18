import React, { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import {
  Target,
  CheckCircle2,
  Layers
} from 'lucide-react'

// Animated metric card in the preview
const MetricCard = ({ label, value, status, delay }) => {
  const statusColors = {
    green: 'bg-emerald-500',
    zinc: 'bg-zinc-500',
    red: 'bg-red-500'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="bg-white/[0.03] rounded-lg p-3 border border-white/[0.06]"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-white/35 uppercase tracking-wider">{label}</span>
        <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
      </div>
      <div className="text-xl font-light text-white">{value}</div>
    </motion.div>
  )
}

// Animated campaign item
const CampaignItem = ({ name, protocol, status, delay }) => {
  const protocolColors = {
    'Authority': 'text-purple-400 bg-purple-500/15',
    'Trust': 'text-gray-400 bg-gray-500/15',
    'Urgency': 'text-zinc-400 bg-zinc-500/15'
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="flex items-center justify-between p-3 bg-white/[0.03] rounded-lg border border-white/[0.06]"
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-white/[0.05] rounded flex items-center justify-center">
          <Layers className="w-4 h-4 text-white/30" />
        </div>
        <div>
          <div className="text-sm text-white">{name}</div>
          <span className={`text-[10px] px-2 py-0.5 rounded ${protocolColors[protocol]}`}>
            {protocol}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {status === 'active' ? (
          <span className="flex items-center gap-1 text-xs text-emerald-400">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
            Active
          </span>
        ) : (
          <span className="text-xs text-white/30">Planned</span>
        )}
      </div>
    </motion.div>
  )
}

// Animated task item
const TaskItem = ({ task, completed, delay }) => (
  <motion.div
    initial={{ opacity: 0, x: -10 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay, duration: 0.4 }}
    className="flex items-center gap-3 py-2"
  >
    <div className={`w-4 h-4 rounded border flex items-center justify-center ${completed ? 'bg-emerald-500/15 border-emerald-500/25' : 'border-white/15'
      }`}>
      {completed && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
    </div>
    <span className={`text-sm ${completed ? 'text-white/30 line-through' : 'text-white/50'}`}>
      {task}
    </span>
  </motion.div>
)

// The mock dashboard
const MockDashboard = () => {
  const [activeTab, setActiveTab] = useState(0)
  const tabs = ['War Room', 'Campaigns', 'Matrix']

  return (
    <div className="bg-card rounded-xl border border-border/50 overflow-hidden shadow-2xl">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-secondary border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/50" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
            <div className="w-3 h-3 rounded-full bg-green-500/50" />
          </div>
          <div className="flex items-center gap-2 ml-4">
            <div className="w-6 h-6 bg-gradient-to-br from-zinc-500 to-zinc-600 rounded flex items-center justify-center">
              <span className="text-black text-[10px] font-bold">Rf</span>
            </div>
            <span className="text-white/50 text-sm">RaptorFlow</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-1 bg-card border border-border/50 rounded-lg p-1">
          {tabs.map((tab, i) => (
            <button
              key={tab}
              onClick={() => setActiveTab(i)}
              className={`px-3 py-1 rounded text-xs transition-all ${activeTab === i
                  ? 'bg-white/[0.08] text-white'
                  : 'text-white/35 hover:text-white/60'
                }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6 min-h-[400px]">
        <AnimatePresence mode="wait">
          {activeTab === 0 && (
            <motion.div
              key="warroom"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {/* Stats row */}
              <div className="grid grid-cols-4 gap-4">
                <MetricCard label="Pipeline" value="₹24.5L" status="green" delay={0.1} />
                <MetricCard label="Win Rate" value="28%" status="zinc" delay={0.2} />
                <MetricCard label="CAC" value="₹4.2K" status="green" delay={0.3} />
                <MetricCard label="NRR" value="112%" status="green" delay={0.4} />
              </div>

              {/* Campaigns */}
              <div>
                <h4 className="text-xs uppercase tracking-wider text-white/30 mb-3">Active Campaigns</h4>
                <div className="space-y-2">
                  <CampaignItem name="Q1 Pipeline Acceleration" protocol="Authority" status="active" delay={0.5} />
                  <CampaignItem name="Enterprise Expansion" protocol="Trust" status="active" delay={0.6} />
                  <CampaignItem name="Churn Prevention Sprint" protocol="Urgency" status="planned" delay={0.7} />
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 1 && (
            <motion.div
              key="campaigns"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-2 gap-6">
                {/* Campaign detail */}
                <div className="bg-white/[0.03] rounded-lg p-4 border border-white/[0.06]">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-purple-500/15 rounded-lg flex items-center justify-center">
                      <Target className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <h4 className="text-white font-medium">Q1 Pipeline</h4>
                      <span className="text-xs text-white/35">Velocity Goal</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/35">Progress</span>
                      <span className="text-white">68%</span>
                    </div>
                    <div className="h-2 bg-white/[0.06] rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: '68%' }}
                        transition={{ delay: 0.5, duration: 1 }}
                        className="h-full bg-gradient-to-r from-purple-500 to-purple-400 rounded-full"
                      />
                    </div>
                  </div>
                </div>

                {/* Tasks */}
                <div className="bg-white/[0.03] rounded-lg p-4 border border-white/[0.06]">
                  <h4 className="text-xs uppercase tracking-wider text-white/30 mb-3">Current Tasks</h4>
                  <TaskItem task="Launch webinar campaign" completed={true} delay={0.3} />
                  <TaskItem task="Create battlecard for Acme" completed={true} delay={0.4} />
                  <TaskItem task="Deploy email sequence" completed={false} delay={0.5} />
                  <TaskItem task="Review pipeline metrics" completed={false} delay={0.6} />
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 2 && (
            <motion.div
              key="matrix"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {/* RAG Summary */}
              <div className="flex items-center justify-between p-4 bg-emerald-500/5 border border-emerald-500/15 rounded-lg">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                  <div>
                    <div className="text-white font-medium">Overall Health: On Track</div>
                    <div className="text-sm text-white/35">8 of 10 metrics green</div>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-light text-emerald-400">8</div>
                    <div className="text-[10px] text-white/35">Green</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-light text-zinc-400">2</div>
                    <div className="text-[10px] text-white/35">zinc</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-light text-red-400">0</div>
                    <div className="text-[10px] text-white/35">Red</div>
                  </div>
                </div>
              </div>

              {/* Metric grid */}
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: 'Website Traffic', value: '12.4K', status: 'green' },
                  { label: 'Demo Requests', value: '48', status: 'green' },
                  { label: 'Conversion Rate', value: '18%', status: 'zinc' },
                  { label: 'Activation', value: '62%', status: 'green' },
                  { label: 'Churn Rate', value: '3.2%', status: 'zinc' },
                  { label: 'LTV:CAC', value: '4.8x', status: 'green' }
                ].map((metric, i) => (
                  <MetricCard key={i} {...metric} delay={0.2 + i * 0.1} />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// Main DashboardPreview component
const DashboardPreview = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  return (
    <section
      ref={sectionRef}
      className="relative py-32 md:py-40 bg-[#030303] overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-zinc-500/3 rounded-full blur-3xl" />
      </div>

      <div className="max-w-6xl mx-auto px-6 md:px-12 relative z-10">
        {/* Section header */}
        <div className="text-center mb-16 md:mb-20">
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="inline-flex items-center gap-3 mb-8"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-zinc-500/50" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-zinc-400/60 font-medium">
              The Interface
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-zinc-500/50" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight mb-8"
          >
            Your{' '}
            <span className="bg-gradient-to-r from-zinc-200 via-zinc-100 to-zinc-200 bg-clip-text text-transparent">
              command center
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg md:text-xl text-white/35 max-w-2xl mx-auto"
          >
            Everything in one place. Strategy, execution, and measurement unified.
          </motion.p>
        </div>

        {/* Dashboard mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="relative"
        >
          {/* Subtle glow - reduced intensity */}
          <div className="absolute -inset-4 bg-gradient-to-r from-zinc-500/10 via-yellow-500/5 to-zinc-500/10 rounded-2xl blur-2xl opacity-30" />

          {/* Dashboard */}
          <div className="relative">
            <MockDashboard />
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default DashboardPreview

