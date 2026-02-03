"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { CheckCircle } from "lucide-react";

import { SectionWrapper, SectionHeader, ContentContainer } from "../shared/SectionWrapper";
import { fadeUp } from "../animations/presets";

// ═══════════════════════════════════════════════════════════════
// PricingV2 - Premium pricing cards
// ═══════════════════════════════════════════════════════════════

const PLANS = [
    {
        tier: "Ascent",
        price: "₹5,000",
        desc: "For founders getting started",
        features: [
            "Foundation setup",
            "3 weekly Moves",
            "Basic Muse AI",
            "Matrix analytics",
            "Email support",
        ],
    },
    {
        tier: "Glide",
        price: "₹7,000",
        desc: "For founders scaling up",
        features: [
            "Everything in Ascent",
            "Unlimited Moves",
            "Advanced Muse (voice training)",
            "Cohort segmentation",
            "Priority support",
            "Blackbox vault",
        ],
        popular: true,
    },
    {
        tier: "Soar",
        price: "₹10,000",
        desc: "For teams",
        features: [
            "Everything in Glide",
            "5 team seats",
            "Custom AI training",
            "API access",
            "Dedicated success manager",
        ],
    },
];

export function PricingV2() {
    return (
        <SectionWrapper id="pricing" variant="surface" bordered>
            <ContentContainer>
                <SectionHeader
                    eyebrow="Pricing"
                    title={
                        <>
                            Simple. Honest.{" "}
                            <span className="text-[var(--muted)]">No surprises.</span>
                        </>
                    }
                    subtitle="Start free. Upgrade when you're ready."
                    centered
                />

                {/* Pricing Grid */}
                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {PLANS.map((plan, i) => (
                        <motion.div
                            key={i}
                            variants={fadeUp}
                            className={`
                relative p-8 rounded-2xl border bg-[var(--canvas)]
                ${plan.popular
                                    ? "border-[var(--ink)] shadow-xl"
                                    : "border-[var(--border)]"
                                }
              `}
                        >
                            {/* Popular Badge */}
                            {plan.popular && (
                                <p className="text-xs uppercase tracking-wider text-[var(--accent)] mb-4 font-semibold">
                                    Most popular
                                </p>
                            )}

                            {/* Tier Name */}
                            <h3 className="text-2xl font-bold mb-2 text-[var(--ink)]">
                                {plan.tier}
                            </h3>

                            {/* Price */}
                            <p className="text-4xl font-mono font-bold mb-1 text-[var(--ink)]">
                                {plan.price}
                                <span className="text-base text-[var(--muted)] font-normal">
                                    /mo
                                </span>
                            </p>

                            {/* Description */}
                            <p className="text-sm text-[var(--muted)] mb-6">{plan.desc}</p>

                            {/* Features */}
                            <ul className="space-y-3 mb-8">
                                {plan.features.map((feature, j) => (
                                    <li key={j} className="flex items-start gap-2 text-sm">
                                        <CheckCircle
                                            className="w-4 h-4 text-[var(--accent)] flex-shrink-0 mt-0.5"
                                        />
                                        <span className="text-[var(--ink)]">{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            {/* CTA */}
                            <Link
                                href="/signup"
                                className={`
                  block w-full py-3 text-center font-semibold rounded-xl transition-all
                  ${plan.popular
                                        ? "bg-[var(--ink)] text-[var(--canvas)] hover:opacity-90"
                                        : "border border-[var(--border)] hover:border-[var(--ink)] text-[var(--ink)]"
                                    }
                `}
                            >
                                Start free trial
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </ContentContainer>
        </SectionWrapper>
    );
}
