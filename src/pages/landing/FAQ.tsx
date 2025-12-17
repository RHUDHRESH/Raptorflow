import React, { useState, useRef } from 'react'
import { motion, AnimatePresence, useInView } from 'framer-motion'

/* ═══════════════════════════════════════════════════════════════════════════
   FAQ - Fixed dark theme styling to match rest of landing page
   ═══════════════════════════════════════════════════════════════════════════ */

// Nanobana-style chevron
const ChevronIcon = ({ className = '', isOpen = false }) => (
  <svg viewBox="0 0 16 16" fill="none" className={`${className} transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}>
    <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

// Search icon
const SearchIcon = () => (
  <svg viewBox="0 0 20 20" className="w-5 h-5" fill="none">
    <circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.5" />
    <path d="M14 14L18 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

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
      q: "What happens after 30 days?",
      a: "Your plan expires gracefully. You can renew anytime to continue. Marketing is a cycle—after each period, review your Matrix, kill what didn't work, and generate a fresh battle plan."
    },
    {
      q: "Can I export the briefs?",
      a: "Yes. All briefs, plans, and assets can be exported to PDF so you can share them with freelancers or your team."
    },
    {
      q: "How is this different from a marketing agency?",
      a: "Agencies operate on retainers and often lack context. Raptorflow is your always-on strategic partner that learns your business, operates at your speed, and costs a fraction of agency fees."
    },
    {
      q: "What if I'm already using other marketing tools?",
      a: "Raptorflow integrates seamlessly. We connect with Slack, Linear, and more. Your existing tools feed into our unified command center."
    },
    {
      q: "Can multiple team members use the same account?",
      a: "Yes! Glide plans support 3 team members, and Soar plans support up to 10. Each member gets their own login and can collaborate on campaigns."
    },
    {
      q: "Is there a money-back guarantee?",
      a: "We offer a 7-day satisfaction guarantee. If Raptorflow isn't the right fit, contact us within the first week for a full refund."
    }
  ]

  // Filter FAQs based on search query
  const filteredFaqs = faqs.filter(faq =>
    faq.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.a.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <section id="faq" ref={sectionRef} className="relative py-32 md:py-40 bg-[#050505] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

        {/* Subtle dot pattern */}
        <svg className="absolute inset-0 w-full h-full opacity-[0.03]" preserveAspectRatio="xMidYMid slice">
          <defs>
            <pattern id="faq-dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
              <circle cx="20" cy="20" r="1" fill="#FFFFFF" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#faq-dots)" />
        </svg>
      </div>

      <div className="max-w-3xl mx-auto px-6 md:px-12 relative z-10">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="inline-flex items-center gap-3 mb-8"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-white/20" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-white/60 font-medium">
              Questions
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-white/20" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-4xl md:text-5xl font-light text-white tracking-tight"
          >
            Common questions
          </motion.h2>
        </div>

        {/* Search filter */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="mb-10"
        >
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30">
              <SearchIcon />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search questions..."
              className="w-full pl-12 pr-4 py-4 bg-zinc-900/40 border border-white/[0.06] rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:border-white/20 transition-colors"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
              >
                <svg viewBox="0 0 16 16" className="w-4 h-4" fill="none">
                  <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            )}
          </div>
        </motion.div>

        {/* FAQ items */}
        <div className="space-y-4">
          {filteredFaqs.length === 0 ? (
            <div className="text-center py-12 text-white/40">
              No questions match your search. Try a different term.
            </div>
          ) : (
            filteredFaqs.map((faq, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.2 + i * 0.05, duration: 0.5 }}
                className="group"
              >
                <div
                  className={`
                    border rounded-xl overflow-hidden transition-all duration-300
                    ${openIndex === i
                      ? 'bg-zinc-900/60 border-white/20'
                      : 'bg-zinc-900/40 border-white/[0.06] hover:border-white/[0.12]'
                    }
                  `}
                >
                  <button
                    onClick={() => setOpenIndex(openIndex === i ? null : i)}
                    className="w-full flex items-center justify-between p-6 text-left"
                  >
                    <span className={`
                      text-lg font-light pr-8 transition-colors duration-300
                      ${openIndex === i ? 'text-white' : 'text-white/70 group-hover:text-white'}
                    `}>
                      {faq.q}
                    </span>
                    <div className={`
                      w-8 h-8 rounded-full border flex items-center justify-center flex-shrink-0 transition-all duration-300
                      ${openIndex === i
                        ? 'bg-white/10 border-white/20 text-white/70'
                        : 'border-white/10 text-white/40 group-hover:border-white/20'
                      }
                    `}>
                      <ChevronIcon className="w-4 h-4" isOpen={openIndex === i} />
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
                        <div className="px-6 pb-6">
                          <div className="pt-2 border-t border-white/[0.06]">
                            <p className="text-white/50 leading-relaxed pt-4">
                              {faq.a}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>
            ))
          )}
        </div>

        {/* Contact CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="mt-16 text-center"
        >
          <div className="p-8 bg-zinc-900/40 border border-white/[0.06] rounded-2xl">
            <h3 className="text-xl font-light text-white mb-3">Still have questions?</h3>
            <p className="text-white/40 mb-6">
              Can't find what you're looking for? Our team is here to help.
            </p>
            <a
              href="mailto:hello@raptorflow.com"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/[0.05] border border-white/10 rounded-xl text-white/70 hover:text-white hover:border-white/20 transition-all text-sm"
            >
              <svg viewBox="0 0 20 20" className="w-4 h-4" fill="none">
                <rect x="2" y="4" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" />
                <path d="M2 6L10 11L18 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              <span>Contact Support</span>
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default FAQ
