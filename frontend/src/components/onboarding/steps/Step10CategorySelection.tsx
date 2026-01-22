"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Check, Play, Shield, Zap, Target, Star, MoreHorizontal,
    Search, Award, Sparkles, AlertCircle, CheckCircle, RefreshCw, Plus
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";
import { StepLoadingState } from "../StepStates";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 10: Capability Audit
   
   PURPOSE: Rate product capabilities on uniqueness.
   - "Quiet Luxury" Refactor: Capability Rating Ledger.
   - 4-Tier Rating System: Only You, Unique, Better Than, Table Stakes.
   - "Verification" simulation for bold claims.
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface Capability {
    id: string;
    name: string;
    rating: "only-you" | "unique" | "better-than" | "table-stakes" | null;
    verified?: boolean; // For "Only You" claims
}

interface Step10Result {
    capabilities: Capability[];
    confirmed: boolean;
}

const RATING_TIERS = [
    { id: "only-you", label: "Only You", color: "text-[var(--accent)]", bg: "bg-[var(--accent)]/10", border: "border-[var(--accent)]", desc: "No one else does this." },
    { id: "unique", label: "Unique Approach", color: "text-[var(--blueprint)]", bg: "bg-[var(--blueprint)]/10", border: "border-[var(--blueprint)]", desc: "Others do it, but you do it differently." },
    { id: "better-than", label: "Better Than", color: "text-[var(--success)]", bg: "bg-[var(--success)]/10", border: "border-[var(--success)]", desc: "Faster, cheaper, or higher quality." },
    { id: "table-stakes", label: "Table Stakes", color: "text-[var(--muted)]", bg: "bg-[var(--muted)]/10", border: "border-[var(--muted)]", desc: "Expected baseline feature." },
];

function CapabilityRow({
    cap,
    onRate,
    onVerify
}: {
    cap: Capability;
    onRate: (id: string, rating: Capability['rating']) => void;
    onVerify: (id: string) => void;
}) {
    const isOnlyYou = cap.rating === "only-you";

    return (
        <div className="group flex items-center justify-between p-4 bg-[var(--paper)] border border-[var(--border-subtle)] hover:border-[var(--ink)] transition-all duration-300">
            <div className="flex-1">
                <input
                    type="text"
                    defaultValue={cap.name}
                    className="w-full bg-transparent font-serif text-lg text-[var(--ink)] outline-none border-b border-transparent focus:border-[var(--border)] transition-colors placeholder:text-[var(--placeholder)]"
                />
            </div>

            <div className="flex items-center gap-2">
                {RATING_TIERS.map((tier) => (
                    <button
                        key={tier.id}
                        onClick={() => onRate(cap.id, tier.id as any)}
                        className={cn(
                            "px-3 py-1.5 rounded text-[10px] font-technical uppercase tracking-wider border transition-all duration-200",
                            cap.rating === tier.id
                                ? `${tier.bg} ${tier.border} ${tier.color} font-bold shadow-sm`
                                : "bg-[var(--canvas)] border-[var(--border-subtle)] text-[var(--muted)] hover:border-[var(--border)] hover:text-[var(--ink)]"
                        )}
                        title={tier.desc}
                    >
                        {tier.label}
                    </button>
                ))}
            </div>

            {/* Verification Badge/Action for 'Only You' */}
            <div className="w-[140px] flex justify-end pl-4">
                {isOnlyYou && !cap.verified && (
                    <button
                        onClick={() => onVerify(cap.id)}
                        className="flex items-center gap-1.5 text-[10px] font-technical uppercase text-[var(--accent)] hover:underline animate-pulse"
                    >
                        <RefreshCw size={10} className="animate-spin-slow" /> Verify Claim
                    </button>
                )}
                {isOnlyYou && cap.verified && (
                    <div className="flex items-center gap-1.5 text-[10px] font-technical uppercase text-[var(--success)]">
                        <Award size={12} fill="currentColor" /> Verified Truth
                    </div>
                )}
            </div>
        </div>
    );
}

export default function Step10CategorySelection() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(10)?.data as Step10Result | undefined;

    const [capabilities, setCapabilities] = useState<Capability[]>(stepData?.capabilities || []);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [verifyingId, setVerifyingId] = useState<string | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const hasData = capabilities.length > 0;

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power2.out" }
        );
    }, [hasData]);

    const handleAddCapability = () => {
        const newCap: Capability = {
            id: `cap-${Date.now()}`,
            name: "New Capability...",
            rating: null
        };
        setCapabilities([...capabilities, newCap]);
    };

    const handleRate = (id: string, rating: Capability['rating']) => {
        const updated = capabilities.map(c => c.id === id ? { ...c, rating, verified: false } : c);
        setCapabilities(updated);
        updateStepData(10, { capabilities: updated, confirmed: false });
    };

    const handleVerify = (id: string) => {
        setVerifyingId(id);
        setTimeout(() => {
            const updated = capabilities.map(c => c.id === id ? { ...c, verified: true } : c);
            setCapabilities(updated);
            setVerifyingId(null);
            updateStepData(10, { capabilities: updated, confirmed: false });
        }, 1500);
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(10, { capabilities, confirmed: true });
        updateStepStatus(10, "complete");
    };

    // Pre-populate if empty
    useEffect(() => {
        if (capabilities.length === 0) {
            setCapabilities([
                { id: "1", name: "AI-Powered Extraction", rating: "unique", verified: false },
                { id: "2", name: "Market Intelligence", rating: "better-than", verified: false },
                { id: "3", name: "Founder-led Strategy", rating: "only-you", verified: false },
            ]);
        }
    }, [capabilities.length]);

    if (verifyingId) {
        return (
            <StepLoadingState
                title="Verifying Claim"
                message={`Cross-referencing feature against market database...`}
                stage="Auditing..."
            />
        );
    }

    return (
        <div ref={containerRef} className="max-w-5xl mx-auto space-y-8 pb-12">

            {/* Header */}
            <div data-animate className="flex justify-between items-end border-b border-[var(--border-subtle)] pb-8">
                <div>
                    <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase block mb-2">Step 10 / 24</span>
                    <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Capability Audit</h2>
                    <p className="text-[var(--secondary)] max-w-xl font-serif text-lg italic">
                        "Be honest. What is truly unique, and what is just expected?"
                    </p>
                </div>
                <BlueprintButton onClick={handleAddCapability} size="sm">
                    <Plus size={12} /> Add Feature
                </BlueprintButton>
            </div>

            {/* Capability List */}
            <div data-animate className="space-y-3">
                {capabilities.map(cap => (
                    <CapabilityRow
                        key={cap.id}
                        cap={cap}
                        onRate={handleRate}
                        onVerify={handleVerify}
                    />
                ))}
            </div>

            {/* Footer */}
            <div data-animate className="flex justify-center pt-8 border-t border-[var(--border-subtle)]">
                {!confirmed ? (
                    <BlueprintButton onClick={handleConfirm} size="lg" className="px-12 py-6">
                        <Check size={16} />
                        <span>Ratify Capabilities</span>
                    </BlueprintButton>
                ) : (
                    <div className="flex items-center gap-2 text-[var(--success)] animate-in zoom-in-50">
                        <CheckCircle size={24} />
                        <span className="font-serif italic font-medium">Claims Audited & Locked</span>
                    </div>
                )}
            </div>
        </div>
    );
}
