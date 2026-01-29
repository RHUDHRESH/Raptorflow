"use client";

import React from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Check } from "lucide-react";
import { MagneticButton } from "../effects/MagneticButton";

// ═══════════════════════════════════════════════════════════════
// Pricing God - Clear, compelling pricing section
// ═══════════════════════════════════════════════════════════════

const plans = [
  {
    name: "Starter",
    description: "For solo founders just getting started",
    price: 49,
    period: "/month",
    features: [
      "1 brand voice",
      "50 AI-generated posts/month",
      "Basic analytics",
      "LinkedIn & Twitter",
      "Email support",
    ],
    cta: "Start free trial",
    popular: false,
  },
  {
    name: "Growth",
    description: "For serious founders ready to scale",
    price: 99,
    period: "/month",
    features: [
      "3 brand voices",
      "Unlimited AI posts",
      "Advanced analytics",
      "All social platforms",
      "Priority support",
      "Strategy templates",
      "Weekly insights",
    ],
    cta: "Start free trial",
    popular: true,
  },
  {
    name: "Scale",
    description: "For teams managing multiple brands",
    price: 249,
    period: "/month",
    features: [
      "Unlimited brand voices",
      "Unlimited everything",
      "Custom integrations",
      "Dedicated account manager",
      "White-label options",
      "API access",
      "SLA guarantee",
    ],
    cta: "Contact sales",
    popular: false,
  },
];

export function PricingGod() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} id="pricing" className="py-32 md:py-40 bg-[var(--paper)]">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-6"
          >
            Pricing
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl font-editorial mb-4"
          >
            Simple, transparent pricing
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg text-[var(--secondary)]"
          >
            Start free for 14 days. No credit card required.
          </motion.p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + i * 0.1 }}
              className={`relative p-8 rounded-2xl border ${
                plan.popular
                  ? "bg-[var(--ink)] text-[var(--canvas)] border-[var(--ink)]"
                  : "bg-[var(--canvas)] border-[var(--border)]"
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-[var(--rf-coral)] text-[var(--ink)] text-xs font-semibold rounded-full">
                  Most Popular
                </span>
              )}

              {/* Plan Info */}
              <div className="mb-6">
                <h3 className="text-2xl font-editorial mb-2">{plan.name}</h3>
                <p className={`text-sm ${plan.popular ? "text-[var(--muted)]" : "text-[var(--secondary)]"}`}>
                  {plan.description}
                </p>
              </div>

              {/* Price */}
              <div className="mb-8">
                <span className="text-5xl font-editorial">${plan.price}</span>
                <span className={plan.popular ? "text-[var(--muted)]" : "text-[var(--secondary)]"}>
                  {plan.period}
                </span>
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-3">
                    <Check className={`w-5 h-5 flex-shrink-0 ${plan.popular ? "text-[var(--rf-coral)]" : "text-green-600"}`} />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <MagneticButton
                className={`w-full py-3 rounded-lg font-medium transition-all ${
                  plan.popular
                    ? "bg-[var(--canvas)] text-[var(--ink)] hover:bg-[var(--canvas)]/90"
                    : "bg-[var(--ink)] text-[var(--canvas)] hover:opacity-90"
                }`}
              >
                <Link href="/signup">{plan.cta}</Link>
              </MagneticButton>
            </motion.div>
          ))}
        </div>

        {/* Bottom Note */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="text-center mt-12 text-[var(--muted)]"
        >
          All plans include 14-day free trial. Cancel anytime.
        </motion.p>
      </div>
    </section>
  );
}
