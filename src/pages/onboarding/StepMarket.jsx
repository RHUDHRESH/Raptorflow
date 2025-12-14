import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowLeft, Crosshair, Plus, X, AlertCircle } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'

const alternativeActions = [
  { value: 'competitor', label: 'Use a competitor', desc: 'They pick a direct competitor' },
  { value: 'hire-internal', label: 'Hire someone internally', desc: 'Build in-house team' },
  { value: 'diy-tools', label: 'DIY with spreadsheets/tools', desc: 'Cobble together a solution' },
  { value: 'nothing', label: 'Do nothing', desc: 'Live with the pain' },
]

const StepMarket = () => {
  const navigate = useNavigate()
  const { market, updateMarket, addCompetitor, removeCompetitor, nextStep, prevStep } = useOnboardingStore()
  
  const [form, setForm] = useState({
    alternativeAction: market.alternativeAction || '',
    realCompetition: market.realCompetition || '',
    pricePosition: market.pricePosition || 50,
    complexityPosition: market.complexityPosition || 50,
    differentiation: market.differentiation || '',
  })
  
  const [competitors, setCompetitors] = useState(market.namedCompetitors || [])
  const [newCompetitor, setNewCompetitor] = useState('')
  const [errors, setErrors] = useState({})

  // Sync to store
  useEffect(() => {
    const debounce = setTimeout(() => {
      updateMarket({ ...form, namedCompetitors: competitors })
    }, 500)
    return () => clearTimeout(debounce)
  }, [form, competitors])

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setErrors(prev => ({ ...prev, [field]: null }))
  }

  const handleAddCompetitor = () => {
    if (newCompetitor.trim() && !competitors.includes(newCompetitor.trim())) {
      setCompetitors([...competitors, newCompetitor.trim()])
      setNewCompetitor('')
    }
  }

  const handleRemoveCompetitor = (name) => {
    setCompetitors(competitors.filter(c => c !== name))
  }

  const isValid = form.alternativeAction && form.differentiation

  const handleNext = () => {
    const newErrors = {}
    if (!form.alternativeAction) newErrors.alternativeAction = 'Please select an option'
    if (!form.differentiation) newErrors.differentiation = 'Please explain your differentiation'
    if (form.alternativeAction === 'competitor' && competitors.length === 0) {
      newErrors.competitors = 'Please name at least one competitor'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    updateMarket({ ...form, namedCompetitors: competitors })
    nextStep()
    navigate('/onboarding/strategy')
  }

  const handleBack = () => {
    prevStep()
    navigate('/onboarding/product')
  }

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col">
      <div className="flex-1 max-w-4xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-amber-500/10 rounded-xl">
              <Crosshair className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 4 of 8 · Market & Competition
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            Who are we <span className="italic text-amber-200">up against?</span>
          </h1>
          <p className="text-white/40 max-w-xl">
            Understanding your competitive landscape helps us position you effectively.
          </p>
        </motion.div>

        <div className="space-y-10">
          {/* Alternative Action */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <label className="block text-sm text-white/60 mb-4">
              If your perfect buyer didn't choose you, what would they most likely do instead?
            </label>
            <div className="grid grid-cols-2 gap-3">
              {alternativeActions.map((action) => (
                <button
                  key={action.value}
                  onClick={() => updateField('alternativeAction', action.value)}
                  className={`
                    p-4 rounded-xl border text-left transition-all
                    ${form.alternativeAction === action.value
                      ? 'bg-amber-500/20 border-amber-500/50 text-white'
                      : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                    }
                  `}
                >
                  <div className="font-medium">{action.label}</div>
                  <div className="text-xs text-white/40 mt-1">{action.desc}</div>
                </button>
              ))}
            </div>
            {errors.alternativeAction && (
              <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> {errors.alternativeAction}
              </p>
            )}
          </motion.div>

          {/* Named Competitors */}
          {form.alternativeAction === 'competitor' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <label className="block text-sm text-white/60 mb-3">
                Name 2-3 specific competitors you lose to most often
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {competitors.map((comp) => (
                  <span
                    key={comp}
                    className="flex items-center gap-2 px-3 py-1.5 bg-white/10 text-white rounded-full text-sm"
                  >
                    {comp}
                    <button
                      onClick={() => handleRemoveCompetitor(comp)}
                      className="text-white/40 hover:text-red-400 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newCompetitor}
                  onChange={(e) => setNewCompetitor(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddCompetitor()}
                  placeholder="Add competitor name"
                  className="flex-1 bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
                />
                <button
                  onClick={handleAddCompetitor}
                  className="px-4 py-3 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 rounded-xl transition-colors"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>
              {errors.competitors && (
                <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.competitors}
                </p>
              )}
            </motion.div>
          )}

          {/* Real Competition */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <label className="block text-sm text-white/60 mb-2">
              Who do you think you <span className="text-amber-400">really</span> compete with?
            </label>
            <p className="text-xs text-white/30 mb-3">
              It might be: 'a junior analyst + Excel' not another SaaS
            </p>
            <textarea
              value={form.realCompetition}
              onChange={(e) => updateField('realCompetition', e.target.value)}
              placeholder="Be honest about what you're really replacing..."
              className="w-full h-28 bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 resize-none focus:outline-none focus:border-amber-500/50 transition-colors"
            />
          </motion.div>

          {/* Position Sliders */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="space-y-8"
          >
            <label className="block text-sm text-white/60 mb-4">
              Where do you think you sit on this spectrum?
            </label>

            {/* Price Position */}
            <div>
              <div className="flex justify-between text-xs text-white/40 mb-2">
                <span>Budget / Cheap</span>
                <span>Premium / Expensive</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={form.pricePosition}
                onChange={(e) => updateField('pricePosition', parseInt(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer
                  [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 
                  [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-amber-500 
                  [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg"
              />
              <div className="text-center text-sm text-amber-400 mt-2">
                {form.pricePosition < 33 ? 'Budget' : form.pricePosition < 66 ? 'Mid-market' : 'Premium'}
              </div>
            </div>

            {/* Complexity Position */}
            <div>
              <div className="flex justify-between text-xs text-white/40 mb-2">
                <span>Simple / Easy</span>
                <span>Complex / Power-user</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={form.complexityPosition}
                onChange={(e) => updateField('complexityPosition', parseInt(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer
                  [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 
                  [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-amber-500 
                  [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg"
              />
              <div className="text-center text-sm text-amber-400 mt-2">
                {form.complexityPosition < 33 ? 'Simple' : form.complexityPosition < 66 ? 'Balanced' : 'Power-user'}
              </div>
            </div>
          </motion.div>

          {/* Differentiation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <label className="block text-sm text-white/60 mb-2">
              In one sentence: how would you explain why you're different?
            </label>
            <textarea
              value={form.differentiation}
              onChange={(e) => updateField('differentiation', e.target.value)}
              placeholder="Unlike [alternatives], we [unique advantage]..."
              className="w-full h-28 bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 resize-none focus:outline-none focus:border-amber-500/50 transition-colors"
            />
            {errors.differentiation && (
              <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> {errors.differentiation}
              </p>
            )}
          </motion.div>

          {/* 2D Map Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
          >
            <h3 className="text-xs uppercase tracking-[0.15em] text-white/40 mb-6">
              Your Position Map
            </h3>
            <div className="relative aspect-square max-w-sm mx-auto">
              {/* Grid */}
              <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 border border-white/10">
                <div className="border-r border-b border-white/10" />
                <div className="border-b border-white/10" />
                <div className="border-r border-white/10" />
                <div />
              </div>
              
              {/* Labels */}
              <div className="absolute -left-2 top-1/2 -translate-y-1/2 -rotate-90 text-[10px] text-white/30 whitespace-nowrap">
                Price →
              </div>
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-6 text-[10px] text-white/30 whitespace-nowrap">
                Complexity →
              </div>

              {/* Your position dot */}
              <motion.div
                className="absolute w-4 h-4 bg-amber-500 rounded-full shadow-lg shadow-amber-500/50"
                animate={{
                  left: `${form.complexityPosition}%`,
                  bottom: `${form.pricePosition}%`,
                }}
                style={{
                  transform: 'translate(-50%, 50%)',
                }}
              >
                <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs text-amber-400 whitespace-nowrap">
                  You
                </span>
              </motion.div>

              {/* Competitor dots */}
              {competitors.slice(0, 3).map((comp, i) => (
                <div
                  key={comp}
                  className="absolute w-3 h-3 bg-white/20 rounded-full"
                  style={{
                    left: `${30 + i * 20}%`,
                    bottom: `${40 + i * 15}%`,
                    transform: 'translate(-50%, 50%)',
                  }}
                >
                  <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] text-white/40 whitespace-nowrap">
                    {comp}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
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
            Continue
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default StepMarket

