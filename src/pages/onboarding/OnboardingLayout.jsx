import React from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, ChevronRight, Loader2 } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'

const steps = [
  { id: 1, name: 'Positioning', path: 'positioning' },
  { id: 2, name: 'Company', path: 'company' },
  { id: 3, name: 'Product', path: 'product' },
  { id: 4, name: 'Market', path: 'market' },
  { id: 5, name: 'Strategy', path: 'strategy' },
  { id: 6, name: 'ICPs', path: 'icps' },
  { id: 7, name: 'War Plan', path: 'warplan' },
  { id: 8, name: 'Choose Plan', path: 'plan' },
]

const OnboardingLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { currentStep, completedSteps, isSaved, isProcessing, getProgress, mode, salesRepName } = useOnboardingStore()

  const progress = getProgress()
  const currentPath = location.pathname.split('/').pop()
  const activeStepIndex = steps.findIndex(s => s.path === currentPath)
  const activeStep = activeStepIndex !== -1 ? activeStepIndex + 1 : currentStep

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Background gradient */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[600px] bg-gradient-radial from-amber-900/10 via-transparent to-transparent opacity-50" />
        <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-gradient-radial from-purple-900/5 via-transparent to-transparent" />
      </div>

      {/* Header */}
      <header className="relative z-20 border-b border-white/5 bg-zinc-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <button 
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
          >
            <span className="text-xl tracking-tight font-light text-white">
              Raptor<span className="italic font-normal text-amber-200">flow</span>
            </span>
          </button>

          {/* Progress indicator */}
          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-32 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <motion.div 
                  className="h-full bg-gradient-to-r from-amber-500 to-amber-400"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <span className="text-xs text-white/40">{progress}%</span>
            </div>
          </div>

          {/* Save status & mode */}
          <div className="flex items-center gap-4">
            {mode === 'sales-assisted' && (
              <span className="text-xs text-amber-400/80 bg-amber-500/10 px-3 py-1 rounded-full">
                Sales: {salesRepName}
              </span>
            )}
            <span className="text-xs text-white/40">
              {isProcessing ? (
                <span className="flex items-center gap-1.5">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Processing...
                </span>
              ) : isSaved ? (
                <span className="flex items-center gap-1.5 text-emerald-400/80">
                  <Check className="w-3 h-3" />
                  Saved
                </span>
              ) : (
                'Saving...'
              )}
            </span>
          </div>
        </div>

        {/* Step indicators */}
        <div className="max-w-7xl mx-auto px-6 pb-4">
          <div className="flex items-center gap-1 overflow-x-auto scrollbar-hide">
            {steps.map((step, index) => {
              const isActive = activeStep === step.id
              const isCompleted = completedSteps.includes(step.id)
              const isPast = step.id < activeStep

              return (
                <React.Fragment key={step.id}>
                  <button
                    onClick={() => {
                      if (isCompleted || isPast || step.id <= activeStep) {
                        navigate(`/onboarding/${step.path}`)
                      }
                    }}
                    disabled={!isCompleted && !isPast && step.id > activeStep}
                    className={`
                      flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all
                      ${isActive 
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' 
                        : isCompleted || isPast
                          ? 'bg-white/5 text-white/60 hover:bg-white/10 cursor-pointer'
                          : 'bg-white/5 text-white/20 cursor-not-allowed'
                      }
                    `}
                  >
                    <span className={`
                      w-5 h-5 rounded-full flex items-center justify-center text-[10px]
                      ${isCompleted ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/10'}
                    `}>
                      {isCompleted ? <Check className="w-3 h-3" /> : step.id}
                    </span>
                    <span className="hidden sm:inline whitespace-nowrap">{step.name}</span>
                  </button>
                  {index < steps.length - 1 && (
                    <ChevronRight className="w-4 h-4 text-white/10 flex-shrink-0" />
                  )}
                </React.Fragment>
              )
            })}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default OnboardingLayout

