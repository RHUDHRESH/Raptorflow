import React from 'react'
import { motion } from 'framer-motion'

const PullQuote = () => {
  return (
    <section className="relative py-40 bg-background overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/90 to-background" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-radial from-primary/10 via-primary/5 to-transparent" />
      </div>

      {/* Lines */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

      <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
        {/* Quote mark */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="mb-8"
        >
          <span className="text-[180px] leading-none font-serif text-amber-500/10">"</span>
        </motion.div>

        {/* Quote */}
        <motion.blockquote
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1 }}
          className="-mt-40 text-3xl md:text-4xl lg:text-5xl font-light text-white leading-tight"
        >
          Most founders don't need
          <span className="italic text-amber-200"> more tactics</span>.
          <br />
          They need a plan they can
          <span className="italic text-amber-200"> actually execute</span>.
        </motion.blockquote>

        {/* Attribution */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="mt-12 flex items-center justify-center gap-4"
        >
          <div className="w-12 h-px bg-gradient-to-r from-transparent to-primary/50" />
          <span className="text-[10px] uppercase tracking-[0.3em] text-muted-foreground">
            The Raptorflow Philosophy
          </span>
          <div className="w-12 h-px bg-gradient-to-l from-transparent to-primary/50" />
        </motion.div>
      </div>
    </section>
  )
}

export default PullQuote
