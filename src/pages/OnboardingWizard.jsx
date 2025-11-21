import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle2,
  Sparkles,
  Target,
  Users,
  TrendingUp
} from 'lucide-react'
import { cn } from '../utils/cn'

// 10-question onboarding flow
const ONBOARDING_QUESTIONS = [
  {
    id: 1,
    section: 'Foundation',
    question: 'What does your business do?',
    type: 'text',
    placeholder: 'Describe your product or service in simple terms',
    required: true
  },
  {
    id: 2,
    section: 'Foundation',
    question: 'What do you sell and what do people pay?',
    type: 'text',
    placeholder: 'Product/Service? One-time or recurring? Price range?',
    required: true
  },
  {
    id: 3,
    section: 'Foundation',
    question: 'Why did you start this business?',
    type: 'textarea',
    placeholder: 'What problem are you solving? What pushed you to start?',
    required: true
  },
  {
    id: 4,
    section: 'Customers',
    question: 'Who are your best customers?',
    type: 'text',
    placeholder: 'Think of 2-3 examples. What business? What size? Who do you deal with?',
    required: true
  },
  {
    id: 5,
    section: 'Customers',
    question: 'What makes your best customers different?',
    type: 'textarea',
    placeholder: 'What traits, behaviors, or characteristics do they share?',
    required: false
  },
  {
    id: 6,
    section: 'Positioning',
    question: 'How do you position yourself vs competitors?',
    type: 'textarea',
    placeholder: 'What makes you different? What\'s your unique angle?',
    required: false
  },
  {
    id: 7,
    section: 'Positioning',
    question: 'Where do your customers find you?',
    type: 'multiselect',
    options: ['LinkedIn', 'Google Search', 'Referrals', 'Events', 'Content', 'Paid Ads', 'Other'],
    required: false
  },
  {
    id: 8,
    section: 'Operations',
    question: 'What marketing capabilities do you have?',
    type: 'multiselect',
    options: ['Email Marketing', 'Social Media', 'Content Creation', 'Paid Ads', 'SEO', 'Analytics', 'CRM'],
    required: false
  },
  {
    id: 9,
    section: 'Operations',
    question: 'What\'s your biggest growth challenge right now?',
    type: 'select',
    options: ['Acquisition', 'Retention', 'Activation', 'Revenue', 'Scaling'],
    required: true
  },
  {
    id: 10,
    section: 'Goals',
    question: 'What would make the next 90 days a success?',
    type: 'textarea',
    placeholder: 'Be specific. What metrics or outcomes matter most?',
    required: true
  }
]

export default function OnboardingWizard() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState({})
  const [selectedOptions, setSelectedOptions] = useState({})

  const currentQuestion = ONBOARDING_QUESTIONS[currentStep]
  const progress = ((currentStep + 1) / ONBOARDING_QUESTIONS.length) * 100
  const canProceed = currentQuestion.required 
    ? answers[currentQuestion.id] || (currentQuestion.type === 'multiselect' && selectedOptions[currentQuestion.id]?.length > 0)
    : true

  const handleAnswer = (value) => {
    setAnswers(prev => ({ ...prev, [currentQuestion.id]: value }))
  }

  const handleMultiSelect = (option) => {
    const current = selectedOptions[currentQuestion.id] || []
    const updated = current.includes(option)
      ? current.filter(o => o !== option)
      : [...current, option]
    setSelectedOptions(prev => ({ ...prev, [currentQuestion.id]: updated }))
  }

  const handleNext = () => {
    if (currentStep < ONBOARDING_QUESTIONS.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      handleComplete()
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleComplete = () => {
    // Save onboarding data
    const onboardingData = {
      answers,
      selectedOptions,
      completedAt: new Date().toISOString()
    }
    localStorage.setItem('onboardingData', JSON.stringify(onboardingData))
    
    // Navigate to dashboard
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-white flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="max-w-2xl w-full space-y-8"
      >
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm text-neutral-600">
            <span>Question {currentStep + 1} of {ONBOARDING_QUESTIONS.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
              className="h-full bg-gradient-to-r from-neutral-700 to-neutral-900 rounded-full"
            />
          </div>
        </div>

        {/* Question Card */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.18 }}
          className="runway-card p-8 space-y-6"
        >
          {/* Section Badge */}
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 text-[10px] font-mono uppercase tracking-[0.2em] bg-neutral-100 text-neutral-700 rounded-lg">
              {currentQuestion.section}
            </span>
          </div>

          {/* Question */}
          <div>
            <h2 className="font-serif text-3xl md:text-4xl text-neutral-900 mb-4 leading-tight">
              {currentQuestion.question}
            </h2>
            {currentQuestion.required && (
              <p className="text-sm text-neutral-500">* Required</p>
            )}
          </div>

          {/* Input */}
          <div className="space-y-4">
            {currentQuestion.type === 'text' && (
              <input
                type="text"
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswer(e.target.value)}
                placeholder={currentQuestion.placeholder}
                className="w-full px-4 py-3 rounded-lg border-2 border-neutral-200 focus:outline-none focus:border-neutral-900 transition-all duration-180 text-lg"
                autoFocus
              />
            )}

            {currentQuestion.type === 'textarea' && (
              <textarea
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswer(e.target.value)}
                placeholder={currentQuestion.placeholder}
                rows={5}
                className="w-full px-4 py-3 rounded-lg border-2 border-neutral-200 focus:outline-none focus:border-neutral-900 transition-all duration-180 resize-none"
                autoFocus
              />
            )}

            {currentQuestion.type === 'select' && (
              <div className="space-y-2">
                {currentQuestion.options.map((option) => (
                  <button
                    key={option}
                    onClick={() => handleAnswer(option)}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-lg border-2 transition-all duration-180",
                      answers[currentQuestion.id] === option
                        ? "border-neutral-900 bg-neutral-900 text-white"
                        : "border-neutral-200 hover:border-neutral-900"
                    )}
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}

            {currentQuestion.type === 'multiselect' && (
              <div className="space-y-2">
                {currentQuestion.options.map((option) => {
                  const isSelected = selectedOptions[currentQuestion.id]?.includes(option)
                  return (
                    <button
                      key={option}
                      onClick={() => handleMultiSelect(option)}
                      className={cn(
                        "w-full text-left px-4 py-3 rounded-lg border-2 transition-all duration-180 flex items-center justify-between",
                        isSelected
                          ? "border-neutral-900 bg-neutral-900 text-white"
                          : "border-neutral-200 hover:border-neutral-900"
                      )}
                    >
                      <span>{option}</span>
                      {isSelected && <CheckCircle2 className="w-5 h-5" />}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </motion.div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className={cn(
              "flex items-center gap-2 px-6 py-3 rounded-lg border-2 transition-all duration-180",
              currentStep === 0
                ? "border-neutral-200 text-neutral-400 cursor-not-allowed"
                : "border-neutral-900 text-neutral-900 hover:bg-neutral-900 hover:text-white"
            )}
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          <button
            onClick={handleNext}
            disabled={!canProceed}
            className={cn(
              "flex items-center gap-2 px-6 py-3 rounded-lg border-2 transition-all duration-180",
              canProceed
                ? "border-neutral-900 bg-neutral-900 text-white hover:bg-neutral-800"
                : "border-neutral-200 text-neutral-400 cursor-not-allowed"
            )}
          >
            {currentStep === ONBOARDING_QUESTIONS.length - 1 ? 'Complete' : 'Next'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </motion.div>
    </div>
  )
}

