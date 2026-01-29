"use client";

import React from "react";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import {
  Brain,
  LineChart,
  FileText,
  Users,
  Sparkles,
  Clock,
  Shield,
  Workflow
} from "lucide-react";
import { GlowCard } from "../effects/GlowCard";

// ═══════════════════════════════════════════════════════════════
// Features Grid - Detailed feature showcase
// ═══════════════════════════════════════════════════════════════

const features = [
  {
    icon: Brain,
    title: "AI Strategy Engine",
    description: "Generates complete 90-day marketing plans based on your ICP, positioning, and business goals.",
    color: "rgba(224, 141, 121, 0.5)",
  },
  {
    icon: LineChart,
    title: "Pipeline Analytics",
    description: "Track which content drives actual revenue, not just vanity metrics.",
    color: "rgba(140, 169, 179, 0.5)",
  },
  {
    icon: FileText,
    title: "Content Generator",
    description: "Create on-brand posts, threads, and long-form content in your voice.",
    color: "rgba(156, 175, 152, 0.5)",
  },
  {
    icon: Users,
    title: "ICP Profiler",
    description: "Build detailed ideal customer profiles from real data and interviews.",
    color: "rgba(179, 165, 184, 0.5)",
  },
  {
    icon: Sparkles,
    title: "Brand Voice Training",
    description: "AI learns your unique voice from samples and stays consistent.",
    color: "rgba(224, 141, 121, 0.5)",
  },
  {
    icon: Clock,
    title: "Smart Scheduling",
    description: "Optimal post timing based on your audience activity patterns.",
    color: "rgba(140, 169, 179, 0.5)",
  },
  {
    icon: Shield,
    title: "Data Privacy",
    description: "Your data stays yours. Enterprise-grade security by default.",
    color: "rgba(156, 175, 152, 0.5)",
  },
  {
    icon: Workflow,
    title: "Integrations",
    description: "Connects with LinkedIn, Twitter, Slack, and your existing tools.",
    color: "rgba(179, 165, 184, 0.5)",
  },
];

export function FeaturesGrid() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="py-32 md:py-40">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-6"
          >
            Features
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-editorial mb-4"
          >
            Everything you need to win
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg text-[var(--secondary)]"
          >
            Powerful features. Simple interface. Designed for founders.
          </motion.p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.1 + i * 0.05 }}
            >
              <GlowCard glowColor={feature.color} className="h-full">
                <div className="p-6">
                  {/* Icon */}
                  <div className="w-12 h-12 bg-[var(--surface)] rounded-xl flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-[var(--ink)]" />
                  </div>

                  {/* Content */}
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-[var(--secondary)] leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </GlowCard>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
