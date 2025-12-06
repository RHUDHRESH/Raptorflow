import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion'
import { Check, Sparkle, Users, Clock, Lightning, ShieldCheck, ArrowRight } from '@phosphor-icons/react'


// 3D tilt card effect
const PricingCard = ({ plan, index, onSelect }) => {
  const [isHovered, setIsHovered] = useState(false)
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const rotateX = useSpring(useTransform(y, [-100, 100], [10, -10]), { stiffness: 300, damping: 30 })
  const rotateY = useSpring(useTransform(x, [-100, 100], [-10, 10]), { stiffness: 300, damping: 30 })

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    x.set(e.clientX - centerX)
    y.set(e.clientY - centerY)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
    setIsHovered(false)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.15 }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX, rotateY, transformStyle: 'preserve-3d' }}
      className={`relative group perspective-1000 ${plan.highlighted ? 'lg:-mt-6 lg:mb-6' : ''}`}
    >
      {/* Glow effect */}
      {plan.highlighted && (
        <motion.div
          className="absolute -inset-[1px] bg-gradient-to-r from-amber-500/50 via-yellow-400/50 to-amber-500/50 rounded-2xl blur-lg"
          animate={{ opacity: isHovered ? 0.5 : 0.2 }}
          transition={{ duration: 0.3 }}
        />
      )}

      {/* Card */}
      <div className={`
        relative h-full p-8 lg:p-10 rounded-2xl border transition-all duration-300
        ${plan.highlighted
          ? 'bg-gradient-to-b from-amber-950/50 to-zinc-900/90 border-amber-500/30'
          : 'bg-zinc-900/70 border-white/[0.05] hover:border-white/10'
        }
      `}>

        {/* Badge */}
        {plan.badge && (
          <motion.div
            className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-gradient-to-r from-amber-500 to-yellow-500 text-black text-[10px] uppercase tracking-wider font-semibold rounded-full shadow-lg shadow-amber-500/30"
            animate={{ y: isHovered ? -2 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <Sparkle weight="fill" className="w-3 h-3 inline mr-1" />
            {plan.badge}
          </motion.div>
        )}

        {/* Hover glow overlay */}
        <motion.div
          className="absolute inset-0 rounded-2xl bg-gradient-to-b from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        />

        {/* Plan header */}
        <div className="relative z-10 mb-6">
          <h3 className="text-2xl font-light text-white mb-1">{plan.name}</h3>
          <p className="text-xs text-white/40 tracking-wide">{plan.tagline}</p>
        </div>

        {/* Price */}
        <div className="relative z-10 mb-2">
          <div className="flex items-baseline gap-1">
            <span className="text-sm text-white/40">₹</span>
            <motion.span
              className="text-5xl font-light text-white tracking-tight"
              animate={{ scale: isHovered ? 1.02 : 1 }}
              transition={{ duration: 0.2 }}
            >
              {plan.price}
            </motion.span>
          </div>
        </div>

        {/* Period with icon */}
        <div className="relative z-10 flex items-center gap-2 mb-6">
          <Clock className="w-3.5 h-3.5 text-white/30" />
          <span className="text-xs text-white/40 uppercase tracking-wider">{plan.period}</span>
        </div>

        {/* Cohort limit highlight */}
        <motion.div
          className={`relative z-10 mb-6 p-3 rounded-xl border ${plan.highlighted ? 'bg-amber-500/10 border-amber-500/20' : 'bg-white/5 border-white/5'}`}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className={`w-4 h-4 ${plan.highlighted ? 'text-amber-400' : 'text-white/40'}`} />
              <span className="text-sm text-white/70">Cohorts</span>
            </div>
            <span className={`text-lg font-medium ${plan.highlighted ? 'text-amber-400' : 'text-white'}`}>
              {plan.cohortLimit}
            </span>
          </div>
        </motion.div>

        {/* Description */}
        <p className="relative z-10 text-sm text-white/50 leading-relaxed mb-6">
          {plan.description}
        </p>

        {/* Features */}
        <ul className="relative z-10 space-y-3 mb-8">
          {plan.features.map((feature, i) => (
            <motion.li
              key={i}
              className="flex items-start gap-3"
              initial={{ opacity: 0, x: -10 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 + i * 0.05 }}
            >
              <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${plan.highlighted ? 'bg-amber-500/20' : 'bg-white/5'}`}>
                <Check className={`w-3 h-3 ${plan.highlighted ? 'text-amber-400' : 'text-white/40'}`} strokeWidth={2.5} />
              </div>
              <span className="text-sm text-white/60">{feature}</span>
            </motion.li>
          ))}
        </ul>

        {/* CTA */}
        <motion.button
          onClick={onSelect}
          className={`
            relative z-10 w-full py-4 rounded-xl font-medium text-sm tracking-wide 
            flex items-center justify-center gap-2 overflow-hidden group/btn
            ${plan.highlighted
              ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-black'
              : 'bg-white/5 text-white border border-white/10'
            }
          `}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {/* Hover shine effect */}
          <motion.div
            className={`absolute inset-0 ${plan.highlighted ? 'bg-gradient-to-r from-transparent via-white/30 to-transparent' : 'bg-gradient-to-r from-transparent via-white/10 to-transparent'}`}
            initial={{ x: '-100%' }}
            whileHover={{ x: '100%' }}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
          />

          <span className="relative z-10">Start with {plan.name}</span>
          <ArrowRight className="w-4 h-4 relative z-10 group-hover/btn:translate-x-1 transition-transform" />
        </motion.button>
      </div>
    </motion.div>
  )
}

const Pricing = () => {
  const navigate = useNavigate()

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
    <section id="pricing" className="relative py-32 md:py-40 bg-black overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[1200px] bg-gradient-radial from-amber-900/15 via-transparent to-transparent" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-gradient-radial from-amber-900/10 via-transparent to-transparent" />
      </div>

      {/* Grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />

      <div className="max-w-6xl mx-auto px-6 relative z-10">

        {/* Header */}
        <div className="text-center mb-20">
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-full text-[10px] uppercase tracking-[0.3em] text-amber-400/80 mb-6"
          >
            <Lightning weight="fill" className="w-3 h-3" />
            Investment
          </motion.span>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-4xl md:text-5xl lg:text-6xl font-light text-white"
          >
            Choose your
            <span className="italic font-normal text-amber-200"> trajectory</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mt-6 text-white/40 text-lg font-light max-w-xl mx-auto"
          >
            30 days of strategic clarity. No auto-renewal. No surprises.
          </motion.p>
        </div>

        {/* Plans */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-4">
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
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          {/* Trust badges */}
          <div className="flex flex-wrap items-center justify-center gap-6 mb-8">
            <div className="flex items-center gap-2 text-white/30 text-sm">
              <ShieldCheck weight="duotone" className="w-4 h-4 text-emerald-400" />
              <span>Secured by PhonePe</span>
            </div>
            <div className="flex items-center gap-2 text-white/30 text-sm">
              <Clock weight="duotone" className="w-4 h-4 text-amber-400" />
              <span>30-day access</span>
            </div>
            <div className="flex items-center gap-2 text-white/30 text-sm">
              <Sparkle weight="fill" className="w-4 h-4 text-blue-400" />
              <span>GST included</span>
            </div>
          </div>

          <p className="text-white/30 text-sm">
            All prices in INR. Plan expires after 30 days.
            <span className="text-white/40"> Renew anytime to continue.</span>
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default Pricing
