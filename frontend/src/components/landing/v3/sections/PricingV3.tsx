"use client";

import React, { useState } from "react";
import { Check } from "lucide-react";
import { ArchButton } from "../ui/ArchButton";

export function PricingV3() {
    const [annual, setAnnual] = useState(true);

    const plans = [
        {
            name: "ASCENT",
            price: annual ? "29" : "39",
            period: "/mo",
            desc: "For solo founders.",
            features: ["3 Weekly Moves", "Muse AI (Basic)", "Matrix Analytics", "90-Day Plan"]
        },
        {
            name: "GLIDE",
            price: annual ? "79" : "99",
            period: "/mo",
            desc: "For scaling teams.",
            features: ["Unlimited Moves", "Muse AI (Pro Voice)", "Cohort Segmentation", "Priority Support", "Blackbox Vault"],
            popular: true
        }
    ];

    return (
        <section className="bg-[#F0F0F0] text-black py-32 border-b border-black/10">
            <div className="max-w-[1200px] mx-auto px-6">

                <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-8">
                    <div>
                        <h2 className="font-mono text-sm uppercase tracking-widest text-black/50 mb-4">
                            // The_Contract
                        </h2>
                        <h3 className="text-4xl md:text-6xl font-bold tracking-tighter">
                            Commit.
                        </h3>
                    </div>

                    {/* Simple Toggle */}
                    <div className="flex items-center gap-4 font-mono text-sm uppercase tracking-widest">
                        <span className={!annual ? "opacity-100 font-bold" : "opacity-40"}>Monthly</span>
                        <div
                            onClick={() => setAnnual(!annual)}
                            className="w-12 h-6 bg-black rounded-full relative cursor-pointer"
                        >
                            <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform duration-200 ${annual ? 'translate-x-6' : 'translate-x-0'}`} />
                        </div>
                        <span className={annual ? "opacity-100 font-bold" : "opacity-40"}>Yearly (-20%)</span>
                    </div>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    {plans.map((plan, i) => (
                        <div
                            key={i}
                            className={`p-12 border ${plan.popular ? 'border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]' : 'border-black/20 bg-[#FAFAFA]'} relative group transition-transform duration-300 hover:-translate-y-1`}
                        >
                            {plan.popular && (
                                <div className="absolute top-0 right-0 bg-black text-white px-4 py-2 font-mono text-xs uppercase tracking-widest">
                                    Recommended
                                </div>
                            )}

                            <h4 className="font-mono text-xl font-bold mb-2">{plan.name}</h4>
                            <div className="flex items-baseline mb-6">
                                <span className="text-6xl md:text-8xl font-bold tracking-tighter">
                                    ${plan.price}
                                </span>
                                <span className="font-mono text-sm opacity-50 ml-2">
                                    {plan.period}
                                </span>
                            </div>
                            <p className="font-mono text-sm opacity-60 mb-12 border-b border-black/10 pb-8">
                                {plan.desc}
                            </p>

                            <ul className="space-y-4 mb-12">
                                {plan.features.map((f, j) => (
                                    <li key={j} className="flex gap-3 items-center font-medium">
                                        <div className="w-1 h-1 bg-black" />
                                        {f}
                                    </li>
                                ))}
                            </ul>

                            <ArchButton
                                className="w-full"
                                variant={plan.popular ? "secondary" : "secondary"} // Forcing secondary (Black) on light mode
                            >
                                Initiate Protocol
                            </ArchButton>
                        </div>
                    ))}
                </div>

            </div>
        </section>
    );
}
