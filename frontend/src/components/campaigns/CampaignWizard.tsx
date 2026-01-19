"use client";

import { useState } from "react";
import { X, ArrowRight, Zap, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { useBCMStore } from "@/stores/bcmStore";

/* ══════════════════════════════════════════════════════════════════════════════
   CAMPAIGN WIZARD — RaptorFlow Quiet Luxury
   4-step campaign creation with editorial styling
   ══════════════════════════════════════════════════════════════════════════════ */

interface CampaignWizardProps {
    isOpen: boolean;
    onClose: () => void;
    onComplete: (campaign: {
        name: string;
        goal: string;
        objective: string;
        duration: string;
        intensity: string;
        icp: string;
        channels: string[];
    }) => void;
}

interface FormData {
    objective: string;
    context: string;
    duration: string;
    intensity: string;
    icp: string;
    channels: string[];
}

const OBJECTIVES = [
    "Market Entry (Launch)",
    "Revenue Scaling",
    "Brand Pivot",
    "Customer Retention",
    "Crisis Management",
    "Product Testing"
];

const DURATIONS = ["30 Days", "60 Days", "90 Days"];

const CHANNELS = [
    "LinkedIn",
    "X (Twitter)",
    "Email",
    "Instagram",
    "YouTube",
    "SEO / Blog",
    "Paid Ads"
];

const ICP_OPTIONS = [
    { value: "Founders", label: "Founders / CEOs" },
    { value: "CTOs", label: "Technical Leads / CTOs" },
    { value: "Marketers", label: "CMOs / Growth Heads" },
    { value: "Investors", label: "VCs / Angels" }
];

export function CampaignWizard({ isOpen, onClose, onComplete }: CampaignWizardProps) {
    const { bcm } = useBCMStore();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState<FormData>({
        objective: "",
        context: "",
        duration: "60 Days",
        intensity: "Marathon",
        icp: "",
        channels: []
    });

    // Get ICP options from BCM or fallback to defaults
    const getICPOptions = () => {
        if (bcm?.icps && bcm.icps.length > 0) {
            return bcm.icps.map((icp: any, index: number) => ({
                value: icp.id || `icp-${index}`,
                label: icp.name || `ICP ${index + 1}`
            }));
        }
        return ICP_OPTIONS;
    };

    // Get suggested channels from BCM competitive data
    const getSuggestedChannels = () => {
        // Could be enhanced with BCM competitive analysis
        return CHANNELS;
    };

    if (!isOpen) return null;

    const nextStep = () => setStep(step + 1);
    const prevStep = () => setStep(step - 1);

    const handleChannelToggle = (ch: string) => {
        setFormData(prev => ({
            ...prev,
            channels: prev.channels.includes(ch)
                ? prev.channels.filter(c => c !== ch)
                : [...prev.channels, ch]
        }));
    };

    const handleComplete = () => {
        // Enhance campaign data with BCM insights
        const companyName = bcm?.foundation?.company || "Your Company";
        const brandVoice = bcm?.messaging?.brand_voice?.tone?.join(', ') || "Professional";
        const valueProps = bcm?.messaging?.value_props || [];
        
        onComplete({
            name: `${companyName}: ${formData.objective} Campaign`,
            goal: formData.context || `${formData.objective} for ${companyName}`,
            objective: formData.objective,
            duration: formData.duration,
            intensity: formData.intensity,
            icp: formData.icp,
            channels: formData.channels
        });
        setStep(1);
        setFormData({
            objective: "",
            context: "",
            duration: "60 Days",
            intensity: "Marathon",
            icp: "",
            channels: []
        });
    };

    return (
        <div className="fixed inset-0 bg-[var(--canvas)]/98 backdrop-blur-md z-50 flex flex-col animate-in fade-in duration-200">
            {/* Header */}
            <div className="h-16 border-b border-[var(--structure)] flex items-center justify-between px-8 bg-[var(--canvas)]">
                <div className="flex items-center gap-4">
                    <span className="font-technical text-[var(--blueprint)] text-xs">NEW_CAMPAIGN</span>
                    <div className="h-px w-6 bg-[var(--structure)]" />
                    <span className="font-technical text-[var(--ink-muted)] text-xs">STEP {step} OF 4</span>
                </div>
                <button
                    onClick={onClose}
                    className="p-2 hover:bg-[var(--surface)] rounded-lg text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
                >
                    <X size={20} />
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 flex items-center justify-center p-8 bg-[var(--surface-subtle)]">
                <div className="w-full max-w-2xl">

                    {/* STEP 1: OBJECTIVE */}
                    {step === 1 && (
                        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-300">
                            <div>
                                <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">What is the Strategic Objective?</h2>
                                <p className="text-[var(--secondary)]">Define the primary outcome for this campaign.</p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                {OBJECTIVES.map(obj => (
                                    <BlueprintCard
                                        key={obj}
                                        onClick={() => setFormData({ ...formData, objective: obj })}
                                        className={cn(
                                            "cursor-pointer hover:border-[var(--blueprint)] transition-all",
                                            formData.objective === obj && "border-[var(--blueprint)] bg-[var(--blueprint-light)]"
                                        )}
                                        padding="md"
                                        showCorners={formData.objective === obj}
                                    >
                                        <h3 className="font-semibold text-lg mb-1 text-[var(--ink)]">{obj.split(" (")[0]}</h3>
                                        <span className="font-technical text-[9px] text-[var(--muted)] uppercase tracking-widest">
                                            {obj.includes("(") ? obj.split(" (")[1].replace(")", "") : "General"}
                                        </span>
                                    </BlueprintCard>
                                ))}
                            </div>

                            <div>
                                <label className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider block mb-2">
                                    Context (Why now?)
                                </label>
                                <textarea
                                    value={formData.context}
                                    onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                                    className="w-full h-24 p-4 text-sm resize-none bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
                                    placeholder="e.g. Competitor just raised prices, Q4 budget available..."
                                />
                            </div>
                        </div>
                    )}

                    {/* STEP 2: CONSTRAINTS */}
                    {step === 2 && (
                        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-300">
                            <div>
                                <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Define Operational Constraints</h2>
                                <p className="text-[var(--secondary)]">How much time and intensity are we committing?</p>
                            </div>

                            <div>
                                <label className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider block mb-4">
                                    Time Horizon
                                </label>
                                <div className="flex gap-4">
                                    {DURATIONS.map(d => (
                                        <button
                                            key={d}
                                            onClick={() => setFormData({ ...formData, duration: d })}
                                            className={cn(
                                                "flex-1 py-4 border rounded-[var(--radius)] text-center font-semibold transition-all",
                                                formData.duration === d
                                                    ? "bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]"
                                                    : "bg-[var(--paper)] border-[var(--structure)] text-[var(--secondary)] hover:border-[var(--ink-muted)]"
                                            )}
                                        >
                                            {d}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider block mb-4">
                                    Execution Intensity
                                </label>
                                <div className="grid grid-cols-2 gap-4">
                                    <BlueprintCard
                                        onClick={() => setFormData({ ...formData, intensity: "Sprint" })}
                                        className={cn(
                                            "cursor-pointer",
                                            formData.intensity === "Sprint" && "border-[var(--blueprint)] bg-[var(--blueprint-light)]"
                                        )}
                                        padding="md"
                                        showCorners={formData.intensity === "Sprint"}
                                    >
                                        <div className="flex items-center gap-2 mb-2">
                                            <Zap size={18} className="text-[var(--ink)]" />
                                            <span className="font-semibold text-[var(--ink)]">Sprint Mode</span>
                                        </div>
                                        <p className="text-xs text-[var(--secondary)]">High volume, short duration. "Break things."</p>
                                    </BlueprintCard>
                                    <BlueprintCard
                                        onClick={() => setFormData({ ...formData, intensity: "Marathon" })}
                                        className={cn(
                                            "cursor-pointer",
                                            formData.intensity === "Marathon" && "border-[var(--blueprint)] bg-[var(--blueprint-light)]"
                                        )}
                                        padding="md"
                                        showCorners={formData.intensity === "Marathon"}
                                    >
                                        <div className="flex items-center gap-2 mb-2">
                                            <Activity size={18} className="text-[var(--ink)]" />
                                            <span className="font-semibold text-[var(--ink)]">Marathon Mode</span>
                                        </div>
                                        <p className="text-xs text-[var(--secondary)]">Steady, compounding growth. "Build systems."</p>
                                    </BlueprintCard>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: TARGETING */}
                    {step === 3 && (
                        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-300">
                            <div>
                                <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Target Acquisition</h2>
                                <p className="text-[var(--secondary)]">Who are we reaching and where?</p>
                            </div>

                            <div>
                                <label className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider block mb-2">
                                    Ideal Customer Profile (ICP)
                                </label>
                                <select
                                    value={formData.icp}
                                    onChange={(e) => setFormData({ ...formData, icp: e.target.value })}
                                    className="w-full p-3 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
                                >
                                    <option value="">Select Primary Persona...</option>
                                    {getICPOptions().map(opt => (
                                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider block mb-4">
                                    Channel Vectors
                                </label>
                                <div className="flex flex-wrap gap-3">
                                    {CHANNELS.map(ch => (
                                        <button
                                            key={ch}
                                            onClick={() => handleChannelToggle(ch)}
                                            className={cn(
                                                "px-4 py-2 border rounded-full text-sm transition-all",
                                                formData.channels.includes(ch)
                                                    ? "bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]"
                                                    : "bg-[var(--paper)] border-[var(--structure)] text-[var(--secondary)]"
                                            )}
                                        >
                                            {ch}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STEP 4: REVIEW */}
                    {step === 4 && (
                        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-300">
                            <div>
                                <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Confirm Strategy</h2>
                                <p className="text-[var(--secondary)]">Review your campaign configuration.</p>
                            </div>

                            <BlueprintCard padding="lg" showCorners className="bg-[var(--surface)]">
                                <div className="flex justify-between items-start mb-6 border-b border-[var(--structure)] pb-4">
                                    <div>
                                        <div className="font-technical text-[9px] text-[var(--muted)] uppercase tracking-wider mb-1">Campaign Archetype</div>
                                        <h3 className="font-serif text-xl text-[var(--ink)]">{formData.objective}</h3>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-technical text-[9px] text-[var(--muted)] uppercase tracking-wider mb-1">Duration</div>
                                        <h3 className="text-xl font-semibold text-[var(--ink)]">{formData.duration}</h3>
                                    </div>
                                </div>

                                <div className="space-y-4 relative pl-4">
                                    <div className="absolute left-[15px] top-2 bottom-2 w-px bg-[var(--structure)]" />

                                    <div className="flex items-center gap-4 relative">
                                        <div className="w-8 h-8 rounded-full bg-[var(--ink)] flex items-center justify-center font-semibold text-sm text-[var(--paper)] z-10">1</div>
                                        <div className="flex-1 p-3 border border-[var(--structure)] rounded-[var(--radius)] bg-[var(--paper)]">
                                            <h4 className="font-semibold text-sm text-[var(--ink)]">Phase 1: Positioning</h4>
                                            <p className="text-xs text-[var(--secondary)]">Establish the wedge against competitors.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4 relative">
                                        <div className="w-8 h-8 rounded-full bg-[var(--ink)] flex items-center justify-center font-semibold text-sm text-[var(--paper)] z-10">2</div>
                                        <div className="flex-1 p-3 border border-[var(--structure)] rounded-[var(--radius)] bg-[var(--paper)]">
                                            <h4 className="font-semibold text-sm text-[var(--ink)]">Phase 2: Validation</h4>
                                            <p className="text-xs text-[var(--secondary)]">Targeting {formData.icp || "Primary ICP"} via {formData.channels[0] || "Selected Channels"}.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4 relative">
                                        <div className="w-8 h-8 rounded-full bg-[var(--ink)] flex items-center justify-center font-semibold text-sm text-[var(--paper)] z-10">3</div>
                                        <div className="flex-1 p-3 border border-[var(--structure)] rounded-[var(--radius)] bg-[var(--paper)]">
                                            <h4 className="font-semibold text-sm text-[var(--ink)]">Phase 3: Scale</h4>
                                            <p className="text-xs text-[var(--secondary)]">{formData.intensity} execution across all vectors.</p>
                                        </div>
                                    </div>
                                </div>
                            </BlueprintCard>
                        </div>
                    )}

                    {/* Footer Nav */}
                    <div className="flex justify-between mt-8 pt-8 border-t border-[var(--structure-subtle)]">
                        {step > 1 ? (
                            <SecondaryButton onClick={prevStep}>Back</SecondaryButton>
                        ) : (
                            <div />
                        )}
                        <BlueprintButton
                            onClick={step === 4 ? handleComplete : nextStep}
                            disabled={step === 1 && !formData.objective}
                        >
                            {step === 4 ? "Launch Campaign" : "Next Step"}
                            {step !== 4 && <ArrowRight size={14} />}
                        </BlueprintButton>
                    </div>
                </div>
            </div>
        </div>
    );
}
