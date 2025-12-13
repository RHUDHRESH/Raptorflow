import React, { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import heroAscent from '../../../assets/artwork/hero-ascent.png'
import raptorVision from '../../../assets/artwork/raptor-vision.png'
import flightPattern from '../../../assets/artwork/flight-pattern.png'
import diveSequence from '../../../assets/artwork/dive-sequence.png'

const FeatureCard = ({ title, category, description, image, index }) => {
  return (
    <div className="flex-shrink-0 w-[85vw] md:w-[60vw] h-[80vh] bg-zinc-900 relative overflow-hidden group mx-4 md:mx-8 border border-white/5">
      <div className="absolute inset-0 bg-cover bg-center transition-transform duration-[1.5s] ease-out group-hover:scale-105" 
           style={{ backgroundImage: `url(${image})` }}>
        <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors duration-700" />
      </div>
      
      <div className="absolute bottom-0 left-0 w-full p-8 md:p-16 bg-gradient-to-t from-black/90 via-black/50 to-transparent">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div>
            <span className="inline-block px-3 py-1 border border-white/30 rounded-full text-xs uppercase tracking-widest mb-6 backdrop-blur-md">
              0{index + 1} — {category}
            </span>
            <h3 className="text-4xl md:text-6xl font-serif text-white mb-4 leading-none">
              {title}
            </h3>
            <p className="max-w-md text-zinc-300 font-light text-lg leading-relaxed">
              {description}
            </p>
          </div>
          
          <button className="w-16 h-16 rounded-full border border-white/30 flex items-center justify-center group-hover:bg-white group-hover:text-black transition-all duration-300">
            <span className="text-2xl">→</span>
          </button>
        </div>
      </div>
    </div>
  )
}

const PremiumFeatures = () => {
  const targetRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: targetRef,
  })

  const x = useTransform(scrollYProgress, [0, 1], ["0%", "-75%"])

  const features = [
    {
      title: "Orchestration",
      category: "Planning",
      description: "Map your entire marketing strategy on a unified canvas. Connect the dots between intuition and execution.",
      image: heroAscent
    },
    {
      title: "Deep Radar",
      category: "Analytics",
      description: "See what others miss. Our sensor fusion technology aggregates signals from every channel into one clear picture.",
      image: raptorVision
    },
    {
      title: "Flight Path",
      category: "Automation",
      description: "Automate the routine. Focus on the creative. Let the system handle the turbulence of daily operations.",
      image: flightPattern
    },
    {
      title: "Precision Strike",
      category: "Execution",
      description: "Launch campaigns with confidence. Real-time feedback loops ensure your message lands exactly where intended.",
      image: diveSequence
    }
  ]

  return (
    <section ref={targetRef} className="relative h-[400vh] bg-background">
      <div className="sticky top-0 flex h-screen items-center overflow-hidden">
        <motion.div style={{ x }} className="flex pl-8 md:pl-24">
          
          {/* Intro Card */}
          <div className="flex-shrink-0 w-[40vw] md:w-[30vw] h-[80vh] flex flex-col justify-center pr-12 md:pr-24">
            <h2 className="text-accent text-sm uppercase tracking-[0.2em] mb-8">The Collection</h2>
            <p className="text-5xl md:text-7xl font-serif leading-none mb-8">
              Tools for <br />
              <span className="italic text-zinc-500">Modern</span> <br />
              Warlords
            </p>
            <p className="text-zinc-400 font-light leading-relaxed">
              A suite of precision instruments designed to give you an unfair advantage in the marketplace.
            </p>
          </div>

          {features.map((feature, i) => (
            <FeatureCard key={i} index={i} {...feature} />
          ))}
          
        </motion.div>
      </div>
    </section>
  )
}

export default PremiumFeatures
