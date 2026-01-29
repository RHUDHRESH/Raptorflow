"use client";

import React from "react";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Compass, Target, Zap } from "lucide-react";
import { GradientOrb } from "../effects/GradientOrb";

// ═══════════════════════════════════════════════════════════════
// Solution Section - Introducing the product
// ═══════════════════════════════════════════════════════════════

const pillars = [
  {
    icon: Compass,
    title: "Positioning",
    description: "Clear ICP definition and value proposition that actually resonates.",
  },
  {
    icon: Target,
    title: "Strategy",
    description: "90-day war plans with weekly moves, not monthly hopes.",
  },
  {
    icon: Zap,
    title: "Execution",
    description: "AI-powered content creation that sounds like you, not a robot.",
  },
];

export function SolutionSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} id="features" className="py-32 md:py-40 relative overflow-hidden bg-[var(--paper)]">
      {/* Background */}
      <GradientOrb color="ocean" size="lg" className="top-0 right-0 opacity-50" />

      <div className="max-w-6xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-20">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-6"
          >
            The Solution
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-6xl font-editorial leading-[1.1] mb-6"
          >
            Meet your Marketing OS
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-[var(--secondary)] max-w-2xl mx-auto"
          >
            Three integrated modules. One unified workflow.
            From strategy to scheduled content in minutes, not days.
          </motion.p>
        </div>

        {/* Three Pillars */}
        <div className="grid md:grid-cols-3 gap-8">
          {pillars.map((pillar, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + i * 0.15 }}
              className="group relative p-8 bg-[var(--canvas)] rounded-2xl border border-[var(--border)] hover:border-[var(--ink)] transition-all duration-300"
            >
              {/* Icon */}
              <div className="w-14 h-14 bg-[var(--ink)] text-[var(--canvas)] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <pillar.icon className="w-7 h-7" />
              </div>

              {/* Content */}
              <h3 className="text-2xl font-editorial mb-3">{pillar.title}</h3>
              <p className="text-[var(--secondary)] leading-relaxed">
                {pillar.description}
              </p>

              {/* Hover Number */}
              <span className="absolute top-6 right-6 text-6xl font-editorial text-[var(--border)] group-hover:text-[var(--structure)] transition-colors">
                0{i + 1}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Bottom Statement */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-16 text-center"
        >
          <p className="text-lg text-[var(--muted)]">
            Everything you need. Nothing you do not.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
