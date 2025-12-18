import React from 'react'
import { motion } from 'framer-motion'

const Manifesto = () => {
  return (
    <section className="py-32 md:py-48 bg-canvas border-b border-line relative overflow-hidden">
      {/* Subtle Noise Texture */}
      <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '600px' }}></div>

      <div className="max-w-4xl mx-auto px-6 md:px-8 relative z-10">
        <div className="space-y-12 md:space-y-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="flex items-center gap-4"
          >
            <div className="w-16 h-px bg-aubergine"></div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-aubergine font-bold">The Manifesto</p>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="font-serif text-4xl md:text-6xl lg:text-7xl leading-[1.1] text-charcoal"
          >
            Most marketing is<br />
            <span className="italic text-aubergine/80">motion without progress.</span>
          </motion.h2>

          <div className="space-y-8 text-lg md:text-xl text-charcoal/70 font-sans font-light leading-relaxed max-w-2xl">
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Founders are told to "be everywhere." So they post on LinkedIn, start a podcast, run ads, and write blogs—all in the same week.
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              The result isn't growth. It's burnout.
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
            >
              Raptorflow is the antidote to random acts of marketing. We believe in doing
              <strong className="text-charcoal font-medium"> fewer things, with higher precision.</strong>
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
            >
              One clear message. One core channel. One 90-day growth roadmap.
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, scaleX: 0 }}
            whileInView={{ opacity: 1, scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6, duration: 1 }}
            className="w-24 h-1 bg-gold origin-left"
          ></motion.div>
        </div>
      </div>
    </section>
  )
}

export default Manifesto

