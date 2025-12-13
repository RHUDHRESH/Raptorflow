import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { clsx } from 'clsx'

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null)

  const faqs = [
    {
      q: "Do I need a marketing team to use this?",
      a: "No. Raptorflow is built specifically for founders and small teams. The moves are designed to be high-leverage and low-overhead, so you can execute them yourself or delegate easily."
    },
    {
      q: "Is this just another AI content generator?",
      a: "Absolutely not. Raptorflow is a strategy OS. While we use AI to accelerate the grunt work (drafting briefs, repurposing assets), the core value is the 7-pillar strategic framework that ensures you're building the right things."
    },
    {
      q: "What happens after 90 days?",
      a: "Marketing is a cycle. After 90 days, you review your Matrix, kill what didn't work, double down on what did, and generate a fresh 90-day war map for the next quarter."
    },
    {
      q: "Can I export the briefs?",
      a: "Yes. All briefs, plans, and assets can be exported to a PDF so you can share them with freelancers or your team."
    }
  ]

  return (
    <section className="py-24 border-b border-line bg-canvas relative">
      <div className="max-w-3xl mx-auto px-6 md:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className="font-serif text-4xl md:text-5xl text-charcoal mb-4">Common questions.</h2>
          <p className="text-charcoal/60 font-sans">Everything you need to know before diving in.</p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, i) => (
            <div 
              key={i} 
              className="border border-line rounded-2xl bg-white/40 backdrop-blur-sm overflow-hidden transition-all duration-300 hover:border-aubergine/30"
            >
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-6 text-left group"
              >
                <span className="font-serif text-lg text-charcoal group-hover:text-aubergine transition-colors pr-8">
                  {faq.q}
                </span>
                <div className={clsx("w-8 h-8 rounded-full border border-charcoal/10 flex items-center justify-center transition-all duration-300", 
                  openIndex === i ? "bg-aubergine text-canvas rotate-180" : "bg-transparent text-charcoal/40 group-hover:border-aubergine group-hover:text-aubergine"
                )}>
                  <ChevronDown className="w-4 h-4" />
                </div>
              </button>
              
              <AnimatePresence>
                {openIndex === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: [0.04, 0.62, 0.23, 0.98] }}
                  >
                    <div className="px-6 pb-6 pt-0">
                      <p className="text-sm text-charcoal/70 leading-relaxed font-sans font-light border-t border-line/50 pt-4">
                        {faq.a}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default FAQ
