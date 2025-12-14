import React from 'react'
import { ReactLenis } from 'lenis/react'
import Header from './landing/Header'
import Footer from './landing/Footer'
import CustomCursor from '../components/CustomCursor'
import TestimonialMarquee from './landing/TestimonialMarquee'
import FAQ from './landing/FAQ'
import { motion } from 'framer-motion'
import { Check, X } from 'lucide-react'

const Pricing = () => {
  const tiers = [
    {
      name: "Founder",
      price: "0",
      description: "For bootstrappers building in public.",
      features: ["Unlimited Strategy Matrices", "3 Active Briefs", "7-Day Analytics History", "Community Support"],
      cta: "Start Free",
      popular: false
    },
    {
      name: "Pro",
      price: "49",
      description: "For serious operators scaling to $1M.",
      features: ["Everything in Founder", "Unlimited Briefs", "Full Analytics History", "Priority Support", "Team Collaboration (up to 3)"],
      cta: "Go Pro",
      popular: true
    },
    {
      name: "Agency",
      price: "199",
      description: "For consultants managing multiple portfolios.",
      features: ["Everything in Pro", "Unlimited Clients", "White-label Reports", "Dedicated Account Manager", "API Access"],
      cta: "Contact Sales",
      popular: false
    }
  ]

  return (
    <ReactLenis root>
      <div className="min-h-screen bg-canvas antialiased font-sans selection:bg-gold/30 relative">
        <CustomCursor />
        
        {/* Texture Overlay */}
        <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03] mix-blend-multiply" 
             style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '120px' }} />

        <Header />
        
        <main className="pt-32 pb-20 px-6 md:px-12 max-w-7xl mx-auto relative z-10">
          <div className="text-center space-y-6 mb-20">
            <span className="text-xs uppercase tracking-[0.3em] text-gold font-medium">Investment</span>
            <h1 className="font-serif text-6xl md:text-8xl text-charcoal">
              Simple <span className="italic text-aubergine">Pricing</span>
            </h1>
            <p className="text-xl text-charcoal/60 max-w-2xl mx-auto font-light">
              Stop paying for tools you don't use. Start executing.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            {tiers.map((tier, index) => (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`relative p-8 rounded-3xl border ${tier.popular ? 'border-gold/50 bg-white shadow-2xl shadow-gold/10' : 'border-charcoal/10 bg-white/50 backdrop-blur-sm'} flex flex-col h-full`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gold text-canvas text-[10px] uppercase tracking-widest rounded-full font-medium">
                    Most Popular
                  </div>
                )}
                
                <div className="mb-8">
                  <h3 className="font-serif text-2xl text-charcoal mb-2">{tier.name}</h3>
                  <p className="text-sm text-charcoal/60 min-h-[40px]">{tier.description}</p>
                </div>

                <div className="mb-8 flex items-baseline gap-1">
                  <span className="text-4xl font-serif text-charcoal">${tier.price}</span>
                  <span className="text-charcoal/40">/mo</span>
                </div>

                <ul className="space-y-4 mb-8 flex-1">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm text-charcoal/70">
                      <Check className="w-4 h-4 text-gold shrink-0 mt-0.5" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <button className={`w-full py-4 rounded-full text-xs uppercase tracking-[0.2em] transition-all duration-300 ${tier.popular ? 'bg-charcoal text-canvas hover:bg-aubergine' : 'border border-charcoal/20 text-charcoal hover:border-charcoal'}`}>
                  {tier.cta}
                </button>
              </motion.div>
            ))}
          </div>
        </main>

        <div className="relative z-10">
            <TestimonialMarquee />
            <FAQ />
        </div>

        <Footer />
      </div>
    </ReactLenis>
  )
}

export default Pricing
