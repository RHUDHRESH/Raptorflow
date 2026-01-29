"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import {
  Compass,
  Target,
  Sparkles,
  BarChart3,
  CheckCircle2
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// Product Demo Section - Interactive UI Showcase
// ═══════════════════════════════════════════════════════════════

const demoScreens = [
  {
    id: "positioning",
    label: "Positioning",
    icon: Compass,
    title: "Define Your ICP",
    description: "Build detailed ideal customer profiles from real data and interviews.",
    features: ["ICP Canvas", "Value Proposition Matrix", "Competitive Positioning"],
  },
  {
    id: "strategy",
    label: "Strategy",
    icon: Target,
    title: "90-Day War Plans",
    description: "Get complete marketing strategies with weekly moves and content themes.",
    features: ["AI Strategy Engine", "Weekly Move Planner", "Growth Experiments"],
  },
  {
    id: "content",
    label: "Content",
    icon: Sparkles,
    title: "AI Content Creation",
    description: "Generate on-brand content that sounds like you, not a robot.",
    features: ["Brand Voice Training", "Multi-Platform Posts", "Thread Generator"],
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: BarChart3,
    title: "Pipeline Analytics",
    description: "Track which content drives actual revenue, not just vanity metrics.",
    features: ["Attribution Tracking", "Revenue Insights", "Content Performance"],
  },
];

export function ProductDemo() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [activeTab, setActiveTab] = useState(0);

  return (
    <section ref={ref} className="py-32 md:py-40 bg-[var(--paper)]">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-6"
          >
            Product Tour
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-editorial mb-4"
          >
            See how it works
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg text-[var(--secondary)] max-w-2xl mx-auto"
          >
            Four integrated modules. One powerful workflow.
          </motion.p>
        </div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-wrap justify-center gap-2 mb-12"
        >
          {demoScreens.map((screen, i) => (
            <button
              key={screen.id}
              onClick={() => setActiveTab(i)}
              className={`flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all ${
                activeTab === i
                  ? "bg-[var(--ink)] text-[var(--canvas)]"
                  : "bg-[var(--surface)] text-[var(--secondary)] hover:text-[var(--ink)]"
              }`}
            >
              <screen.icon className="w-4 h-4" />
              {screen.label}
            </button>
          ))}
        </motion.div>

        {/* Demo Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="grid lg:grid-cols-2 gap-12 items-center"
          >
            {/* UI Mockup */}
            <div className="relative">
              {/* Browser Frame */}
              <div className="bg-[var(--ink)] rounded-2xl p-4 shadow-2xl">
                {/* Browser Header */}
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                  </div>
                  <div className="flex-1 bg-[var(--canvas)]/10 rounded-md py-1 px-3 text-xs text-[var(--canvas)]/60 text-center">
                    app.raptorflow.io/{demoScreens[activeTab].id}
                  </div>
                </div>

                {/* App Content */}
                <div className="bg-[var(--canvas)] rounded-xl p-6 min-h-[400px]">
                  {/* Mock UI Content */}
                  <div className="flex items-center gap-4 mb-6 pb-4 border-b border-[var(--border)]">
                    <div className="w-10 h-10 bg-[var(--ink)] rounded-lg flex items-center justify-center">
                      {React.createElement(demoScreens[activeTab].icon, {
                        className: "w-5 h-5 text-[var(--canvas)]"
                      })}
                    </div>
                    <div>
                      <h3 className="font-semibold">{demoScreens[activeTab].title}</h3>
                      <p className="text-sm text-[var(--muted)]">{demoScreens[activeTab].description}</p>
                    </div>
                  </div>

                  {/* Mock Dashboard Content */}
                  <div className="space-y-4">
                    <div className="h-32 bg-[var(--surface)] rounded-lg flex items-center justify-center">
                      <span className="text-[var(--muted)] text-sm">Interactive Dashboard Preview</span>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="h-20 bg-[var(--surface)] rounded-lg" />
                      <div className="h-20 bg-[var(--surface)] rounded-lg" />
                      <div className="h-20 bg-[var(--surface)] rounded-lg" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Badge */}
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="absolute -right-4 top-1/4 bg-white rounded-xl shadow-xl p-4 border border-[var(--border)]"
              >
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="text-sm font-medium">Strategy Generated</span>
                </div>
              </motion.div>
            </div>

            {/* Feature List */}
            <div>
              <h3 className="text-3xl font-editorial mb-4">
                {demoScreens[activeTab].title}
              </h3>
              <p className="text-lg text-[var(--secondary)] mb-8">
                {demoScreens[activeTab].description}
              </p>

              <ul className="space-y-4">
                {demoScreens[activeTab].features.map((feature, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center gap-3"
                  >
                    <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                    </div>
                    <span className="font-medium">{feature}</span>
                  </motion.li>
                ))}
              </ul>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}
