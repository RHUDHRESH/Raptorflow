import React from 'react'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Target, Diamond, Fingerprint, Binoculars, Compass, Megaphone, SealCheck } from '@phosphor-icons/react'

const pillars = [
  {
    id: '01',
    title: 'Audience',
    desc: 'Know exactly who you serve — and who you ignore.',
    icon: Target,
    size: 'large'
  },
  {
    id: '02',
    title: 'Value Prop',
    desc: 'Articulate why they should buy from you, not others.',
    icon: Diamond,
    size: 'medium'
  },
  {
    id: '03',
    title: 'Differentiation',
    desc: "What you can claim that they can't copy in two weeks.",
    icon: Fingerprint,
    size: 'small'
  },
  {
    id: '04',
    title: 'Competition',
    desc: 'Position yourself to flank alternatives effectively.',
    icon: Binoculars,
    size: 'medium'
  },
  {
    id: '05',
    title: 'Discovery',
    desc: 'Map the channels where your audience actually gathers.',
    icon: Compass,
    size: 'small'
  },
  {
    id: '06',
    title: 'Remarkability',
    desc: 'Craft stories worth spreading — that earn attention.',
    icon: Megaphone,
    size: 'medium'
  },
  {
    id: '07',
    title: 'Proof',
    desc: 'Build evidence that makes your claims believable.',
    icon: SealCheck,
    size: 'large'
  }
]

const getGridClass = (size, index) => {
  if (index === 0) return 'md:col-span-2 md:row-span-2'
  if (index === 6) return 'md:col-span-2'
  if (size === 'medium') return 'md:col-span-1 md:row-span-1'
  return ''
}

const PillarCard = ({ pillar, index }) => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const Icon = pillar.icon

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay: index * 0.08 }}
      className={`group relative ${getGridClass(pillar.size, index)}`}
    >
      <div className="h-full p-6 md:p-8 rounded-2xl bg-zinc-900/40 border border-white/[0.05] hover:border-amber-500/20 transition-all duration-500 overflow-hidden">

        {/* Subtle background glow on hover */}
        <div className="absolute inset-0 bg-gradient-radial from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl" />

        {/* Number - editorial style */}
        <span className="relative z-10 text-5xl md:text-6xl font-extralight text-white/[0.08] group-hover:text-amber-500/15 transition-colors duration-500">
          {pillar.id}
        </span>

        {/* Icon */}
        <div className="relative z-10 mt-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/15 flex items-center justify-center group-hover:scale-105 group-hover:border-amber-500/25 transition-all duration-500">
            <Icon className="w-6 h-6 text-amber-400/80" weight="regular" />
          </div>
        </div>

        {/* Content */}
        <h3 className="relative z-10 text-xl md:text-2xl font-light text-white group-hover:text-amber-100 transition-colors duration-300 mb-2">
          {pillar.title}
        </h3>

        <p className="relative z-10 text-sm text-white/35 group-hover:text-white/50 transition-colors duration-300 leading-relaxed">
          {pillar.desc}
        </p>
      </div>
    </motion.div>
  )
}

const SevenPillars = () => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section ref={ref} id="curriculum" className="py-32 md:py-40 bg-[#050505] relative">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">

        {/* Header - consistent styling */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-20 md:mb-24"
        >
          <div className="inline-flex items-center gap-3 mb-8">
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-amber-500/50" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-amber-400/60 font-medium">
              The Framework
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-amber-500/50" />
          </div>

          <h2 className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight mb-6">
            Seven pillars of{' '}
            <span className="bg-gradient-to-r from-amber-200 via-amber-100 to-amber-200 bg-clip-text text-transparent">
              strategic clarity
            </span>
          </h2>

          <p className="text-lg md:text-xl text-white/35 max-w-2xl mx-auto">
            The complete positioning framework. Answer these seven questions,
            and chaos transforms into strategic focus.
          </p>
        </motion.div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-5">
          {pillars.map((pillar, index) => (
            <PillarCard key={pillar.id} pillar={pillar} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}

export default SevenPillars

