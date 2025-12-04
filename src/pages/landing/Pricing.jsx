import React from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Check, Sparkles } from 'lucide-react'

const Pricing = () => {
  const navigate = useNavigate()

  const plans = [
    {
      name: 'Ascent',
      tagline: 'Start building your strategy',
      price: '5,000',
      period: 'one-time',
      description: 'Perfect for solo founders ready to bring clarity to their chaos.',
      features: [
        'Complete 7-pillar strategy intake',
        '1 strategic workspace',
        'AI-powered plan generation',
        '90-day war map creation',
        'PDF & Notion export',
        'Email support',
        '30-day access to methodology library'
      ],
      highlighted: false,
      gradient: 'from-zinc-800 to-zinc-900'
    },
    {
      name: 'Glide',
      tagline: 'For founders who mean business',
      price: '7,000',
      period: 'one-time',
      description: 'Advanced tools and ongoing support for serious operators.',
      features: [
        'Everything in Ascent',
        '3 strategic workspaces',
        'Advanced AI strategy engine',
        'Real-time collaboration (up to 3)',
        'Integrations: Notion, Slack, Linear',
        'Priority support',
        '90-day methodology access',
        'Monthly strategy review call'
      ],
      highlighted: true,
      badge: 'Most Popular',
      gradient: 'from-amber-900/40 to-yellow-900/20'
    },
    {
      name: 'Soar',
      tagline: 'The complete strategic arsenal',
      price: '10,000',
      period: 'one-time',
      description: 'For teams and founders who demand excellence at every turn.',
      features: [
        'Everything in Glide',
        'Unlimited workspaces',
        'Team collaboration (up to 10)',
        'White-label exports',
        'API access',
        'Dedicated success manager',
        '1-on-1 strategy onboarding call',
        'Lifetime methodology access',
        'Quarterly strategy sessions'
      ],
      highlighted: false,
      gradient: 'from-zinc-800 to-zinc-900'
    }
  ]

  return (
    <section className="relative py-32 md:py-40 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-gradient-radial from-amber-900/10 via-transparent to-transparent" />
      </div>

      <div className="max-w-6xl mx-auto px-6 relative z-10">
        
        {/* Header */}
        <div className="text-center mb-20">
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-[10px] uppercase tracking-[0.4em] text-amber-400/60"
          >
            Investment
          </motion.span>
          
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mt-6 text-4xl md:text-5xl lg:text-6xl font-light text-white"
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
            One-time investment. Lifetime strategic clarity.
          </motion.p>
        </div>

        {/* Plans */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-4">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
              className={`relative group ${plan.highlighted ? 'lg:-mt-4 lg:mb-4' : ''}`}
            >
              {/* Card */}
              <div className={`relative h-full p-8 lg:p-10 bg-gradient-to-b ${plan.gradient} border border-white/[0.05] ${plan.highlighted ? 'border-amber-500/30' : ''}`}>
                
                {/* Badge */}
                {plan.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-amber-500 to-yellow-500 text-black text-[10px] uppercase tracking-wider font-medium">
                    {plan.badge}
                  </div>
                )}

                {/* Glow for highlighted */}
                {plan.highlighted && (
                  <div className="absolute inset-0 bg-gradient-to-b from-amber-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                )}

                {/* Plan header */}
                <div className="relative z-10 mb-8">
                  <h3 className="text-2xl font-light text-white mb-1">{plan.name}</h3>
                  <p className="text-xs text-white/40 tracking-wide">{plan.tagline}</p>
                </div>

                {/* Price */}
                <div className="relative z-10 mb-8">
                  <div className="flex items-baseline gap-1">
                    <span className="text-sm text-white/40">₹</span>
                    <span className="text-5xl font-light text-white tracking-tight">{plan.price}</span>
                  </div>
                  <span className="text-xs text-white/30 uppercase tracking-wider">{plan.period}</span>
                </div>

                {/* Description */}
                <p className="relative z-10 text-sm text-white/50 leading-relaxed mb-8">
                  {plan.description}
                </p>

                {/* Features */}
                <ul className="relative z-10 space-y-3 mb-10">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${plan.highlighted ? 'text-amber-400' : 'text-white/30'}`} strokeWidth={2} />
                      <span className="text-sm text-white/60">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                <button
                  onClick={() => navigate('/start')}
                  className={`relative z-10 w-full py-4 font-medium text-sm tracking-wide transition-all duration-300 ${
                    plan.highlighted
                      ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-black hover:from-amber-400 hover:to-yellow-400'
                      : 'bg-white/5 text-white border border-white/10 hover:bg-white/10 hover:border-white/20'
                  }`}
                >
                  Start with {plan.name}
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom note */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          <p className="text-white/30 text-sm">
            All prices in INR. Includes GST. 
            <span className="text-white/50"> 7-day satisfaction guarantee.</span>
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default Pricing
