import React, { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { Check, Sparkle, Users, Clock, ShieldCheck, ArrowRight } from '@phosphor-icons/react'

// Premium pricing card - no tilt, refined hover
const PricingCard = ({ plan, index, onSelect }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay: index * 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className={`relative group ${plan.highlighted ? 'lg:-mt-4 lg:mb-4' : ''}`}
    >
      {/* Subtle glow for highlighted */}
      {plan.highlighted && (
        <div className="absolute -inset-px bg-gradient-to-b from-amber-500/20 to-amber-500/5 rounded-2xl blur-xl opacity-50" />
      )}

      {/* Card */}
      <div className={`
        relative h-full p-8 lg:p-10 rounded-2xl border transition-all duration-500
        ${plan.highlighted
          ? 'bg-zinc-900/60 border-amber-500/20'
          : 'bg-zinc-900/40 border-white/[0.05] hover:border-white/[0.1]'
        }
        hover:shadow-[0_20px_60px_-15px_rgba(0,0,0,0.5)]
      `}>
        {/* Subtle hover gradient */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        {/* Badge */}
        {plan.badge && (
          <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-amber-400 text-black text-[10px] uppercase tracking-[0.1em] font-semibold rounded-full">
            {plan.badge}
          </div>
        )}

        {/* Plan header */}
        <div className="relative z-10 mb-8">
          <h3 className="text-2xl font-light text-white mb-2">{plan.name}</h3>
          <p className="text-xs text-white/35 tracking-wide">{plan.tagline}</p>
        </div>

        {/* Price */}
        <div className="relative z-10 mb-2">
          <div className="flex items-baseline gap-1">
            <span className="text-sm text-white/30">₹</span>
            <span className="text-5xl font-extralight text-white tracking-tight">
              {plan.price}
            </span>
          </div>
        </div>

        {/* Period */}
        <div className="relative z-10 flex items-center gap-2 mb-8">
          <Clock className="w-3.5 h-3.5 text-white/25" weight="regular" />
          <span className="text-[11px] text-white/35 uppercase tracking-[0.15em]">{plan.period}</span>
        </div>

        {/* Cohort limit */}
        <div className={`
          relative z-10 mb-8 p-4 rounded-xl border
          ${plan.highlighted
            ? 'bg-amber-500/5 border-amber-500/15'
            : 'bg-white/[0.02] border-white/[0.05]'
          }
        `}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className={`w-4 h-4 ${plan.highlighted ? 'text-amber-400/60' : 'text-white/30'}`} weight="regular" />
              <span className="text-sm text-white/50">Cohorts</span>
            </div>
            <span className={`text-lg font-light ${plan.highlighted ? 'text-amber-300' : 'text-white'}`}>
              {plan.cohortLimit}
            </span>
          </div>
        </div>

        {/* Description */}
        <p className="relative z-10 text-sm text-white/40 leading-relaxed mb-8">
          {plan.description}
        </p>

        {/* Features */}
        <ul className="relative z-10 space-y-3 mb-10">
          {plan.features.map((feature, i) => (
            <li key={i} className="flex items-start gap-3">
              <div className={`
                w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0
                ${plan.highlighted ? 'bg-amber-500/15' : 'bg-white/[0.05]'}
              `}>
                <Check
                  className={`w-3 h-3 ${plan.highlighted ? 'text-amber-400' : 'text-white/35'}`}
                  weight="bold"
                />
              </div>
              <span className="text-sm text-white/50">{feature}</span>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <button
          onClick={onSelect}
          className={`
            relative z-10 w-full py-4 font-medium text-sm tracking-wide 
            flex items-center justify-center gap-2 overflow-hidden group/btn transition-all duration-300
            ${plan.highlighted
              ? 'bg-white text-black hover:bg-amber-50'
              : 'bg-white/[0.05] text-white/60 border border-white/[0.08] hover:border-white/[0.15] hover:text-white'
            }
          `}
        >
          <span>Start with {plan.name}</span>
          <ArrowRight className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" weight="bold" />
        </button>
      </div>
    </motion.div>
  )
}

const Pricing = () => {
  const navigate = useNavigate()
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  const plans = [
    {
      name: 'Ascent',
      tagline: 'Start building your strategy',
      price: '5,000',
      period: '30 days',
      cohortLimit: 3,
      description: 'Perfect for solo founders ready to bring clarity to their chaos.',
      features: [
        'Complete 7-pillar strategy intake',
        '1 strategic workspace',
        'AI-powered plan generation',
        '90-day war map creation',
        'Up to 3 cohorts',
        'Radar trend matching',
        'PDF & Notion export',
        'Email support'
      ],
      highlighted: false
    },
    {
      name: 'Glide',
      tagline: 'For founders who mean business',
      price: '7,000',
      period: '30 days',
      cohortLimit: 5,
      description: 'Advanced tools and ongoing support for serious operators.',
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
      badge: 'Most Popular'
    },
    {
      name: 'Soar',
      tagline: 'The complete strategic arsenal',
      price: '10,000',
      period: '30 days',
      cohortLimit: 10,
      description: 'For teams and founders who demand excellence at every turn.',
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
      highlighted: false
    }
  ]

  return (
    <section id="pricing" ref={sectionRef} className="relative py-32 md:py-40 bg-[#050505] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-gradient-radial from-amber-950/10 to-transparent blur-3xl" />
      </div>

      <div className="max-w-6xl mx-auto px-6 md:px-12 relative z-10">
        {/* Header */}
        <div className="text-center mb-20 md:mb-24">
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="inline-flex items-center gap-3 mb-8"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-amber-500/50" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-amber-400/60 font-medium">
              Investment
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-amber-500/50" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight mb-8"
          >
            Choose your{' '}
            <span className="bg-gradient-to-r from-amber-200 via-amber-100 to-amber-200 bg-clip-text text-transparent">
              trajectory
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg md:text-xl text-white/35 max-w-xl mx-auto"
          >
            30 days of strategic clarity. No auto-renewal. No surprises.
          </motion.p>
        </div>

        {/* Plans */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-5">
          {plans.map((plan, index) => (
            <PricingCard
              key={plan.name}
              plan={plan}
              index={index}
              onSelect={() => navigate('/start')}
            />
          ))}
        </div>

        {/* Bottom section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="mt-16 text-center"
        >
          {/* Trust badges */}
          <div className="flex flex-wrap items-center justify-center gap-8 mb-6">
            <div className="flex items-center gap-2 text-white/25 text-sm">
              <ShieldCheck weight="regular" className="w-4 h-4 text-emerald-400/60" />
              <span>Secured by PhonePe</span>
            </div>
            <div className="flex items-center gap-2 text-white/25 text-sm">
              <Clock weight="regular" className="w-4 h-4 text-amber-400/60" />
              <span>30-day access</span>
            </div>
            <div className="flex items-center gap-2 text-white/25 text-sm">
              <Sparkle weight="fill" className="w-4 h-4 text-blue-400/60" />
              <span>GST included</span>
            </div>
          </div>

          <p className="text-white/20 text-sm">
            All prices in INR. Plan expires after 30 days.
            <span className="text-white/30"> Renew anytime to continue.</span>
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default Pricing
