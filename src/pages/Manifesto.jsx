import React from 'react'
import { ReactLenis } from 'lenis/react'
import Header from './landing/Header'
import Footer from './landing/Footer'
import CustomCursor from '../components/CustomCursor'
import RevealText from '../components/RevealText'
import { motion, useScroll, useTransform } from 'framer-motion'

const Manifesto = () => {
  const { scrollYProgress } = useScroll()
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0.5])

  return (
    <ReactLenis root>
      <div className="min-h-screen bg-canvas antialiased font-sans selection:bg-gold/30 relative">
        <CustomCursor />
        <Header />
        
        {/* Texture Overlay */}
        <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.04] mix-blend-multiply" 
             style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '120px' }} />

        <main className="relative z-10 pt-40 pb-24 px-6 md:px-12 max-w-4xl mx-auto">
          
          {/* Header */}
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
            className="text-center mb-32"
          >
            <span className="text-xs uppercase tracking-[0.4em] text-gold font-medium block mb-6">
                <RevealText text="The Philosophy" />
            </span>
            <h1 className="font-serif text-6xl md:text-8xl lg:text-9xl text-charcoal leading-[0.9]">
              <RevealText text="Less," /><br />
              <span className="italic text-aubergine">
                <RevealText text="but better." delay={0.5} />
              </span>
            </h1>
          </motion.div>

          {/* Article Content */}
          <div className="prose prose-xl md:prose-2xl prose-charcoal mx-auto space-y-12 font-serif leading-relaxed">
            
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{ duration: 0.8 }}
            >
                <p className="text-2xl md:text-3xl font-sans font-light leading-relaxed text-charcoal/80 first-letter:text-7xl first-letter:font-serif first-letter:text-aubergine first-letter:float-left first-letter:mr-3 first-letter:mt-[-10px]">
                    Founders are drowning in advice. "Be everywhere." "Post daily." "Launch a podcast." "Run ads." The modern playbook is a recipe for burnout, not growth. It confuses motion with progress.
                </p>
            </motion.div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{ duration: 0.8 }}
                className="pl-6 md:pl-12 border-l-2 border-gold/30 italic text-charcoal/60 text-3xl md:text-4xl py-4 my-12"
            >
                "Strategy is not about what you do. It's about what you choose not to do."
            </motion.div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{ duration: 0.8 }}
            >
                <h3 className="text-3xl font-sans font-medium text-aubergine mt-16 mb-6">The Biological Limit</h3>
                <p className="font-sans font-light text-charcoal/70">
                    Your brain is not designed to hold 50 priorities. It can handle about three. Yet, most project management tools are designed to let you add infinite tickets, infinite tasks, infinite noise.
                </p>
                <p className="font-sans font-light text-charcoal/70 mt-6">
                    Raptorflow is an operating system built around biological constraints. We force you to pick 3-5 moves for a 90-day cycle. Not because the software can't handle more, but because <strong>you</strong> can't.
                </p>
            </motion.div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{ duration: 0.8 }}
            >
                <h3 className="text-3xl font-sans font-medium text-aubergine mt-16 mb-6">Deep Work vs. Shallow Work</h3>
                <p className="font-sans font-light text-charcoal/70">
                    Shallow work is answering emails, tweaking colors on a landing page, or checking analytics for the 10th time. Deep work is writing the sales letter that changes your trajectory.
                </p>
                <p className="font-sans font-light text-charcoal/70 mt-6">
                    Our interface is minimal by design. No notifications. No "team activity" feeds popping up. Just you, your strategy, and the execution. It is a quiet room in a noisy world.
                </p>
            </motion.div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{ duration: 0.8 }}
                className="pt-16 flex justify-center"
            >
                <div className="w-24 h-px bg-charcoal/20"></div>
            </motion.div>
          </div>

        </main>

        <Footer />
      </div>
    </ReactLenis>
  )
}

export default Manifesto
