import React, { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { ArrowRight, Shield, Clock, CheckCircle2 } from 'lucide-react'
import { BrandIcon, type BrandIconName } from '@/components/brand/BrandSystem'

// Value proposition item
type ValuePropProps = {
  icon?: React.ComponentType<{ className?: string }>
  text: string
  delay: number
  isBrandIcon?: boolean
  brandIconName?: BrandIconName
}

const ValueProp = ({ icon: Icon, text, delay, isBrandIcon = false, brandIconName }: ValuePropProps) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.5 }}
    className="flex items-center gap-3"
  >
    <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
      {isBrandIcon ? (
        brandIconName ? <BrandIcon name={brandIconName as BrandIconName} className="w-4 h-4 text-white/70" /> : null
      ) : (
        Icon ? <Icon className="w-4 h-4 text-white/70" /> : null
      )}
    </div>
    <span className="text-white/50 text-sm">{text}</span>
  </motion.div>
)

// Premium CTA button
const PremiumCTAButton = ({ onClick, children, primary = true }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ scale: 1.01 }}
    whileTap={{ scale: 0.99 }}
    className={`
      group relative px-10 py-5 font-medium tracking-wide overflow-hidden transition-all duration-500
      ${primary
        ? 'bg-white text-black hover:bg-white/90'
        : 'text-white/50 hover:text-white border border-white/10 hover:border-white/20'
      }
    `}
  >
    <span className="relative z-10 flex items-center gap-3 text-sm uppercase tracking-[0.1em]">
      {children}
    </span>

    {primary && (
      <motion.div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          boxShadow: 'inset 0 0 30px rgba(255, 255, 255, 0.18)'
        }}
      />
    )}
  </motion.button>
)

// Main CTASection component
const CTASection = () => {
  const navigate = useNavigate()
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  return (
    <section
      ref={sectionRef}
      className="relative py-32 md:py-40 bg-[#030303] overflow-hidden"
    >
      {/* Subtle background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* Minimal gradient */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-gradient-radial from-white/10 to-transparent blur-3xl" />
      </div>

      <div className="max-w-4xl mx-auto px-6 relative z-10">
        {/* Main content */}
        <div className="text-center">
          {/* Minimal eyebrow */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="inline-flex items-center gap-3 mb-10"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-white/20" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-white/60 font-medium">
              Get Started
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-white/20" />
          </motion.div>

          {/* Headline */}
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight mb-8"
          >
            Ready to stop{' '}
            <span className="text-white/40">guessing</span>
            <br />
            and start{' '}
            <span className="text-white">
              commanding
            </span>
            ?
          </motion.h2>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg md:text-xl text-white/35 max-w-2xl mx-auto mb-16 leading-relaxed"
          >
            Join founders who are building GTM strategies that actually ship.
            <span className="text-white/50"> Your first Spike is 30 days away from clarity.</span>
          </motion.p>

          {/* Value props */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="flex flex-wrap justify-center gap-8 mb-14"
          >
            <ValueProp icon={Clock} text="15-minute strategic intake" delay={0.4} />
            <ValueProp icon={Shield} text="Kill switch protection" delay={0.5} />
            <ValueProp isBrandIcon brandIconName="speed" text="30-day execution sprint" delay={0.6} />
          </motion.div>

          {/* CTA buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-14"
          >
            <PremiumCTAButton onClick={() => navigate('/start')} primary>
              Launch Your Spike
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </PremiumCTAButton>

            <PremiumCTAButton onClick={() => navigate('/login')} primary={false}>
              Sign in to your account
            </PremiumCTAButton>
          </motion.div>

          {/* Trust signals */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="flex flex-wrap justify-center gap-8 text-sm text-white/25"
          >
            {[
              "No credit card required",
              "Cancel anytime",
              "7-day satisfaction guarantee"
            ].map((item, i) => (
              <span key={i} className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-amber-500/30" />
                {item}
              </span>
            ))}
          </motion.div>
        </div>

        {/* Bottom quote - editorial style */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.9, duration: 0.6 }}
          className="mt-28 pt-20 border-t border-white/[0.05] text-center"
        >
          <blockquote className="text-2xl md:text-3xl text-white/30 font-extralight tracking-wide max-w-2xl mx-auto leading-relaxed">
            "Strategy without execution is a daydream. Execution without strategy is a nightmare."
          </blockquote>
          <p className="mt-6 text-[11px] uppercase tracking-[0.3em] text-white/20">
            — Japanese Proverb
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default CTASection
