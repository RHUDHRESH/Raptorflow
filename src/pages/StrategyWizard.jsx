import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, ArrowRight, ArrowLeft, CheckCircle2, Target, Users, TrendingUp, Zap } from 'lucide-react'
import { cn } from '../utils/cn'

const steps = [
  {
    id: 1,
    title: 'Business Context',
    description: 'Tell us about your business',
    icon: Target,
  },
  {
    id: 2,
    title: 'Target Market',
    description: 'Define your ideal customers',
    icon: Users,
  },
  {
    id: 3,
    title: 'Value Proposition',
    description: 'What makes you unique?',
    icon: Zap,
  },
  {
    id: 4,
    title: 'Success Metrics',
    description: 'How will you measure success?',
    icon: TrendingUp,
  },
]

export default function StrategyWizard() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    businessContext: '',
    targetMarket: '',
    valueProposition: '',
    successMetrics: '',
  })

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    } else {
      // Complete wizard
      navigate('/strategy')
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const currentStepData = steps[currentStep - 1]
  const Icon = currentStepData.icon

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-4xl w-full space-y-8">
        {/* Progress */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div className={cn(
                    "w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all",
                    currentStep > step.id
                      ? "bg-primary-600 border-primary-600 text-white"
                      : currentStep === step.id
                      ? "border-primary-600 bg-white text-primary-600"
                      : "border-neutral-300 bg-white text-neutral-400"
                  )}>
                    {currentStep > step.id ? (
                      <CheckCircle2 className="w-6 h-6" />
                    ) : (
                      <step.icon className="w-6 h-6" />
                    )}
                  </div>
                  <div className="mt-2 text-center">
                    <div className={cn(
                      "text-sm font-medium",
                      currentStep >= step.id ? "text-neutral-900" : "text-neutral-400"
                    )}>
                      {step.title}
                    </div>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className={cn(
                    "flex-1 h-0.5 mx-4 transition-colors",
                    currentStep > step.id ? "bg-primary-600" : "bg-neutral-300"
                  )} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="glass rounded-2xl p-12"
        >
          <div className="text-center mb-8">
            <div className="w-20 h-20 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center mx-auto mb-4">
              <Icon className="w-10 h-10" />
            </div>
            <h2 className="text-3xl font-display font-bold mb-2">{currentStepData.title}</h2>
            <p className="text-neutral-600 text-lg">{currentStepData.description}</p>
          </div>

          <div className="space-y-6">
            {currentStep === 1 && (
              <textarea
                rows={8}
                placeholder="Describe your business, industry, current situation, and goals..."
                value={formData.businessContext}
                onChange={(e) => setFormData({ ...formData, businessContext: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              />
            )}
            {currentStep === 2 && (
              <textarea
                rows={8}
                placeholder="Describe your ideal customer profile, their pain points, and how you serve them..."
                value={formData.targetMarket}
                onChange={(e) => setFormData({ ...formData, targetMarket: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              />
            )}
            {currentStep === 3 && (
              <textarea
                rows={8}
                placeholder="What makes your solution unique? What value do you provide that competitors don't?"
                value={formData.valueProposition}
                onChange={(e) => setFormData({ ...formData, valueProposition: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              />
            )}
            {currentStep === 4 && (
              <textarea
                rows={8}
                placeholder="What metrics will you track? How will you measure success?"
                value={formData.successMetrics}
                onChange={(e) => setFormData({ ...formData, successMetrics: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              />
            )}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-8 border-t border-neutral-200">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className={cn(
                "flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-colors",
                currentStep === 1
                  ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                  : "bg-neutral-100 text-neutral-700 hover:bg-neutral-200"
              )}
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>
            <button
              onClick={handleNext}
              className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
            >
              {currentStep === steps.length ? 'Complete' : 'Next'}
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

