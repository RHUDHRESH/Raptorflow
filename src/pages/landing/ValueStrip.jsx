import React from 'react'
import { motion } from 'framer-motion'
import { Target, Compass, Map, Zap, BarChart3, Rocket } from 'lucide-react'

// Curriculum item
const CurriculumItem = ({ number, icon: Icon, title, description, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.8 }}
    className="group relative flex gap-6"
  >
    {/* Number & line */}
    <div className="flex flex-col items-center">
      <div className="w-12 h-12 border border-white/10 bg-black flex items-center justify-center group-hover:border-amber-500/30 transition-colors duration-500">
        <span className="text-[10px] text-white/40 font-mono">{number}</span>
      </div>
      <div className="w-px flex-1 bg-gradient-to-b from-white/10 to-transparent" />
    </div>

    {/* Content */}
    <div className="pb-12">
      <div className="flex items-center gap-3 mb-3">
        <Icon className="w-5 h-5 text-amber-500/60" strokeWidth={1.5} />
        <h3 className="text-xl font-light text-white group-hover:text-amber-200 transition-colors duration-500">
          {title}
        </h3>
      </div>
      <p className="text-white/40 font-light leading-relaxed max-w-md">
        {description}
      </p>
    </div>
  </motion.div>
)

const ValueStrip = () => {
  const curriculum = [
    {
      icon: Target,
      title: "Define Your Hunting Ground",
      description: "Identify your exact target audience. No more 'everyone who needs X'. You'll know precisely who you're hunting and why they'll buy."
    },
    {
      icon: Compass,
      title: "Crystallize Your Position",
      description: "Extract your unique value proposition and competitive moat. The thing that makes copying you pointless."
    },
    {
      icon: Map,
      title: "Build Your 90-Day War Map",
      description: "Transform strategy into a visual execution plan. Every move mapped, every milestone clear, every week accounted for."
    },
    {
      icon: Zap,
      title: "Select Your Winning Moves",
      description: "Cut 37 random tactics down to 3-5 focused plays. The moves you can actually execute with your current resources."
    },
    {
      icon: BarChart3,
      title: "Track What Matters",
      description: "Set up your strategic dashboard. Know which metrics actually move the needle vs. vanity metrics that lie."
    },
    {
      icon: Rocket,
      title: "Execute With Precision",
      description: "Turn your plan into weekly sprints. The system that keeps you on track when chaos tries to pull you off course."
    }
  ]

  return (
    <section className="relative py-32 md:py-40 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-amber-950/10 to-transparent" />
      </div>

      <div className="max-w-6xl mx-auto px-6 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24">
          
          {/* Left - Header */}
          <div className="lg:sticky lg:top-32 lg:self-start">
            <motion.span
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-[10px] uppercase tracking-[0.4em] text-amber-400/60"
            >
              The Curriculum
            </motion.span>
            
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="mt-6 text-4xl md:text-5xl font-light text-white leading-tight"
            >
              What you'll
              <br />
              <span className="italic font-normal text-amber-200">master</span>
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="mt-6 text-white/40 font-light leading-relaxed max-w-md"
            >
              Six modules. One methodology. Complete strategic clarity in 90 days or less.
            </motion.p>

            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="mt-8 flex items-center gap-4"
            >
              <div className="flex -space-x-2">
                {['AM', 'PS', 'VS', 'RK'].map((initials, i) => (
                  <div 
                    key={i}
                    className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500/20 to-amber-700/20 border-2 border-black flex items-center justify-center"
                  >
                    <span className="text-[8px] text-amber-400">{initials}</span>
                  </div>
                ))}
              </div>
              <span className="text-xs text-white/40">500+ founders using Raptorflow</span>
            </motion.div>
          </div>

          {/* Right - Curriculum */}
          <div>
            {curriculum.map((item, index) => (
              <CurriculumItem
                key={index}
                number={String(index + 1).padStart(2, '0')}
                icon={item.icon}
                title={item.title}
                description={item.description}
                delay={index * 0.1}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

export default ValueStrip
