"use client";

import React from "react";
import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { TextReveal } from "../effects/TextReveal";

// ═══════════════════════════════════════════════════════════════
// Problem Section - The pain point, emotionally resonant
// ═══════════════════════════════════════════════════════════════

export function ProblemSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const problems = [
    "15 hours a week on marketing tasks",
    "6 different tools that don't talk",
    "Posting without a strategy",
    "Zero pipeline from 6 months of content",
  ];

  return (
    <section ref={ref} className="py-32 md:py-40 relative overflow-hidden">
      <div className="max-w-5xl mx-auto px-6">
        {/* Section Label */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6 }}
          className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-12"
        >
          The Problem
        </motion.p>

        {/* Main Statement */}
        <div className="mb-16">
          <h2 className="text-3xl md:text-5xl lg:text-6xl font-editorial leading-[1.15] mb-8">
            <TextReveal once>
              You did not start a company to spend your days fighting with AI prompts and social media schedulers.
            </TextReveal>
          </h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-xl md:text-2xl text-[var(--muted)] max-w-3xl"
          >
            Tool sprawl is the silent killer of founder-led growth.
            Six months of posting. Zero pipeline. Sound familiar?
          </motion.p>
        </div>

        {/* Problem Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {problems.map((problem, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={isInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.5 + i * 0.1 }}
              className="flex items-start gap-4 p-6 bg-[var(--surface)] rounded-xl border border-[var(--border)]"
            >
              <span className="text-[var(--muted)] text-2xl">×</span>
              <p className="text-lg text-[var(--secondary)]">{problem}</p>
            </motion.div>
          ))}
        </div>

        {/* Bottom Statement */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.9 }}
          className="mt-16 p-8 bg-[var(--ink)] text-[var(--canvas)] rounded-2xl"
        >
          <p className="text-2xl md:text-3xl font-editorial leading-relaxed">
            The problem is not your effort. It is your architecture.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
