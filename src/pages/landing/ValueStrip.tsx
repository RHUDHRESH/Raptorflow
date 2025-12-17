import React, { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Target, Compass, Map, BarChart3, Rocket } from 'lucide-react'
import { BRAND_ICONS } from '@/components/brand/BrandSystem'

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
      <div className="w-12 h-12 border border-white/[0.06] bg-zinc-900/40 flex items-center justify-center group-hover:border-amber-500/20 transition-colors duration-500">
        <span className="text-[10px] text-white/30 font-mono">{number}</span>
      </div>
      <div className="w-px flex-1 bg-gradient-to-b from-white/[0.06] to-transparent" />
    </div>

    {/* Content */}
    <div className="pb-12">
      <div className="flex items-center gap-3 mb-3">
        <Icon className="w-5 h-5 text-amber-500/50" strokeWidth={1.5} />
        <h3 className="text-xl font-light text-white group-hover:text-amber-200 transition-colors duration-500">
          {title}
        </h3>
      </div>
      <p className="text-white/35 font-light leading-relaxed max-w-md">
        {description}
      </p>
    </div>
  </motion.div>
)

const ValueStrip = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

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
      icon: BRAND_ICONS.speed,
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
    <section ref={sectionRef} className="relative py-32 md:py-40 bg-background overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/5 to-transparent" />
      </div>

      <div className="max-w-6xl mx-auto px-6 md:px-12 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24">

          {/* Left - Header */}
          <div className="lg:sticky lg:top-32 lg:self-start">
            <motion.div
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              className="inline-flex items-center gap-3 mb-8"
            >
              <span className="w-12 h-px bg-gradient-to-r from-transparent to-primary/50" />
              <span className="text-caption text-primary">
                The Curriculum
              </span>
              <span className="w-12 h-px bg-gradient-to-l from-transparent to-primary/50" />
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1, duration: 0.7 }}
              className="text-display text-5xl md:text-6xl lg:text-7xl text-foreground leading-tight"
            >
              What you'll
              <br />
              <span className="italic text-primary">master</span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="mt-6 text-muted-foreground leading-relaxed max-w-md"
            >
              Six modules. One methodology. Complete strategic clarity in 90 days or less.
            </motion.p>

            <motion.div
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="mt-8 flex items-center gap-4"
            >
              <div className="flex -space-x-2">
                {['AM', 'PS', 'VS', 'RK'].map((initials, i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-full bg-primary/10 border-2 border-background flex items-center justify-center"
                  >
                    <span className="text-[8px] text-primary">{initials}</span>
                  </div>
                ))}
              </div>
              <span className="text-caption text-muted-foreground">Founders who ship, not spin 🚀</span>
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

