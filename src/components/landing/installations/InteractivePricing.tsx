"use client";

import React, { useState, useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import Link from "next/link";
import { CheckCircle } from "lucide-react";

interface PricingPlan {
    tier: string;
    price: string;
    desc: string;
    features: string[];
    popular?: boolean;
}

const PLANS: PricingPlan[] = [
    {
        tier: "Ascent",
        price: "₹5,000",
        desc: "For founders getting started",
        features: ["Foundation setup", "3 weekly Moves", "Basic Muse AI", "Matrix analytics", "Email support"]
    },
    {
        tier: "Glide",
        price: "₹7,000",
        desc: "For founders scaling up",
        features: ["Everything in Ascent", "Unlimited Moves", "Advanced Muse (voice training)", "Cohort segmentation", "Priority support", "Blackbox vault"],
        popular: true
    },
    {
        tier: "Soar",
        price: "₹10,000",
        desc: "For teams",
        features: ["Everything in Glide", "5 team seats", "Custom AI training", "API access", "Dedicated success manager"]
    }
];

function PricingCard({ plan, index }: { plan: PricingPlan; index: number }) {
    const cardRef = useRef<HTMLDivElement>(null);
    const [isHovered, setIsHovered] = useState(false);

    const x = useMotionValue(0);
    const y = useMotionValue(0);

    const mouseXSpring = useSpring(x, { stiffness: 500, damping: 100 });
    const mouseYSpring = useSpring(y, { stiffness: 500, damping: 100 });

    const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["8deg", "-8deg"]);
    const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-8deg", "8deg"]);

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const xPct = mouseX / width - 0.5;
        const yPct = mouseY / height - 0.5;
        x.set(xPct);
        y.set(yPct);
    };

    const handleMouseLeave = () => {
        x.set(0);
        y.set(0);
        setIsHovered(false);
    };

    return (
        <motion.div
            ref={cardRef}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.15, type: "spring", stiffness: 100 }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
            style={{
                rotateX,
                rotateY,
                transformStyle: "preserve-3d",
            }}
            className="relative perspective-1000"
        >
            {/* Glow effect */}
            <motion.div
                className="absolute -inset-2 rounded-3xl opacity-0 blur-xl transition-opacity duration-500"
                animate={{ opacity: isHovered ? 0.6 : 0 }}
                style={{
                    background: plan.popular
                        ? "linear-gradient(135deg, rgba(224, 141, 121, 0.4), rgba(140, 169, 179, 0.3))"
                        : "rgba(140, 169, 179, 0.2)"
                }}
            />

            <div
                className={`
                    relative p-8 rounded-2xl border transition-all duration-300
                    ${plan.popular
                        ? "border-[var(--ink)] bg-[var(--canvas)] shadow-2xl"
                        : "border-[var(--border)] bg-[var(--canvas)]"
                    }
                    ${isHovered ? "border-[var(--ink)]" : ""}
                `}
                style={{ transform: "translateZ(50px)" }}
            >
                {plan.popular && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-[var(--rf-coral)] to-[var(--rf-ocean)] text-white text-xs uppercase tracking-wider font-semibold rounded-full"
                    >
                        Most popular
                    </motion.div>
                )}

                <h3 className="text-2xl font-bold mb-2">{plan.tier}</h3>

                <motion.div
                    className="relative"
                    animate={{ scale: isHovered ? 1.05 : 1 }}
                    transition={{ type: "spring", stiffness: 300 }}
                >
                    <span className="text-5xl font-mono font-bold">{plan.price}</span>
                    <span className="text-base text-[var(--muted)] font-normal">/mo</span>
                </motion.div>

                <p className="text-sm text-[var(--muted)] mt-2 mb-6">{plan.desc}</p>

                <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, i) => (
                        <motion.li
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.3 + i * 0.05 }}
                            className="flex items-start gap-2 text-sm"
                        >
                            <CheckCircle className={`w-4 h-4 flex-shrink-0 mt-0.5 transition-colors duration-300 ${isHovered ? "text-[var(--rf-coral)]" : "text-[var(--accent)]"}`} />
                            <span>{feature}</span>
                        </motion.li>
                    ))}
                </ul>

                <Link
                    href="/signup"
                    className={`
                        block w-full py-3.5 text-center font-semibold rounded-xl transition-all duration-300
                        ${plan.popular
                            ? "bg-[var(--ink)] text-[var(--canvas)] hover:bg-[var(--ink)]/90"
                            : `border border-[var(--border)] ${isHovered ? "bg-[var(--ink)] text-[var(--canvas)] border-[var(--ink)]" : "hover:border-[var(--ink)]"}`
                        }
                    `}
                >
                    Choose Plan
                </Link>
            </div>
        </motion.div>
    );
}

export default function InteractivePricing() {
    return (
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto perspective-1000">
            {PLANS.map((plan, i) => (
                <PricingCard key={plan.tier} plan={plan} index={i} />
            ))}
        </div>
    );
}
