"use client";

import React, { useState } from "react";
import { motion, AnimatePresence, useInView } from "framer-motion";
import { useRef } from "react";
import { Plus, Minus } from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// FAQ Section - Accordion style FAQ
// ═══════════════════════════════════════════════════════════════

const faqs = [
  {
    question: "How is RaptorFlow different from other AI marketing tools?",
    answer: "Unlike generic AI tools that just generate content, RaptorFlow is a complete operating system. It starts with strategy—understanding your ICP and positioning—then creates content that actually converts. Everything is connected: strategy informs content, content drives analytics, and analytics improve strategy.",
  },
  {
    question: "Do I need marketing experience to use RaptorFlow?",
    answer: "Not at all. RaptorFlow is designed for founders who want results without becoming marketing experts. Our AI guides you through strategy creation, and the interface is built for busy founders who want to get in, get results, and get back to building.",
  },
  {
    question: "How does the AI learn my brand voice?",
    answer: "You provide samples of your best content—posts that performed well, emails that got replies, anything that sounds like you. Our AI analyzes tone, vocabulary, sentence structure, and creates a unique voice profile. Every piece of content then matches that voice.",
  },
  {
    question: "Can I connect my existing social media accounts?",
    answer: "Yes. RaptorFlow integrates with LinkedIn, Twitter/X, and more. You can schedule posts directly from the platform, and we will automatically post at optimal times based on your audience activity.",
  },
  {
    question: "What happens after the free trial?",
    answer: "After 14 days, you can choose a plan that fits your needs. There is no automatic billing—we will remind you before the trial ends. If you choose not to continue, you can export all your data.",
  },
  {
    question: "Is my data secure?",
    answer: "Absolutely. We use enterprise-grade encryption, never train our AI on your data, and comply with GDPR and CCPA. Your strategy, content, and customer data belong to you.",
  },
];

function FAQItem({ faq, index }: { faq: typeof faqs[0]; index: number }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="border-b border-[var(--border)]"
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full py-6 flex items-center justify-between text-left group"
      >
        <span className="text-lg font-medium pr-8 group-hover:text-[var(--secondary)] transition-colors">
          {faq.question}
        </span>
        <span className="flex-shrink-0 w-8 h-8 rounded-full border border-[var(--border)] flex items-center justify-center group-hover:border-[var(--ink)] transition-colors">
          {isOpen ? (
            <Minus className="w-4 h-4" />
          ) : (
            <Plus className="w-4 h-4" />
          )}
        </span>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <p className="pb-6 text-[var(--secondary)] leading-relaxed">
              {faq.answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function FAQSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} id="faq" className="py-32 md:py-40">
      <div className="max-w-3xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-6"
          >
            FAQ
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-editorial"
          >
            Questions? Answered.
          </motion.h2>
        </div>

        {/* FAQ List */}
        <div>
          {faqs.map((faq, i) => (
            <FAQItem key={i} faq={faq} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
