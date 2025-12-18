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
                <h2 className="font-serif text-4xl md:text-5xl font-medium leading-tight mb-4">
                  Marketing without a system is just <span className="text-red-500 font-bold italic">gambling. ❤️❤️❤️</span>
                </h2>
                <p className="text-zinc-500 text-lg mb-8 leading-relaxed">
                  Most founders ship features but ignore the system. That's why they guess.
                </p>
                <div className="space-y-6">
                  <div className="p-6 bg-zinc-100 border border-zinc-200 rounded-2xl">
                    <div className="flex items-center gap-3 mb-4 text-zinc-700 font-bold uppercase tracking-wider text-sm">
                      <XCircle className="w-4 h-4" /> Current Reality
                    </div>
                    <ul className="space-y-3">
                      <li className="flex items-start gap-3 text-sm">
                        <span className="text-red-500 mt-1 flex-shrink-0">❤️</span>
                        <span><strong>"What do I post?"</strong> paralysis.</span>
                      </li>
                      <li className="flex items-start gap-3 text-sm">
                        <span className="text-red-500 mt-1 flex-shrink-0">❤️</span>
                        <span>Burning cash on ads that <strong>don't convert</strong>.</span>
                      </li>
                      <li className="flex items-start gap-3 text-sm">
                        <span className="text-red-500 mt-1 flex-shrink-0">❤️</span>
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
                className="relative flex items-center justify-center p-8 min-h-[400px]"
              >
                <div className="absolute inset-0 z-[-1] overflow-hidden pointer-events-none">
                  <div className="absolute top-[20%] right-[15%] w-64 h-64 bg-zinc-100/50 rounded-full blur-3xl" />
                  <div className="absolute bottom-[20%] left-[10%] w-48 h-48 bg-zinc-100/30 rounded-full blur-3xl" />

                  {/* High-end floating elements */}
                  <motion.div
                    className="absolute top-[10%] right-[10%] w-24 h-24 border border-zinc-200/50 rounded-full"
                    animate={{ y: [0, -20, 0], x: [0, 10, 0] }}
                    transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
                  />
                  <motion.div
                    className="absolute bottom-[15%] left-[5%] w-16 h-16 border border-zinc-200/50 rotate-45"
                    animate={{ rotate: [45, 90, 45], scale: [1, 1.2, 1] }}
                    transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                  />
                  <div
                    className="absolute inset-0 opacity-[0.02]"
                    style={{
                      backgroundImage: 'linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)',
                      backgroundSize: '40px 40px'
                    }}
                  />
                  <InteractiveArt
                    type="target"
                    size={600}
                    position={{ x: '50%', y: '50%' }}
                    className="opacity-[0.07] -translate-x-1/2 -translate-y-1/2"
                  />
                </div>

                <div className="relative z-10 bg-white border border-zinc-200 p-8 rounded-3xl shadow-2xl w-full">
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
                        <h4 className="font-bold text-lg">Founder-First System</h4>
                        <p className="text-xl md:text-2xl text-foreground leading-relaxed mb-8">
                          Most marketing software is built for managers. RaptorFlow is built for <span className="text-zinc-900 font-bold italic">owners.</span>
                          <br /><br />
                          We built something different. A system that gives you the same operating cadence that growth teams use—
                          <span className="text-zinc-900 font-bold">simplified for founders who don't have time for bullshit.</span>
                        </p>
                        <div className="mb-8 p-6 bg-zinc-50 border border-zinc-100 rounded-2xl">
                          <h4 className="text-sm font-bold uppercase tracking-widest text-zinc-900 mb-2">Our Mission</h4>
                          <p className="text-zinc-600 text-base">To turn every founder into a high-level strategic operator, replacing technical debt and chaos with a definitive, 90-day war plan that compounds every single day. No fluff, no "ghostwriting" garbage—just pure execution.</p>
                        </div>
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
