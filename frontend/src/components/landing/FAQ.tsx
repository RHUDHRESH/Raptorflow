"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowDown01Icon, ArrowUp01Icon } from "hugeicons-react";

const FAQ_ITEMS = [
    {
        question: "How is RaptorFlow different from other marketing tools?",
        answer: "RaptorFlow isn't a tool—it's a complete operating system. While others give you features in isolation (scheduling, analytics, AI writing), RaptorFlow connects your strategy to your execution in one unified workflow. You define your positioning once, and everything flows from there."
    },
    {
        question: "Do I need a marketing team to use this?",
        answer: "No. RaptorFlow is built specifically for founders and lean teams. The system generates your weekly execution packets, so you don't need a dedicated marketer. If you can write an email, you can use RaptorFlow."
    },
    {
        question: "What if I don't know my positioning or ICP yet?",
        answer: "That's exactly what Foundation is for. The onboarding asks you strategic questions and uses AI to synthesize your ideal customer profile, positioning, and 90-day plan. Most users complete it in under 20 minutes."
    },
    {
        question: "How long until I see results?",
        answer: "Most users ship their first marketing 'Move' within the first week. Measurable pipeline impact typically shows within 4-6 weeks of consistent execution. RaptorFlow is about compounding, not overnight virality."
    },
    {
        question: "Can I cancel anytime?",
        answer: "Yes. No contracts, no hidden fees. If RaptorFlow isn't delivering value, you can cancel with one click. We keep your data for 30 days in case you return."
    },
    {
        question: "What happens to my data?",
        answer: "Your data is yours. We use bank-level encryption, never sell your information, and you can export everything at any time. We only use your data to power your personal RaptorFlow experience."
    }
];

function FAQItem({ item, isOpen, onToggle }: { item: typeof FAQ_ITEMS[0]; isOpen: boolean; onToggle: () => void }) {
    return (
        <div className="border-b border-[var(--border)] last:border-b-0">
            <button
                onClick={onToggle}
                className="w-full py-6 flex items-center justify-between text-left group"
            >
                <span className="text-lg font-semibold text-[var(--ink)] group-hover:text-[var(--accent)] transition-colors pr-4">
                    {item.question}
                </span>
                <div className="flex-shrink-0 w-8 h-8 rounded-full border border-[var(--border)] group-hover:border-[var(--ink)] flex items-center justify-center transition-colors">
                    {isOpen
                        ? React.createElement(ArrowUp01Icon as any, { className: "w-4 h-4 text-[var(--ink)]" })
                        : React.createElement(ArrowDown01Icon as any, { className: "w-4 h-4 text-[var(--ink)]" })
                    }
                </div>
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        <p className="pb-6 text-[var(--secondary)] leading-relaxed max-w-3xl">
                            {item.answer}
                        </p>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export function FAQ() {
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    return (
        <section id="faq" className="py-24 md:py-32 bg-[var(--canvas)]">
            <div className="max-w-4xl mx-auto px-6">

                {/* Header */}
                <div className="text-center mb-16">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-block px-3 py-1 bg-[var(--surface)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--secondary)] mb-6"
                    >
                        Frequently Asked
                    </motion.div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-5xl font-editorial text-[var(--ink)]"
                    >
                        Questions? <span className="italic text-[var(--muted)]">Answered.</span>
                    </motion.h2>
                </div>

                {/* FAQ List */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="border border-[var(--border)] rounded-2xl bg-[var(--surface)] px-8"
                >
                    {FAQ_ITEMS.map((item, i) => (
                        <FAQItem
                            key={i}
                            item={item}
                            isOpen={openIndex === i}
                            onToggle={() => setOpenIndex(openIndex === i ? null : i)}
                        />
                    ))}
                </motion.div>
            </div>
        </section>
    );
}
