"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    AlertTriangle, AlertCircle, HelpCircle, Check, ChevronDown, ChevronUp,
    Upload, MessageSquare, FileText, Play, Loader2, RefreshCw, Filter
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { StepLoadingState, StepEmptyState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 3: Contradictions

   PURPOSE: Analyze extracted facts for contradictions/ambiguities
   - Flag inconsistencies (e.g., "premium" vs low price)
   - Highlight missing pieces (no clear benefit, bold claims without proof)
   - Prioritize issues by severity
   - Surface conflicting quotes side-by-side for resolution
   ══════════════════════════════════════════════════════════════════════════════ */

// Types
interface Issue {
    id: string;
    type: "contradiction" | "unproven" | "missing" | "ambiguous";
    priority: "high" | "medium" | "low";
    title: string;
    description: string;
    sources?: { name: string; excerpt: string }[];
    resolution?: string;
    resolved: boolean;
    code: string;
}

interface AnalysisResult {
    issues: Issue[];
    summary: string;
    analysisComplete: boolean;
}

// Issue type configurations
const ISSUE_TYPE_CONFIG = {
    contradiction: {
        icon: AlertTriangle,
        label: "Contradiction",
        description: "Conflicting information between sources",
        color: "error" as const,
    },
    unproven: {
        icon: HelpCircle,
        label: "Unproven Claim",
        description: "Bold claim without supporting evidence",
        color: "warning" as const,
    },
    missing: {
        icon: AlertCircle,
        label: "Missing Info",
        description: "Required information not found",
        color: "default" as const,
    },
    ambiguous: {
        icon: MessageSquare,
        label: "Ambiguous",
        description: "Unclear or vague information",
        color: "blueprint" as const,
    },
};

function IssueCard({
    issue,
    onResolve,
}: {
    issue: Issue;
    onResolve: (id: string, resolution: string) => void;
}) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [resolution, setResolution] = useState(issue.resolution || "");
    const [selectedSource, setSelectedSource] = useState<number | null>(null);

    const handleResolve = () => {
        if (!resolution.trim() && issue.type !== "contradiction") return;
        const finalResolution = issue.type === "contradiction" && selectedSource !== null
            ? `Keep source ${selectedSource + 1}: ${issue.sources?.[selectedSource]?.name}`
            : resolution;
        onResolve(issue.id, finalResolution);
    };

    const config = ISSUE_TYPE_CONFIG[issue.type];
    const Icon = config.icon;

    const priorityColors = {
        high: "border-[var(--error)]/30 bg-[var(--error-light)]",
        medium: "border-[var(--warning)]/30",
        low: "",
    };

    if (issue.resolved) {
        return (
            <BlueprintCard
                code={issue.code}
                showCorners
                padding="md"
                className="border-[var(--success)]/30 bg-[var(--success-light)] opacity-75"
            >
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--success)] flex items-center justify-center">
                        <Check size={14} strokeWidth={1.5} className="text-[var(--paper)]" />
                    </div>
                    <div className="flex-1">
                        <h4 className="text-sm font-medium text-[var(--ink)] line-through">{issue.title}</h4>
                        <p className="font-technical text-[var(--muted)]">{issue.resolution}</p>
                    </div>
                    <BlueprintBadge variant="success" dot>RESOLVED</BlueprintBadge>
                </div>
            </BlueprintCard>
        );
    }

    return (
        <BlueprintCard
            code={issue.code}
            showCorners
            padding="md"
            className={priorityColors[issue.priority]}
        >
            <div className="flex items-start gap-3 mb-3">
                <div className={`w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--${config.color})] flex items-center justify-center mt-0.5`}>
                    <Icon size={14} strokeWidth={1.5} className="text-[var(--paper)]" />
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <h4 className="text-sm font-semibold text-[var(--ink)]">{issue.title}</h4>
                        <BlueprintBadge
                            variant={issue.priority === "high" ? "error" : issue.priority === "medium" ? "warning" : "default"}
                        >
                            {issue.priority.toUpperCase()}
                        </BlueprintBadge>
                        <BlueprintBadge variant={config.color}>{config.label.toUpperCase()}</BlueprintBadge>
                    </div>
                    <p className="text-sm text-[var(--secondary)]">{issue.description}</p>
                </div>
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="p-1.5 text-[var(--muted)] hover:text-[var(--ink)] rounded-[var(--radius-xs)] transition-colors"
                >
                    {isExpanded ? <ChevronUp size={14} strokeWidth={1.5} /> : <ChevronDown size={14} strokeWidth={1.5} />}
                </button>
            </div>

            {isExpanded && (
                <div className="pt-3 border-t border-[var(--border-subtle)] space-y-4">
                    {/* Sources */}
                    {issue.sources && issue.sources.length > 0 && (
                        <div>
                            <span className="font-technical text-[var(--muted)] block mb-2">CONFLICTING SOURCES</span>
                            <div className="space-y-2">
                                {issue.sources.map((source, i) => (
                                    <div
                                        key={i}
                                        className={`p-3 rounded-[var(--radius-sm)] border transition-all cursor-pointer ${selectedSource === i
                                                ? "bg-[var(--blueprint-light)] border-[var(--blueprint)]"
                                                : "bg-[var(--canvas)] border-[var(--border-subtle)] hover:border-[var(--blueprint)]"
                                            }`}
                                        onClick={() => issue.type === "contradiction" && setSelectedSource(i)}
                                    >
                                        <div className="flex items-center justify-between mb-1">
                                            <div className="flex items-center gap-2">
                                                <FileText size={10} strokeWidth={1.5} className="text-[var(--muted)]" />
                                                <span className="font-technical text-[var(--secondary)]">{source.name}</span>
                                            </div>
                                            {issue.type === "contradiction" && (
                                                <span className="font-technical text-[8px] text-[var(--blueprint)]">
                                                    {selectedSource === i ? "SELECTED" : "CLICK TO SELECT"}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-[var(--ink)] italic">&ldquo;{source.excerpt}&rdquo;</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Resolution */}
                    <div>
                        <span className="font-technical text-[var(--muted)] block mb-2">RESOLUTION</span>
                        <div className="space-y-3">
                            {issue.type === "contradiction" && (
                                <div className="grid grid-cols-2 gap-2">
                                    {issue.sources?.map((source, i) => (
                                        <button
                                            key={i}
                                            onClick={() => setSelectedSource(i)}
                                            className={`px-4 py-2 font-technical rounded-[var(--radius-sm)] transition-all ${selectedSource === i
                                                    ? "bg-[var(--blueprint)] text-[var(--paper)]"
                                                    : "bg-[var(--canvas)] text-[var(--muted)] hover:border-[var(--blueprint)] border border-[var(--border)]"
                                                }`}
                                        >
                                            SOURCE {i + 1}
                                        </button>
                                    ))}
                                </div>
                            )}

                            {issue.type === "unproven" && (
                                <div className="flex gap-2">
                                    <SecondaryButton
                                        size="sm"
                                        onClick={() => setResolution("Soften claim - remove specific numbers")}
                                        className={resolution.includes("Soften") ? "border-[var(--blueprint)]" : ""}
                                    >
                                        <MessageSquare size={10} strokeWidth={1.5} />
                                        Soften Claim
                                    </SecondaryButton>
                                    <SecondaryButton
                                        size="sm"
                                        onClick={() => setResolution("Will add supporting proof")}
                                        className={resolution.includes("proof") ? "border-[var(--blueprint)]" : ""}
                                    >
                                        <Upload size={10} strokeWidth={1.5} />
                                        Add Proof Later
                                    </SecondaryButton>
                                    <SecondaryButton
                                        size="sm"
                                        onClick={() => setResolution("Remove claim entirely")}
                                        className={resolution.includes("Remove") ? "border-[var(--blueprint)]" : ""}
                                    >
                                        Remove Claim
                                    </SecondaryButton>
                                </div>
                            )}

                            {(issue.type === "missing" || issue.type === "ambiguous") && (
                                <textarea
                                    value={resolution}
                                    onChange={(e) => setResolution(e.target.value)}
                                    placeholder="Provide the missing information or clarification..."
                                    className="w-full min-h-[80px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                                />
                            )}

                            <BlueprintButton
                                size="sm"
                                onClick={handleResolve}
                                disabled={!resolution.trim() && selectedSource === null}
                                className="w-full"
                            >
                                <Check size={12} strokeWidth={1.5} />
                                Mark Resolved
                            </BlueprintButton>
                        </div>
                    </div>
                </div>
            )}
        </BlueprintCard>
    );
}

export default function Step3Contradictions() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const step2Data = getStepById(2)?.data as { facts?: any[]; extractionComplete?: boolean } | undefined;
    const stepData = getStepById(3)?.data as AnalysisResult | undefined;

    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [issues, setIssues] = useState<Issue[]>(stepData?.issues || []);
    const [activeFilter, setActiveFilter] = useState<"all" | "contradiction" | "unproven" | "missing" | "ambiguous">("all");
    const containerRef = useRef<HTMLDivElement>(null);

    const hasExtractionData = step2Data?.extractionComplete && (step2Data?.facts?.length || 0) > 0;
    const hasAnalysisData = issues.length > 0;

    // Animation
    useEffect(() => {
        if (!containerRef.current || isAnalyzing) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, [hasAnalysisData, isAnalyzing]);

    // Run analysis
    const runAnalysis = useCallback(async () => {
        if (!session?.sessionId) return;

        setIsAnalyzing(true);

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            const response = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/3/run`,
                {
                    method: "POST",
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            );

            if (response.ok) {
                // Poll for results
                const pollInterval = setInterval(async () => {
                    const statusRes = await fetch(
                        `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/3`,
                        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
                    );

                    if (statusRes.ok) {
                        const data = await statusRes.json();
                        if (data?.data?.issues) {
                            clearInterval(pollInterval);
                            setIssues(data.data.issues);
                            updateStepData(3, { issues: data.data.issues, analysisComplete: true });
                            setIsAnalyzing(false);
                        }
                    }
                }, 2000);

                setTimeout(() => {
                    clearInterval(pollInterval);
                    if (isAnalyzing) {
                        // Use mock data
                        const mockIssues = generateMockIssues();
                        setIssues(mockIssues);
                        updateStepData(3, { issues: mockIssues, analysisComplete: true });
                        setIsAnalyzing(false);
                    }
                }, 20000);
            }
        } catch (error) {
            console.error("Analysis error:", error);
            // Use mock data as fallback
            const mockIssues = generateMockIssues();
            setIssues(mockIssues);
            updateStepData(3, { issues: mockIssues, analysisComplete: true });
            setIsAnalyzing(false);
        }
    }, [session, updateStepData, isAnalyzing]);

    const generateMockIssues = (): Issue[] => [
        {
            id: "1",
            type: "contradiction",
            priority: "high",
            title: "Conflicting target market claims",
            description: "Website says 'enterprise companies' but pitch deck mentions 'SMBs and startups'.",
            sources: [
                { name: "website", excerpt: "We serve enterprise companies..." },
                { name: "pitch-deck.pdf", excerpt: "Perfect for SMBs and startups..." }
            ],
            resolved: false,
            code: "ISS-01"
        },
        {
            id: "2",
            type: "unproven",
            priority: "high",
            title: "Cost reduction claim lacks evidence",
            description: "The claim about cost savings has no supporting case study or data.",
            sources: [{ name: "pitch-deck.pdf", excerpt: "Reduce costs significantly" }],
            resolved: false,
            code: "ISS-02"
        },
        {
            id: "3",
            type: "missing",
            priority: "medium",
            title: "No pricing information found",
            description: "Unable to extract pricing tiers or model from any uploaded evidence.",
            resolved: false,
            code: "ISS-03"
        },
        {
            id: "4",
            type: "ambiguous",
            priority: "low",
            title: "Unclear differentiation",
            description: "What makes this solution different from competitors is not clearly stated.",
            resolved: false,
            code: "ISS-04"
        },
    ];

    const handleResolve = (id: string, resolution: string) => {
        const updated = issues.map(i => i.id === id ? { ...i, resolved: true, resolution } : i);
        setIssues(updated);
        updateStepData(3, { issues: updated });

        // Check if all high-priority issues are resolved
        const highPriorityUnresolved = updated.filter(i => i.priority === "high" && !i.resolved);
        if (highPriorityUnresolved.length === 0) {
            updateStepStatus(3, "complete");
        }
    };

    // Filters
    const filteredIssues = issues.filter(i => activeFilter === "all" || i.type === activeFilter);
    const resolvedCount = issues.filter(i => i.resolved).length;
    const highPriorityUnresolved = issues.filter(i => i.priority === "high" && !i.resolved).length;

    const filterCounts = {
        all: issues.length,
        contradiction: issues.filter(i => i.type === "contradiction").length,
        unproven: issues.filter(i => i.type === "unproven").length,
        missing: issues.filter(i => i.type === "missing").length,
        ambiguous: issues.filter(i => i.type === "ambiguous").length,
    };

    // No extraction data
    if (!hasExtractionData && !hasAnalysisData) {
        return (
            <StepEmptyState
                title="No Extracted Facts"
                description="Please complete Step 2 to extract facts from your evidence before analyzing contradictions."
                icon={FileText}
            />
        );
    }

    // Loading
    if (isAnalyzing) {
        return (
            <StepLoadingState
                title="Analyzing for Contradictions"
                message="Scanning extracted facts for inconsistencies and gaps..."
                stage="Comparing sources..."
            />
        );
    }

    // Ready to analyze
    if (!hasAnalysisData) {
        return (
            <div className="flex flex-col items-center justify-center p-12 text-center space-y-6">
                <div className="w-16 h-16 rounded-[var(--radius-md)] bg-[var(--warning)] flex items-center justify-center ink-bleed-md">
                    <AlertTriangle size={30} className="text-[var(--paper)]" />
                </div>
                <div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">Ready to Analyze</h3>
                    <p className="text-sm text-[var(--secondary)] max-w-md mx-auto mt-2">
                        We&apos;ll scan your {step2Data?.facts?.length || 0} extracted facts for contradictions,
                        unproven claims, and missing information.
                    </p>
                </div>
                <BlueprintButton size="lg" onClick={runAnalysis}>
                    <Play size={14} strokeWidth={1.5} fill="currentColor" />
                    Start Analysis
                </BlueprintButton>
            </div>
        );
    }

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Status Card */}
            <BlueprintCard
                data-animate
                showCorners
                padding="md"
                className={highPriorityUnresolved > 0
                    ? "border-[var(--error)]/30 bg-[var(--error-light)]"
                    : "border-[var(--success)]/30 bg-[var(--success-light)]"
                }
            >
                <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-[var(--radius-sm)] flex items-center justify-center ${highPriorityUnresolved > 0 ? "bg-[var(--error)]" : "bg-[var(--success)]"
                        }`}>
                        {highPriorityUnresolved > 0
                            ? <AlertTriangle size={18} strokeWidth={1.5} className="text-[var(--paper)]" />
                            : <Check size={18} strokeWidth={1.5} className="text-[var(--paper)]" />
                        }
                    </div>
                    <div className="flex-1">
                        <h3 className="text-sm font-semibold text-[var(--ink)]">
                            {highPriorityUnresolved > 0
                                ? `${highPriorityUnresolved} high-priority issue${highPriorityUnresolved > 1 ? "s" : ""} to resolve`
                                : "All high-priority issues resolved"
                            }
                        </h3>
                        <p className="font-technical text-[var(--muted)]">{resolvedCount}/{issues.length} RESOLVED</p>
                    </div>
                    <SecondaryButton size="sm" onClick={runAnalysis}>
                        <RefreshCw size={10} strokeWidth={1.5} />
                        Re-analyze
                    </SecondaryButton>
                </div>
            </BlueprintCard>

            {/* Filters */}
            <div data-animate className="flex gap-2 flex-wrap">
                {(["all", "contradiction", "unproven", "missing", "ambiguous"] as const).map((filter) => (
                    <button
                        key={filter}
                        onClick={() => setActiveFilter(filter)}
                        className={`px-4 py-2 font-technical text-xs rounded-[var(--radius-sm)] transition-all ${activeFilter === filter
                                ? "bg-[var(--blueprint)] text-[var(--paper)]"
                                : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)] hover:border-[var(--blueprint)]"
                            }`}
                    >
                        {filter === "all" ? "ALL" : filter.toUpperCase()} ({filterCounts[filter]})
                    </button>
                ))}
            </div>

            {/* Issues List */}
            <div className="space-y-4">
                {filteredIssues.map((issue) => (
                    <IssueCard key={issue.id} issue={issue} onResolve={handleResolve} />
                ))}
            </div>

            {filteredIssues.length === 0 && (
                <BlueprintCard showCorners padding="lg" className="text-center">
                    <Check size={28} strokeWidth={1.5} className="mx-auto mb-3 text-[var(--success)]" />
                    <h3 className="text-sm font-semibold text-[var(--ink)] mb-1">No issues found</h3>
                    <p className="font-technical text-[var(--muted)]">
                        {activeFilter === "all" ? "ALL CLEAR" : `NO ${activeFilter.toUpperCase()} ISSUES`}
                    </p>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">
                    DOCUMENT: CONTRADICTIONS | STEP 03/25 | {issues.length} ISSUES
                </span>
            </div>
        </div>
    );
}
