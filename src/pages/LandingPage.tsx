import React from 'react'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { Check, ArrowRight, Play, XCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import { MarketingLayout } from '@/components/MarketingLayout'

// Components
import { StickyCTABar } from '@/pages/landing/StickyCTABar'
import { HeroSection } from '@/pages/landing/components/HeroSection'
import { InteractiveArt } from '@/pages/landing/components/InteractiveArt'
import { InteractivePlayground } from '@/pages/landing/InteractivePlayground'
import { WarRoomSection } from '@/pages/landing/WarRoomSection'
import { OutcomePathsSection } from '@/pages/landing/OutcomePathsSection'
import { FounderStory } from '@/pages/landing/FounderStory'
import { ComparisonTable } from '@/pages/landing/ComparisonTable'
import Pricing from '@/pages/landing/Pricing'
import FAQ from '@/pages/landing/FAQ'
import { LegendaryFooter } from '@/components/landing/LegendaryFooter'
import { WarRoomBackground } from '@/components/ui/WarRoomBackground'
import { Magnetic } from '@/components/ui/Magnetic'

// Inline Sub-components
const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-primary mb-6">
    <span className="w-8 h-0.5 bg-primary" />{children}
  </div>
)


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

        {/* 5. WAR ROOM - Scroll-driven features */}
        <WarRoomSection />

        {/* 6. COMPARISON TABLE (Restored) */}
        <ComparisonTable />

        {/* 7. OUTCOME PATHS - Goal-based selection */}
        <OutcomePathsSection />

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
