import React from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Quotes, ArrowRight, Sparkle } from '@phosphor-icons/react'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'
import manifestoHeroArt from '../assets/manifesto_hero_art.png'

// Animated reveal text component
const RevealText = ({ children, delay = 0, className = '' }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: '-50px' }}
    transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
    className={className}
  >
    {children}
  </motion.div>
)

// Premium blockquote with glass styling
const PremiumBlockquote = ({ children }) => (
  <GlassCard className="my-16 p-8 md:p-12">
    <div className="flex gap-4">
      <Quotes weight="fill" className="w-10 h-10 text-amber-500/60 flex-shrink-0 -mt-2" />
      <blockquote className="text-2xl md:text-3xl lg:text-4xl text-white/70 italic font-light leading-relaxed">
        {children}
      </blockquote>
    </div>
  </GlassCard>
)

// Section with gradient divider
const Section = ({ title, children, delay = 0 }) => (
  <RevealText delay={delay}>
    <div className="mb-16">
      <div className="flex items-center gap-4 mb-6">
        <div className="w-8 h-px bg-gradient-to-r from-amber-500 to-transparent" />
        <h3 className="text-xl md:text-2xl font-medium text-amber-400">
          {title}
        </h3>
      </div>
      <div className="text-lg md:text-xl text-white/60 leading-relaxed space-y-6 font-light">
        {children}
      </div>
    </div>
  </RevealText>
)

const Manifesto = () => {
  const { scrollYProgress } = useScroll()
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0])
  const heroScale = useTransform(scrollYProgress, [0, 0.15], [1, 1.05])

  return (
    <PremiumPageLayout>
      {/* Hero Section with Custom Artwork */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background artwork with parallax */}
        <motion.div
          style={{ opacity: heroOpacity, scale: heroScale }}
          className="absolute inset-0 z-0"
        >
          <img
            src={manifestoHeroArt}
            alt=""
            className="absolute inset-0 w-full h-full object-cover opacity-40"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-transparent to-[#0a0a0a]" />
        </motion.div>

        <div className="relative z-10 text-center px-6 max-w-5xl mx-auto pt-32 pb-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.3 }}
            className="mb-8"
          >
            <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium">
              <Sparkle weight="fill" className="w-4 h-4" />
              The Philosophy
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1.2, delay: 0.5 }}
            className="text-6xl md:text-8xl lg:text-9xl font-light text-white leading-[0.9] mb-8"
          >
            Less,
            <br />
            <span className="italic bg-gradient-to-r from-amber-300 via-amber-400 to-orange-400 text-transparent bg-clip-text">
              but better.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.9 }}
            className="text-xl md:text-2xl text-white/50 max-w-2xl mx-auto leading-relaxed font-light"
          >
            The strategic discipline that separates legendary brands from the noise.
          </motion.p>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
            className="absolute bottom-16 left-1/2 -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="flex flex-col items-center gap-4"
            >
              <span className="text-[10px] uppercase tracking-[0.3em] text-white/30">
                Scroll to read
              </span>
              <div className="w-px h-12 bg-gradient-to-b from-white/30 to-transparent" />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Main Content */}
      <section className="max-w-4xl mx-auto px-6 md:px-12 py-24">

        {/* Opening paragraph with drop cap */}
        <RevealText>
          <p className="text-2xl md:text-3xl text-white/80 leading-relaxed font-light mb-16 first-letter:text-7xl first-letter:font-normal first-letter:text-amber-400 first-letter:float-left first-letter:mr-4 first-letter:mt-[-8px]">
            Founders are drowning in advice. "Be everywhere." "Post daily." "Launch a podcast."
            "Run ads." The modern playbook is a recipe for burnout, not growth. It confuses
            motion with progress.
          </p>
        </RevealText>

        <PremiumBlockquote>
          Strategy is not about what you do. It's about what you choose not to do.
        </PremiumBlockquote>

        <Section title="The Biological Limit" delay={0.1}>
          <p>
            Your brain is not designed to hold 50 priorities. It can handle about three.
            Yet, most project management tools are designed to let you add infinite tickets,
            infinite tasks, infinite noise.
          </p>
          <p>
            Raptorflow is an operating system built around biological constraints. We force
            you to pick 3-5 moves for a 90-day cycle. Not because the software can't handle
            more, but because <span className="text-amber-400/80 font-medium">you</span> can't.
          </p>
        </Section>

        <Section title="Deep Work vs. Shallow Work" delay={0.15}>
          <p>
            Shallow work is answering emails, tweaking colors on a landing page, or checking
            analytics for the 10th time. Deep work is writing the sales letter that changes
            your trajectory.
          </p>
          <p>
            Our interface is minimal by design. No notifications. No "team activity" feeds
            popping up. Just you, your strategy, and the execution. It is a quiet room in
            a noisy world.
          </p>
        </Section>

        <Section title="The Myth of More" delay={0.2}>
          <p>
            More channels. More content. More campaigns. The industry profits from your
            exhaustion. We don't.
          </p>
          <p>
            We believe in the power of constraint. The brands that last aren't the ones
            that did everything—they're the ones that did the right things with
            <span className="text-amber-400/80 font-medium"> relentless consistency</span>.
          </p>
        </Section>

        <PremiumBlockquote>
          The goal isn't to be busy. The goal is to be{' '}
          <span className="text-amber-400">unmistakable</span>.
        </PremiumBlockquote>

        {/* Closing CTA */}
        <RevealText delay={0.2}>
          <div className="text-center mt-24 pt-16 border-t border-white/5">
            <h3 className="text-3xl md:text-4xl font-light text-white mb-6">
              Ready to build with intention?
            </h3>
            <p className="text-white/50 mb-10 text-lg max-w-xl mx-auto">
              Join founders who've traded chaos for clarity.
            </p>
            <motion.a
              href="/start"
              className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-amber-500 to-amber-400 text-black font-medium rounded-full overflow-hidden"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Get started
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" weight="bold" />
            </motion.a>
          </div>
        </RevealText>
      </section>
    </PremiumPageLayout>
  )
}

export default Manifesto
