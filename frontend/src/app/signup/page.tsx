"use client";

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle2, ChevronRight, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import AuthLayout from '@/components/auth/AuthLayout';

export const runtime = 'edge';

const TIERS = [
    {
        name: "Ascent",
        price: "Γé╣5,000",
        priceValue: 500000,
        planId: "PLN-ASC",
        desc: "Foundation for data-driven entry.",
        features: ["TAM/SAM/SOM Calc", "Brand Audit", "Competitive Scraping"],
        popular: false
    },
    {
        name: "Glide",
        price: "Γé╣7,000",
        priceValue: 700000,
        planId: "PLN-GLD",
        desc: "Scale with algorithmic precision.",
        features: ["Success Prediction (RF)", "Market Signals", "Gap Analysis", "5 Seats"],
        popular: true
    },
    {
        name: "Soar",
        price: "Γé╣10,000",
        priceValue: 1000000,
        planId: "PLN-SOA",
        desc: "Category dominance.",
        features: ["Custom AI Finetuning", "White-label Decks", "Strategist Access"],
        popular: false
    }
];

export default function SignupPage() {
    const router = useRouter();
    const [agreed, setAgreed] = useState(false);
    const [selectedTier, setSelectedTier] = useState<string | null>(null);

    const handleSelect = (planId: string, planName: string, priceValue: number) => {
        if (!agreed) {
            const checkbox = document.getElementById('terms-checkbox');
            if (checkbox) {
                checkbox.parentElement?.classList.add('animate-pulse');
                setTimeout(() => checkbox.parentElement?.classList.remove('animate-pulse'), 500);
            }
            return;
        }
        // Store plan details and redirect
        sessionStorage.setItem('selectedPlan', JSON.stringify({ planId, planName, priceValue }));
        router.push(`/pay/${planId}`);
    };

    return (
        <AuthLayout
            title={
                <>
                    Select Tier <br />
                    <span className="text-[var(--structure)] opacity-80">Begin Partnership.</span>
                </>
            }
            subtitle="Choose the level of intelligence required for your operation."
            sysCode="SYS.V.2.0.4 // TIER_SELECT"
        >
            <div className="w-full">
                {/* Header */}
                <div className="mb-6">
                    <div className="flex items-baseline justify-between">
                        <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">
                            Pricing Plans
                        </h2>
                        <span className="text-xs font-technical uppercase tracking-wider text-[var(--ink-muted)]">
                            Step 1 of 2
                        </span>
                    </div>
                    <p className="text-[var(--ink-secondary)] text-sm">
                        Select a plan to proceed to secure checkout.
                    </p>
                </div>

                {/* Vertical Tier Stack */}
                <div className="space-y-3 mb-8">
                    {TIERS.map((tier) => (
                        <div
                            key={tier.planId}
                            onClick={() => agreed && handleSelect(tier.planId, tier.name, tier.priceValue)}
                            className={`
                                relative group cursor-pointer 
                                bg-[var(--paper)] rounded-[var(--radius-md)] p-4 
                                border transition-all duration-200
                                ${tier.popular ? 'border-[var(--ink)] shadow-sm' : 'border-[var(--border)]'}
                                ${selectedTier === tier.planId ? 'ring-1 ring-[var(--ink)]' : ''}
                                ${!agreed ? 'opacity-70 grayscale-[0.8]' : 'hover:border-[var(--ink-muted)] hover:shadow-md'}
                            `}
                        >
                            {tier.popular && (
                                <div className="absolute top-0 right-0 transform translate-x-2 -translate-y-2">
                                    <span className="bg-[var(--ink)] text-[var(--paper)] text-[9px] font-bold tracking-widest uppercase px-2 py-1 rounded-full shadow-sm">
                                        Recommended
                                    </span>
                                </div>
                            )}

                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h3 className="font-serif text-lg text-[var(--ink)] leading-none mb-1">{tier.name}</h3>
                                    <p className="text-xs text-[var(--ink-secondary)]">{tier.desc}</p>
                                </div>
                                <div className="text-right">
                                    <span className="text-lg font-bold text-[var(--ink)]">{tier.price}</span>
                                    <span className="text-[10px] text-[var(--ink-muted)] block">/year</span>
                                </div>
                            </div>

                            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 pt-3 border-t border-[var(--border-subtle)]">
                                {tier.features.slice(0, 3).map((f, i) => (
                                    <span key={i} className="text-[10px] text-[var(--ink-secondary)] flex items-center gap-1">
                                        <Check size={10} className="text-[var(--success)]" /> {f}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Terms Checkbox */}
                <div className="relative mb-8 pb-8 border-b border-[var(--border)]">
                    <div className="flex items-start gap-3">
                        <div className="relative flex items-center mt-0.5">
                            <input
                                type="checkbox"
                                id="terms-checkbox"
                                checked={agreed}
                                onChange={(e) => setAgreed(e.target.checked)}
                                className="peer h-4 w-4 cursor-pointer appearance-none rounded border border-[var(--ink-muted)] checked:bg-[var(--ink)] checked:border-[var(--ink)] transition-all"
                            />
                            <CheckCircle2 size={12} className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[var(--paper)] opacity-0 peer-checked:opacity-100 transition-opacity" />
                        </div>
                        <label htmlFor="terms-checkbox" className="text-xs text-[var(--ink-secondary)] cursor-pointer select-none leading-relaxed">
                            I verify that I have read and agree to the <Link href="/legal/terms" className="underline hover:text-[var(--ink)]" target="_blank">Terms of Service</Link> and <Link href="/legal/privacy" className="underline hover:text-[var(--ink)]" target="_blank">Privacy Policy</Link>.
                        </label>
                    </div>
                </div>

                <div className="text-center">
                    <p className="text-xs text-[var(--ink-muted)] mb-3">
                        Already have a workspace?
                    </p>
                    <Link href="/login" className="text-sm font-semibold text-[var(--ink)] hover:underline decoration-1 underline-offset-4">
                        Sign In instead
                    </Link>
                </div>
            </div>
        </AuthLayout>
    );
}
