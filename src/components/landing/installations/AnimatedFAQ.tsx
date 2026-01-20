"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface FAQItem {
    q: string;
    a: string;
}

const FAQS: FAQItem[] = [
    { q: "How is RaptorFlow different from other marketing tools?", a: "RaptorFlow isn't a tool—it's an operating system. Others give you features in isolation. We connect strategy to execution in one unified workflow." },
    { q: "Do I need a marketing team?", a: "No. Built specifically for founders and lean teams. The system generates your weekly execution packets—no dedicated marketer needed." },
    { q: "What if I don't know my positioning yet?", a: "That's what Foundation is for. Our onboarding synthesizes your ICP, positioning, and 90-day plan in under 20 minutes." },
    { q: "How long until I see results?", a: "Most users ship their first Move within a week. Measurable pipeline impact typically shows within 4-6 weeks of consistent execution." }
];

function FAQCard({ item, index, isOpen, onToggle }: {
    item: FAQItem;
    index: number;
    isOpen: boolean;
    onToggle: () => void;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1 }}
            className="relative"
        >
            {/* Glow effect when open */}
            <motion.div
                className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-[var(--rf-coral)] via-[var(--rf-ocean)] to-[var(--rf-mint)] opacity-0 blur-lg"
                animate={{ opacity: isOpen ? 0.15 : 0 }}
                transition={{ duration: 0.3 }}
            />

            <motion.div
                className={`
                    relative p-6 rounded-xl border cursor-pointer overflow-hidden
                    transition-all duration-300
                    ${isOpen
                        ? "bg-[var(--canvas)] border-[var(--ink)] shadow-xl"
                        : "bg-[var(--canvas)] border-[var(--border)] hover:border-[var(--structure-strong)]"
                    }
                `}
                onClick={onToggle}
                whileHover={{ scale: isOpen ? 1 : 1.01 }}
                whileTap={{ scale: 0.99 }}
            >
                {/* Question */}
                <div className="flex items-start justify-between gap-4">
                    <h3 className={`text-lg font-bold transition-colors duration-300 ${isOpen ? "text-[var(--ink)]" : "text-[var(--ink)]"}`}>
                        {item.q}
                    </h3>

                    {/* Animated toggle icon */}
                    <motion.div
                        className="flex-shrink-0 w-8 h-8 rounded-full border border-[var(--border)] flex items-center justify-center"
                        animate={{
                            backgroundColor: isOpen ? "var(--ink)" : "transparent",
                            borderColor: isOpen ? "var(--ink)" : "var(--border)"
                        }}
                    >
                        <motion.span
                            className={`text-xl font-light leading-none transition-colors ${isOpen ? "text-[var(--canvas)]" : "text-[var(--ink)]"}`}
                            animate={{ rotate: isOpen ? 45 : 0 }}
                            transition={{ type: "spring", stiffness: 300, damping: 20 }}
                        >
                            +
                        </motion.span>
                    </motion.div>
                </div>

                {/* Answer with smooth expand */}
                <AnimatePresence>
                    {isOpen && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                            className="overflow-hidden"
                        >
                            <motion.p
                                initial={{ y: -10 }}
                                animate={{ y: 0 }}
                                exit={{ y: -10 }}
                                className="pt-4 text-[var(--secondary)] leading-relaxed border-t border-[var(--border)] mt-4"
                            >
                                {item.a}
                            </motion.p>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Animated underline indicator */}
                <motion.div
                    className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-[var(--rf-coral)] to-[var(--rf-ocean)]"
                    initial={{ width: "0%" }}
                    animate={{ width: isOpen ? "100%" : "0%" }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                />
            </motion.div>
        </motion.div>
    );
}

export default function AnimatedFAQ() {
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    return (
        <div className="space-y-4">
            {FAQS.map((item, i) => (
                <FAQCard
                    key={i}
                    item={item}
                    index={i}
                    isOpen={openIndex === i}
                    onToggle={() => setOpenIndex(openIndex === i ? null : i)}
                />
            ))}
        </div>
    );
}
