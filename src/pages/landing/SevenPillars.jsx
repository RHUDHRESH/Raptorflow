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
  // Create visual interest with varied spans
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
      <div className="h-full p-6 md:p-8 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-amber-500/30 transition-all duration-500 overflow-hidden hover:shadow-[0_0_60px_rgba(245,158,11,0.08)]">

        {/* Background glow on hover */}
        <div className="absolute inset-0 bg-gradient-radial from-amber-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl" />

        {/* Number */}
        <span className="relative z-10 text-4xl md:text-5xl font-light text-white/10 group-hover:text-amber-500/20 transition-colors duration-500">
          {pillar.id}
        </span>

        {/* Icon */}
        <div className="relative z-10 mt-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/20 flex items-center justify-center group-hover:scale-110 group-hover:border-amber-500/40 transition-all duration-500">
            <Icon className="w-6 h-6 text-amber-400" weight="duotone" />
          </div>
        </div>

        {/* Content */}
        <h3 className="relative z-10 text-xl md:text-2xl font-light text-white group-hover:text-amber-100 transition-colors duration-300 mb-2">
          {pillar.title}
        </h3>

        <p className="relative z-10 text-sm text-white/40 group-hover:text-white/60 transition-colors duration-300 leading-relaxed">
          {pillar.desc}
        </p>

        {/* Corner accent */}
        <div className="absolute -bottom-8 -right-8 w-24 h-24 rounded-full bg-gradient-radial from-amber-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 blur-xl" />
      </div>
    </motion.div>
  )
}

const SevenPillars = () => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section ref={ref} id="curriculum" className="py-32 relative">
      {/* Background elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-radial from-amber-500/5 to-transparent blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-gradient-radial from-orange-500/5 to-transparent blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-6">
            <span className="w-8 h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent" />
            The Framework
            <span className="w-8 h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent" />
          </span>

          <h2 className="text-5xl md:text-6xl font-light text-white leading-tight mb-6">
            Seven pillars of
            <span className="block italic bg-gradient-to-r from-amber-300 via-amber-400 to-orange-400 text-transparent bg-clip-text">
              strategic clarity
            </span>
          </h2>

          <p className="text-lg text-white/40 max-w-2xl mx-auto">
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
