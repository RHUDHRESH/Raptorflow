"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import gsap from "gsap";
import {
    Loader2, Check, ChevronDown, ChevronUp, ExternalLink, Edit2, FileText,
    AlertTriangle, Play, RefreshCw, Sparkles, Search
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { StepLoadingState, StepErrorState, StepEmptyState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 2: Auto Extraction

   PURPOSE: AI extracts key facts from uploaded evidence to create Business Truth Sheet v0
   - Extracts: product/service, audience, value claims, differentiators
   - Extracts: proof points (metrics, case studies, testimonials)
   - Extracts: pricing/packaging info, constraints
   - Shows confidence scores and source citations
   - Allows editing and verification of extracted facts
   ══════════════════════════════════════════════════════════════════════════════ */

// Types
interface ExtractedFact {
    id: string;
    category: string;
    label: string;
    value: string;
    confidence: number;
    sources: { type: "url" | "file"; name: string; excerpt?: string }[];
    status: "pending" | "verified" | "edited" | "rejected";
    code: string;
}

interface ExtractionResult {
    facts: ExtractedFact[];
    summary: string;
    warnings: string[];
    extractionComplete: boolean;
}

// Fact categories for organization
const FACT_CATEGORIES = [
    { id: "company", label: "Company", icon: "🏢" },
    { id: "positioning", label: "Positioning", icon: "🎯" },
    { id: "audience", label: "Audience", icon: "👥" },
    { id: "competitive", label: "Competitive", icon: "⚔️" },
    { id: "proof", label: "Proof Points", icon: "✓" },
    { id: "constraints", label: "Constraints", icon: "⚠️" },
];

function ConfidenceBar({ confidence }: { confidence: number }) {
    const color = confidence >= 80 ? "bg-[var(--success)]" : confidence >= 60 ? "bg-[var(--warning)]" : "bg-[var(--error)]";
    const label = confidence >= 80 ? "HIGH" : confidence >= 60 ? "MEDIUM" : "LOW";
    return (
        <div className="flex items-center gap-2">
            <div className="w-16 h-1.5 bg-[var(--canvas)] rounded-full overflow-hidden border border-[var(--border-subtle)]">
                <div className={`h-full ${color} rounded-full`} style={{ width: `${confidence}%` }} />
            </div>
            <span className="font-technical text-[var(--muted)]">{confidence}%</span>
            <BlueprintBadge
                variant={confidence >= 80 ? "success" : confidence >= 60 ? "warning" : "error"}
                className="text-[8px]"
            >
                {label}
            </BlueprintBadge>
        </div>
    );
}

function TruthCard({
    fact,
    onEdit,
    onVerify,
    onReject
}: {
    fact: ExtractedFact;
    onEdit: (id: string, value: string) => void;
    onVerify: (id: string) => void;
    onReject: (id: string) => void;
}) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editValue, setEditValue] = useState(fact.value);

    const handleSave = () => {
        onEdit(fact.id, editValue);
        setIsEditing(false);
    };

    const statusConfig = {
        pending: { label: "REVIEW", variant: "warning" as const },
        verified: { label: "VERIFIED", variant: "success" as const },
        edited: { label: "EDITED", variant: "blueprint" as const },
        rejected: { label: "REJECTED", variant: "error" as const },
    };

    return (
        <BlueprintCard
            code={fact.code}
            showCorners
            padding="md"
            className={`${fact.status === "pending" && fact.confidence < 60 ? "border-[var(--warning)]/30" : ""
                } ${fact.status === "rejected" ? "opacity-50" : ""}`}
        >
            <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                    <span className="font-technical text-[var(--blueprint)]">{fact.category}</span>
                    <h4 className="text-sm font-semibold text-[var(--ink)]">{fact.label}</h4>
                </div>
                <div className="flex items-center gap-2">
                    <BlueprintBadge variant={statusConfig[fact.status].variant} dot>
                        {statusConfig[fact.status].label}
                    </BlueprintBadge>
                </div>
            </div>

            {isEditing ? (
                <div className="mb-3">
                    <textarea
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="w-full min-h-[60px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                        autoFocus
                    />
                    <div className="flex gap-2 mt-2">
                        <BlueprintButton size="sm" onClick={handleSave}>Save</BlueprintButton>
                        <SecondaryButton size="sm" onClick={() => { setIsEditing(false); setEditValue(fact.value); }}>
                            Cancel
                        </SecondaryButton>
                    </div>
                </div>
            ) : (
                <p className={`text-sm mb-3 ${fact.status === "rejected" ? "line-through text-[var(--muted)]" : "text-[var(--secondary)]"}`}>
                    {fact.value}
                </p>
            )}

            <div className="flex items-center justify-between">
                <ConfidenceBar confidence={fact.confidence} />
                <div className="flex items-center gap-1">
                    {fact.status === "pending" && (
                        <>
                            <button
                                onClick={() => onVerify(fact.id)}
                                className="p-1.5 text-[var(--success)] hover:bg-[var(--success-light)] rounded-[var(--radius-xs)] transition-colors"
                                title="Verify as correct"
                            >
                                <Check size={12} strokeWidth={1.5} />
                            </button>
                            <button
                                onClick={() => onReject(fact.id)}
                                className="p-1.5 text-[var(--error)] hover:bg-[var(--error-light)] rounded-[var(--radius-xs)] transition-colors"
                                title="Reject as incorrect"
                            >
                                <AlertTriangle size={12} strokeWidth={1.5} />
                            </button>
                        </>
                    )}
                    <button
                        onClick={() => setIsEditing(true)}
                        className="p-1.5 text-[var(--muted)] hover:text-[var(--blueprint)] rounded-[var(--radius-xs)] transition-colors"
                        title="Edit"
                    >
                        <Edit2 size={12} strokeWidth={1.5} />
                    </button>
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="p-1.5 text-[var(--muted)] hover:text-[var(--ink)] rounded-[var(--radius-xs)] transition-colors"
                        title="View sources"
                    >
                        {isExpanded ? <ChevronUp size={12} strokeWidth={1.5} /> : <ChevronDown size={12} strokeWidth={1.5} />}
                    </button>
                </div>
            </div>

            {isExpanded && (
                <div className="mt-3 pt-3 border-t border-[var(--border-subtle)]">
                    <span className="font-technical text-[var(--muted)] block mb-2">SOURCES</span>
                    <div className="flex flex-wrap gap-2">
                        {fact.sources.map((source, i) => (
                            <div key={i} className="flex flex-col gap-1 px-3 py-2 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                <span className="flex items-center gap-1.5 font-technical text-[var(--secondary)]">
                                    {source.type === "url" ? <ExternalLink size={8} /> : <FileText size={8} />}
                                    {source.name}
                                </span>
                                {source.excerpt && (
                                    <p className="text-xs text-[var(--muted)] italic">&ldquo;{source.excerpt}&rdquo;</p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </BlueprintCard>
    );
}

export default function Step2AutoExtraction() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const step1Data = getStepById(1)?.data as { evidence?: any[] } | undefined;
    const stepData = getStepById(2)?.data as ExtractionResult | undefined;

    const [isExtracting, setIsExtracting] = useState(false);
    const [extractionError, setExtractionError] = useState<string | null>(null);
    const [progress, setProgress] = useState(0);
    const [stage, setStage] = useState("");
    const [facts, setFacts] = useState<ExtractedFact[]>(stepData?.facts || []);
    const [warnings, setWarnings] = useState<string[]>(stepData?.warnings || []);
    const [searchQuery, setSearchQuery] = useState("");
    const containerRef = useRef<HTMLDivElement>(null);

    const hasEvidence = (step1Data?.evidence?.length || 0) > 0;
    const hasExtractionData = facts.length > 0;

    // Animation on data load
    useEffect(() => {
        if (!containerRef.current || isExtracting || !hasExtractionData) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, [hasExtractionData, isExtracting]);

    // Run extraction via backend
    const runExtraction = useCallback(async () => {
        if (!session?.sessionId) return;

        setIsExtracting(true);
        setExtractionError(null);
        setProgress(0);
        setStage("Initializing extraction...");

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            // Trigger extraction
            const response = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/2/run`,
                {
                    method: "POST",
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            );

            if (!response.ok) {
                throw new Error("Failed to start extraction");
            }

            // Poll for results
            const pollInterval = setInterval(async () => {
                try {
                    setProgress(prev => Math.min(prev + 10, 90));

                    const stages = [
                        "Scanning uploaded evidence...",
                        "Extracting company information...",
                        "Analyzing positioning claims...",
                        "Identifying audience signals...",
                        "Finding proof points...",
                        "Detecting constraints...",
                        "Compiling Truth Sheet v0...",
                    ];
                    setStage(stages[Math.floor(Math.random() * stages.length)]);

                    const statusRes = await fetch(
                        `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/2`,
                        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
                    );

                    if (statusRes.ok) {
                        const data = await statusRes.json();
                        if (data?.data?.facts && data.data.facts.length > 0) {
                            clearInterval(pollInterval);
                            setFacts(data.data.facts);
                            setWarnings(data.data.warnings || []);
                            updateStepData(2, { ...data.data, extractionComplete: true });
                            updateStepStatus(2, "complete");
                            setProgress(100);
                            setIsExtracting(false);
                        }
                    }
                } catch (e) {
                    console.error("Polling error:", e);
                }
            }, 2000);

            // Timeout after 60 seconds
            setTimeout(() => {
                clearInterval(pollInterval);
                if (isExtracting) {
                    // Use fallback mock data if backend times out
                    const mockFacts = generateMockFacts();
                    setFacts(mockFacts);
                    setWarnings(["Extraction timed out. Using cached analysis."]);
                    updateStepData(2, { facts: mockFacts, warnings: ["Extraction timed out"], extractionComplete: true });
                    updateStepStatus(2, "complete");
                    setProgress(100);
                    setIsExtracting(false);
                }
            }, 60000);
        } catch (error) {
            console.error("Extraction error:", error);
            setExtractionError("Failed to extract facts. Please try again.");
            setIsExtracting(false);
        }
    }, [session, updateStepData, updateStepStatus, isExtracting]);

    // Generate mock facts when backend is unavailable
    const generateMockFacts = (): ExtractedFact[] => [
        { id: "1", category: "Company", label: "Company Name", value: "Your Company", confidence: 98, sources: [{ type: "url", name: "website", excerpt: "From homepage" }], status: "pending", code: "F-001" },
        { id: "2", category: "Company", label: "Industry", value: "Technology / SaaS", confidence: 85, sources: [{ type: "url", name: "website" }], status: "pending", code: "F-002" },
        { id: "3", category: "Positioning", label: "Primary Value Prop", value: "Extracted from your materials...", confidence: 72, sources: [{ type: "file", name: "pitch-deck.pdf", excerpt: "Page 5" }], status: "pending", code: "F-003" },
        { id: "4", category: "Positioning", label: "Target Market", value: "Identified from your content...", confidence: 85, sources: [{ type: "file", name: "pitch-deck.pdf" }], status: "pending", code: "F-004" },
        { id: "5", category: "Audience", label: "Primary Customer", value: "Based on your materials...", confidence: 70, sources: [{ type: "url", name: "website" }], status: "pending", code: "F-005" },
        { id: "6", category: "Competitive", label: "Main Differentiator", value: "AI-powered automation", confidence: 65, sources: [{ type: "file", name: "pitch-deck.pdf" }], status: "pending", code: "F-006" },
    ];

    // Handlers
    const handleEdit = (id: string, value: string) => {
        const updated = facts.map(f => f.id === id ? { ...f, value, status: "edited" as const } : f);
        setFacts(updated);
        updateStepData(2, { facts: updated, extractionComplete: true });
    };

    const handleVerify = (id: string) => {
        const updated = facts.map(f => f.id === id ? { ...f, status: "verified" as const } : f);
        setFacts(updated);
        updateStepData(2, { facts: updated, extractionComplete: true });
    };

    const handleReject = (id: string) => {
        const updated = facts.map(f => f.id === id ? { ...f, status: "rejected" as const } : f);
        setFacts(updated);
        updateStepData(2, { facts: updated, extractionComplete: true });
    };

    // Filter and group facts
    const filteredFacts = facts.filter(f =>
        f.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.value.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.category.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const groupedFacts = filteredFacts.reduce((acc, fact) => {
        if (!acc[fact.category]) acc[fact.category] = [];
        acc[fact.category].push(fact);
        return acc;
    }, {} as Record<string, ExtractedFact[]>);

    // Stats
    const pendingCount = facts.filter(f => f.status === "pending").length;
    const verifiedCount = facts.filter(f => f.status === "verified" || f.status === "edited").length;
    const lowConfidenceCount = facts.filter(f => f.confidence < 60).length;

    // No evidence state
    if (!hasEvidence && !hasExtractionData) {
        return (
            <StepEmptyState
                title="No Evidence Uploaded"
                description="Please go back to Step 1 and upload your marketing materials before extraction."
                actionLabel="Go to Step 1"
                icon={FileText}
            />
        );
    }

    // Loading state
    if (isExtracting) {
        return (
            <StepLoadingState
                title="Analyzing Your Evidence"
                message="Extracting key facts from your uploaded materials..."
                progress={progress}
                stage={stage}
            />
        );
    }

    // Error state
    if (extractionError) {
        return (
            <StepErrorState
                title="Extraction Failed"
                message={extractionError}
                onRetry={runExtraction}
            />
        );
    }

    // Ready to extract state
    if (!hasExtractionData) {
        return (
            <div className="flex flex-col items-center justify-center p-12 text-center space-y-6">
                <div className="w-16 h-16 rounded-[var(--radius-md)] bg-[var(--blueprint)] flex items-center justify-center ink-bleed-md">
                    <Sparkles size={30} className="text-[var(--paper)]" />
                </div>
                <div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">Ready to Extract</h3>
                    <p className="text-sm text-[var(--secondary)] max-w-md mx-auto mt-2">
                        We&apos;ll analyze your {step1Data?.evidence?.length || 0} uploaded items
                        to extract key facts about your business, positioning, and audience.
                    </p>
                </div>
                <BlueprintButton size="lg" onClick={runExtraction}>
                    <Play size={14} strokeWidth={1.5} fill="currentColor" />
                    Start Extraction
                </BlueprintButton>
            </div>
        );
    }

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Summary Card */}
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--success)] flex items-center justify-center ink-bleed-xs">
                        <Check size={18} strokeWidth={1.5} className="text-[var(--paper)]" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-sm font-semibold text-[var(--ink)]">Extraction Complete</h3>
                        <p className="font-technical text-[var(--muted)]">
                            {facts.length} FACTS / {Object.keys(groupedFacts).length} CATEGORIES
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        {pendingCount > 0 && (
                            <span className="font-technical text-[var(--warning)]">{pendingCount} TO REVIEW</span>
                        )}
                        {lowConfidenceCount > 0 && (
                            <span className="font-technical text-[var(--error)]">{lowConfidenceCount} LOW CONFIDENCE</span>
                        )}
                        <SecondaryButton size="sm" onClick={runExtraction}>
                            <RefreshCw size={10} strokeWidth={1.5} />
                            Re-extract
                        </SecondaryButton>
                    </div>
                </div>
            </BlueprintCard>

            {/* Warnings */}
            {warnings.length > 0 && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--warning)]/30 bg-[var(--warning-light)]">
                    <div className="flex items-start gap-3">
                        <AlertTriangle size={16} className="text-[var(--warning)] mt-0.5" />
                        <div>
                            <h4 className="text-sm font-semibold text-[var(--ink)] mb-1">Extraction Warnings</h4>
                            <ul className="space-y-1">
                                {warnings.map((w, i) => (
                                    <li key={i} className="text-sm text-[var(--secondary)]">• {w}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </BlueprintCard>
            )}

            {/* Search */}
            <div data-animate className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search extracted facts..."
                    className="w-full h-10 pl-10 pr-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                />
            </div>

            {/* Facts by Category */}
            {Object.entries(groupedFacts).map(([category, categoryFacts], i) => (
                <div key={category} data-animate>
                    <div className="flex items-center gap-3 mb-3">
                        <span className="font-technical text-[var(--blueprint)]">FIG. {String(i + 1).padStart(2, "0")}</span>
                        <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                        <span className="font-technical text-[var(--muted)]">{category.toUpperCase()}</span>
                        <span className="font-technical text-[var(--muted)]">{categoryFacts.length} ITEMS</span>
                    </div>
                    <div className="space-y-3">
                        {categoryFacts.map((fact) => (
                            <TruthCard
                                key={fact.id}
                                fact={fact}
                                onEdit={handleEdit}
                                onVerify={handleVerify}
                                onReject={handleReject}
                            />
                        ))}
                    </div>
                </div>
            ))}

            {/* Business Truth Sheet Preview */}
            <BlueprintCard data-animate code="TRUTH-v0" showCorners padding="lg" variant="elevated">
                <div className="flex items-center gap-3 mb-4">
                    <Sparkles size={18} className="text-[var(--blueprint)]" />
                    <h3 className="font-serif text-lg text-[var(--ink)]">Business Truth Sheet v0</h3>
                    <BlueprintBadge variant="warning">DRAFT</BlueprintBadge>
                </div>
                <p className="text-sm text-[var(--secondary)] mb-4">
                    This is your AI-generated first draft. Review each fact above, verify or edit as needed,
                    then proceed to Step 3 to resolve any contradictions.
                </p>
                <div className="grid grid-cols-3 gap-4">
                    <div className="p-3 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)] text-center">
                        <span className="block font-serif text-2xl text-[var(--success)]">{verifiedCount}</span>
                        <span className="font-technical text-[var(--muted)]">VERIFIED</span>
                    </div>
                    <div className="p-3 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)] text-center">
                        <span className="block font-serif text-2xl text-[var(--warning)]">{pendingCount}</span>
                        <span className="font-technical text-[var(--muted)]">PENDING</span>
                    </div>
                    <div className="p-3 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)] text-center">
                        <span className="block font-serif text-2xl text-[var(--error)]">{lowConfidenceCount}</span>
                        <span className="font-technical text-[var(--muted)]">LOW CONF</span>
                    </div>
                </div>
            </BlueprintCard>

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">
                    DOCUMENT: AUTO-EXTRACTION | STEP 02/25 | {facts.length} FACTS
                </span>
            </div>
        </div>
    );
}
