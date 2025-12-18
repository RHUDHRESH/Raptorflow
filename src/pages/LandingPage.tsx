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
  <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-zinc-600 mb-6">
    <span className="w-8 h-0.5 bg-zinc-400" />{children}
  </div>
)


const LandingPage = () => {
  return (
    <HelmetProvider>
      <Helmet>
        <title>RaptorFlow - The Marketing System for Founders</title>
        <meta name="description" content="Stop guessing. Start executing. RaptorFlow connects strategy to daily moves. No fluff, just results." />
      </Helmet>

      {/* Reverted Global Background - Returning to warm usage in sections */}

      <MarketingLayout showFooter={false}>
        <StickyCTABar />

        {/* 1. HERO SECTION */}
        <HeroSection />
        {/* 3. PROBLEM (The Pain) */}
        <section className="relative py-24 md:py-32 overflow-hidden bg-muted/40">
          <div className="absolute inset-0 pointer-events-none opacity-40">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-destructive/10 via-background to-background" />
          </div>

          <div className="max-w-5xl mx-auto px-6 relative z-10">
            <div className="grid md:grid-cols-2 gap-16 items-center">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
              >
                <h2 className="font-serif text-4xl md:text-5xl font-medium leading-tight mb-8">
                  Marketing without a system is just <span className="text-destructive line-through decoration-destructive/50">gambling</span>.
                </h2>
                <div className="space-y-6">
                  <div className="p-6 bg-destructive/5 border border-destructive/15 rounded-2xl">
                    <div className="flex items-center gap-3 mb-4 text-destructive font-bold uppercase tracking-wider text-sm">
                      <XCircle className="w-4 h-4" /> Current Reality
                    </div>
                    <ul className="space-y-3">
                      <li className="flex items-start gap-3 text-sm">
                        <span className="text-lg">🛑</span>
                        <span><strong>"What do I post?"</strong> paralysis.</span>
                      </li>
                      <li className="flex items-start gap-3 text-sm">
                        <span className="text-lg">💸</span>
                        <span>Burning cash on ads that <strong>don't convert</strong>.</span>
                      </li>
                      <li className="flex items-start gap-3 text-sm">
                        <span className="text-lg">📉</span>
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
                  <div className="flex items-center gap-3 mb-6 text-zinc-700 font-bold uppercase tracking-wider text-sm">
                    <Check className="w-4 h-4" /> RaptorFlow Reality
                  </div>
                  <ul className="space-y-6">
                    <li className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-zinc-100 flex items-center justify-center shrink-0">
                        <Check className="w-5 h-5 text-zinc-700" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Sniper Positioning</h4>
                        <p className="text-sm text-muted-foreground">Know exactly who you serve in the market.</p>
                      </div>
                    </li>
                    <li className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-zinc-100 flex items-center justify-center shrink-0">
                        <Check className="w-5 h-5 text-zinc-700" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Daily Growth Plan</h4>
                        <p className="text-sm text-muted-foreground">Wake up. Execute list. Win.</p>
                      </div>
                    </li>
                    <li className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-zinc-100 flex items-center justify-center shrink-0">
                        <Check className="w-5 h-5 text-zinc-700" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Scientific Execution</h4>
                        <p className="text-sm text-muted-foreground">Data dictates decisions. No feelings.</p>
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

        {/* 5. EXECUTION SYSTEM - Scroll-driven features */}
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
