'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import { Check, Zap, Star, Shield, Loader2, Sparkles, ArrowRight, Crown } from 'lucide-react'
import { clientAuth } from '@/lib/auth-service'

// =============================================================================
// TYPES
// =============================================================================

interface Plan {
  id: string
  slug: string
  name: string
  description?: string
  price_monthly_paise: number
  price_yearly_paise: number
  storage_limit_bytes?: number
  features?: string[]
  popular?: boolean
}

// Plan configurations with features
const PLAN_CONFIGS = {
  ascent: {
    description: "For founders just getting started with systematic marketing.",
    features: [
      "5 GB storage",
      "3 projects",
      "Email support"
    ]
  },
  glide: {
    description: "For founders scaling their marketing engine.",
    features: [
      "25 GB storage",
      "Unlimited projects",
      "5 team members",
      "Priority support"
    ],
    popular: true
  },
  soar: {
    description: "For teams running multi-channel campaigns.",
    features: [
      "100 GB storage",
      "Unlimited projects",
      "Unlimited team members",
      "Dedicated support"
    ]
  }
}

// =============================================================================
// ANIMATION VARIANTS
// =============================================================================

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
}

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 40, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: 'spring' as const,
      stiffness: 200,
      damping: 25
    }
  }
}

const shimmerVariants: Variants = {
  initial: { x: '-100%' },
  animate: {
    x: '100%',
    transition: {
      repeat: Infinity,
      duration: 3,
      ease: 'linear' as const
    }
  }
}

// =============================================================================
// PLANS PAGE
// =============================================================================

export default function ChoosePlan() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  const [error, setError] = useState('')
  const [userEmail, setUserEmail] = useState<string | null>(null)
  const [userName, setUserName] = useState<string>('there')
  const router = useRouter()

  useEffect(() => {
    fetchPlans()
    fetchUserForGreeting(setUserEmail, setUserName)
  }, [])

  async function fetchUserForGreeting(
    setEmail: (email: string | null) => void,
    setName: (name: string) => void
  ) {
    try {
      const user = await clientAuth.getCurrentUser();

      if (user) {
        setEmail(user.email)
        setName(user.fullName || user.email.split('@')[0] || 'there')
      }
    } catch (err) {
      console.warn('Failed to load user for greeting', err)
    }
  }

  async function fetchPlans() {
    try {
      const response = await fetch('/api/plans')
      const data = await response.json()

      if (data.plans) {
        const mergedPlans = data.plans.map((plan: Plan) => {
          const config = PLAN_CONFIGS[plan.slug as keyof typeof PLAN_CONFIGS]
          return {
            ...plan,
            description: plan.description || config?.description,
            features: plan.features?.length ? plan.features : config?.features,
            popular: plan.popular ?? config?.popular
          }
        })
        setPlans(mergedPlans)
      } else {
        setError('Failed to load plans')
      }
    } catch (err) {
      setError('Failed to load plans')
    } finally {
      setIsFetching(false)
    }
  }

  async function handleSelectPlan() {
    if (!selectedPlan) return

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('/api/onboarding/select-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          planId: selectedPlan,
          billingCycle: 'monthly'
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to initiate payment')
      }

      if (data.success) {
        router.push('/onboarding/payment')
      } else {
        throw new Error(data.error || 'Payment initiation failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsLoading(false)
    }
  }

  function formatPrice(paise: number): string {
    return `₹${(paise / 100).toLocaleString('en-IN')}`
  }

  function formatStorage(bytes: number): string {
    const gb = bytes / (1024 * 1024 * 1024)
    if (gb >= 1000) {
      return `${(gb / 1024).toFixed(0)} TB`
    }
    return `${gb.toFixed(0)} GB`
  }

  function getPlanGradient(planId: string, isSelected: boolean) {
    if (isSelected) {
      return 'from-indigo-500 via-purple-500 to-pink-500'
    }
    switch (planId) {
      case 'ascent':
        return 'from-blue-500/20 to-cyan-500/20'
      case 'glide':
        return 'from-purple-500/20 to-pink-500/20'
      case 'soar':
        return 'from-amber-500/20 to-orange-500/20'
      default:
        return 'from-gray-500/20 to-gray-600/20'
    }
  }

  function getPlanIcon(planSlug: string) {
    const iconClass = "w-7 h-7"
    switch (planSlug) {
      case 'ascent':
        return <Zap className={iconClass} />
      case 'glide':
        return <Star className={iconClass} />
      case 'soar':
        return <Crown className={iconClass} />
      default:
        return <Zap className={iconClass} />
    }
  }

  if (isFetching) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <Loader2 className="w-12 h-12 animate-spin text-indigo-500 mx-auto mb-4" />
          <p className="text-slate-400 font-medium">Loading plans...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-indigo-500/5 to-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 py-16">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Sparkles className="w-4 h-4" />
            Choose Your Plan
          </motion.div>

          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Hey {userName}, unlock your full
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"> Potential</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            Select the plan that fits your needs. All plans include a 30-day money-back guarantee.
          </p>
        </motion.div>

        {/* Plans Grid */}
        <motion.div
          className="grid md:grid-cols-3 gap-6 lg:gap-8 mb-12"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {plans.map((plan, index) => {
            const isSelected = selectedPlan === plan.slug
            const isPopular = plan.popular

            return (
              <motion.div
                key={plan.name}
                variants={cardVariants}
                whileHover={{ y: -8, transition: { duration: 0.3 } }}
                onClick={() => setSelectedPlan(plan.slug)}
                className={`relative group cursor-pointer ${isPopular ? 'md:-mt-4 md:mb-4' : ''}`}
              >
                {/* Popular badge */}
                {isPopular && (
                  <motion.div
                    className="absolute -top-4 left-1/2 -translate-x-1/2 z-20"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                  >
                    <div className="px-4 py-1.5 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-bold uppercase tracking-wider shadow-lg shadow-indigo-500/25">
                      Most Popular
                    </div>
                  </motion.div>
                )}

                {/* Card */}
                <div className={`relative h-full rounded-3xl p-[1px] transition-all duration-500 ${isSelected
                    ? 'bg-gradient-to-b from-indigo-500 via-purple-500 to-pink-500'
                    : isPopular
                      ? 'bg-gradient-to-b from-slate-600 to-slate-800'
                      : 'bg-slate-800/50'
                  }`}>
                  {/* Inner card */}
                  <div className={`relative h-full rounded-[calc(1.5rem-1px)] p-8 transition-all duration-500 ${isSelected
                      ? 'bg-slate-900'
                      : 'bg-slate-900/90 group-hover:bg-slate-900'
                    }`}>
                    {/* Shimmer effect */}
                    {isSelected && (
                      <div className="absolute inset-0 rounded-[calc(1.5rem-1px)] overflow-hidden pointer-events-none">
                        <motion.div
                          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
                          variants={shimmerVariants}
                          initial="initial"
                          animate="animate"
                        />
                      </div>
                    )}

                    {/* Icon */}
                    <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-6 transition-all duration-300 ${isSelected
                        ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/30'
                        : 'bg-slate-800 text-slate-400 group-hover:text-indigo-400 group-hover:bg-indigo-500/10'
                      }`}>
                      {getPlanIcon(plan.slug)}
                    </div>

                    {/* Plan name and description */}
                    <h3 className="text-2xl font-bold text-white mb-2">{plan.name.charAt(0).toUpperCase() + plan.name.slice(1)}</h3>
                    <p className="text-slate-400 text-sm mb-6">{plan.description}</p>

                    {/* Price */}
                    <div className="mb-8">
                      <div className="flex items-baseline gap-1">
                        <span className="text-4xl font-bold text-white">{formatPrice(plan.price_monthly_paise)}</span>
                        <span className="text-slate-500">/month</span>
                      </div>
                      <p className="text-sm text-slate-500 mt-1">
                        {formatPrice(plan.price_yearly_paise)} billed yearly
                      </p>
                    </div>

                    {/* Features */}
                    <ul className="space-y-4 mb-8">
                      {plan.features?.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center gap-3 text-slate-300">
                          <div className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center ${isSelected ? 'bg-indigo-500/20' : 'bg-slate-800'
                            }`}>
                            <Check className={`w-3 h-3 ${isSelected ? 'text-indigo-400' : 'text-slate-500'}`} />
                          </div>
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>

                    {/* Select button */}
                    <button
                      className={`w-full py-4 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${isSelected
                          ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
                        }`}
                    >
                      {isSelected ? (
                        <>
                          <Check className="w-5 h-5" />
                          Selected
                        </>
                      ) : (
                        'Select Plan'
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Error message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="max-w-md mx-auto mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-center"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Continue button */}
        <motion.div
          className="flex justify-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <button
            onClick={handleSelectPlan}
            disabled={!selectedPlan || isLoading}
            className={`group relative px-12 py-4 rounded-2xl font-semibold text-lg transition-all duration-300 flex items-center gap-3 ${selectedPlan
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-xl shadow-indigo-500/25 hover:shadow-2xl hover:shadow-indigo-500/40 hover:scale-105'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
              }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                {userEmail ? `Continue to Payment, ${userName}` : 'Continue to Payment'}
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </motion.div>

        {/* Trust badges */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <p className="text-slate-500 text-sm mb-6">
            Trusted by 10,000+ founders building the next generation of companies
          </p>
          <div className="flex justify-center items-center gap-8 text-slate-500">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              <span className="text-sm">Secure Payments</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              <span className="text-sm">Instant Access</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5" />
              <span className="text-sm">30-Day Guarantee</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
