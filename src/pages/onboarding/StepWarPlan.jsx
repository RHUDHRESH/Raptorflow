import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowLeft, Map, Sparkles, Target, Zap, Shield, Users, Clock, ChevronRight, Check } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'

const protocols = {
  A: { name: 'Authority Blitz', icon: Sparkles, desc: 'Build thought leadership fast', color: 'text-purple-400 bg-purple-500/10' },
  B: { name: 'Trust Anchor', icon: Shield, desc: 'Validation and social proof', color: 'text-blue-400 bg-blue-500/10' },
  C: { name: 'Cost of Inaction', icon: Target, desc: 'Create urgency to act', color: 'text-red-400 bg-red-500/10' },
  D: { name: 'Facilitator Nudge', icon: Zap, desc: 'Smooth onboarding & activation', color: 'text-green-400 bg-green-500/10' },
  E: { name: 'Champions Armory', icon: Users, desc: 'Arm your internal advocates', color: 'text-amber-400 bg-amber-500/10' },
  F: { name: 'Churn Intercept', icon: Clock, desc: 'Retention & expansion plays', color: 'text-pink-400 bg-pink-500/10' },
}

const generateWarPlan = (strategy, icps) => {
  const selectedICPs = icps.filter(i => i.selected)
  
  return {
    phases: [
      {
        id: 1,
        name: 'Discovery & Authority',
        days: '1-30',
        objectives: [
          'Establish thought leadership positioning',
          'Build initial content foundation',
          'Set up tracking & attribution'
        ],
        campaigns: ['Authority Blitz', 'Content Waterfall'],
        kpis: [
          { name: 'Content pieces published', target: '8-12' },
          { name: 'Website traffic', target: '+30%' },
          { name: 'LinkedIn impressions', target: '50k' }
        ]
      },
      {
        id: 2,
        name: 'Launch & Validation',
        days: '31-60',
        objectives: [
          'Launch demand capture campaigns',
          'Build trust & social proof',
          'Start outbound to ICP accounts'
        ],
        campaigns: ['Trust Anchor', 'Spear Attack'],
        kpis: [
          { name: 'Demo conversion rate', target: '15%+' },
          { name: 'Pipeline generated', target: '$100k+' },
          { name: 'Case studies collected', target: '3' }
        ]
      },
      {
        id: 3,
        name: 'Optimization & Scale',
        days: '61-90',
        objectives: [
          'Double down on winning channels',
          'Kill underperforming experiments',
          'Prepare for next quarter'
        ],
        campaigns: ['Expansion Plays', 'Churn Intercept'],
        kpis: [
          { name: 'CAC payback', target: '<12 months' },
          { name: 'Win rate', target: '25%+' },
          { name: 'NRR', target: '110%+' }
        ]
      }
    ],
    activeProtocols: strategy.recommendedProtocols || ['A', 'B']
  }
}

const StepWarPlan = () => {
  const navigate = useNavigate()
  const { strategy, icps, warPlan, setWarPlan, toggleProtocol, nextStep, prevStep } = useOnboardingStore()
  
  const [isGenerating, setIsGenerating] = useState(true)
  const [activePhase, setActivePhase] = useState(1)

  // Generate war plan on mount
  useEffect(() => {
    if (!warPlan.generated) {
      setTimeout(() => {
        const plan = generateWarPlan(strategy, icps)
        setWarPlan({
          generated: true,
          phases: plan.phases,
          protocols: Object.keys(protocols).reduce((acc, key) => ({
            ...acc,
            [key]: {
              ...protocols[key],
              active: plan.activeProtocols.includes(key)
            }
          }), {}),
          skeleton: plan
        })
        setIsGenerating(false)
      }, 2000)
    } else {
      setIsGenerating(false)
    }
  }, [])

  const handleNext = () => {
    nextStep()
    navigate('/onboarding/plan')
  }

  const handleBack = () => {
    prevStep()
    navigate('/onboarding/icps')
  }

  if (isGenerating) {
    return (
      <div className="min-h-[calc(100vh-140px)] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="relative mb-8">
            <div className="w-20 h-20 border-4 border-amber-500/20 rounded-full animate-pulse" />
            <Map className="absolute inset-0 m-auto w-8 h-8 text-amber-400 animate-pulse" />
          </div>
          <h2 className="text-2xl font-light text-white mb-2">Building your 90-Day War Plan...</h2>
          <p className="text-white/40">Mapping strategies to tactical execution</p>
        </motion.div>
      </div>
    )
  }

  const selectedICPs = icps.filter(i => i.selected)

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col">
      <div className="flex-1 max-w-6xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-amber-500/10 rounded-xl">
              <Map className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 7 of 8 · War Plan Preview
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            Your 90-Day <span className="italic text-amber-200">War Plan</span>
          </h1>
          <p className="text-white/40 max-w-xl">
            Here's your strategic roadmap. Review the phases and protocols we've recommended.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main content - 2 columns */}
          <div className="lg:col-span-2 space-y-8">
            {/* Summary cards */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-3 gap-4"
            >
              <div className="p-4 bg-zinc-900/50 border border-white/10 rounded-xl text-center">
                <div className="text-3xl font-light text-white mb-1">{selectedICPs.length}</div>
                <div className="text-xs text-white/40">Target ICPs</div>
              </div>
              <div className="p-4 bg-zinc-900/50 border border-white/10 rounded-xl text-center">
                <div className="text-3xl font-light text-white mb-1">3</div>
                <div className="text-xs text-white/40">Phases</div>
              </div>
              <div className="p-4 bg-zinc-900/50 border border-white/10 rounded-xl text-center">
                <div className="text-3xl font-light text-white mb-1">
                  {Object.values(warPlan.protocols).filter(p => p.active).length}
                </div>
                <div className="text-xs text-white/40">Active Protocols</div>
              </div>
            </motion.div>

            {/* Timeline */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">
                90-Day Timeline
              </h3>

              {/* Phase tabs */}
              <div className="flex gap-2 mb-6">
                {warPlan.phases?.map((phase) => (
                  <button
                    key={phase.id}
                    onClick={() => setActivePhase(phase.id)}
                    className={`
                      flex-1 p-4 rounded-xl border text-left transition-all
                      ${activePhase === phase.id
                        ? 'bg-amber-500/20 border-amber-500/50'
                        : 'bg-white/5 border-white/10 hover:border-white/20'
                      }
                    `}
                  >
                    <div className="text-xs text-white/40 mb-1">Days {phase.days}</div>
                    <div className={`font-medium ${activePhase === phase.id ? 'text-white' : 'text-white/60'}`}>
                      {phase.name}
                    </div>
                  </button>
                ))}
              </div>

              {/* Active phase details */}
              {warPlan.phases?.filter(p => p.id === activePhase).map((phase) => (
                <div key={phase.id} className="space-y-6">
                  {/* Objectives */}
                  <div>
                    <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Objectives</h4>
                    <ul className="space-y-2">
                      {phase.objectives.map((obj, i) => (
                        <li key={i} className="flex items-center gap-3 text-sm text-white/80">
                          <Check className="w-4 h-4 text-amber-400" />
                          {obj}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Campaigns */}
                  <div>
                    <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Campaigns</h4>
                    <div className="flex flex-wrap gap-2">
                      {phase.campaigns.map((campaign, i) => (
                        <span key={i} className="px-3 py-1.5 bg-amber-500/10 text-amber-400 rounded-full text-sm">
                          {campaign}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* KPIs */}
                  <div>
                    <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Key Metrics</h4>
                    <div className="grid grid-cols-3 gap-3">
                      {phase.kpis.map((kpi, i) => (
                        <div key={i} className="p-3 bg-white/5 rounded-lg">
                          <div className="text-lg font-light text-white">{kpi.target}</div>
                          <div className="text-xs text-white/40">{kpi.name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Sidebar - Protocols */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-4"
          >
            <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl">
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-4">
                Execution Protocols
              </h3>

              <div className="space-y-3">
                {Object.entries(warPlan.protocols).map(([key, protocol]) => {
                  const Icon = protocols[key].icon
                  return (
                    <button
                      key={key}
                      onClick={() => toggleProtocol(key, !protocol.active)}
                      className={`
                        w-full p-4 rounded-xl border text-left transition-all flex items-center gap-3
                        ${protocol.active
                          ? 'bg-gradient-to-r from-amber-500/10 to-transparent border-amber-500/30'
                          : 'bg-white/5 border-white/10 opacity-50 hover:opacity-75'
                        }
                      `}
                    >
                      <div className={`p-2 rounded-lg ${protocols[key].color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <div className={`text-sm font-medium ${protocol.active ? 'text-white' : 'text-white/60'}`}>
                          {protocol.name}
                        </div>
                        <div className="text-xs text-white/40">{protocols[key].desc}</div>
                      </div>
                      <div className={`
                        w-5 h-5 rounded-full border-2 flex items-center justify-center
                        ${protocol.active ? 'border-amber-500 bg-amber-500' : 'border-white/20'}
                      `}>
                        {protocol.active && <Check className="w-3 h-3 text-black" />}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Target ICPs summary */}
            <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl">
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-4">
                Target ICPs
              </h3>
              <div className="space-y-2">
                {selectedICPs.map((icp) => (
                  <div key={icp.id} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                    <Users className="w-4 h-4 text-amber-400" />
                    <span className="text-sm text-white">{icp.label}</span>
                    <span className="text-xs text-white/40 ml-auto">{icp.fitScore}%</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-white/40 hover:text-white text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          <button
            onClick={handleNext}
            className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium bg-amber-500 hover:bg-amber-400 text-black transition-all"
          >
            Choose Your Plan
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default StepWarPlan

