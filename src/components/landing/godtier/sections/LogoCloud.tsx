"use client";

import React, { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Star, Award, TrendingUp } from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// Logo Cloud / Trust Bar - Infinite scrolling marquee with trust indicators
// ═══════════════════════════════════════════════════════════════

interface LogoCategory {
  label: string;
  logos: string[];
}

const categories: LogoCategory[] = [
  {
    label: "Backed by",
    logos: ["Y Combinator", "Techstars", "500 Global", "Sequoia", "Accel", "A16z"],
  },
  {
    label: "Featured in",
    logos: ["TechCrunch", "Product Hunt", "Forbes", "Wired", "The Verge", "Bloomberg"],
  },
  {
    label: "Trusted by",
    logos: ["Notion", "Figma", "Linear", "Vercel", "Stripe", "OpenAI", "Anthropic", "Supabase"],
  },
];

// G2 Rating Data
const g2Data = {
  rating: 4.9,
  reviews: "2,400+",
  badge: "High Performer",
  category: "Winter 2026",
};

// Marquee Row Component with infinite scroll
function MarqueeRow({
  items,
  direction = "left",
  speed = 30,
  isInView
}: {
  items: string[];
  direction?: "left" | "right";
  speed?: number;
  isInView: boolean;
}) {
  // Duplicate items for seamless loop
  const duplicatedItems = [...items, ...items, ...items];

  return (
    <div className="relative overflow-hidden py-4 group">
      {/* Gradient masks for smooth edges */}
      <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-[var(--canvas)] to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-[var(--canvas)] to-transparent z-10 pointer-events-none" />

      <motion.div
        className="flex gap-12 items-center"
        animate={isInView ? {
          x: direction === "left" ? ["0%", "-33.33%"] : ["-33.33%", "0%"],
        } : {}}
        transition={{
          duration: speed,
          ease: "linear",
          repeat: Infinity,
          repeatType: "loop",
        }}
      >
        {duplicatedItems.map((item, index) => (
          <div
            key={`${item}-${index}`}
            className="flex-shrink-0 px-6 py-3 rounded-xl border-2 border-[var(--border)] bg-[var(--surface)]
                       grayscale hover:grayscale-0 transition-all duration-500 cursor-pointer
                       hover:border-[var(--ink)] hover:shadow-lg group/logo"
          >
            <span className="text-lg font-medium text-[var(--ink-secondary)] group-hover/logo:text-[var(--ink)] whitespace-nowrap">
              {item}
            </span>
          </div>
        ))}
      </motion.div>
    </div>
  );
}

// G2 Badge Component
function G2Badge() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: 0.4 }}
      className="flex flex-col sm:flex-row items-center justify-center gap-6 mt-16 pt-12 border-t border-[var(--border)]"
    >
      {/* G2 Logo and Rating */}
      <div className="flex items-center gap-4">
        <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-[var(--surface)] border-2 border-[var(--border)]">
          <span className="text-2xl font-bold text-[var(--ink)]">G2</span>
        </div>
        <div>
          <div className="flex items-center gap-1 mb-1">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-5 h-5 ${
                  i < Math.floor(g2Data.rating)
                    ? "fill-amber-400 text-amber-400"
                    : "text-[var(--border)]"
                }`}
              />
            ))}
          </div>
          <p className="text-sm text-[var(--muted)]">
            <span className="font-semibold text-[var(--ink)]">{g2Data.rating}</span>/5 from {g2Data.reviews} reviews
          </p>
        </div>
      </div>

      {/* Divider */}
      <div className="hidden sm:block w-px h-12 bg-[var(--border)]" />

      {/* Badge */}
      <div className="flex items-center gap-3 px-5 py-3 rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-200">
        <Award className="w-6 h-6 text-amber-600" />
        <div>
          <p className="text-sm font-semibold text-amber-800">{g2Data.badge}</p>
          <p className="text-xs text-amber-600">{g2Data.category}</p>
        </div>
      </div>

      {/* Trend indicator */}
      <div className="flex items-center gap-2 text-emerald-600">
        <TrendingUp className="w-5 h-5" />
        <span className="text-sm font-medium">Top 5% in category</span>
      </div>
    </motion.div>
  );
}

// Main Logo Cloud Component
export function LogoCloud() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section
      ref={ref}
      className="py-24 md:py-32 bg-[var(--canvas)] overflow-hidden"
    >
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          {/* Label */}
          <span className="inline-block px-4 py-1.5 mb-6 text-xs font-medium uppercase tracking-[0.2em] text-[var(--muted)] bg-[var(--surface)] border border-[var(--border)] rounded-full">
            Social Proof
          </span>

          {/* Headline */}
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-editorial font-medium text-[var(--ink)] mb-4">
            Trusted by founders at companies of all sizes
          </h2>

          {/* Subheadline */}
          <p className="text-lg text-[var(--secondary)] max-w-2xl mx-auto">
            From pre-seed startups to Fortune 500s, the world's most ambitious teams choose us.
          </p>
        </motion.div>

        {/* Logo Marquees */}
        <div className="space-y-8">
          {categories.map((category, index) => (
            <motion.div
              key={category.label}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 * (index + 1) }}
            >
              {/* Category Label */}
              <div className="flex items-center gap-4 mb-4">
                <span className="text-sm font-medium text-[var(--muted)] uppercase tracking-wider">
                  {category.label}
                </span>
                <div className="flex-1 h-px bg-[var(--border)]" />
              </div>

              {/* Marquee - alternate directions for visual interest */}
              <MarqueeRow
                items={category.logos}
                direction={index % 2 === 0 ? "left" : "right"}
                speed={35 + index * 5}
                isInView={isInView}
              />
            </motion.div>
          ))}
        </div>

        {/* G2 Badge Section */}
        <G2Badge />

        {/* Bottom trust indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-12 flex flex-wrap justify-center gap-8 text-center"
        >
          {[
            { value: "SOC 2", label: "Type II Certified" },
            { value: "GDPR", label: "Compliant" },
            { value: "99.9%", label: "Uptime SLA" },
          ].map((item, i) => (
            <div key={i} className="px-6 py-3 rounded-xl bg-[var(--surface)] border border-[var(--border)]">
              <p className="text-lg font-semibold text-[var(--ink)]">{item.value}</p>
              <p className="text-xs text-[var(--muted)] uppercase tracking-wider">{item.label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

export default LogoCloud;
