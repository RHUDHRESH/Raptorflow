import React, { useState, useRef } from 'react'
import { motion, AnimatePresence, useInView } from 'framer-motion'
import { Plus, Minus } from 'lucide-react'

const FAQItem = ({ question, answer, isOpen, onClick }) => {
  return (
    <div
      className="border-b border-white/[0.05]"
      onClick={onClick}
    >
      <button className="w-full py-6 flex items-start justify-between gap-4 text-left group">
        <span className={`text-lg font-light transition-colors duration-300 ${isOpen ? 'text-amber-200' : 'text-white/60 group-hover:text-white/80'}`}>
          {question}
        </span>
        <span className="mt-1 flex-shrink-0">
          {isOpen ? (
            <Minus className="w-4 h-4 text-amber-400/70" />
          ) : (
            <Plus className="w-4 h-4 text-white/25 group-hover:text-white/50" />
          )}
        </span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <p className="pb-6 text-white/35 font-light leading-relaxed">
              {answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(0)
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  const faqs = [
    {
      question: "Is this a course or a software tool?",
      answer: "Both. Raptorflow is a strategic methodology delivered through an interactive platform. You get the frameworks, the AI-powered planning tools, and a system that turns your inputs into a precise 90-day execution plan. Think of it as a strategy consultant meets productivity tool."
    },
    {
      question: "What if I'm just starting out?",
      answer: "Even better. Most founders waste their first 6-12 months on scattered tactics. Raptorflow helps you cut through that noise from day one. The methodology works whether you're pre-revenue or scaling to your next million."
    },
    {
      question: "How long does it take to complete?",
      answer: "The core intake takes 1-2 hours of focused time. Your first war map is generated immediately. Most founders iterate 2-3 times over the first week before locking in their plan. Then it's execution mode."
    },
    {
      question: "What's the refund policy?",
      answer: "7 days, no questions asked. If Raptorflow doesn't help you see your path forward with clarity, we'll refund you completely. We believe in the methodology—but we also believe in making this risk-free for you."
    },
    {
      question: "Do I get lifetime access?",
      answer: "Access duration depends on your plan. Ascent includes 30 days of methodology library access, Glide includes 90 days, and Soar includes lifetime access to all current and future updates."
    },
    {
      question: "Can I upgrade later?",
      answer: "Absolutely. Pay the difference and upgrade anytime. All your existing work and war maps carry over."
    },
    {
      question: "What industries does this work for?",
      answer: "Raptorflow is industry-agnostic. The 7-pillar methodology works for SaaS, DTC, services, marketplaces, and anything where you need to go from idea to execution. We've had founders in fintech, healthtech, edtech, and beyond."
    }
  ]

  return (
    <section ref={sectionRef} className="relative py-32 md:py-40 bg-[#030303] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />
      </div>

      <div className="max-w-4xl mx-auto px-6 md:px-12 relative z-10">

        {/* Header - consistent styling */}
        <div className="text-center mb-16 md:mb-20">
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="inline-flex items-center gap-3 mb-8"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-amber-500/50" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-amber-400/60 font-medium">
              Questions
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-amber-500/50" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight"
          >
            Frequently{' '}
            <span className="bg-gradient-to-r from-amber-200 via-amber-100 to-amber-200 bg-clip-text text-transparent">
              asked
            </span>
          </motion.h2>
        </div>

        {/* FAQs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          {faqs.map((faq, index) => (
            <FAQItem
              key={index}
              question={faq.question}
              answer={faq.answer}
              isOpen={openIndex === index}
              onClick={() => setOpenIndex(openIndex === index ? -1 : index)}
            />
          ))}
        </motion.div>

        {/* Contact CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-16 text-center"
        >
          <p className="text-white/25 text-sm">
            Still have questions?{' '}
            <a href="mailto:hello@raptorflow.com" className="text-amber-400/50 hover:text-amber-400/70 transition-colors">
              Get in touch
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default FAQ

