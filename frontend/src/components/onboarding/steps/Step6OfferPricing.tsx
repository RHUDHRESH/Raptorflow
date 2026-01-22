"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
    Check, Plus, Trash2, Clock, Target, DollarSign, Package, Repeat,
    Gauge, HelpCircle, Edit2, Shield, CheckCircle, Zap, RefreshCw
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 5: Offer Architecture

   PURPOSE: Define the core revenue model and pricing structure.
   - "Quiet Luxury" Refactor: Strategic Definition aesthetic.
   - Comparison Cards for Revenue Model (Recurring vs One-Time).
   - Validation Seal for the Guarantee.
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface PricingOption {
    id: string;
    name: string;
    price: string;
    description: string;
    features: string[];
    isPopular?: boolean;
}

interface PricingData {
    coreDeliverable: string;
    promisedOutcome: string;
    timeToValue: string;
    pricingModel: "recurring" | "one-time" | "hybrid";
    modelDescription: string;
    billingCycle?: string;
    options?: PricingOption[];
    guarantees: string;
    confirmed: boolean;
}

const INITIAL_OPTIONS: PricingOption[] = [
    { id: "1", name: "Standard", price: "$499", description: "Core access", features: [] },
    { id: "2", name: "Premium", price: "$999", description: "Full suite", features: [], isPopular: true },
];

function ModelSelectionCard({
    id,
    label,
    description,
    icon: Icon,
    isSelected,
    onSelect
}: {
    id: "recurring" | "one-time";
    label: string;
    description: string;
    icon: any;
    isSelected: boolean;
    onSelect: () => void;
}) {
    return (
        <button
            onClick={onSelect}
            className={cn(
                "group relative w-full text-left p-8 border transition-all duration-300 ease-out",
                isSelected
                    ? "bg-[var(--ink)] border-[var(--ink)] text-[var(--paper)] shadow-lg scale-[1.02]"
                    : "bg-[var(--paper)] border-[var(--border)] text-[var(--ink)] hover:border-[var(--ink)] hover:shadow-md"
            )}
        >
            <div className="flex items-start justify-between mb-6">
                <div className={cn(
                    "p-3 rounded-full border transition-colors",
                    isSelected
                        ? "bg-[var(--paper)] border-[var(--paper)] text-[var(--ink)]"
                        : "bg-[var(--canvas)] border-[var(--border-subtle)] text-[var(--muted)] group-hover:text-[var(--ink)] group-hover:border-[var(--ink)]"
                )}>
                    <Icon size={24} strokeWidth={1} />
                </div>
                {isSelected && (
                    <div className="px-2 py-0.5 bg-[var(--paper)]/20 border border-[var(--paper)]/30 rounded text-[10px] font-technical uppercase tracking-widest text-[var(--paper)]">
                        Selected
                    </div>
                )}
            </div>

            <h3 className={cn(
                "font-serif text-2xl mb-2",
                isSelected ? "text-[var(--paper)]" : "text-[var(--ink)]"
            )}>
                {label}
            </h3>
            <p className={cn(
                "text-sm font-serif italic leading-relaxed max-w-[90%]",
                isSelected ? "text-[var(--paper)]/80" : "text-[var(--secondary)]"
            )}>
                {description}
            </p>
        </button>
    );
}

function PricingTierCompact({
    option,
    onUpdate,
    onRemove
}: {
    option: PricingOption;
    onUpdate: (id: string, updates: Partial<PricingOption>) => void;
    onRemove: (id: string) => void;
}) {
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState(option);

    const handleSave = () => {
        onUpdate(option.id, editData);
        setIsEditing(false);
    };

    if (isEditing) {
        return (
            <div className="p-4 border border-[var(--blueprint)] bg-[var(--paper)] animate-in fade-in zoom-in-95 duration-200">
                <div className="space-y-3">
                    <input
                        type="text"
                        value={editData.name}
                        onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                        className="w-full text-lg font-serif font-bold bg-transparent border-b border-[var(--border)] focus:border-[var(--blueprint)] outline-none text-[var(--ink)] pb-1"
                        placeholder="Tier Name"
                        autoFocus
                    />
                    <div className="flex items-center gap-2">
                        <span className="text-[var(--muted)]">$</span>
                        <input
                            type="text"
                            value={editData.price.replace('$', '')}
                            onChange={(e) => setEditData({ ...editData, price: `$${e.target.value}` })}
                            className="w-full font-technical text-base bg-transparent border-b border-[var(--border)] focus:border-[var(--blueprint)] outline-none text-[var(--ink)]"
                            placeholder="Price"
                        />
                    </div>
                    <input
                        type="text"
                        value={editData.description}
                        onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                        className="w-full text-xs font-serif italic bg-transparent border-b border-[var(--border)] focus:border-[var(--blueprint)] outline-none text-[var(--secondary)] pb-1"
                        placeholder="Brief positioning statement"
                    />
                    <div className="flex justify-end gap-2 pt-2">
                        <button onClick={() => setIsEditing(false)} className="text-[10px] uppercase font-technical text-[var(--muted)] hover:text-[var(--ink)]">Cancel</button>
                        <button onClick={handleSave} className="text-[10px] uppercase font-technical text-[var(--blueprint)] hover:text-[var(--blueprint-dark)] font-bold">Save</button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="group relative p-6 bg-[var(--paper)] border border-[var(--border-subtle)] hover:border-[var(--ink)] hover:shadow-sm transition-all duration-300">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h4 className="font-serif text-lg text-[var(--ink)]">{option.name}</h4>
                    <p className="text-xs text-[var(--secondary)] italic font-serif mt-1">{option.description}</p>
                </div>
                <div className="font-technical text-xl text-[var(--ink)]">{option.price}</div>
            </div>

            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2 bg-[var(--paper)] px-2">
                <button onClick={() => setIsEditing(true)} className="p-1 hover:bg-[var(--canvas)] rounded"><Edit2 size={12} className="text-[var(--ink)]" /></button>
                <button onClick={() => onRemove(option.id)} className="p-1 hover:bg-[var(--error)]/10 rounded"><Trash2 size={12} className="text-[var(--error)]" /></button>
            </div>
        </div>
    );
}

export default function Step6OfferPricing() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(6)?.data as PricingData | undefined;

    const [pricingModel, setPricingModel] = useState<"recurring" | "one-time">(stepData?.pricingModel as "recurring" | "one-time" || "recurring");
    const [coreDeliverable, setCoreDeliverable] = useState(stepData?.coreDeliverable || "");
    const [promisedOutcome, setPromisedOutcome] = useState(stepData?.promisedOutcome || "");
    const [options, setOptions] = useState<PricingOption[]>(stepData?.options || INITIAL_OPTIONS);
    const [guarantees, setGuarantees] = useState(stepData?.guarantees || "");
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power2.out" }
        );
    }, []);

    const saveData = (updates: Record<string, unknown> = {}) => {
        updateStepData(6, {
            pricingModel, coreDeliverable, promisedOutcome, options, guarantees, ...updates
        });
    };

    const handleUpdateOption = (id: string, updates: Partial<PricingOption>) => {
        const updated = options.map((o) => (o.id === id ? { ...o, ...updates } : o));
        setOptions(updated);
        saveData({ options: updated });
    };

    const handleRemoveOption = (id: string) => {
        const updated = options.filter((o) => o.id !== id);
        setOptions(updated);
        saveData({ options: updated });
    };

    const handleAddOption = () => {
        const newOption: PricingOption = {
            id: `opt-${Date.now()}`,
            name: "New Tier",
            price: "$XXX",
            description: "Target audience",
            features: [],
        };
        setOptions([...options, newOption]);
        saveData({ options: [...options, newOption] });
    };

    const handleConfirm = () => {
        setConfirmed(true);
        saveData({ confirmed: true });
        updateStepStatus(6, "complete");
    };

    return (
        <div ref={containerRef} className="max-w-4xl mx-auto space-y-16 pb-24">

            {/* Header */}
            <div data-animate className="text-center space-y-4">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 05 / 24</span>
                <h2 className="font-serif text-4xl text-[var(--ink)]">Offer Architecture</h2>
                <p className="text-[var(--secondary)] max-w-lg mx-auto font-serif text-lg italic leading-relaxed">
                    "How do you make money, and how do you guarantee the result?"
                </p>
            </div>

            {/* Model Selection */}
            <div data-animate className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ModelSelectionCard
                    id="recurring"
                    label="Recurring Revenue"
                    description="Subscription, retainer, or membership. Predictable cash flow compounding over time."
                    icon={RefreshCw}
                    isSelected={pricingModel === "recurring"}
                    onSelect={() => { setPricingModel("recurring"); saveData({ pricingModel: "recurring" }); }}
                />
                <ModelSelectionCard
                    id="one-time"
                    label="Transactional"
                    description="One-time purchase, project fee, or unit sales. Immediate cash flow for delivered value."
                    icon={Zap}
                    isSelected={pricingModel === "one-time"}
                    onSelect={() => { setPricingModel("one-time"); saveData({ pricingModel: "one-time" }); }}
                />
            </div>

            {/* Core Offer Definition */}
            <div data-animate className="bg-[var(--paper)] border border-[var(--border)] p-8 relative">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[var(--canvas)] px-3 py-1 border border-[var(--border)]">
                    <span className="text-[10px] font-technical tracking-widest uppercase text-[var(--muted)]">Strategic Definition</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <div className="space-y-6">
                        <div>
                            <label className="block text-[10px] font-technical uppercase tracking-widest text-[var(--muted)] mb-2">Primary Deliverable</label>
                            <input
                                type="text"
                                value={coreDeliverable}
                                onChange={(e) => { setCoreDeliverable(e.target.value); saveData({ coreDeliverable: e.target.value }); }}
                                placeholder="e.g. Enterprise Marketing OS"
                                className="w-full text-xl font-serif text-[var(--ink)] bg-transparent border-b border-[var(--border-subtle)] pb-2 outline-none focus:border-[var(--ink)] placeholder:text-[var(--placeholder)] transition-colors"
                            />
                        </div>
                        <div>
                            <label className="block text-[10px] font-technical uppercase tracking-widest text-[var(--muted)] mb-2">Promised Outcome</label>
                            <textarea
                                value={promisedOutcome}
                                onChange={(e) => { setPromisedOutcome(e.target.value); saveData({ promisedOutcome: e.target.value }); }}
                                placeholder="e.g. 50% reduction in CAC within 90 days"
                                className="w-full h-24 text-base font-serif text-[var(--secondary)] bg-transparent border border-[var(--border-subtle)] p-3 outline-none focus:border-[var(--ink)] resize-none transition-colors"
                            />
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="flex justify-between items-end pb-2 border-b border-[var(--border-subtle)]">
                            <h3 className="font-serif text-lg text-[var(--ink)]">Pricing Structure</h3>
                            <button onClick={handleAddOption} className="text-[10px] font-technical text-[var(--blueprint)] hover:underline uppercase tracking-wide flex items-center gap-1">
                                <Plus size={10} /> Add Tier
                            </button>
                        </div>
                        <div className="space-y-4">
                            {options.map((option) => (
                                <PricingTierCompact
                                    key={option.id}
                                    option={option}
                                    onUpdate={handleUpdateOption}
                                    onRemove={handleRemoveOption}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* The Guarantee Seal */}
            <div data-animate className="relative group">
                <div className="absolute inset-0 bg-[#F4F1EA] -skew-y-1 transform origin-bottom-right rounded-sm -z-10 group-hover:-skew-y-2 transition-transform duration-500" />
                <div className="bg-[var(--ink)] text-[var(--paper)] p-8 md:p-10 relative overflow-hidden rounded-[1px]">
                    <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
                        <Shield size={140} />
                    </div>

                    <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start">
                        <div className="shrink-0 pt-1">
                            <Shield size={32} className="text-[var(--paper)]" strokeWidth={1.5} />
                        </div>
                        <div className="flex-1 space-y-4">
                            <div>
                                <h3 className="font-serif text-2xl text-[var(--paper)] mb-1">Risk Reversal</h3>
                                <p className="text-xs font-technical uppercase tracking-widest text-[var(--paper)]/60">The Guarantee</p>
                            </div>
                            <textarea
                                value={guarantees}
                                onChange={(e) => { setGuarantees(e.target.value); saveData({ guarantees: e.target.value }); }}
                                placeholder="State your guarantee clearly. e.g. 'If you don't see value in 30 days, we issue a full refund, no questions asked.'"
                                className="w-full h-24 bg-transparent border-b border-[var(--paper)]/20 text-[var(--paper)] placeholder:text-[var(--paper)]/30 outline-none resize-none text-xl font-serif font-light leading-relaxed focus:border-[var(--paper)]/60 transition-colors"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer Action */}
            <div data-animate className="flex justify-center pt-8">
                {!confirmed ? (
                    <BlueprintButton onClick={handleConfirm} size="lg" className="px-12 py-6 text-base">
                        <span>Ratify Offer Structure</span>
                    </BlueprintButton>
                ) : (
                    <div className="flex flex-col items-center gap-2 animate-in zoom-in-50 duration-300">
                        <div className="w-12 h-12 rounded-full bg-[var(--success)]/10 flex items-center justify-center text-[var(--success)]">
                            <CheckCircle size={24} />
                        </div>
                        <span className="font-serif text-[var(--ink)]">Offer Logic Locked</span>
                    </div>
                )}
            </div>

        </div>
    );
}
