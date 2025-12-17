import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Lightbulb, Target, AlertCircle } from 'lucide-react'
import { BrandIcon } from '@/components/brand/BrandSystem'
import useOnboardingStore from '../../store/onboardingStore'

const promptChips = {
  kennedy: [
    "We save X hours per week",
    "We increase Y% revenue",
    "We reduce Z risk",
    "We replace expensive consultants",
    "We simplify a painful process"
  ],
  dunford: [
    "Better than [competitor] for [segment]",
    "Perfect when you need [outcome]",
    "Built specifically for [industry]",
    "Ideal for teams struggling with [pain]",
    "Designed for [role] who hate [task]"
  ]
}

const StepPositioning = () => {
  const navigate = useNavigate()
  const { positioning, updatePositioning, nextStep } = useOnboardingStore()

  const [danKennedy, setDanKennedy] = useState(positioning.danKennedy || '')
  const [dunford, setDunford] = useState(positioning.dunford || '')
  const [activeField, setActiveField] = useState('kennedy')
  const [errors, setErrors] = useState({})

  // Sync to store on blur
  useEffect(() => {
    const debounce = setTimeout(() => {
      updatePositioning({ danKennedy, dunford })
    }, 500)
    return () => clearTimeout(debounce)
  }, [danKennedy, dunford])

  const kennedyLength = danKennedy.trim().length
  const dunfordLength = dunford.trim().length
  const kennedyValid = kennedyLength >= 50
  const dunfordValid = dunfordLength >= 50

  const handleNext = () => {
    const newErrors = {}
    if (!kennedyValid) newErrors.kennedy = 'Please write at least 50 characters'
    if (!dunfordValid) newErrors.dunford = 'Please write at least 50 characters'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    updatePositioning({ danKennedy, dunford })
    nextStep()
    navigate('/onboarding/company')
  }

  const insertChip = (text) => {
    if (activeField === 'kennedy') {
      setDanKennedy(prev => prev ? `${prev} ${text}` : text)
    } else {
      setDunford(prev => prev ? `${prev} ${text}` : text)
    }
  }

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col">
      <div className="flex-1 max-w-4xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-amber-500/10 rounded-xl">
              <Target className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 1 of 8 · Positioning Raw Material
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            What makes you <span className="italic text-amber-200">worth buying?</span>
          </h1>
          <p className="text-white/40 max-w-xl">
            Write it badly, that's fine. We'll clean it up. Just be honest about why someone should choose you.
          </p>
        </motion.div>

        {/* Questions */}
        <div className="space-y-10">
          {/* Dan Kennedy Question */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className={`relative p-6 md:p-8 rounded-2xl border transition-colors ${activeField === 'kennedy'
              ? 'bg-amber-500/5 border-amber-500/30'
              : 'bg-zinc-900/50 border-white/5 hover:border-white/10'
              }`}
            onClick={() => setActiveField('kennedy')}
          >
            <div className="flex items-start gap-4 mb-6">
              <BrandIcon name="speed" className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-lg font-medium text-white mb-1">
                The Dan Kennedy Question
              </h2>
              <p className="text-white/50 text-sm leading-relaxed">
                "Why should I choose you over every other option – including doing nothing?"
              </p>
            </div>

            <textarea
              value={danKennedy}
              onChange={(e) => {
                setDanKennedy(e.target.value)
                setErrors(prev => ({ ...prev, kennedy: null }))
              }}
              onFocus={() => setActiveField('kennedy')}
              placeholder="Be specific. What problem do you solve? What outcome do you deliver? Why you and not a competitor or spreadsheet?"
              className="w-full h-40 bg-black/30 border border-white/10 rounded-xl p-4 text-white placeholder:text-white/20 resize-none focus:outline-none focus:border-amber-500/50 transition-colors"
            />

            {/* Character count & error */}
            <div className="flex items-center justify-between mt-3">
              <div className="flex flex-wrap gap-2">
                {promptChips.kennedy.slice(0, 3).map((chip, i) => (
                  <button
                    key={i}
                    onClick={() => insertChip(chip)}
                    className="text-xs px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white/40 hover:text-white/60 rounded-full transition-colors"
                  >
                    {chip}
                  </button>
                ))}
              </div>
              <span className={`text-xs ${kennedyValid ? 'text-emerald-400' : 'text-white/30'}`}>
                {kennedyLength}/50 min
              </span>
            </div>

            {errors.kennedy && (
              <div className="flex items-center gap-2 mt-3 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                {errors.kennedy}
              </div>
            )}
          </motion.div>

      {/* April Dunford Question */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className={`relative p-6 md:p-8 rounded-2xl border transition-colors ${activeField === 'dunford'
          ? 'bg-amber-500/5 border-amber-500/30'
          : 'bg-zinc-900/50 border-white/5 hover:border-white/10'
          }`}
        onClick={() => setActiveField('dunford')}
      >
        <div className="flex items-start gap-4 mb-6">
          <div className="p-2 bg-white/5 rounded-lg flex-shrink-0">
            <Lightbulb className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg font-medium text-white mb-1">
              The April Dunford Question
            </h2>
            <p className="text-white/50 text-sm leading-relaxed">
              "Who is your product <span className="text-amber-300">obviously better</span> for – and in what situations?"
            </p>
          </div>
        </div>

        <textarea
          value={dunford}
          onChange={(e) => {
            setDunford(e.target.value)
            setErrors(prev => ({ ...prev, dunford: null }))
          }}
          onFocus={() => setActiveField('dunford')}
          placeholder="Example: 'We're better than HubSpot for B2B SaaS teams with long sales cycles and complex buying committees.'"
          className="w-full h-40 bg-black/30 border border-white/10 rounded-xl p-4 text-white placeholder:text-white/20 resize-none focus:outline-none focus:border-amber-500/50 transition-colors"
        />

        {/* Character count & error */}
        <div className="flex items-center justify-between mt-3">
          <div className="flex flex-wrap gap-2">
            {promptChips.dunford.slice(0, 3).map((chip, i) => (
              <button
                key={i}
                onClick={() => insertChip(chip)}
                className="text-xs px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white/40 hover:text-white/60 rounded-full transition-colors"
              >
                {chip}
              </button>
            ))}
          </div>
          <span className={`text-xs ${dunfordValid ? 'text-emerald-400' : 'text-white/30'}`}>
            {dunfordLength}/50 min
          </span>
        </div>

        {errors.dunford && (
          <div className="flex items-center gap-2 mt-3 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            {errors.dunford}
          </div>
        )}
      </motion.div>
        </div>
      </div>

      {/* Footer navigation */}
      <div className="border-t border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="text-white/40 hover:text-white text-sm transition-colors"
          >
            Cancel
          </button>

          <button
            onClick={handleNext}
            disabled={!kennedyValid || !dunfordValid}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all
              ${kennedyValid && dunfordValid
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

export default StepPositioning

