"use client";

import React, { useState } from "react";
import { motion, AnimatePresence, useInView } from "framer-motion";
import { useRef } from "react";
import {
  Coffee,
  Lightbulb,
  PenTool,
  Calendar,
  BarChart3,
  Zap,
  CheckCircle2,
  ArrowRight,
  Clock,
  Target,
  Sparkles,
  TrendingUp,
  Users,
  ChevronRight,
  Play,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// Features Workflow - Minimalist, personality-driven, depth-filled
// ═══════════════════════════════════════════════════════════════

const workflows = [
  {
    id: "morning",
    label: "Morning Ritual",
    icon: Coffee,
    time: "5 min",
    headline: "Know before you sip",
    subtext: "Your daily briefing while the coffee brews",
    color: "from-amber-500/20 to-orange-500/20",
    glow: "amber-500",
    features: [
      {
        icon: BarChart3,
        title: "What worked yesterday",
        subtitle: "Pipeline Analytics",
        description: "See which post drove actual revenue. Not likes. Actual money.",
        stat: "Revenue, not vanity",
      },
      {
        icon: TrendingUp,
        title: "Your momentum",
        subtitle: "Performance Snapshot",
        description: "One glance. All platforms. No spreadsheet gymnastics.",
        stat: "One view, zero tabs",
      },
      {
        icon: Target,
        title: "Are you on track?",
        subtitle: "Goal Tracking",
        description: "Weekly targets, monthly goals, yearly vision—all in one place.",
        stat: "Always know",
      },
    ],
  },
  {
    id: "strategy",
    label: "Strategize",
    icon: Lightbulb,
    time: "10 min",
    headline: "Let AI do the thinking",
    subtext: "Strategy that used to take days, now takes minutes",
    color: "from-violet-500/20 to-purple-500/20",
    glow: "violet-500",
    features: [
      {
        icon: Sparkles,
        title: "Your 90-day war plan",
        subtitle: "AI Strategy Engine",
        description: "Generated from your goals, your audience, your voice. Not generic templates.",
        stat: "Personalized, not templated",
      },
      {
        icon: Users,
        title: "Who you're talking to",
        subtitle: "ICP Profiler",
        description: "Deep customer profiles from real data. Stop marketing to everyone.",
        stat: "Targeted, not scattered",
      },
      {
        icon: Zap,
        title: "What competitors miss",
        subtitle: "Market Intelligence",
        description: "Spot opportunities they're sleeping on. Move first.",
        stat: "First mover advantage",
      },
    ],
  },
  {
    id: "create",
    label: "Create",
    icon: PenTool,
    time: "15 min",
    headline: "Write like you, faster",
    subtext: "Your voice, amplified. Not a robot pretending to be you.",
    color: "from-emerald-500/20 to-teal-500/20",
    glow: "emerald-500",
    features: [
      {
        icon: PenTool,
        title: "It learns your voice",
        subtitle: "Brand Voice AI",
        description: "Trained on your best work. Sounds like you because it IS you.",
        stat: "Authentic, not generic",
      },
      {
        icon: Sparkles,
        title: "One click, many formats",
        subtitle: "Multi-Format Generator",
        description: "Posts, threads, carousels, long-form. One brief, endless variations.",
        stat: "10x faster",
      },
      {
        icon: CheckCircle2,
        title: "Will this land?",
        subtitle: "Impact Scoring",
        description: "Real-time feedback before you hit publish. Post with confidence.",
        stat: "Data-backed confidence",
      },
    ],
  },
  {
    id: "schedule",
    label: "Ship It",
    icon: Calendar,
    time: "5 min",
    headline: "Set it and forget it",
    subtext: "Your content, scheduled when your audience is actually watching",
    color: "from-blue-500/20 to-cyan-500/20",
    glow: "blue-500",
    features: [
      {
        icon: Clock,
        title: "Perfect timing, automatic",
        subtitle: "Smart Scheduler",
        description: "Posts when YOUR audience is most active. Not generic 'best times'.",
        stat: "Audience-optimized",
      },
      {
        icon: Zap,
        title: "Write once, publish everywhere",
        subtitle: "Cross-Platform Publisher",
        description: "LinkedIn, Twitter, threads—each optimized for the platform.",
        stat: "One to many",
      },
      {
        icon: Calendar,
        title: "See the whole picture",
        subtitle: "Content Calendar",
        description: "Visual timeline. No gaps. No surprises. Just consistent presence.",
        stat: "Never miss a day",
      },
    ],
  },
];

const allFeatures = [
  { name: "Pipeline Analytics", category: "Analytics", emoji: "📊" },
  { name: "AI Strategy Engine", category: "Strategy", emoji: "🧠" },
  { name: "Brand Voice AI", category: "Creation", emoji: "✍️" },
  { name: "Smart Scheduler", category: "Publishing", emoji: "⏰" },
  { name: "ICP Profiler", category: "Strategy", emoji: "🎯" },
  { name: "Performance Snapshot", category: "Analytics", emoji: "📈" },
  { name: "Content Generator", category: "Creation", emoji: "⚡" },
  { name: "Cross-Platform Publisher", category: "Publishing", emoji: "🚀" },
  { name: "Goal Tracking", category: "Analytics", emoji: "🎖️" },
  { name: "Market Intelligence", category: "Strategy", emoji: "🔍" },
  { name: "Impact Scoring", category: "Creation", emoji: "💎" },
  { name: "Content Calendar", category: "Publishing", emoji: "📅" },
  { name: "Data Privacy", category: "Security", emoji: "🔒" },
  { name: "Team Workspace", category: "Collaboration", emoji: "👥" },
  { name: "Integrations Hub", category: "Connect", emoji: "🔌" },
];

export function FeaturesWorkflow() {
  const [activeTab, setActiveTab] = useState("morning");
  const [showAllFeatures, setShowAllFeatures] = useState(false);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const activeWorkflow = workflows.find((w) => w.id === activeTab);

  return (
    <section ref={ref} id="features" className="py-32 md:py-40 bg-[var(--canvas)]">
      <div className="max-w-6xl mx-auto px-6">
        {/* Section Header - Minimalist */}
        <div className="mb-20">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm tracking-[0.2em] text-[var(--muted)] mb-4"
          >
            The Workflow
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-editorial mb-6"
          >
            35 minutes.<br />
            <span className="text-[var(--muted)]">From chaos to shipped.</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg text-[var(--secondary)] max-w-xl"
          >
            No more context switching. No more tool juggling. Just four simple rituals that transform your marketing from a burden into a superpower.
          </motion.p>
        </div>

        {/* Tab Navigation - Minimal Pill Style */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-wrap gap-2 mb-16"
        >
          {workflows.map((workflow) => (
            <button
              key={workflow.id}
              onClick={() => setActiveTab(workflow.id)}
              className={`group relative px-6 py-3 rounded-full text-sm font-medium transition-all duration-300 ${
                activeTab === workflow.id
                  ? "bg-[var(--ink)] text-[var(--canvas)]"
                  : "bg-[var(--surface)] text-[var(--secondary)] hover:text-[var(--ink)]"
              }`}
            >
              <span className="flex items-center gap-2">
                <workflow.icon className="w-4 h-4" />
                {workflow.label}
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  activeTab === workflow.id
                    ? "bg-[var(--canvas)]/20 text-[var(--canvas)]"
                    : "bg-[var(--canvas)] text-[var(--muted)]"
                }`}>
                  {workflow.time}
                </span>
              </span>
            </button>
          ))}
        </motion.div>

        {/* Active Workflow Content */}
        <AnimatePresence mode="wait">
          {activeWorkflow && (
            <motion.div
              key={activeWorkflow.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            >
              {/* Workflow Header */}
              <div className="mb-12">
                <h3 className="text-3xl font-editorial mb-3">{activeWorkflow.headline}</h3>
                <p className="text-lg text-[var(--muted)]">{activeWorkflow.subtext}</p>
              </div>

              {/* Features Grid - Minimal Cards with Depth */}
              <div className="grid md:grid-cols-3 gap-6">
                {activeWorkflow.features.map((feature, i) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                    className="group relative"
                  >
                    <div className="relative p-8 bg-[var(--surface)] rounded-2xl border border-[var(--border)] hover:border-[var(--ink)]/30 transition-all duration-500 hover:shadow-xl hover:shadow-[var(--ink)]/5">
                      {/* Gradient Glow on Hover */}
                      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${activeWorkflow.color} opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10 blur-xl`} />

                      {/* Icon */}
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${activeWorkflow.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                        <feature.icon className="w-6 h-6 text-[var(--ink)]" />
                      </div>

                      {/* Content */}
                      <p className="text-xs text-[var(--muted)] uppercase tracking-wider mb-2">{feature.subtitle}</p>
                      <h4 className="text-xl font-editorial mb-3">{feature.title}</h4>
                      <p className="text-[var(--secondary)] text-sm leading-relaxed mb-4">{feature.description}</p>

                      {/* Stat Badge */}
                      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[var(--canvas)] rounded-full">
                        <Zap className="w-3 h-3 text-[var(--ink)]" />
                        <span className="text-xs font-medium">{feature.stat}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Total Time Summary - Minimal */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-20 pt-12 border-t border-[var(--border)]"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">
            <div>
              <p className="text-5xl md:text-6xl font-editorial mb-2">35 min</p>
              <p className="text-[var(--muted)]">That's your entire marketing workflow. What used to take a week.</p>
            </div>
            <div className="flex gap-4">
              <div className="text-right">
                <p className="text-2xl font-editorial">15+ hrs</p>
                <p className="text-sm text-[var(--muted)]">Before</p>
              </div>
              <div className="text-[var(--muted)] text-2xl">→</div>
              <div className="text-right">
                <p className="text-2xl font-editorial text-green-600">35 min</p>
                <p className="text-sm text-[var(--muted)]">With RaptorFlow</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* All Features Toggle - Minimal */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="mt-16 text-center"
        >
          <button
            onClick={() => setShowAllFeatures(!showAllFeatures)}
            className="group inline-flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
          >
            {showAllFeatures ? "Hide" : "Explore"} all capabilities
            <ChevronRight className={`w-4 h-4 transition-transform ${showAllFeatures ? "rotate-90" : "group-hover:translate-x-1"}`} />
          </button>
        </motion.div>

        {/* All Features Grid */}
        <AnimatePresence>
          {showAllFeatures && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.4 }}
              className="mt-8 overflow-hidden"
            >
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {allFeatures.map((feature, i) => (
                  <motion.div
                    key={feature.name}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: i * 0.02 }}
                    className="group p-4 bg-[var(--surface)] rounded-xl hover:bg-[var(--ink)] hover:text-[var(--canvas)] transition-all duration-300 cursor-pointer"
                  >
                    <span className="text-2xl mb-2 block">{feature.emoji}</span>
                    <p className="font-medium text-sm">{feature.name}</p>
                    <p className="text-xs text-[var(--muted)] group-hover:text-[var(--canvas)]/60 mt-1">{feature.category}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
