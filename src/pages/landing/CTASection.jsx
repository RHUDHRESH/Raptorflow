import React, { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { Rocket, ArrowRight, Shield, Clock, Zap, CheckCircle2 } from 'lucide-react'

// Floating particle background
const FloatingParticles = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    {[...Array(20)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-1 h-1 bg-amber-400/30 rounded-full"
        initial={{
          x: Math.random() * 100 + '%',
          y: Math.random() * 100 + '%',
          opacity: Math.random() * 0.5 + 0.2
        }}
        animate={{
          y: [null, '-20%', null],
          opacity: [null, 0.6, null]
        }}
        transition={{
          duration: 3 + Math.random() * 2,
          repeat: Infinity,
          delay: Math.random() * 2
        }}
      />
    ))}
  </div>
)

// Value proposition item
const ValueProp = ({ icon: Icon, text, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.4 }}
    className="flex items-center gap-3"
  >
    <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
      <Icon className="w-4 h-4 text-amber-400" />
    </div>
    <span className="text-white/70 text-sm">{text}</span>
  </motion.div>
)

// Main CTA button with effects
const CTAButton = ({ onClick, children, primary = true }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    className={`
      relative group px-8 py-4 font-medium tracking-wide overflow-hidden transition-all duration-300
      ${primary 
        ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-black' 
        : 'bg-white/5 text-white border border-white/20 hover:border-white/30'
      }
    `}
  >
    {/* Animated background */}
    {primary && (
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-yellow-400 to-amber-400"
        initial={{ x: '-100%' }}
        whileHover={{ x: '0%' }}
        transition={{ duration: 0.3 }}
      />
    )}
    
    {/* Glow */}
    {primary && (
      <div className="absolute inset-0 bg-amber-400/50 blur-xl opacity-0 group-hover:opacity-50 transition-opacity" />
    )}
    
    <span className="relative z-10 flex items-center justify-center gap-2">
      {children}
    </span>
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
      className="relative py-32 bg-black overflow-hidden"
    >
      {/* Background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
        
        {/* Gradient orbs */}
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl" />
        
        <FloatingParticles />
      </div>

      <div className="max-w-4xl mx-auto px-6 relative z-10">
        {/* Main content */}
        <div className="text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-full mb-8"
          >
            <Rocket className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-medium tracking-wide text-amber-400">Start your first Spike</span>
          </motion.div>

          {/* Headline */}
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-4xl md:text-5xl lg:text-6xl font-light text-white mb-6"
          >
            Ready to stop{' '}
            <span className="italic font-normal text-white/50">guessing</span>
            <br />
            and start{' '}
            <span className="italic font-normal bg-gradient-to-r from-amber-200 via-yellow-100 to-amber-200 bg-clip-text text-transparent">
              commanding
            </span>
            ?
          </motion.h2>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg text-white/40 max-w-2xl mx-auto mb-12"
          >
            Join founders who are building GTM strategies that actually ship.
            Your first Spike is 30 days away from clarity.
          </motion.p>

          {/* Value props */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="flex flex-wrap justify-center gap-8 mb-12"
          >
            <ValueProp icon={Clock} text="15-minute strategic intake" delay={0.4} />
            <ValueProp icon={Shield} text="Kill switch protection" delay={0.5} />
            <ValueProp icon={Zap} text="30-day execution sprint" delay={0.6} />
          </motion.div>

          {/* CTA buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
          >
            <CTAButton onClick={() => navigate('/start')} primary>
              <Rocket className="w-4 h-4" />
              Launch Your Spike
              <ArrowRight className="w-4 h-4 ml-1" />
            </CTAButton>

            <CTAButton onClick={() => navigate('/login')} primary={false}>
              Already have an account? Sign in
            </CTAButton>
          </motion.div>

          {/* Trust signals */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="flex flex-wrap justify-center gap-6 text-sm text-white/30"
          >
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-amber-400/40" />
              No credit card required to start
            </span>
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-amber-400/40" />
              Cancel anytime
            </span>
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-amber-400/40" />
              7-day satisfaction guarantee
            </span>
          </motion.div>
        </div>

        {/* Bottom quote */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.9, duration: 0.6 }}
          className="mt-20 text-center"
        >
          <blockquote className="text-xl text-white/50 font-light italic max-w-2xl mx-auto">
            "Strategy without execution is a daydream. Execution without strategy is a nightmare."
          </blockquote>
          <p className="mt-4 text-sm text-white/30">
            — Japanese Proverb
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default CTASection

