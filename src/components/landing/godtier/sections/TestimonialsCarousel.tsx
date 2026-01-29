"use client";

import React, { useState } from "react";
import { motion, AnimatePresence, useInView } from "framer-motion";
import { useRef } from "react";
import { ChevronLeft, ChevronRight, Quote } from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// Testimonials Carousel - Social proof with customer quotes
// ═══════════════════════════════════════════════════════════════

const testimonials = [
  {
    quote: "RaptorFlow helped us 3x our inbound pipeline in 60 days. The AI actually understands our ICP and creates content that converts.",
    author: "Sarah Chen",
    role: "CEO, TechStart AI",
    company: "YC W23",
  },
  {
    quote: "I went from spending 20 hours a week on marketing to 4 hours. The strategy module alone is worth 10x the price.",
    author: "Marcus Johnson",
    role: "Founder, GrowthLabs",
    company: "Bootstrapped to $2M ARR",
  },
  {
    quote: "Finally, a marketing tool built for founders who actually want results, not just vanity metrics.",
    author: "Emily Rodriguez",
    role: "Co-founder, SaaScale",
    company: "Series A",
  },
  {
    quote: "The brand voice training is incredible. Our posts sound like me, not some generic AI output.",
    author: "David Kim",
    role: "Solo Founder",
    company: "Indie Hackers",
  },
];

export function TestimonialsCarousel() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [current, setCurrent] = useState(0);

  const next = () => setCurrent((prev) => (prev + 1) % testimonials.length);
  const prev = () => setCurrent((prev) => (prev - 1 + testimonials.length) % testimonials.length);

  return (
    <section ref={ref} className="py-32 md:py-40">
      <div className="max-w-5xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-6"
          >
            Testimonials
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-editorial"
          >
            Loved by founders
          </motion.h2>
        </div>

        {/* Testimonial Carousel */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="relative"
        >
          {/* Quote Icon */}
          <Quote className="absolute -top-4 -left-4 w-12 h-12 text-[var(--border)]" />

          {/* Content */}
          <div className="relative bg-[var(--surface)] rounded-2xl p-8 md:p-12 min-h-[300px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={current}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="flex flex-col justify-center h-full"
              >
                {/* Quote */}
                <p className="text-2xl md:text-3xl font-editorial leading-relaxed mb-8">
                  &ldquo;{testimonials[current].quote}&rdquo;
                </p>

                {/* Author */}
                <div>
                  <p className="font-semibold text-lg">{testimonials[current].author}</p>
                  <p className="text-[var(--secondary)]">{testimonials[current].role}</p>
                  <p className="text-sm text-[var(--muted)]">{testimonials[current].company}</p>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Navigation */}
            <div className="absolute bottom-8 right-8 flex gap-2">
              <button
                onClick={prev}
                className="w-10 h-10 rounded-full border border-[var(--border)] flex items-center justify-center hover:border-[var(--ink)] transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={next}
                className="w-10 h-10 rounded-full border border-[var(--border)] flex items-center justify-center hover:border-[var(--ink)] transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Dots */}
          <div className="flex justify-center gap-2 mt-6">
            {testimonials.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrent(i)}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  i === current ? "bg-[var(--ink)] w-6" : "bg-[var(--border)]"
                }`}
              />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
