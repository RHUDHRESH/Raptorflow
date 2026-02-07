import React from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import SpotlightCard from '../../components/SpotlightCard'

const SevenPillars = () => {
  const pillars = [
    {
      id: '01',
      title: 'Audience',
      desc: 'Know exactly who to hunt first.',
      size: 'large',
      art: (
        <div className="absolute -right-20 -top-20 w-64 h-64 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
          <div className="absolute inset-0 rounded-full border-4 border-aubergine"></div>
          <div className="absolute inset-8 rounded-full border-2 border-aubergine"></div>
          <div className="absolute inset-16 rounded-full border border-aubergine"></div>
        </div>
      )
    },
    {
      id: '02',
      title: 'Value prop',
      desc: 'Clarify why anyone should buy from you now.',
      size: 'medium',
      art: (
        <div className="absolute -right-16 -bottom-16 w-48 h-48 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
          <svg viewBox="0 0 100 100" className="w-full h-full text-gold">
            <polygon points="50,10 61,35 89,35 67,52 75,78 50,63 25,78 33,52 11,35 39,35" fill="currentColor" opacity="0.3" />
          </svg>
        </div>
      )
    },
    {
      id: '03',
      title: 'Differentiation',
      desc: "What you can say they can't copy in 2 weeks.",
      size: 'small',
      art: (
        <div className="absolute -left-8 -bottom-8 w-32 h-32 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:rotate-12">
          <div className="absolute inset-0 border-4 border-aubergine rounded-lg rotate-12"></div>
          <div className="absolute inset-4 border-2 border-aubergine rounded-lg rotate-6"></div>
        </div>
      )
    },
    {
      id: '04',
      title: 'Competition',
      desc: 'Where you can flank existing alternatives.',
      size: 'medium',
      art: (
        <div className="absolute -right-12 top-1/2 -translate-y-1/2 w-40 h-40 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
          <div className="absolute inset-0 rounded-full border-4 border-gold"></div>
          <div className="absolute inset-6 rounded-full border-2 border-gold"></div>
        </div>
      )
    },
    {
      id: '05',
      title: 'Discovery',
      desc: 'How they actually find you.',
      size: 'small',
      art: (
        <div className="absolute -right-10 -top-10 w-36 h-36 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:scale-110">
          <div className="absolute inset-0 rounded-full border-4 border-aubergine"></div>
          <div className="absolute bottom-2 right-2 w-12 h-1 bg-aubergine origin-top-right rotate-45"></div>
        </div>
      )
    },
    {
      id: '06',
      title: 'Remarkability',
      desc: 'The story worth talking about.',
      size: 'medium',
      art: (
        <div className="absolute -left-12 -top-12 w-44 h-44 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:rotate-45">
          <svg viewBox="0 0 100 100" className="w-full h-full text-gold">
            <path d="M50 10 L55 45 L90 50 L55 55 L50 90 L45 55 L10 50 L45 45 Z" fill="currentColor" opacity="0.4" />
          </svg>
        </div>
      )
    },
    {
      id: '07',
      title: 'Proof',
      desc: 'Evidence that makes it believable.',
      size: 'large',
      art: (
        <div className="absolute -right-16 -bottom-16 w-56 h-56 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
          <svg viewBox="0 0 100 100" className="w-full h-full text-aubergine">
            <path d="M50 10 L80 25 L80 50 Q80 75 50 90 Q20 75 20 50 L20 25 Z" fill="currentColor" opacity="0.3" />
            <path d="M35 50 L45 60 L65 35" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.6" />
          </svg>
        </div>
      )
    }
  ]

  // Determine column spans based on size
  const getColSpan = (size) => {
    switch (size) {
      case 'large': return 'md:col-span-7'
      case 'medium': return 'md:col-span-5'
      case 'small': return 'md:col-span-4'
      default: return 'md:col-span-4'
    }
  }

  return (
    <section id="pillars" className="py-20 md:py-32 border-b border-line relative overflow-hidden">
      {/* Dramatic Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-aubergine/10 via-canvas to-gold/10"></div>
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '1400px' }}></div>

      {/* Large animated orbs */}
      <motion.div
        animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.2, 0.1] }}
        transition={{ duration: 10, repeat: Infinity }}
        className="absolute top-1/4 right-1/3 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-gold/20 to-transparent blur-3xl"
      />
      <motion.div
        animate={{ scale: [1, 1.1, 1], opacity: [0.1, 0.2, 0.1] }}
        transition={{ duration: 12, repeat: Infinity, delay: 2 }}
        className="absolute bottom-1/4 left-1/3 w-[700px] h-[700px] rounded-full bg-gradient-to-tl from-aubergine/20 to-transparent blur-3xl"
      />

      <div className="max-w-7xl mx-auto px-6 md:px-8 lg:px-12 relative z-10">
        {/* Dramatic Header */}
        <div className="text-center max-w-4xl mx-auto mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center justify-center gap-4 mb-8">
              <div className="w-20 h-px bg-gradient-to-r from-transparent via-gold to-transparent"></div>
              <p className="text-[10px] uppercase tracking-[0.4em] text-gold font-bold">
                The 7 Pillars
              </p>
              <div className="w-20 h-px bg-gradient-to-r from-transparent via-gold to-transparent"></div>
            </div>
            <h2 className="font-serif text-6xl md:text-7xl lg:text-8xl leading-[0.95] mb-8 text-charcoal">
              The strategy spine<br />behind every plan.
            </h2>
            <p className="text-xl text-charcoal/80 leading-relaxed max-w-2xl mx-auto font-sans">
              Every campaign, move, and brief must answer to these seven.<br className="hidden md:block" />
              No more random tactics unlinked from positioning.
            </p>
          </motion.div>
        </div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 auto-rows-[minmax(200px,auto)]">
          {/* Row 1: 7 + 5 */}
          {pillars.slice(0, 2).map((pillar, i) => (
            <PillarCard key={i} pillar={pillar} className={getColSpan(pillar.size)} />
          ))}

          {/* Row 2: 4 + 4 + 4 (But wait, current layout is 4+4+4=12? No, let's check array) 
               Indices 2,3,4 -> Sizes S, M, S -> 4+5+? Wait.
               Let's force layout for row 2: S(4) + M(4) + S(4) = 12.
               Wait, M is usually 5. 
               Let's adjust the `getColSpan` logic or manually assign for perfect bento.
               Actually, let's just map them and let CSS Grid auto-flow if we use dense, or stick to the defined spans.
               
               Let's stick to the explicit logic defined in original file which was carefully crafted:
               Row 1: Large(7) + Medium(5) = 12
               Row 2: Small(4) + Medium(4) + Small(4) = 12 (Wait, Medium was col-span-4 in original row 2? Let's check)
               Original Row 2: 
               03 (Small) -> col-span-4
               04 (Medium) -> col-span-4 (Wait, previous code said col-span-4 for Competition)
               05 (Small) -> col-span-4
               Total 12. Perfect.

               Row 3: Medium(5) + Large(7) = 12.
            */}

          {/* Row 2 */}
          {pillars.slice(2, 5).map((pillar, i) => (
            <PillarCard key={i + 2} pillar={pillar} className="md:col-span-4" />
          ))}

          {/* Row 3 */}
          {pillars.slice(5, 7).map((pillar, i) => (
            <PillarCard key={i + 5} pillar={pillar} className={getColSpan(pillar.size)} />
          ))}
        </div>
      </div>
    </section>
  )
}

const PillarCard = ({ pillar, className }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5 }}
      className={clsx("group relative h-full", className)}
      style={{ willChange: 'transform, opacity' }}
    >
      <div className="absolute -inset-0.5 bg-gradient-to-br from-aubergine/20 to-gold/20 rounded-[2rem] opacity-0 group-hover:opacity-100 transition-all duration-700 blur-xl" style={{ willChange: 'opacity' }}></div>
      <SpotlightCard className="h-full bg-white border-2 border-charcoal/20 rounded-[2rem] hover:bg-white hover:border-aubergine/50 hover:shadow-2xl transition-all duration-500">
        <div className="relative h-full p-8 md:p-10 flex flex-col justify-between overflow-hidden">
          {/* Artistic Element */}
          {pillar.art}

          <div className="relative z-10 pointer-events-none">
            <div className="mb-4">
              <span className="text-[10px] uppercase tracking-[0.3em] text-gold font-bold bg-canvas px-3 py-1.5 rounded-full">
                {pillar.id}
              </span>
            </div>
            <h3 className={clsx("font-serif mb-4 group-hover:text-aubergine transition-colors leading-tight text-charcoal",
              pillar.size === 'large' ? 'text-4xl md:text-5xl' : 'text-3xl md:text-4xl'
            )}>
              {pillar.title}
            </h3>
            <p className="text-sm md:text-base text-charcoal leading-relaxed font-sans max-w-md">
              {pillar.desc}
            </p>
          </div>

          {/* Hover Indicator */}
          <div className="absolute bottom-8 right-8 w-8 h-8 rounded-full border border-charcoal/10 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-500 transform translate-y-4 group-hover:translate-y-0 pointer-events-none">
            <div className="w-1.5 h-1.5 bg-aubergine rounded-full"></div>
          </div>
        </div>
      </SpotlightCard>
    </motion.div>
  )
}

export default SevenPillars
