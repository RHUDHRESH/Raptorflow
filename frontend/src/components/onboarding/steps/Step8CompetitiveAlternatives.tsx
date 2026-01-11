"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Check, Plus, Shield, Zap, Target, Trash2, Edit2, ChevronDown, ChevronUp,
    Play, RefreshCw, AlertTriangle, X, Swords, ArrowLeftRight
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { StepLoadingState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 8: Competitive Alternatives Map

   PURPOSE: Map all customer alternatives (not just direct competitors)
   - Status Quo (doing nothing / manual)
   - Indirect alternatives (agencies, freelancers, other solutions)
   - Direct competitors (similar products)
   - Note each alternative's core promise, appeal, and weakness
   ══════════════════════════════════════════════════════════════════════════════ */

// Types
interface Alternative {
    id: string;
    name: string;
    type: "direct" | "indirect" | "status-quo";
    corePromise: string;
    appeal: string;
    weakness: string;
    threatLevel: "high" | "medium" | "low";
    code: string;
    // Enhanced fields
    yourLeverage?: string;      // Your advantages over them
    theirLeverage?: string;     // Their advantages over you
    switchTriggers?: string;    // What makes customers switch to/from them
}

interface AlternativesResult {
    alternatives: Alternative[];
    matrix: { dimension: string; you: string; alternatives: Record<string, string> }[];
    confirmed: boolean;
}

// Detail Modal Component
function AlternativeDetailModal({
    alt,
    onClose,
    onSave
}: {
    alt: Alternative;
    onClose: () => void;
    onSave: (alt: Alternative) => void;
}) {
    const [editData, setEditData] = useState(alt);
    const [isEditing, setIsEditing] = useState(false);

    const typeConfig = {
        "status-quo": { icon: Shield, label: "STATUS QUO", color: "text-[var(--muted)]", bg: "bg-[var(--canvas)]" },
        indirect: { icon: Zap, label: "INDIRECT", color: "text-[var(--warning)]", bg: "bg-[var(--warning-light)]" },
        direct: { icon: Target, label: "DIRECT", color: "text-[var(--error)]", bg: "bg-[var(--error-light)]" },
    };
    const config = typeConfig[alt.type];
    const Icon = config.icon;

    const handleSave = () => {
        onSave(editData);
        setIsEditing(false);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[var(--ink)]/50 backdrop-blur-sm">
            <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-[var(--paper)] rounded-[var(--radius-md)] border border-[var(--border)] shadow-xl">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-[var(--border)]">
                    <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-[var(--radius-sm)] ${config.bg} flex items-center justify-center ${config.color}`}>
                            <Icon size={18} strokeWidth={1.5} />
                        </div>
                        <div>
                            <h2 className="text-lg font-serif text-[var(--ink)]">{alt.name}</h2>
                            <span className="font-technical text-[var(--muted)]">{config.label} • {alt.code}</span>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 text-[var(--muted)] hover:text-[var(--ink)] rounded-[var(--radius-sm)] hover:bg-[var(--canvas)] transition-all">
                        <X size={18} strokeWidth={1.5} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {isEditing ? (
                        <div className="space-y-4">
                            <div>
                                <label className="font-technical text-[var(--muted)] text-[10px] block mb-2">ALTERNATIVE NAME</label>
                                <input
                                    type="text"
                                    value={editData.name}
                                    onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                                    className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                />
                            </div>
                            <div>
                                <label className="font-technical text-[var(--muted)] text-[10px] block mb-2">CORE PROMISE</label>
                                <input
                                    type="text"
                                    value={editData.corePromise}
                                    onChange={(e) => setEditData({ ...editData, corePromise: e.target.value })}
                                    placeholder="What they promise to customers"
                                    className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="font-technical text-[var(--muted)] text-[10px] block mb-2">THEIR APPEAL</label>
                                    <textarea
                                        value={editData.appeal}
                                        onChange={(e) => setEditData({ ...editData, appeal: e.target.value })}
                                        placeholder="Why customers choose them"
                                        className="w-full min-h-[80px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                    />
                                </div>
                                <div>
                                    <label className="font-technical text-[var(--muted)] text-[10px] block mb-2">THEIR WEAKNESS</label>
                                    <textarea
                                        value={editData.weakness}
                                        onChange={(e) => setEditData({ ...editData, weakness: e.target.value })}
                                        placeholder="Where they fall short"
                                        className="w-full min-h-[80px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="font-technical text-[var(--success)] text-[10px] flex items-center gap-1 mb-2">
                                        <Swords size={10} />YOUR LEVERAGE
                                    </label>
                                    <textarea
                                        value={editData.yourLeverage || ""}
                                        onChange={(e) => setEditData({ ...editData, yourLeverage: e.target.value })}
                                        placeholder="Your advantages over them"
                                        className="w-full min-h-[80px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                    />
                                </div>
                                <div>
                                    <label className="font-technical text-[var(--error)] text-[10px] flex items-center gap-1 mb-2">
                                        <Swords size={10} className="rotate-180" />THEIR LEVERAGE
                                    </label>
                                    <textarea
                                        value={editData.theirLeverage || ""}
                                        onChange={(e) => setEditData({ ...editData, theirLeverage: e.target.value })}
                                        placeholder="Their advantages over you"
                                        className="w-full min-h-[80px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="font-technical text-[var(--blueprint)] text-[10px] flex items-center gap-1 mb-2">
                                    <ArrowLeftRight size={10} />SWITCH TRIGGERS
                                </label>
                                <textarea
                                    value={editData.switchTriggers || ""}
                                    onChange={(e) => setEditData({ ...editData, switchTriggers: e.target.value })}
                                    placeholder="What makes customers switch to/from this alternative"
                                    className="w-full min-h-[60px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                />
                            </div>
                            <div className="flex gap-2 pt-2">
                                <BlueprintButton size="sm" onClick={handleSave} className="flex-1">Save Changes</BlueprintButton>
                                <SecondaryButton size="sm" onClick={() => setIsEditing(false)}>Cancel</SecondaryButton>
                            </div>
                        </div>
                    ) : (
                        <>
                            {/* Core Promise */}
                            <div className="p-4 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                <span className="font-technical text-[var(--muted)] text-[10px] block mb-1">CORE PROMISE</span>
                                <p className="text-sm text-[var(--ink)]">{alt.corePromise || "Not defined"}</p>
                            </div>

                            {/* Appeal & Weakness */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-[var(--radius-sm)] bg-[var(--success-light)] border border-[var(--success)]/20">
                                    <span className="font-technical text-[var(--success)] text-[10px] block mb-1">THEIR APPEAL</span>
                                    <p className="text-sm text-[var(--ink)]">{alt.appeal || "Not analyzed"}</p>
                                </div>
                                <div className="p-4 rounded-[var(--radius-sm)] bg-[var(--error-light)] border border-[var(--error)]/20">
                                    <span className="font-technical text-[var(--error)] text-[10px] block mb-1">THEIR WEAKNESS</span>
                                    <p className="text-sm text-[var(--ink)]">{alt.weakness || "Not analyzed"}</p>
                                </div>
                            </div>

                            {/* Leverage Comparison */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-[var(--radius-sm)] border border-[var(--border-subtle)]">
                                    <span className="font-technical text-[var(--success)] text-[10px] flex items-center gap-1 mb-1">
                                        <Swords size={10} />YOUR LEVERAGE
                                    </span>
                                    <p className="text-sm text-[var(--secondary)]">{alt.yourLeverage || "Add your advantages..."}</p>
                                </div>
                                <div className="p-4 rounded-[var(--radius-sm)] border border-[var(--border-subtle)]">
                                    <span className="font-technical text-[var(--error)] text-[10px] flex items-center gap-1 mb-1">
                                        <Swords size={10} className="rotate-180" />THEIR LEVERAGE
                                    </span>
                                    <p className="text-sm text-[var(--secondary)]">{alt.theirLeverage || "Add their advantages..."}</p>
                                </div>
                            </div>

                            {/* Switch Triggers */}
                            <div className="p-4 rounded-[var(--radius-sm)] bg-[var(--blueprint-light)] border border-[var(--blueprint)]/20">
                                <span className="font-technical text-[var(--blueprint)] text-[10px] flex items-center gap-1 mb-1">
                                    <ArrowLeftRight size={10} />SWITCH TRIGGERS
                                </span>
                                <p className="text-sm text-[var(--ink)]">{alt.switchTriggers || "What makes customers switch to/from this alternative?"}</p>
                            </div>

                            <SecondaryButton onClick={() => setIsEditing(true)} className="w-full">
                                <Edit2 size={12} strokeWidth={1.5} />Edit Details
                            </SecondaryButton>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

function AlternativeCard({
    alt,
    onEdit,
    onRemove,
    onClick,
    isEditing,
    onSave,
    onCancel
}: {
    alt: Alternative;
    onEdit: (id: string) => void;
    onRemove: (id: string) => void;
    onClick: (alt: Alternative) => void;
    isEditing: boolean;
    onSave: (alt: Alternative) => void;
    onCancel: () => void;
}) {
    const [editData, setEditData] = useState(alt);

    const typeConfig = {
        "status-quo": { icon: Shield, variant: "default" as const, label: "STATUS QUO", color: "text-[var(--muted)]" },
        indirect: { icon: Zap, variant: "warning" as const, label: "INDIRECT", color: "text-[var(--warning)]" },
        direct: { icon: Target, variant: "error" as const, label: "DIRECT", color: "text-[var(--error)]" },
    };
    const config = typeConfig[alt.type];
    const Icon = config.icon;

    const threatConfig = {
        high: { label: "HIGH THREAT", variant: "error" as const },
        medium: { label: "MEDIUM", variant: "warning" as const },
        low: { label: "LOW", variant: "default" as const },
    };

    if (isEditing) {
        return (
            <BlueprintCard code="EDIT" showCorners padding="md" className="border-[var(--blueprint)]">
                <div className="space-y-4">
                    <input
                        type="text"
                        value={editData.name}
                        onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                        className="w-full h-10 px-4 text-sm font-semibold bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Alternative name"
                    />
                    <div className="flex gap-2">
                        {(["status-quo", "indirect", "direct"] as const).map((type) => (
                            <button
                                key={type}
                                onClick={() => setEditData({ ...editData, type })}
                                className={`flex-1 px-3 py-2 font-technical text-[10px] rounded-[var(--radius-sm)] capitalize transition-all ${editData.type === type
                                    ? "bg-[var(--blueprint)] text-[var(--paper)]"
                                    : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)]"
                                    }`}
                            >
                                {type.replace("-", " ")}
                            </button>
                        ))}
                    </div>
                    <input
                        type="text"
                        value={editData.corePromise}
                        onChange={(e) => setEditData({ ...editData, corePromise: e.target.value })}
                        className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Core promise (what they claim)"
                    />
                    <input
                        type="text"
                        value={editData.appeal}
                        onChange={(e) => setEditData({ ...editData, appeal: e.target.value })}
                        className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Appeal (why customers choose them)"
                    />
                    <input
                        type="text"
                        value={editData.weakness}
                        onChange={(e) => setEditData({ ...editData, weakness: e.target.value })}
                        className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        placeholder="Weakness (their limitation)"
                    />
                    <div className="flex gap-2">
                        <span className="font-technical text-[var(--muted)] self-center">THREAT:</span>
                        {(["low", "medium", "high"] as const).map((level) => (
                            <button
                                key={level}
                                onClick={() => setEditData({ ...editData, threatLevel: level })}
                                className={`px-3 py-1.5 font-technical text-[10px] rounded-[var(--radius-sm)] capitalize transition-all ${editData.threatLevel === level
                                    ? `bg-[var(--${level === "high" ? "error" : level === "medium" ? "warning" : "muted"})] text-[var(--paper)]`
                                    : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)]"
                                    }`}
                            >
                                {level}
                            </button>
                        ))}
                    </div>
                    <div className="flex gap-2">
                        <BlueprintButton size="sm" onClick={() => onSave(editData)}>Save</BlueprintButton>
                        <SecondaryButton size="sm" onClick={onCancel}>Cancel</SecondaryButton>
                    </div>
                </div>
            </BlueprintCard>
        );
    }

    return (
        <BlueprintCard code={alt.code} showCorners padding="md" className="cursor-pointer hover:border-[var(--blueprint)] transition-all" onClick={() => onClick(alt)}>
            <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center flex-shrink-0 ${config.color}`}>
                    <Icon size={18} strokeWidth={1.5} />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-sm font-semibold text-[var(--ink)]">{alt.name}</h3>
                        <BlueprintBadge variant={config.variant}>{config.label}</BlueprintBadge>
                        <BlueprintBadge variant={threatConfig[alt.threatLevel].variant} className="text-[8px]">
                            {threatConfig[alt.threatLevel].label}
                        </BlueprintBadge>
                    </div>
                    <p className="text-xs text-[var(--secondary)] mb-1">{alt.corePromise}</p>
                    <span className="font-technical text-[10px] text-[var(--blueprint)]">CLICK FOR DETAILS →</span>
                </div>
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                    <button
                        onClick={() => onEdit(alt.id)}
                        className="p-1.5 text-[var(--muted)] hover:text-[var(--blueprint)] hover:bg-[var(--canvas)] rounded-[var(--radius-xs)] transition-all"
                    >
                        <Edit2 size={12} strokeWidth={1.5} />
                    </button>
                    <button
                        onClick={() => onRemove(alt.id)}
                        className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] hover:bg-[var(--error-light)] rounded-[var(--radius-xs)] transition-all"
                    >
                        <Trash2 size={12} strokeWidth={1.5} />
                    </button>
                </div>
            </div>
        </BlueprintCard>
    );
}

export default function Step8CompetitiveAlternatives() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const step7Data = getStepById(7)?.data as { competitors?: any[] } | undefined;
    const stepData = getStepById(8)?.data as AlternativesResult | undefined;

    const [isGenerating, setIsGenerating] = useState(false);
    const [alternatives, setAlternatives] = useState<Alternative[]>(stepData?.alternatives || []);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [isAdding, setIsAdding] = useState(false);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [selectedAlt, setSelectedAlt] = useState<Alternative | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const hasData = alternatives.length > 0;

    // Initialize from Step 7 if available
    useEffect(() => {
        if (alternatives.length === 0 && step7Data?.competitors) {
            const converted: Alternative[] = step7Data.competitors.map((c: any, i: number) => ({
                id: c.id || `alt-${i}`,
                name: c.name,
                type: c.type || "direct",
                corePromise: c.coreClaim || "",
                appeal: c.strengths?.[0] || "",
                weakness: c.weaknesses?.[0] || "",
                threatLevel: "medium" as const,
                code: `ALT-${String(i + 1).padStart(2, "0")}`,
            }));
            setAlternatives(converted);
            updateStepData(8, { alternatives: converted });
        }
    }, [step7Data, alternatives.length, updateStepData]);

    // Animation
    useEffect(() => {
        if (!containerRef.current || isGenerating) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, [hasData, isGenerating]);

    // Generate from AI
    const generateAlternatives = useCallback(async () => {
        if (!session?.sessionId) return;
        setIsGenerating(true);

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            const res = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/8/run`,
                {
                    method: "POST",
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            );

            if (res.ok) {
                const pollInterval = setInterval(async () => {
                    const statusRes = await fetch(
                        `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/8`,
                        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
                    );
                    if (statusRes.ok) {
                        const data = await statusRes.json();
                        if (data?.data?.alternatives) {
                            clearInterval(pollInterval);
                            setAlternatives(data.data.alternatives);
                            updateStepData(8, data.data);
                            setIsGenerating(false);
                        }
                    }
                }, 2000);

                setTimeout(() => {
                    clearInterval(pollInterval);
                    if (isGenerating) {
                        const mock = generateMockAlternatives();
                        setAlternatives(mock);
                        updateStepData(8, { alternatives: mock });
                        setIsGenerating(false);
                    }
                }, 20000);
            }
        } catch (error) {
            console.error("Generation error:", error);
            const mock = generateMockAlternatives();
            setAlternatives(mock);
            updateStepData(8, { alternatives: mock });
            setIsGenerating(false);
        }
    }, [session, updateStepData, isGenerating]);

    const generateMockAlternatives = (): Alternative[] => [
        { id: "1", name: "Manual / Spreadsheets", type: "status-quo", corePromise: "Free and flexible", appeal: "No learning curve, familiar tools", weakness: "Time-consuming, no strategic guidance", threatLevel: "medium", code: "ALT-01" },
        { id: "2", name: "Marketing Agencies", type: "indirect", corePromise: "Done-for-you expertise", appeal: "No internal work needed", weakness: "Expensive, slow turnaround, loss of control", threatLevel: "high", code: "ALT-02" },
        { id: "3", name: "Freelance Consultants", type: "indirect", corePromise: "Expert advice at lower cost", appeal: "Personalized attention", weakness: "Variable quality, not scalable", threatLevel: "medium", code: "ALT-03" },
        { id: "4", name: "HubSpot / Marketo", type: "direct", corePromise: "All-in-one marketing platform", appeal: "Feature-rich, established brand", weakness: "Complex, expensive, overkill for SMBs", threatLevel: "high", code: "ALT-04" },
    ];

    const handleSaveEdit = (alt: Alternative) => {
        const updated = alternatives.map(a => a.id === alt.id ? alt : a);
        setAlternatives(updated);
        updateStepData(8, { alternatives: updated });
        setEditingId(null);
    };

    const handleRemove = (id: string) => {
        const updated = alternatives.filter(a => a.id !== id);
        setAlternatives(updated);
        updateStepData(8, { alternatives: updated });
    };

    const handleAddNew = () => {
        const newAlt: Alternative = {
            id: `alt-${Date.now()}`,
            name: "New Alternative",
            type: "direct",
            corePromise: "",
            appeal: "",
            weakness: "",
            threatLevel: "medium",
            code: `ALT-${String(alternatives.length + 1).padStart(2, "0")}`,
        };
        setAlternatives([...alternatives, newAlt]);
        setEditingId(newAlt.id);
        setIsAdding(false);
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(8, { alternatives, confirmed: true });
        updateStepStatus(8, "complete");
    };

    // Group by type
    const byType = {
        "status-quo": alternatives.filter(a => a.type === "status-quo"),
        indirect: alternatives.filter(a => a.type === "indirect"),
        direct: alternatives.filter(a => a.type === "direct"),
    };

    // Stats
    const highThreatCount = alternatives.filter(a => a.threatLevel === "high").length;

    if (isGenerating) {
        return (
            <StepLoadingState
                title="Mapping Competitive Landscape"
                message="Analyzing alternatives from customer perspective..."
                stage="Identifying status quo, indirect, and direct competitors..."
            />
        );
    }

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Description */}
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <p className="text-sm text-[var(--secondary)]">
                    Map all alternatives your customers consider — not just direct competitors.
                    Include status quo (doing nothing) and indirect solutions.
                </p>
            </BlueprintCard>

            {/* Stats */}
            {hasData && (
                <div data-animate className="grid grid-cols-4 gap-4">
                    <BlueprintCard showCorners padding="sm" className="text-center">
                        <span className="block font-serif text-2xl text-[var(--ink)]">{alternatives.length}</span>
                        <span className="font-technical text-[8px] text-[var(--muted)]">TOTAL</span>
                    </BlueprintCard>
                    <BlueprintCard showCorners padding="sm" className="text-center">
                        <span className="block font-serif text-2xl text-[var(--muted)]">{byType["status-quo"].length}</span>
                        <span className="font-technical text-[8px] text-[var(--muted)]">STATUS QUO</span>
                    </BlueprintCard>
                    <BlueprintCard showCorners padding="sm" className="text-center">
                        <span className="block font-serif text-2xl text-[var(--warning)]">{byType.indirect.length}</span>
                        <span className="font-technical text-[8px] text-[var(--muted)]">INDIRECT</span>
                    </BlueprintCard>
                    <BlueprintCard showCorners padding="sm" className="text-center">
                        <span className="block font-serif text-2xl text-[var(--error)]">{byType.direct.length}</span>
                        <span className="font-technical text-[8px] text-[var(--muted)]">DIRECT</span>
                    </BlueprintCard>
                </div>
            )}

            {/* High threat warning */}
            {highThreatCount > 0 && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--error)]/30 bg-[var(--error-light)]">
                    <div className="flex items-center gap-3">
                        <AlertTriangle size={16} className="text-[var(--error)]" />
                        <span className="text-sm text-[var(--ink)]">
                            <strong>{highThreatCount} high-threat</strong> alternative{highThreatCount > 1 ? "s" : ""} identified
                        </span>
                    </div>
                </BlueprintCard>
            )}

            {/* Alternatives List */}
            <div data-animate className="space-y-3">
                {alternatives.map((alt) => (
                    <AlternativeCard
                        key={alt.id}
                        alt={alt}
                        onEdit={setEditingId}
                        onRemove={handleRemove}
                        onClick={setSelectedAlt}
                        isEditing={editingId === alt.id}
                        onSave={handleSaveEdit}
                        onCancel={() => setEditingId(null)}
                    />
                ))}
            </div>

            {/* Detail Modal */}
            {selectedAlt && (
                <AlternativeDetailModal
                    alt={selectedAlt}
                    onClose={() => setSelectedAlt(null)}
                    onSave={(updated) => {
                        handleSaveEdit(updated);
                        setSelectedAlt(null);
                    }}
                />
            )}

            {/* Add Button */}
            <SecondaryButton data-animate onClick={handleAddNew} className="w-full">
                <Plus size={12} strokeWidth={1.5} />
                Add Alternative
            </SecondaryButton>

            {/* Confirm */}
            {!confirmed && alternatives.length >= 3 ? (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                    <Check size={14} strokeWidth={1.5} />
                    Confirm Alternatives Map
                </BlueprintButton>
            ) : null}

            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3">
                        <Check size={18} strokeWidth={1.5} className="text-[var(--success)]" />
                        <span className="text-sm font-medium text-[var(--ink)]">{alternatives.length} alternatives mapped</span>
                        <BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">
                    COMPETITIVE-ALTERNATIVES • STEP 07/24 • {alternatives.length} ITEMS
                </span>
            </div>
        </div>
    );
}
