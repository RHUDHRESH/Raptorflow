import React, { useState } from 'react'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { Check, ArrowRight, Play, XCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import { MarketingLayout } from '@/components/MarketingLayout'

// Components
import { UseCases } from '@/pages/landing/UseCases'
import { StickyCTABar } from '@/pages/landing/StickyCTABar'
import { HeroSection } from '@/pages/landing/components/HeroSection'
import { InteractiveArt } from '@/pages/landing/components/InteractiveArt'
import { InteractivePlayground } from '@/pages/landing/InteractivePlayground'

// Restored Components
import { FounderStory } from '@/pages/landing/FounderStory'
import { ComparisonTable } from '@/pages/landing/ComparisonTable'
import Pricing from '@/pages/landing/Pricing' // Default export
import FAQ from '@/pages/landing/FAQ' // Default export
import { LegendaryFooter } from '@/components/landing/LegendaryFooter'

// Data Layer
import { FEATURES } from '@/data/landing-content'

// Inline Sub-components
const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-primary mb-6">
    <span className="w-8 h-0.5 bg-primary" />{children}
  </div>
)

import { WarRoomBackground } from '@/components/ui/WarRoomBackground'
import { Magnetic } from '@/components/ui/Magnetic'

const LandingPage = () => {
  return (
    <HelmetProvider>
      <Helmet>
        <title>RaptorFlow - The War Room for Founders</title>
        <meta name="description" content="Stop guessing. Start executing. RaptorFlow connects strategy to daily moves. No fluff, just revenue." />
      </Helmet>

      {/* Reverted Global Background - Returning to warm usage in sections */}

      <MarketingLayout showFooter={false}>
        <StickyCTABar />

        {/* 1. HERO SECTION */}
        <HeroSection />

        {/* 2. DEMO (The Investment) */}
        <section id="demo" className="relative py-24 md:py-32 overflow-hidden bg-muted/20">
          <div className="container-editorial relative z-10">
            <motion.div
              className="max-w-4xl mx-auto text-center mb-16"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <SectionLabel>See It In Action</SectionLabel>
              <h2 className="font-serif text-4xl md:text-6xl font-medium text-foreground">
                Don't Trust Words. <span className="text-primary italic">Trust Code.</span>
              </h2>
              <p className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto">
                Click below. Generate a strategy. See the war plan build itself.
              </p>
            </motion.div>

            <InteractivePlayground />

            <div className="mt-16 text-center flex justify-center">
              <Link
                to="/signup"
                className="group inline-flex items-center gap-2 px-10 py-5 bg-foreground text-background rounded-full font-bold text-lg hover:opacity-90 transition-all shadow-xl"
              >
                Start My War Campaign
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </section>

        {/* 3. PROBLEM (The Pain) */}
        <section className="relative py-24 md:py-40 overflow-hidden">
          <div className="absolute inset-0 pointer-events-none opacity-40">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-red-900/10 via-background to-background" />
          </div>

          <div className="container-editorial relative z-10">
            <div className="grid md:grid-cols-2 gap-20 items-center">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
              >
                <h2 className="font-serif text-4xl md:text-5xl font-medium leading-tight mb-8">
                  Marketing without a system is just <span className="text-red-500 line-through decoration-red-500/50">gambling</span>.
                </h2>
                <div className="space-y-6">
                  <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-2xl">
                    <div className="flex items-center gap-3 mb-4 text-red-400 font-bold uppercase tracking-wider text-sm">
                      <XCircle className="w-4 h-4" /> Current Reality
                    </div>
                    <ul className="space-y-3">
                      <li className="flex items-start gap-3">
                        <span className="text-xl">🛑</span>
                        <span><strong>"What do I post?"</strong> paralysis.</span>
                      </li>
                      <li className="flex items-start gap-3">
                        <span className="text-xl">💸</span>
                        <span>Burning cash on ads that <strong>don't convert</strong>.</span>
                      </li>
                      <li className="flex items-start gap-3">
                        <span className="text-xl">📉</span>
                        <span>Zero data. Just <strong>vibes and hope</strong>.</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="relative"
              >
                <InteractiveArt type="target" size={300} position={{ x: '50%', y: '50%' }} className="opacity-10 pointer-events-none -translate-x-1/2 -translate-y-1/2" />

                <div className="relative bg-card border border-border/50 p-8 rounded-3xl shadow-2xl">
                  <div className="flex items-center gap-3 mb-6 text-primary font-bold uppercase tracking-wider text-sm">
                    <Check className="w-4 h-4" /> RaptorFlow Reality
                  </div>
                  <ul className="space-y-6">
                    <li className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                        <Check className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Sniper Positioning</h4>
                        <p className="text-muted-foreground">Know exactly who you kill in the market.</p>
                      </div>
                    </li>
                    <li className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                        <Check className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Daily Battle Plan</h4>
                        <p className="text-muted-foreground">Wake up. Execute list. Win.</p>
                      </div>
                    </li>
                    <li className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                        <Check className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Scientific Growth</h4>
                        <p className="text-muted-foreground">Data dictates decisions. No feelings.</p>
                      </div>
                    </li>
                  </ul>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* 4. FOUNDER STORY (Restored - Trust Bridge) */}
        <FounderStory />

        {/* 5. THE SYSTEM (Features) */}
        <section id="features" className="relative py-24 md:py-32 bg-gradient-to-b from-card to-background border-y border-border overflow-hidden">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-30">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(245,158,11,0.08),transparent_50%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(251,146,60,0.06),transparent_50%)]" />
          </div>

          <div className="container-editorial relative z-10">
            <motion.div
              className="text-center max-w-3xl mx-auto mb-20"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <SectionLabel>The System</SectionLabel>
              <h2 className="font-serif text-4xl md:text-6xl font-medium bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground to-foreground/80">
                How we win the war
              </h2>
              <p className="mt-6 text-xl text-muted-foreground">Four steps. Daily execution. No guesswork.</p>
            </motion.div>

            {/* Feature grid with connecting line */}
            <div className="relative">
              {/* Connecting flow line */}
              <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent -translate-y-1/2" />

              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-4">
                {FEATURES.map((feature, i) => (
                  <motion.div
                    key={i}
                    className="group relative"
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.5 }}
                  >
                    {/* Card */}
                    <div className="relative h-full p-8 rounded-3xl bg-background/80 backdrop-blur-sm border border-border group-hover:border-primary/50 transition-all duration-500 group-hover:-translate-y-2 group-hover:shadow-xl group-hover:shadow-primary/10">
                      {/* Hover glow */}
                      <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                      {/* Step number badge */}
                      <div className="absolute -top-3 -right-3 w-10 h-10 rounded-full bg-gradient-to-br from-primary to-orange-500 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary/25">
                        {feature.step}
                      </div>

                      {/* Icon with animated background */}
                      <motion.div
                        className="relative w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-orange-500/20 flex items-center justify-center mb-6 border border-primary/20"
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <motion.div
                          className="absolute inset-0 rounded-2xl bg-primary/10"
                          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
                          transition={{ duration: 3, repeat: Infinity, delay: i * 0.5 }}
                        />
                        <feature.icon className="w-8 h-8 text-primary relative z-10" />
                      </motion.div>

                      <h3 className="text-xl font-bold mb-3 text-foreground group-hover:text-primary transition-colors">{feature.title}</h3>
                      <p className="text-muted-foreground leading-relaxed mb-4">{feature.description}</p>

                      {feature.details && (
                        <ul className="space-y-2 pt-4 border-t border-border/50">
                          {feature.details.map((detail: string, j: number) => (
                            <li key={j} className="text-sm text-muted-foreground/80 flex items-center gap-2">
                              <motion.span
                                className="w-1.5 h-1.5 rounded-full bg-primary"
                                animate={{ scale: [1, 1.3, 1] }}
                                transition={{ duration: 2, repeat: Infinity, delay: j * 0.2 }}
                              />
                              {detail}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* 6. COMPARISON TABLE (Restored) */}
        <ComparisonTable />

        {/* 7. USE CASES (Restored) */}
        <UseCases />

        {/* 8. PRICING (Restored) */}
        <Pricing />

        {/* 9. FAQ (Restored) */}
        <FAQ />

        {/* 10. LEGENDARY FOOTER (Restored) */}
        <LegendaryFooter />

      </MarketingLayout>
    </HelmetProvider>
  )
}

export default LandingPage
