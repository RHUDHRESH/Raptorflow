"use client";

import React from "react";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Upload, Settings, Rocket } from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// How It Works - Simple 3-step process
// ═══════════════════════════════════════════════════════════════

const steps = [
  {
    number: "01",
    icon: Upload,
    title: "Upload Your Context",
    description: "Share your positioning, ICP research, and brand voice samples. Our AI learns what makes you unique.",
    duration: "5 minutes",
  },
  {
    number: "02",
    icon: Settings,
    title: "Generate Your Strategy",
    description: "Get a complete 90-day marketing plan with weekly moves, content themes, and growth experiments.",
    duration: "2 minutes",
  },
  {
    number: "03",
    icon: Rocket,
    title: "Execute & Optimize",
    description: "Create, schedule, and publish content. Track what works and let AI improve your strategy weekly.",
    duration: "Ongoing",
  },
];

export function HowItWorks() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} id="how-it-works" className="py-32 md:py-40 bg-[var(--ink)] text-[var(--canvas)]">
      <div className="max-w-6xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-20">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-6"
          >
            How It Works
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-6xl font-editorial mb-6"
          >
            From zero to launched in 20 minutes
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-[var(--muted)] max-w-2xl mx-auto"
          >
            No complex setup. No learning curve. Just results.
          </motion.p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Line */}
          <div className="absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[var(--muted)] to-transparent hidden md:block" />

          <div className="grid md:grid-cols-3 gap-12">
            {steps.map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 40 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.3 + i * 0.15 }}
                className="relative text-center"
              >
                {/* Number */}
                <span className="absolute -top-8 left-1/2 -translate-x-1/2 text-8xl font-editorial text-[var(--canvas)] opacity-5">
                  {step.number}
                </span>

                {/* Icon Circle */}
                <div className="relative z-10 w-20 h-20 mx-auto mb-8 bg-[var(--canvas)] text-[var(--ink)] rounded-full flex items-center justify-center">
                  <step.icon className="w-8 h-8" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-editorial mb-4">{step.title}</h3>
                <p className="text-[var(--muted)] mb-4 leading-relaxed">
                  {step.description}
                </p>
                <span className="inline-block px-3 py-1 bg-[var(--canvas)]/10 rounded-full text-sm text-[var(--muted)]">
                  {step.duration}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
