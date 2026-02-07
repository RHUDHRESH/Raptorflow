import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Minus } from 'lucide-react'

const FAQItem = ({ question, answer, isOpen, onClick }) => {
  return (
    <div 
      className="border-b border-white/5"
      onClick={onClick}
    >
      <button className="w-full py-6 flex items-start justify-between gap-4 text-left group">
        <span className={`text-lg font-light transition-colors duration-300 ${isOpen ? 'text-amber-200' : 'text-white/70 group-hover:text-white'}`}>
          {question}
        </span>
        <span className="mt-1 flex-shrink-0">
          {isOpen ? (
            <Minus className="w-4 h-4 text-amber-400" />
          ) : (
            <Plus className="w-4 h-4 text-white/30 group-hover:text-white/60" />
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
            <p className="pb-6 text-white/40 font-light leading-relaxed">
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
    <section className="relative py-32 md:py-40 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-black via-zinc-950 to-black" />
      </div>

      <div className="max-w-4xl mx-auto px-6 relative z-10">
        
        {/* Header */}
        <div className="text-center mb-16">
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-[10px] uppercase tracking-[0.4em] text-amber-400/60"
          >
            Questions
          </motion.span>
          
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mt-6 text-4xl md:text-5xl font-light text-white"
          >
            Frequently
            <span className="italic font-normal text-amber-200"> asked</span>
          </motion.h2>
        </div>

        {/* FAQs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
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
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="mt-16 text-center"
        >
          <p className="text-white/30 text-sm">
            Still have questions?{' '}
            <a href="mailto:hello@raptorflow.com" className="text-amber-400/60 hover:text-amber-400 transition-colors">
              Get in touch
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default FAQ
