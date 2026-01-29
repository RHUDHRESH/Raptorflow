"use client";

import React from "react";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { AnimatedCounter } from "../effects/AnimatedCounter";

// ═══════════════════════════════════════════════════════════════
// Social Proof Bar - Trust indicators and stats
// ═══════════════════════════════════════════════════════════════

const stats = [
  { value: 500, suffix: "+", label: "Founders onboarded" },
  { value: 50, suffix: "K+", label: "Posts generated" },
  { value: 98, suffix: "%", label: "Customer satisfaction" },
  { value: 4.9, suffix: "/5", label: "Average rating" },
];

const logos = [
  "Product Hunt",
  "Indie Hackers",
  "YC",
  "Techstars",
  "500 Global",
];

export function SocialProof() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="py-20 border-y border-[var(--border)] bg-[var(--surface)]">
      <div className="max-w-7xl mx-auto px-6">
        {/* Trusted By Text */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          className="text-center text-sm uppercase tracking-[0.2em] text-[var(--muted)] mb-12"
        >
          Trusted by founders from
        </motion.p>

        {/* Logos */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="flex flex-wrap justify-center items-center gap-8 md:gap-16 mb-16"
        >
          {logos.map((logo, i) => (
            <span
              key={i}
              className="text-lg font-medium text-[var(--muted)] hover:text-[var(--ink)] transition-colors cursor-default"
            >
              {logo}
            </span>
          ))}
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-12 border-t border-[var(--border)]">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.2 + i * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-editorial mb-2">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  duration={2}
                />
              </div>
              <p className="text-sm text-[var(--muted)]">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
