import React from 'react'
import { motion } from 'framer-motion'
import { GridFour, TextAa, ArrowRight, Sparkle, Stack, Lightning } from '@phosphor-icons/react'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'
import SevenPillars from './landing/SevenPillars'
import IntegrationGrid from './landing/IntegrationGrid'

const Product = () => {
  return (
    <PremiumPageLayout>
      <div className="pt-32 pb-20">
        <div className="px-6 md:px-12 max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-24"
          >
            {/* Hero Section */}
            <section className="text-center space-y-6">
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium"
              >
                <Sparkle weight="fill" className="w-4 h-4" />
                The Engine
              </motion.span>
              <h1 className="text-6xl md:text-8xl font-light text-white leading-[0.95]">
                Precision{' '}
                <span className="italic bg-gradient-to-r from-amber-300 via-amber-400 to-orange-400 text-transparent bg-clip-text">
                  Engineering
                </span>
              </h1>
              <p className="text-xl text-white/50 max-w-2xl mx-auto font-light leading-relaxed">
                Raptorflow isn't just a dashboard. It's a methodology codified into software.
                Designed to force clarity and eliminate strategic drift.
              </p>
            </section>

            {/* Feature 1: The Matrix */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center py-12 border-t border-white/5">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="space-y-6"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/20 flex items-center justify-center">
                    <GridFour weight="duotone" className="w-6 h-6 text-amber-400" />
                  </div>
                  <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-medium">Feature</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-light text-white">The Strategy Matrix</h2>
                <p className="text-white/60 text-lg leading-relaxed">
                  Most founders drown in tasks. The Matrix forces you to choose 3-5 strategic bets.
                  If it doesn't fit in the grid, it doesn't happen.
                </p>
                <ul className="space-y-3 text-sm text-white/40 pt-4">
                  <li className="flex items-center gap-3">
                    <span className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-500 to-orange-500" />
                    Constraint-based Planning
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-500 to-orange-500" />
                    Visual Trade-offs
                  </li>
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
              >
                <GlassCard className="aspect-square overflow-hidden p-8 group">
                  {/* Abstract Representation of Matrix */}
                  <div className="h-full grid grid-cols-2 gap-4 opacity-60 group-hover:opacity-100 transition-opacity duration-700">
                    <div className="bg-white/5 rounded-lg border border-white/10 group-hover:border-amber-500/30 transition-colors" />
                    <div className="bg-white/5 rounded-lg border border-white/10 group-hover:border-amber-500/30 transition-colors" />
                    <div className="bg-white/5 rounded-lg border border-white/10 group-hover:border-amber-500/30 transition-colors" />
                    <div className="bg-amber-500/10 rounded-lg border-2 border-dashed border-amber-500/30 flex items-center justify-center">
                      <span className="text-amber-400/50 text-xs uppercase tracking-widest">+Add</span>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            </section>

            {/* Feature 2: The Brief */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center py-12 border-t border-white/5">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="order-2 md:order-1"
              >
                <GlassCard className="aspect-square overflow-hidden p-8 group relative">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-white/5 text-[200px] font-serif italic group-hover:text-amber-500/10 transition-colors duration-700">Aa</span>
                  </div>
                  <div className="relative z-10 h-full flex flex-col justify-end">
                    <div className="space-y-3 bg-gradient-to-t from-[#0a0a0a] to-transparent pt-12">
                      <div className="h-4 w-1/2 bg-white/20 rounded" />
                      <div className="h-2 w-full bg-white/10 rounded" />
                      <div className="h-2 w-3/4 bg-white/10 rounded" />
                    </div>
                  </div>
                </GlassCard>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="space-y-6 order-1 md:order-2"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/20 flex items-center justify-center">
                    <TextAa weight="duotone" className="w-6 h-6 text-amber-400" />
                  </div>
                  <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-medium">Feature</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-light text-white">Muse-Grade Briefs</h2>
                <p className="text-white/60 text-lg leading-relaxed">
                  Stop writing boring documents. Our editor is designed for high-stakes creativity.
                  Minimalist, focused, and beautiful enough to present directly to investors.
                </p>
              </motion.div>
            </section>

            {/* Feature 3: AI Engine */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center py-12 border-t border-white/5">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="space-y-6"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/20 flex items-center justify-center">
                    <Lightning weight="duotone" className="w-6 h-6 text-amber-400" />
                  </div>
                  <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-medium">Feature</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-light text-white">AI War Room</h2>
                <p className="text-white/60 text-lg leading-relaxed">
                  Your strategic advisor that never sleeps. Get instant positioning insights,
                  competitive analysis, and campaign ideas generated from your unique context.
                </p>
                <ul className="space-y-3 text-sm text-white/40 pt-4">
                  <li className="flex items-center gap-3">
                    <span className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-500 to-orange-500" />
                    Context-aware suggestions
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-500 to-orange-500" />
                    One-click brief generation
                  </li>
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
              >
                <GlassCard className="aspect-square overflow-hidden p-8 group relative">
                  <div className="absolute inset-0 bg-gradient-radial from-amber-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                  <div className="relative z-10 h-full flex flex-col items-center justify-center gap-6">
                    <motion.div
                      animate={{ scale: [1, 1.05, 1] }}
                      transition={{ duration: 3, repeat: Infinity }}
                      className="w-24 h-24 rounded-full bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/30 flex items-center justify-center"
                    >
                      <Lightning weight="fill" className="w-12 h-12 text-amber-400" />
                    </motion.div>
                    <div className="text-center">
                      <p className="text-xs uppercase tracking-widest text-white/30">Powered by</p>
                      <p className="text-white/60">Advanced AI</p>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            </section>

            <section className="border-t border-white/5 pt-20">
              <SevenPillars />
            </section>

            <section className="py-20">
              <IntegrationGrid />
            </section>

          </motion.div>
        </div>
      </div>
    </PremiumPageLayout>
  )
}

export default Product
