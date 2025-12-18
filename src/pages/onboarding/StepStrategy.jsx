import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowLeft, Compass, Rocket, Target, DollarSign, Clock, Shield, AlertCircle } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'

const goalOptions = [
  { 
    value: 'velocity', 
    label: 'Velocity', 
    subtitle: 'Aggressive Growth',
    desc: "We're okay burning more on CAC if it means faster top-line growth.",
    bullets: ['Higher ad spend', 'More experiments', 'CAC can be ugly short-term'],
    icon: Rocket,
    color: 'from-red-500/20 to-orange-500/10 border-red-500/30'
  },
  { 
    value: 'efficiency', 
    label: 'Efficiency', 
    subtitle: 'Profitability',
    desc: "Every rupee must defend itself. Growth can be slower.",
    bullets: ['Kill unproven channels', 'Strict payback windows', 'Optimize before scaling'],
    icon: Target,
    color: 'from-green-500/20 to-emerald-500/10 border-green-500/30'
  },
  { 
    value: 'penetration', 
    label: 'Penetration', 
    subtitle: 'Steal Market Share',
    desc: "We're willing to invest in brand and long-term awareness.",
    bullets: ['Heavy top-of-funnel', 'Competitive campaigns', 'Brand building'],
    icon: Compass,
    color: 'from-orange-500/20 to-orange-500/10 border-orange-500/30'
  },
]

const demandOptions = [
  { 
    value: 'capture', 
    label: 'Demand Capture',
    desc: 'Target the in-market 5% who are actively searching',
    examples: 'SEO, Google Ads, G2/Capterra, Intent data'
  },
  { 
    value: 'creation', 
    label: 'Demand Creation',
    desc: 'Educate the 95% who don\'t know they need you yet',
    examples: 'Content, LinkedIn, Podcasts, Webinars'
  },
  { 
    value: 'expansion', 
    label: 'Expansion',
    desc: 'Squeeze more value from existing customers',
    examples: 'Upsell, Cross-sell, Referrals, Case studies'
  },
]

const persuasionOptions = [
  { 
    value: 'money', 
    label: 'Money',
    icon: DollarSign,
    desc: 'Your buyers care most about ROI and revenue impact',
    examples: '"Save $50k/year", "2x conversion rates"'
  },
  { 
    value: 'time', 
    label: 'Time',
    icon: Clock,
    desc: 'Your buyers care most about speed and efficiency',
    examples: '"Launch in days, not months", "Save 10 hrs/week"'
  },
  { 
    value: 'risk-image', 
    label: 'Risk / Image',
    icon: Shield,
    desc: 'Your buyers care about safety, compliance, or status',
    examples: '"SOC2 compliant", "Used by Fortune 500"'
  },
]

const StepStrategy = () => {
  const navigate = useNavigate()
  const { strategy, updateStrategy, nextStep, prevStep, setProcessing } = useOnboardingStore()
  
  const [form, setForm] = useState({
    goalPrimary: strategy.goalPrimary || '',
    goalSecondary: strategy.goalSecondary || '',
    demandSource: strategy.demandSource || '',
    persuasionAxis: strategy.persuasionAxis || '',
  })
  
  const [errors, setErrors] = useState({})

  // Sync to store
  useEffect(() => {
    const debounce = setTimeout(() => {
      updateStrategy(form)
    }, 500)
    return () => clearTimeout(debounce)
  }, [form])

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setErrors(prev => ({ ...prev, [field]: null }))
  }

  const isValid = form.goalPrimary && form.demandSource && form.persuasionAxis

  const handleNext = () => {
    const newErrors = {}
    if (!form.goalPrimary) newErrors.goalPrimary = 'Please select a primary goal'
    if (!form.demandSource) newErrors.demandSource = 'Please select a demand source'
    if (!form.persuasionAxis) newErrors.persuasionAxis = 'Please select a persuasion lever'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    // Derive recommended protocols based on selections
    const impliedTradeoffs = []
    const recommendedProtocols = []

    if (form.goalPrimary === 'velocity') {
      impliedTradeoffs.push('Accept higher CAC short-term')
      recommendedProtocols.push('A', 'B')
    } else if (form.goalPrimary === 'efficiency') {
      impliedTradeoffs.push('Focus on proven channels only')
      recommendedProtocols.push('B', 'C')
    } else if (form.goalPrimary === 'penetration') {
      impliedTradeoffs.push('Invest heavily in brand')
      recommendedProtocols.push('A', 'C')
    }

    if (form.demandSource === 'creation') {
      impliedTradeoffs.push('70%+ budget to content & paid social')
      recommendedProtocols.push('A')
    } else if (form.demandSource === 'capture') {
      impliedTradeoffs.push('Double down on search & intent')
      recommendedProtocols.push('B', 'C')
    } else if (form.demandSource === 'expansion') {
      recommendedProtocols.push('D', 'E', 'F')
    }

    updateStrategy({ 
      ...form, 
      impliedTradeoffs,
      recommendedProtocols: [...new Set(recommendedProtocols)]
    })

    // Show processing for ICP generation
    setProcessing(true)
    setTimeout(() => {
      setProcessing(false)
      nextStep()
      navigate('/onboarding/icps')
    }, 1500)
  }

  const handleBack = () => {
    prevStep()
    navigate('/onboarding/market')
  }

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col">
      <div className="flex-1 max-w-5xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-amber-500/10 rounded-xl">
              <Compass className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 5 of 8 · Strategic Trade-offs
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            Pick your <span className="italic text-amber-200">non-negotiables</span>
          </h1>
          <p className="text-white/40 max-w-xl">
            Strategy is about trade-offs. You can't optimize for everything at once.
          </p>
        </motion.div>

        <div className="space-y-12">
          {/* Matrix 1: Goal Focus */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">
              Matrix 1: What's your primary goal?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {goalOptions.map((goal) => {
                const Icon = goal.icon
                const isSelected = form.goalPrimary === goal.value
                return (
                  <button
                    key={goal.value}
                    onClick={() => updateField('goalPrimary', goal.value)}
                    className={`
                      p-6 rounded-2xl border text-left transition-all relative overflow-hidden
                      ${isSelected
                        ? `bg-gradient-to-br ${goal.color}`
                        : 'bg-zinc-900/50 border-white/10 hover:border-white/20'
                      }
                    `}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`p-2 rounded-lg ${isSelected ? 'bg-white/20' : 'bg-white/5'}`}>
                        <Icon className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-white/40'}`} />
                      </div>
                      <div>
                        <div className={`font-medium ${isSelected ? 'text-white' : 'text-white/80'}`}>
                          {goal.label}
                        </div>
                        <div className="text-xs text-white/40">{goal.subtitle}</div>
                      </div>
                    </div>
                    <p className={`text-sm mb-4 ${isSelected ? 'text-white/80' : 'text-white/50'}`}>
                      {goal.desc}
                    </p>
                    <ul className="space-y-1">
                      {goal.bullets.map((bullet, i) => (
                        <li key={i} className="text-xs text-white/40 flex items-center gap-2">
                          <span className="w-1 h-1 bg-current rounded-full" />
                          {bullet}
                        </li>
                      ))}
                    </ul>
                    {isSelected && (
                      <div className="absolute top-3 right-3 w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">
                        <div className="w-2.5 h-2.5 bg-white rounded-full" />
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
            {form.goalPrimary && (
              <p className="text-xs text-white/30 mt-4">
                Optional: Secondary priority?{' '}
                {goalOptions.filter(g => g.value !== form.goalPrimary).map((g, i) => (
                  <button
                    key={g.value}
                    onClick={() => updateField('goalSecondary', g.value)}
                    className={`
                      ml-2 px-2 py-0.5 rounded text-xs transition-colors
                      ${form.goalSecondary === g.value
                        ? 'bg-white/20 text-white'
                        : 'text-white/40 hover:text-white/60'
                      }
                    `}
                  >
                    {g.label}
                  </button>
                ))}
              </p>
            )}
            {errors.goalPrimary && (
              <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> {errors.goalPrimary}
              </p>
            )}
          </motion.div>

          {/* Matrix 2: Demand Source */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">
              Matrix 2: Where will demand come from?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {demandOptions.map((demand) => {
                const isSelected = form.demandSource === demand.value
                return (
                  <button
                    key={demand.value}
                    onClick={() => updateField('demandSource', demand.value)}
                    className={`
                      p-6 rounded-2xl border text-left transition-all
                      ${isSelected
                        ? 'bg-amber-500/20 border-amber-500/50 text-white'
                        : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                      }
                    `}
                  >
                    <div className="font-medium text-lg mb-2">{demand.label}</div>
                    <p className={`text-sm mb-3 ${isSelected ? 'text-white/80' : 'text-white/50'}`}>
                      {demand.desc}
                    </p>
                    <p className="text-xs text-white/30">{demand.examples}</p>
                    {isSelected && (
                      <div className="mt-4 w-full h-1 bg-amber-500/50 rounded-full overflow-hidden">
                        <motion.div 
                          className="h-full bg-amber-500"
                          initial={{ width: 0 }}
                          animate={{ width: '100%' }}
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
            {errors.demandSource && (
              <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> {errors.demandSource}
              </p>
            )}
          </motion.div>

          {/* Matrix 3: Persuasion Lever */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">
              Matrix 3: What lever convinces your buyer?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {persuasionOptions.map((lever) => {
                const Icon = lever.icon
                const isSelected = form.persuasionAxis === lever.value
                return (
                  <button
                    key={lever.value}
                    onClick={() => updateField('persuasionAxis', lever.value)}
                    className={`
                      p-6 rounded-2xl border text-left transition-all
                      ${isSelected
                        ? 'bg-amber-500/20 border-amber-500/50 text-white'
                        : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                      }
                    `}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`p-2 rounded-lg ${isSelected ? 'bg-amber-500/20' : 'bg-white/5'}`}>
                        <Icon className={`w-5 h-5 ${isSelected ? 'text-amber-400' : 'text-white/40'}`} />
                      </div>
                      <div className="font-medium text-lg">{lever.label}</div>
                    </div>
                    <p className={`text-sm mb-3 ${isSelected ? 'text-white/80' : 'text-white/50'}`}>
                      {lever.desc}
                    </p>
                    <p className="text-xs text-amber-400/60 italic">{lever.examples}</p>
                  </button>
                )
              })}
            </div>
            {errors.persuasionAxis && (
              <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> {errors.persuasionAxis}
              </p>
            )}
          </motion.div>

          {/* Strategy Summary */}
          {isValid && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/20 rounded-2xl"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-amber-400/60 mb-4">
                Your Strategy Profile
              </h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-light text-white">
                    {goalOptions.find(g => g.value === form.goalPrimary)?.label}
                  </div>
                  <div className="text-xs text-white/40">Primary Goal</div>
                </div>
                <div>
                  <div className="text-2xl font-light text-white">
                    {demandOptions.find(d => d.value === form.demandSource)?.label}
                  </div>
                  <div className="text-xs text-white/40">Demand Source</div>
                </div>
                <div>
                  <div className="text-2xl font-light text-white">
                    {persuasionOptions.find(p => p.value === form.persuasionAxis)?.label}
                  </div>
                  <div className="text-xs text-white/40">Persuasion Axis</div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-white/40 hover:text-white text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          <button
            onClick={handleNext}
            disabled={!isValid}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all
              ${isValid
                ? 'bg-amber-500 hover:bg-amber-400 text-black'
                : 'bg-white/10 text-white/30 cursor-not-allowed'
              }
            `}
          >
            Generate ICPs
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default StepStrategy

