"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/auth/AuthProvider';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';

const PLANS = [
    {
        name: "Ascent",
        price: { monthly: 29, annual: 24 },
        description: "For founders just getting started with systematic marketing.",
        features: [
            "Foundation setup (ICP + Positioning)",
            "Weekly Moves (3 per week)",
            "Basic Muse AI generation",
            "Matrix analytics dashboard",
            "Email support"
        ],
        cta: "Start Now",
        highlighted: false
    },
    {
        name: "Glide",
        price: { monthly: 79, annual: 66 },
        description: "For founders scaling their marketing engine.",
        features: [
            "Everything in Ascent",
            "Unlimited Moves",
            "Advanced Muse (voice training)",
            "Cohort segmentation",
            "Campaign planning tools",
            "Priority support",
            "Blackbox learnings vault"
        ],
        cta: "Start Now",
        highlighted: true
    },
    {
        name: "Soar",
        price: { monthly: 199, annual: 166 },
        description: "For teams running multi-channel campaigns.",
        features: [
            "Everything in Glide",
            "Team seats (up to 5)",
            "White-label exports",
            "Custom AI training",
            "API access",
            "Dedicated success manager",
            "Custom integrations"
        ],
        cta: "Contact Sales",
        highlighted: false
    }
];

export function Pricing() {
    const [isAnnual, setIsAnnual] = useState(true);
    const router = useRouter();
    const { user } = useAuth();
    const { authenticatedFetch } = useAuthenticatedApi();
    const [isLoading, setIsLoading] = useState(false);

    const handlePlanSelection = async (planName: string, billingCycle: string) => {
      // If user is not authenticated, redirect to signup first
      if (!user) {
        router.push('/signup');
        return;
      }

      setIsLoading(true);

      try {
        // Use authenticated fetch for plan selection
        const selectionResponse = await authenticatedFetch('/api/onboarding/select-plan', {
          method: 'POST',
          body: JSON.stringify({
            planId: planName.toLowerCase(), // Convert to plan ID format
            billingCycle: billingCycle
          })
        });

        if (selectionResponse.ok) {
          // Redirect to payment page
          router.push('/onboarding/payment');
        } else {
          const errorData = await selectionResponse.json();
          console.error('Plan selection failed:', errorData);
          alert(`Failed to select plan: ${errorData.error || 'Unknown error'}`);
        }
      } catch (error) {
        console.error('Plan selection error:', error);
        // Error is already handled by useAuthenticatedApi hook
        // No need to show alert for auth errors
        if (!(error instanceof Error && error.message.includes('authenticated'))) {
          alert('Plan selection failed. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    return (
        <section id="pricing" className="py-24 md:py-32 bg-[var(--surface)] border-y border-[var(--border)]">
            <div className="max-w-7xl mx-auto px-6">

                {/* Header */}
                <div className="text-center mb-16">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-block px-3 py-1 bg-[var(--canvas)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--secondary)] mb-6"
                    >
                        Simple Pricing
                    </motion.div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-5xl font-editorial text-[var(--ink)] mb-4"
                    >
                        Invest in clarity. <span className="italic text-[var(--muted)]">Not chaos.</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.15 }}
                        className="text-lg text-[var(--secondary)] max-w-2xl mx-auto"
                    >
                        Start Now. No credit card required. Cancel anytime.
                    </motion.p>
                </div>

                {/* Toggle */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="flex items-center justify-center gap-4 mb-12"
                >
                    <span className={`text-sm font-medium ${!isAnnual ? 'text-[var(--ink)]' : 'text-[var(--muted)]'}`}>Monthly</span>
                    <button
                        onClick={() => setIsAnnual(!isAnnual)}
                        className={`relative w-14 h-7 rounded-full transition-colors ${isAnnual ? 'bg-[var(--ink)]' : 'bg-[var(--border)]'}`}
                    >
                        <div className={`absolute top-1 w-5 h-5 rounded-full bg-white shadow transition-transform ${isAnnual ? 'translate-x-8' : 'translate-x-1'}`} />
                    </button>
                    <span className={`text-sm font-medium ${isAnnual ? 'text-[var(--ink)]' : 'text-[var(--muted)]'}`}>
                        Annual <span className="text-[var(--accent)]">(Save 20%)</span>
                    </span>
                </motion.div>

                {/* Pricing Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {PLANS.map((plan, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 + i * 0.1 }}
                            className={`relative p-8 rounded-2xl border ${plan.highlighted
                                    ? 'border-[var(--ink)] bg-[var(--canvas)] shadow-xl'
                                    : 'border-[var(--border)] bg-[var(--canvas)]'
                                }`}
                        >
                            {/* Popular Badge */}
                            {plan.highlighted && (
                                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-[var(--ink)] text-[var(--canvas)] text-xs font-bold uppercase tracking-wider rounded-full">
                                    Most Popular
                                </div>
                            )}

                            <div className="mb-6">
                                <h3 className="text-xl font-bold text-[var(--ink)] mb-2">{plan.name}</h3>
                                <p className="text-sm text-[var(--muted)]">{plan.description}</p>
                            </div>

                            <div className="mb-6">
                                <span className="text-4xl font-bold text-[var(--ink)] font-mono">
                                    ${isAnnual ? plan.price.annual : plan.price.monthly}
                                </span>
                                <span className="text-[var(--muted)]">/month</span>
                                {isAnnual && (
                                    <div className="text-xs text-[var(--accent)] mt-1">
                                        Billed annually (${plan.price.annual * 12}/year)
                                    </div>
                                )}
                            </div>

                            <ul className="space-y-3 mb-8">
                                {plan.features.map((feature, j) => (
                                    <li key={j} className="flex items-start gap-2 text-sm text-[var(--secondary)]">
                                        <Check className="w-4 h-4 text-[var(--accent)] flex-shrink-0 mt-0.5" />
                                        <span>{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            <button
                                onClick={() => handlePlanSelection(plan.name.toLowerCase(), isAnnual ? 'annual' : 'monthly')}
                                disabled={isLoading}
                                className={`block w-full py-3 text-center font-semibold rounded-xl transition-colors ${plan.highlighted
                                        ? 'bg-[var(--ink)] text-[var(--canvas)] hover:bg-[var(--ink)]/90'
                                        : 'border border-[var(--border)] text-[var(--ink)] hover:border-[var(--ink)]'
                                    }`}
                            >
                                {isLoading ? (
                                    <div className="flex items-center justify-center gap-2">
                                        <div className="w-4 h-4 border-2 border-[var(--paper)] border-t-transparent rounded-full animate-spin" />
                                        <span>Processing...</span>
                                    </div>
                                ) : (
                                    plan.cta
                                )}
                            </button>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
