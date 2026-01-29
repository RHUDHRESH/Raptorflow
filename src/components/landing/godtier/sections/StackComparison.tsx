"use client";

import React, { useState } from "react";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import {
  X,
  Check,
  ArrowRight,
  Clock,
  DollarSign,
  Layers,
  AlertCircle,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// Stack Comparison - Minimalist, personality-driven, depth-filled
// ═══════════════════════════════════════════════════════════════

const comparisons = [
  {
    category: "Strategy",
    old: {
      tools: ["Notion", "Sheets", "Docs"],
      time: "4 hrs/week",
      pain: "Ideas scattered everywhere",
    },
    new: {
      tools: ["AI Strategy Engine"],
      time: "30 min/week",
      benefit: "One unified plan",
    },
  },
  {
    category: "Creation",
    old: {
      tools: ["ChatGPT", "Canva", "Copy.ai"],
      time: "6 hrs/week",
      pain: "Generic, needs heavy editing",
    },
    new: {
      tools: ["Brand Voice AI"],
      time: "1 hr/week",
      benefit: "Sounds like you instantly",
    },
  },
  {
    category: "Publishing",
    old: {
      tools: ["Buffer", "Hootsuite"],
      time: "3 hrs/week",
      pain: "Manual scheduling nightmare",
    },
    new: {
      tools: ["Smart Publisher"],
      time: "15 min/week",
      benefit: "Optimal timing, automatic",
    },
  },
  {
    category: "Analytics",
    old: {
      tools: ["Analytics", "Excel", "Native"],
      time: "2 hrs/week",
      pain: "Data everywhere, insights nowhere",
    },
    new: {
      tools: ["Pipeline Dashboard"],
      time: "15 min/week",
      benefit: "Revenue attribution clear",
    },
  },
];

const savings = [
  { label: "Time saved", before: "15 hrs/week", after: "2 hrs/week", percent: "87%" },
  { label: "Monthly cost", before: "$160+/mo", after: "$49/mo", percent: "69%" },
  { label: "Tool count", before: "10+ tools", after: "1 platform", percent: "90%" },
];

export function StackComparison() {
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="py-32 md:py-40 bg-[var(--paper)]">
      <div className="max-w-5xl mx-auto px-6">
        {/* Section Header - Minimalist */}
        <div className="mb-16">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm tracking-[0.2em] text-[var(--muted)] mb-4"
          >
            The Reality
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-editorial mb-6"
          >
            Stop paying<br />
            <span className="text-[var(--muted)]">the tool tax.</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg text-[var(--secondary)] max-w-xl"
          >
            Ten tools. Ten logins. Ten bills. Zero integration.
            Or one platform that actually works as a team.
          </motion.p>
        </div>

        {/* Savings Summary - Minimal Cards */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="grid md:grid-cols-3 gap-4 mb-16"
        >
          {savings.map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.4 + i * 0.1 }}
              className="group p-6 bg-[var(--canvas)] rounded-2xl border border-[var(--border)] hover:border-[var(--ink)]/20 transition-all duration-300"
            >
              <p className="text-sm text-[var(--muted)] mb-4">{item.label}</p>
              <div className="flex items-baseline gap-3 mb-2">
                <span className="text-lg text-[var(--muted)] line-through">{item.before}</span>
                <ArrowRight className="w-4 h-4 text-[var(--muted)]" />
                <span className="text-2xl font-editorial">{item.after}</span>
              </div>
              <span className="inline-flex items-center px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                Save {item.percent}
              </span>
            </motion.div>
          ))}
        </motion.div>

        {/* Comparison Table - Minimal with Depth */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="bg-[var(--canvas)] rounded-3xl border border-[var(--border)] overflow-hidden"
        >
          {/* Table Header */}
          <div className="grid grid-cols-2 gap-px bg-[var(--border)]">
            <div className="p-6 md:p-8 bg-[var(--canvas)]">
              <p className="text-sm text-red-500 font-medium mb-1">Your current stack</p>
              <p className="text-2xl font-editorial">10+ tools, scattered</p>
            </div>
            <div className="p-6 md:p-8 bg-[var(--canvas)]">
              <p className="text-sm text-green-600 font-medium mb-1">With RaptorFlow</p>
              <p className="text-2xl font-editorial">One platform, unified</p>
            </div>
          </div>

          {/* Table Rows */}
          <div className="divide-y divide-[var(--border)]">
            {comparisons.map((comp, i) => {
              const isHovered = hoveredRow === i;
              return (
                <motion.div
                  key={comp.category}
                  initial={{ opacity: 0, x: -20 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.4, delay: 0.6 + i * 0.1 }}
                  className="grid grid-cols-2 gap-px bg-[var(--border)] group"
                  onMouseEnter={() => setHoveredRow(i)}
                  onMouseLeave={() => setHoveredRow(null)}
                >
                  {/* Old Stack */}
                  <div className={`p-6 md:p-8 bg-[var(--canvas)] transition-all duration-300 ${isHovered ? "bg-red-50/50" : ""}`}>
                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <X className="w-4 h-4 text-red-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium mb-1">{comp.category}</p>
                        <p className="text-sm text-[var(--muted)] mb-3">{comp.old.tools.join(" → ")}</p>
                        <div className="flex items-center gap-2 text-xs">
                          <Clock className="w-3 h-3 text-red-400" />
                          <span className="text-red-500">{comp.old.time}</span>
                        </div>
                        {isHovered && (
                          <motion.p
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-xs text-red-500 mt-3"
                          >
                            {comp.old.pain}
                          </motion.p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* New Stack */}
                  <div className={`p-6 md:p-8 bg-[var(--canvas)] transition-all duration-300 ${isHovered ? "bg-green-50/50" : ""}`}>
                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Check className="w-4 h-4 text-green-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium mb-1">{comp.category}</p>
                        <p className="text-sm text-[var(--muted)] mb-3">{comp.new.tools[0]}</p>
                        <div className="flex items-center gap-2 text-xs">
                          <Clock className="w-3 h-3 text-green-500" />
                          <span className="text-green-600">{comp.new.time}</span>
                        </div>
                        {isHovered && (
                          <motion.p
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-xs text-green-600 mt-3"
                          >
                            {comp.new.benefit}
                          </motion.p>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Table Footer - Total */}
          <div className="grid grid-cols-2 gap-px bg-[var(--border)]">
            <div className="p-6 md:p-8 bg-red-50/30">
              <p className="text-sm text-[var(--muted)] mb-1">Total cost of chaos</p>
              <p className="text-3xl font-editorial text-red-600">$160+/mo</p>
              <p className="text-sm text-red-500 mt-1">Plus 15+ hours of your life</p>
            </div>
            <div className="p-6 md:p-8 bg-green-50/30">
              <p className="text-sm text-[var(--muted)] mb-1">RaptorFlow investment</p>
              <p className="text-3xl font-editorial text-green-600">$49/mo</p>
              <p className="text-sm text-green-600 mt-1">2 hours, done</p>
            </div>
          </div>
        </motion.div>

        {/* Bottom CTA - Minimal */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 1 }}
          className="mt-16 text-center"
        >
          <div className="inline-flex items-center gap-4 px-8 py-4 bg-[var(--ink)] text-[var(--canvas)] rounded-full">
            <div className="text-left">
              <p className="text-sm text-[var(--canvas)]/60">Your annual savings</p>
              <p className="font-medium">$1,332 + 676 hours reclaimed</p>
            </div>
            <ArrowRight className="w-5 h-5" />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
