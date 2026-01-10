"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Plus, Trash2, Clock, Target, DollarSign, Package, Repeat, Gauge, HelpCircle, Edit2 } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 6: Offer Pricing (Universal)
   Define core offer and pricing structure for ANY business model:
   - Subscription (SaaS)
   - One-time (Products, Services, Projects)
   - Usage-based (Pay-as-you-go)
   - Hybrid/Custom
   ══════════════════════════════════════════════════════════════════════════════ */

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
    pricingModel: string;
    modelDescription: string;
    // Subscription fields
    billingCycle?: string;
    options?: PricingOption[];
    // Usage-based fields
    usageUnit?: string;
    usageExample?: string;
    typicalUsage?: string;
    // One-time fields
    paymentTerms?: string;
    whatsIncluded?: string;
    // Guarantees
    guarantees: string;
    confirmed: boolean;
}

// Model configurations with dynamic fields
const PRICING_MODELS = [
    {
        id: "subscription",
        label: "Recurring",
        icon: Repeat,
        description: "Monthly/annual subscriptions",
        examples: "SaaS, Memberships, Retainers"
    },
    {
        id: "one-time",
        label: "One-Time",
        icon: Package,
        description: "Single payment for product/service",
        examples: "Products, Projects, Courses"
    },
    {
        id: "usage-based",
        label: "Usage-Based",
        icon: Gauge,
        description: "Pay per use or consumption",
        examples: "API calls, Credits, Transactions"
    },
    {
        id: "hybrid",
        label: "Hybrid / Custom",
        icon: HelpCircle,
        description: "Mix of models",
        examples: "Base + Usage, Tiered + Overage"
    },
];

const INITIAL_OPTIONS: PricingOption[] = [
    { id: "1", name: "Starter", price: "$29/mo", description: "For individuals getting started", features: ["Core features", "Email support"] },
    { id: "2", name: "Pro", price: "$79/mo", description: "For growing teams", features: ["All features", "Priority support", "API access"], isPopular: true },
    { id: "3", name: "Enterprise", price: "Custom", description: "For large organizations", features: ["Custom limits", "Dedicated support"] },
];

function PricingOptionCard({
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
            <BlueprintCard showCorners padding="md" className="border-[var(--blueprint)]">
                <div className="space-y-3">
                    <input
                        type="text"
                        value={editData.name}
                        onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                        className="w-full h-9 px-3 text-sm font-semibold bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Option name"
                    />
                    <input
                        type="text"
                        value={editData.price}
                        onChange={(e) => setEditData({ ...editData, price: e.target.value })}
                        className="w-full h-9 px-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Price (e.g., $99/mo, $499, Custom)"
                    />
                    <input
                        type="text"
                        value={editData.description}
                        onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                        className="w-full h-9 px-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Short description"
                    />
                    <textarea
                        value={editData.features.join("\n")}
                        onChange={(e) => setEditData({ ...editData, features: e.target.value.split("\n").filter(Boolean) })}
                        className="w-full min-h-[60px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Features (one per line)"
                    />
                    <div className="flex gap-2">
                        <BlueprintButton size="sm" onClick={handleSave} className="flex-1">Save</BlueprintButton>
                        <SecondaryButton size="sm" onClick={() => setIsEditing(false)}>Cancel</SecondaryButton>
                    </div>
                </div>
            </BlueprintCard>
        );
    }

    return (
        <BlueprintCard showCorners padding="md" className={option.isPopular ? "border-[var(--blueprint)] ring-1 ring-[var(--blueprint)]" : ""}>
            {option.isPopular && (
                <BlueprintBadge variant="blueprint" className="absolute -top-2 left-1/2 -translate-x-1/2">POPULAR</BlueprintBadge>
            )}
            <div className="text-center mb-3 pt-1">
                <h4 className="text-sm font-semibold text-[var(--ink)]">{option.name}</h4>
                <p className="text-xl font-bold text-[var(--ink)] mt-1">{option.price}</p>
                <p className="text-xs text-[var(--secondary)]">{option.description}</p>
            </div>
            <ul className="space-y-1 mb-3">
                {option.features.map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-xs text-[var(--secondary)]">
                        <Check size={10} strokeWidth={1.5} className="text-[var(--success)]" />{f}
                    </li>
                ))}
            </ul>
            <div className="flex gap-2 pt-3 border-t border-[var(--border-subtle)]">
                <button onClick={() => setIsEditing(true)} className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs font-technical text-[var(--muted)] hover:text-[var(--blueprint)] transition-colors">
                    <Edit2 size={10} strokeWidth={1.5} />Edit
                </button>
                <button onClick={() => onRemove(option.id)} className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] transition-colors">
                    <Trash2 size={10} strokeWidth={1.5} />
                </button>
            </div>
        </BlueprintCard>
    );
}

export default function Step6OfferPricing() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(6)?.data as PricingData | undefined;

    const [coreDeliverable, setCoreDeliverable] = useState(stepData?.coreDeliverable || "");
    const [promisedOutcome, setPromisedOutcome] = useState(stepData?.promisedOutcome || "");
    const [timeToValue, setTimeToValue] = useState(stepData?.timeToValue || "");
    const [pricingModel, setPricingModel] = useState(stepData?.pricingModel || "subscription");
    const [modelDescription, setModelDescription] = useState(stepData?.modelDescription || "");

    // Model-specific fields
    const [billingCycle, setBillingCycle] = useState(stepData?.billingCycle || "monthly");
    const [options, setOptions] = useState<PricingOption[]>(stepData?.options || INITIAL_OPTIONS);
    const [usageUnit, setUsageUnit] = useState(stepData?.usageUnit || "");
    const [usageExample, setUsageExample] = useState(stepData?.usageExample || "");
    const [typicalUsage, setTypicalUsage] = useState(stepData?.typicalUsage || "");
    const [paymentTerms, setPaymentTerms] = useState(stepData?.paymentTerms || "");
    const [whatsIncluded, setWhatsIncluded] = useState(stepData?.whatsIncluded || "");

    const [guarantees, setGuarantees] = useState(stepData?.guarantees || "");
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    const saveData = (updates: Record<string, unknown> = {}) => {
        updateStepData(6, {
            coreDeliverable, promisedOutcome, timeToValue, pricingModel, modelDescription,
            billingCycle, options, usageUnit, usageExample, typicalUsage, paymentTerms, whatsIncluded,
            guarantees, ...updates
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
            name: "New Option",
            price: "$XX",
            description: "Short description",
            features: ["Feature 1"],
        };
        setOptions([...options, newOption]);
        saveData({ options: [...options, newOption] });
    };

    const handleConfirm = () => {
        setConfirmed(true);
        saveData({ confirmed: true });
        updateStepStatus(6, "complete");
    };

    const selectedModel = PRICING_MODELS.find(m => m.id === pricingModel);
    const ModelIcon = selectedModel?.icon || DollarSign;

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Core Offer Definition */}
            <BlueprintCard data-animate figure="FIG. 01" title="Core Offer Definition" code="OFFER" showCorners padding="md">
                <div className="space-y-4">
                    <div>
                        <label className="flex items-center gap-2 font-technical text-[var(--muted)] mb-2">
                            <Target size={10} strokeWidth={1.5} />CORE DELIVERABLE
                        </label>
                        <input
                            type="text"
                            value={coreDeliverable}
                            onChange={(e) => { setCoreDeliverable(e.target.value); saveData({ coreDeliverable: e.target.value }); }}
                            placeholder="What exactly do customers get? (e.g., 'Marketing strategy document', 'SaaS platform access')"
                            className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                        />
                    </div>
                    <div>
                        <label className="flex items-center gap-2 font-technical text-[var(--muted)] mb-2">
                            <Check size={10} strokeWidth={1.5} />PROMISED OUTCOME
                        </label>
                        <input
                            type="text"
                            value={promisedOutcome}
                            onChange={(e) => { setPromisedOutcome(e.target.value); saveData({ promisedOutcome: e.target.value }); }}
                            placeholder="What result will they achieve? (e.g., '10x more leads', 'Clear brand positioning')"
                            className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                        />
                    </div>
                    <div>
                        <label className="flex items-center gap-2 font-technical text-[var(--muted)] mb-2">
                            <Clock size={10} strokeWidth={1.5} />TIME TO VALUE
                        </label>
                        <input
                            type="text"
                            value={timeToValue}
                            onChange={(e) => { setTimeToValue(e.target.value); saveData({ timeToValue: e.target.value }); }}
                            placeholder="How quickly do they see results? (e.g., '2 weeks', 'Same day', 'First month')"
                            className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                        />
                    </div>
                </div>
            </BlueprintCard>

            {/* Pricing Model Selection */}
            <div data-animate>
                <div className="flex items-center gap-3 mb-4">
                    <span className="font-technical text-[var(--blueprint)]">FIG. 02</span>
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    <span className="font-technical text-[var(--muted)]">PRICING MODEL</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                    {PRICING_MODELS.map((model) => {
                        const Icon = model.icon;
                        const isSelected = pricingModel === model.id;
                        return (
                            <button
                                key={model.id}
                                onClick={() => { setPricingModel(model.id); saveData({ pricingModel: model.id }); }}
                                className={`p-4 rounded-[var(--radius-sm)] border text-left transition-all ${isSelected
                                        ? "bg-[var(--blueprint)] border-[var(--blueprint)] text-[var(--paper)]"
                                        : "bg-[var(--canvas)] border-[var(--border)] text-[var(--ink)] hover:border-[var(--blueprint)]"
                                    }`}
                            >
                                <Icon size={18} strokeWidth={1.5} className={isSelected ? "text-[var(--paper)]" : "text-[var(--blueprint)]"} />
                                <h4 className={`text-sm font-semibold mt-2 ${isSelected ? "text-[var(--paper)]" : "text-[var(--ink)]"}`}>
                                    {model.label}
                                </h4>
                                <p className={`text-xs mt-1 ${isSelected ? "text-[var(--paper)]/70" : "text-[var(--muted)]"}`}>
                                    {model.examples}
                                </p>
                            </button>
                        );
                    })}
                </div>

                {/* Model Description - Always visible */}
                <BlueprintCard showCorners padding="md">
                    <label className="flex items-center gap-2 font-technical text-[var(--muted)] mb-2">
                        <ModelIcon size={10} strokeWidth={1.5} />DESCRIBE YOUR PRICING
                    </label>
                    <textarea
                        value={modelDescription}
                        onChange={(e) => { setModelDescription(e.target.value); saveData({ modelDescription: e.target.value }); }}
                        placeholder={
                            pricingModel === "subscription" ? "Describe your subscription tiers, what's included at each level, and billing options..." :
                                pricingModel === "one-time" ? "Describe what's included in your offering, payment terms, and any variations..." :
                                    pricingModel === "usage-based" ? "Describe how usage is measured, pricing per unit, and typical customer usage..." :
                                        "Describe your pricing structure, how different models combine, and any special arrangements..."
                        }
                        className="w-full min-h-[80px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                    />
                </BlueprintCard>
            </div>

            {/* Model-specific fields */}
            {pricingModel === "subscription" && (
                <div data-animate>
                    <div className="flex items-center gap-3 mb-4">
                        <span className="font-technical text-[var(--blueprint)]">FIG. 03</span>
                        <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                        <span className="font-technical text-[var(--muted)]">SUBSCRIPTION OPTIONS</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        {options.map((option) => (
                            <PricingOptionCard
                                key={option.id}
                                option={option}
                                onUpdate={handleUpdateOption}
                                onRemove={handleRemoveOption}
                            />
                        ))}
                    </div>
                    <SecondaryButton onClick={handleAddOption} className="w-full">
                        <Plus size={12} strokeWidth={1.5} />Add Option
                    </SecondaryButton>
                </div>
            )}

            {pricingModel === "usage-based" && (
                <BlueprintCard data-animate figure="FIG. 03" title="Usage-Based Details" code="USAGE" showCorners padding="md">
                    <div className="space-y-4">
                        <div>
                            <label className="font-technical text-[var(--muted)] mb-2 block">UNIT OF MEASUREMENT</label>
                            <input
                                type="text"
                                value={usageUnit}
                                onChange={(e) => { setUsageUnit(e.target.value); saveData({ usageUnit: e.target.value }); }}
                                placeholder="e.g., API calls, Credits, Transactions, Seats"
                                className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                            />
                        </div>
                        <div>
                            <label className="font-technical text-[var(--muted)] mb-2 block">PRICING EXAMPLE</label>
                            <input
                                type="text"
                                value={usageExample}
                                onChange={(e) => { setUsageExample(e.target.value); saveData({ usageExample: e.target.value }); }}
                                placeholder="e.g., $0.01 per API call, $5 per 1000 credits"
                                className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                            />
                        </div>
                        <div>
                            <label className="font-technical text-[var(--muted)] mb-2 block">TYPICAL MONTHLY USAGE</label>
                            <input
                                type="text"
                                value={typicalUsage}
                                onChange={(e) => { setTypicalUsage(e.target.value); saveData({ typicalUsage: e.target.value }); }}
                                placeholder="e.g., Most customers use 500-2000 credits/month (~$50-200)"
                                className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                            />
                        </div>
                    </div>
                </BlueprintCard>
            )}

            {pricingModel === "one-time" && (
                <BlueprintCard data-animate figure="FIG. 03" title="One-Time Details" code="ONETIME" showCorners padding="md">
                    <div className="space-y-4">
                        <div>
                            <label className="font-technical text-[var(--muted)] mb-2 block">WHAT&apos;S INCLUDED</label>
                            <textarea
                                value={whatsIncluded}
                                onChange={(e) => { setWhatsIncluded(e.target.value); saveData({ whatsIncluded: e.target.value }); }}
                                placeholder="List everything included in the purchase..."
                                className="w-full min-h-[80px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                            />
                        </div>
                        <div>
                            <label className="font-technical text-[var(--muted)] mb-2 block">PAYMENT TERMS</label>
                            <input
                                type="text"
                                value={paymentTerms}
                                onChange={(e) => { setPaymentTerms(e.target.value); saveData({ paymentTerms: e.target.value }); }}
                                placeholder="e.g., 50% upfront, 50% on delivery; Net 30; Payment plans available"
                                className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                            />
                        </div>
                    </div>
                </BlueprintCard>
            )}

            {/* Guarantees - Always show */}
            <BlueprintCard data-animate figure={pricingModel === "subscription" ? "FIG. 04" : "FIG. 04"} title="Guarantees & Risk Reversals" code="GUAR" showCorners padding="md">
                <textarea
                    value={guarantees}
                    onChange={(e) => { setGuarantees(e.target.value); saveData({ guarantees: e.target.value }); }}
                    placeholder="Money-back guarantee, satisfaction promise, SLA commitments, free trial period..."
                    className="w-full min-h-[80px] p-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                />
            </BlueprintCard>

            {/* Confirm */}
            {!confirmed ? (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                    <Check size={14} strokeWidth={1.5} />Confirm Offer
                </BlueprintButton>
            ) : (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3">
                        <Check size={18} strokeWidth={1.5} className="text-[var(--success)]" />
                        <span className="text-sm font-medium text-[var(--ink)]">Offer structure confirmed</span>
                        <BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">OFFER-PRICING • STEP 06/25</span>
            </div>
        </div>
    );
}
