import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Check, Crown, Sparkles, CreditCard, Shield, Loader2, Clock, Lock } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'
import { useAuth } from '../../contexts/AuthContext'
import { initiatePayment, PLAN_PRICES } from '../../lib/phonepe'

// Plans are now 30-day subscriptions
const plans = [
  {
    id: 'ascent',
    name: 'Ascent',
    tagline: 'Start building your strategy',
    price: 5000,
    priceDisplay: '₹5,000',
    period: '30 days',
    description: 'Perfect for solo founders ready to bring clarity to their chaos.',
    cohortLimit: 3,
    features: [
      'Complete 7-pillar strategy intake',
      '1 strategic workspace',
      'AI-powered plan generation',
      '90-day war map creation',
      'Up to 3 cohorts',
      'Radar trend matching',
      'PDF & Notion export',
      'Email support',
    ],
    highlighted: false,
  },
  {
    id: 'glide',
    name: 'Glide',
    tagline: 'For founders who mean business',
    price: 7000,
    priceDisplay: '₹7,000',
    period: '30 days',
    description: 'Advanced tools and ongoing support for serious operators.',
    cohortLimit: 5,
    features: [
      'Everything in Ascent',
      '3 strategic workspaces',
      'Advanced AI strategy engine',
      'Up to 5 cohorts',
      'Real-time collaboration (up to 3)',
      'Integrations: Notion, Slack, Linear',
      'Priority support',
      'Monthly strategy review call'
    ],
    highlighted: true,
    badge: 'Most Popular',
  },
  {
    id: 'soar',
    name: 'Soar',
    tagline: 'The complete strategic arsenal',
    price: 10000,
    priceDisplay: '₹10,000',
    period: '30 days',
    description: 'For teams and founders who demand excellence at every turn.',
    cohortLimit: 10,
    features: [
      'Everything in Glide',
      'Unlimited workspaces',
      'Up to 10 cohorts',
      'Team collaboration (up to 10)',
      'White-label exports',
      'API access',
      'Dedicated success manager',
      '1-on-1 strategy onboarding call',
      'Quarterly strategy sessions'
    ],
    highlighted: false,
  }
]

const StepPlan = () => {
  const navigate = useNavigate()
  const { user, profile } = useAuth()
  const { 
    selectedPlan, 
    selectPlan, 
    setPaymentStatus,
    mode,
    generateShareToken,
    icps,
    prevStep 
  } = useOnboardingStore()
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [planLocked, setPlanLocked] = useState(false)
  const [daysRemaining, setDaysRemaining] = useState(0)

  const selectedICPCount = icps?.filter(i => i.selected)?.length || 0

  // Check if user has an active plan (can't change until it expires)
  useEffect(() => {
    if (profile?.plan && profile.plan !== 'none' && profile.plan !== 'free' && profile.plan_status === 'active') {
      // Check if plan hasn't expired
      if (profile.plan_expires_at) {
        const expiryDate = new Date(profile.plan_expires_at)
        const now = new Date()
        if (expiryDate > now) {
          setPlanLocked(true)
          const diffTime = expiryDate - now
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
          setDaysRemaining(diffDays)
        }
      }
    }
  }, [profile])

  const handleSelectPlan = async (planId) => {
    // Block if plan is locked (no proration)
    if (planLocked) {
      setError(`Your current ${profile?.plan} plan is active for ${daysRemaining} more days. Upgrades/changes are available after it expires.`)
      return
    }

    selectPlan(planId)
    
    if (mode === 'sales-assisted') {
      const token = generateShareToken()
      alert(`Share link generated: ${window.location.origin}/shared/${token}`)
      return
    }

    // Self-service: initiate payment
    setLoading(true)
    setError('')
    setPaymentStatus('processing')

    try {
      const result = await initiatePayment({
        userId: user?.id,
        plan: planId,
        userEmail: user?.email,
      })

      if (result.success) {
        // Check if it's an external URL (real PhonePe) or internal
        if (result.isExternal) {
          // Redirect to PhonePe
          window.location.href = result.redirectUrl
        } else {
          // Navigate to our payment process page
          navigate(result.redirectUrl)
        }
      } else {
        setError(result.error || 'Payment initiation failed')
        setPaymentStatus('failed')
      }
    } catch (err) {
      setError(err.message || 'Something went wrong')
      setPaymentStatus('failed')
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    prevStep()
    navigate('/onboarding/warplan')
  }

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col">
      <div className="flex-1 max-w-6xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-2 bg-amber-500/10 rounded-xl">
              <Crown className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 8 of 8 · Choose Your Plan
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            Choose your <span className="italic text-amber-200">trajectory</span>
          </h1>
          <p className="text-white/40 max-w-xl mx-auto">
            {selectedICPCount > 0 
              ? `You've created ${selectedICPCount} cohort${selectedICPCount !== 1 ? 's' : ''} and a 90-day war plan.`
              : "You've built your strategy foundation."
            }
            {' '}Pick a plan to unlock everything.
          </p>
        </motion.div>

        {/* Plan locked warning */}
        {planLocked && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-2xl mx-auto mb-8 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-start gap-3"
          >
            <Lock className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-amber-400 font-medium">Active Plan: {profile?.plan}</p>
              <p className="text-amber-400/60 text-sm mt-1">
                Your current plan has {daysRemaining} days remaining. Plan changes are available after expiry.
                PhonePe doesn't support proration, so upgrades are blocked until your current plan ends.
              </p>
            </div>
          </motion.div>
        )}

        {/* Error message */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-md mx-auto mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-center"
          >
            <p className="text-red-400 text-sm">{error}</p>
          </motion.div>
        )}

        {/* Plans grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {plans.map((plan, index) => {
            const isSelected = selectedPlan === plan.id
            const isCurrentPlan = profile?.plan === plan.id && planLocked
            const isTooFewCohorts = plan.cohortLimit && selectedICPCount > plan.cohortLimit
            
            return (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`relative ${plan.highlighted ? 'lg:-mt-4 lg:mb-4' : ''}`}
              >
                <div className={`
                  relative h-full p-8 rounded-2xl border transition-all
                  ${plan.highlighted 
                    ? 'bg-gradient-to-b from-amber-900/30 to-amber-900/10 border-amber-500/30' 
                    : 'bg-zinc-900/50 border-white/10'
                  }
                  ${isSelected ? 'ring-2 ring-amber-500' : ''}
                  ${isCurrentPlan ? 'ring-2 ring-emerald-500' : ''}
                `}>
                  {/* Badge */}
                  {plan.badge && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-amber-500 to-yellow-500 text-black text-[10px] uppercase tracking-wider font-medium rounded-full">
                      {plan.badge}
                    </div>
                  )}

                  {/* Current plan badge */}
                  {isCurrentPlan && (
                    <div className="absolute -top-3 right-4 px-3 py-1 bg-emerald-500 text-black text-[10px] uppercase tracking-wider font-medium rounded-full">
                      Current Plan
                    </div>
                  )}

                  {/* Plan header */}
                  <div className="mb-6">
                    <h3 className="text-2xl font-light text-white mb-1">{plan.name}</h3>
                    <p className="text-xs text-white/40">{plan.tagline}</p>
                  </div>

                  {/* Price */}
                  <div className="mb-6">
                    <div className="flex items-baseline gap-1">
                      <span className="text-sm text-white/40">₹</span>
                      <span className="text-4xl font-light text-white tracking-tight">
                        {plan.price.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <Clock className="w-3 h-3 text-white/30" />
                      <span className="text-xs text-white/30 uppercase tracking-wider">{plan.period}</span>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-white/50 leading-relaxed mb-6">
                    {plan.description}
                  </p>

                  {/* Cohort limit info */}
                  <div className="mb-4 p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-white/40">Cohort limit</span>
                      <span className="text-sm text-white font-medium">{plan.cohortLimit} cohorts</span>
                    </div>
                  </div>

                  {/* Cohort limit warning */}
                  {isTooFewCohorts && (
                    <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                      <p className="text-xs text-amber-400">
                        ⚠️ You have {selectedICPCount} cohorts but this plan supports {plan.cohortLimit}. 
                        Consider upgrading.
                      </p>
                    </div>
                  )}

                  {/* Features */}
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${plan.highlighted ? 'text-amber-400' : 'text-white/30'}`} />
                        <span className="text-sm text-white/60">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleSelectPlan(plan.id)}
                    disabled={loading || isCurrentPlan}
                    className={`
                      w-full py-4 rounded-xl font-medium text-sm tracking-wide transition-all flex items-center justify-center gap-2
                      ${isCurrentPlan
                        ? 'bg-emerald-500/20 text-emerald-400 cursor-not-allowed'
                        : plan.highlighted
                          ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-black hover:from-amber-400 hover:to-yellow-400'
                          : 'bg-white/5 text-white border border-white/10 hover:bg-white/10 hover:border-white/20'
                      }
                      ${loading && selectedPlan === plan.id ? 'opacity-75' : ''}
                      ${planLocked && !isCurrentPlan ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                  >
                    {isCurrentPlan ? (
                      <>
                        <Check className="w-4 h-4" />
                        Active ({daysRemaining}d remaining)
                      </>
                    ) : loading && selectedPlan === plan.id ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </>
                    ) : planLocked ? (
                      <>
                        <Lock className="w-4 h-4" />
                        Locked
                      </>
                    ) : (
                      <>
                        <CreditCard className="w-4 h-4" />
                        {mode === 'sales-assisted' ? 'Generate Payment Link' : `Pay ${plan.priceDisplay}`}
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Bottom note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-12 text-center"
        >
          <div className="flex items-center justify-center gap-2 text-white/30 text-sm mb-4">
            <Shield className="w-4 h-4" />
            <span>Secured by PhonePe Payment Gateway</span>
          </div>
          <p className="text-white/30 text-sm">
            All prices in INR. Includes GST. 
            <span className="text-white/50"> 30-day access. No auto-renewal.</span>
          </p>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-white/40 hover:text-white text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to War Plan
          </button>

          <p className="text-xs text-white/30">
            Need help? <a href="mailto:support@raptorflow.com" className="text-amber-400 hover:underline">Contact us</a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default StepPlan
