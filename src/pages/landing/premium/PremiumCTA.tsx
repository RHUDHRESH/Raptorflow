import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const PremiumCTA = () => {
  return (
    <section className="bg-background py-32 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-accent/5" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[100px]" />

      <div className="container mx-auto px-6 relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="font-serif text-6xl md:text-8xl mb-8 leading-none">
            Begin the <br />
            <span className="italic text-accent">Transformation</span>
          </h2>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-12 font-light">
            Join the exclusive circle of founders who have mastered the art of growth.
          </p>

          <Link 
            to="/start"
            className="inline-flex items-center gap-4 px-12 py-5 bg-foreground text-background text-lg font-medium uppercase tracking-widest hover:bg-accent hover:text-white transition-all duration-300 rounded-none"
          >
            Request Access <ArrowRight />
          </Link>
        </motion.div>
      </div>
    </section>
  )
}

export default PremiumCTA

