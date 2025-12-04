import React from 'react'
import { ReactLenis } from 'lenis/react'
import Header from './landing/Header'
import Footer from './landing/Footer'
import CustomCursor from '../components/CustomCursor'
import SevenPillars from './landing/SevenPillars'
import IntegrationGrid from './landing/IntegrationGrid'
import { motion } from 'framer-motion'

const Product = () => {
  return (
    <ReactLenis root>
      <div className="min-h-screen bg-canvas antialiased font-sans selection:bg-gold/30 relative">
        <CustomCursor />
        
        {/* Texture Overlay */}
        <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03] mix-blend-multiply" 
             style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '120px' }} />

        <Header />
        
        <main className="pt-32 pb-20 relative z-10">
          <div className="px-6 md:px-12 max-w-7xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-20"
          >
            {/* Hero Section */}
            <section className="text-center space-y-6">
              <span className="text-xs uppercase tracking-[0.3em] text-gold font-medium">The Engine</span>
              <h1 className="font-serif text-6xl md:text-8xl text-charcoal">
                Precision <span className="italic text-aubergine">Engineering</span>
              </h1>
              <p className="text-xl text-charcoal/60 max-w-2xl mx-auto font-light leading-relaxed">
                Raptorflow isn't just a dashboard. It's a methodology codified into software.
                Designed to force clarity and eliminate strategic drift.
              </p>
            </section>

            {/* Feature 1: The Matrix */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center py-20 border-t border-charcoal/10">
              <div className="space-y-6">
                <h2 className="font-serif text-4xl text-charcoal">The Strategy Matrix</h2>
                <p className="text-charcoal/70 text-lg leading-relaxed">
                  Most founders drown in tasks. The Matrix forces you to choose 3-5 strategic bets. 
                  If it doesn't fit in the grid, it doesn't happen.
                </p>
                <ul className="space-y-3 text-sm uppercase tracking-widest text-charcoal/50 pt-4">
                  <li className="flex items-center gap-3">
                    <span className="w-1.5 h-1.5 bg-gold rounded-full"></span>
                    Constraint-based Planning
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="w-1.5 h-1.5 bg-gold rounded-full"></span>
                    Visual Trade-offs
                  </li>
                </ul>
              </div>
              <div className="aspect-square bg-charcoal/5 rounded-3xl border border-charcoal/10 overflow-hidden relative group">
                 <div className="absolute inset-0 bg-gradient-to-br from-transparent to-charcoal/10"></div>
                 {/* Abstract Representation of Matrix */}
                 <div className="absolute inset-10 grid grid-cols-2 gap-4 opacity-50 group-hover:opacity-100 transition-opacity duration-700">
                    <div className="bg-white rounded-lg shadow-sm"></div>
                    <div className="bg-white rounded-lg shadow-sm"></div>
                    <div className="bg-white rounded-lg shadow-sm"></div>
                    <div className="bg-charcoal/20 rounded-lg border-2 border-dashed border-charcoal/30"></div>
                 </div>
              </div>
            </section>

            {/* Feature 2: The Brief */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center py-20 border-t border-charcoal/10 md:flex-row-reverse">
               <div className="aspect-square bg-aubergine/5 rounded-3xl border border-aubergine/10 relative overflow-hidden order-2 md:order-1">
                  <div className="absolute inset-0 flex items-center justify-center text-aubergine/20 font-serif text-9xl italic">Aa</div>
               </div>
              <div className="space-y-6 order-1 md:order-2">
                <h2 className="font-serif text-4xl text-charcoal">Muse-Grade Briefs</h2>
                <p className="text-charcoal/70 text-lg leading-relaxed">
                  Stop writing boring documents. Our editor is designed for high-stakes creativity.
                  Minimalist, focused, and beautiful enough to present directly to investors.
                </p>
              </div>
            </section>

            <section className="border-t border-charcoal/10 pt-20">
                <SevenPillars />
            </section>

            <section className="py-20">
                <IntegrationGrid />
            </section>

          </motion.div>
          </div>
        </main>

        <Footer />
      </div>
    </ReactLenis>
  )
}

export default Product
