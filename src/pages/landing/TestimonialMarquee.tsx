import React from 'react'
import { motion } from 'framer-motion'
import { Target, Shield, TrendingUp, Clock, Users } from 'lucide-react'
import { BRAND_ICONS } from '@/components/brand/BrandSystem'

// Replaced fake testimonials with honest value props
const TestimonialMarquee = () => {
  const valueProps = [
    {
      icon: Target,
      title: "Clarity in 10 Minutes",
      description: "Transform scattered thoughts into a structured 90-day execution plan. No fluff, just focused action.",
      gradient: "from-gray-500/20 to-gray-700/10"
    },
    {
      icon: BRAND_ICONS.speed,
      title: "AI-Powered Moves",
      description: "Every move is crafted by AI that understands your cohorts, barriers, and growth stage.",
      gradient: "from-zinc-500/20 to-zinc-700/10"
    },
    {
      icon: Shield,
      title: "Built-in Guardrails",
      description: "Kill switches and RAG scoring ensure you never waste budget on underperforming campaigns.",
      gradient: "from-emerald-500/20 to-emerald-700/10"
    }
  ]

  const principles = [
    { icon: TrendingUp, text: "Strategy that ships" },
    { icon: Clock, text: "Built for speed" },
    { icon: Users, text: "Made for founders" },
  ]

  return (
    <section className="relative py-32 bg-black overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-zinc-950 to-black" />

      {/* Decorative lines */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">

        {/* Section header */}
        <div className="text-center mb-20">
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-[10px] uppercase tracking-[0.4em] text-zinc-400/60"
          >
            Why Raptorflow
          </motion.span>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mt-6 text-3xl md:text-4xl font-light text-white"
          >
            Built for founders who
            <span className="italic font-normal text-zinc-200"> demand clarity</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mt-4 text-white/40 max-w-lg mx-auto"
          >
            Stop guessing. Start executing with precision.
          </motion.p>
        </div>

        {/* Value prop cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
          {valueProps.map((prop, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
              className="group relative"
            >
              <div className={`relative p-8 bg-gradient-to-b ${prop.gradient} border border-white/[0.05] hover:border-white/[0.1] transition-all duration-500 rounded-xl`}>

                {/* Icon */}
                <div className="mb-6 w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <prop.icon className="w-6 h-6 text-zinc-400" />
                </div>

                {/* Title */}
                <h3 className="text-xl font-light text-white mb-3">
                  {prop.title}
                </h3>

                {/* Description */}
                <p className="text-white/50 leading-relaxed">
                  {prop.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Principles bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="flex flex-wrap justify-center gap-8 md:gap-16"
        >
          {principles.map((principle, i) => (
            <div key={i} className="flex items-center gap-3 text-white/40">
              <principle.icon className="w-5 h-5 text-zinc-500/50" />
              <span className="text-sm tracking-wide">{principle.text}</span>
            </div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6 }}
          className="mt-16 text-center"
        >
          <p className="text-white/30 text-sm">
            Join early adopters building their GTM with precision.
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default TestimonialMarquee

