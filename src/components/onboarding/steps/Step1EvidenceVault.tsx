"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Upload, Link as LinkIcon, FileText, Image as ImageIcon, Video, Plus, X, Check,
    AlertCircle, Loader2, ExternalLink, File, Scan, Tag, RefreshCw,
    Building2, Presentation, ShieldCheck, Mail, Database, Sparkles
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { OnboardingStepLayout } from "../OnboardingStepLayout";
import { cn } from "@/lib/utils";
import { supabase } from "@/lib/supabaseClient";

/* ══════════════════════════════════════════════════════════════════════════════
   PHASE 01: FOUNDATION — Step 1: Evidence Vault

   "Quiet Luxury: Decisive, Calm, Expensive."
   Updated for compact layout and auto-recognition.
   ══════════════════════════════════════════════════════════════════════════════ */

interface EvidenceItem {
    id: string;
    type: "url" | "file";
    name: string;
    status: "pending" | "processing" | "complete" | "error";
    url?: string;
    fileType?: string;
    size?: number;
    tags: string[];
    ocrProcessed?: boolean;
    errorMessage?: string;
    matchedCategory?: string;
}

// Relaxed requirement: These are just targets, not hard blockers
const RECOMMENDED_ITEMS = [
    { id: "manifesto", label: "Brand Manifesto", icon: FileText, required: true, description: "Mission, vision, and core values." },
    { id: "product_screenshots", label: "Product Interface", icon: ImageIcon, required: true, description: "Screenshots or design files." },
    { id: "sales_deck", label: "Sales Deck / Pitch", icon: Presentation, required: true, description: "How you sell to customers." },
    { id: "website", label: "Company Website", icon: Building2, required: true, description: "Live URL or landing page." },
    { id: "testimonials", label: "Proofs & Case Studies", icon: ShieldCheck, required: false, description: "Social proof and results." },
    { id: "competitors", label: "Competitor Intelligence", icon: Database, required: false, description: "Pricing or feature maps." },
];

const getAuthHeaders = async (): Promise<Record<string, string>> => {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export default function Step1EvidenceVault() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(1)?.data as { evidence?: EvidenceItem[] } | undefined;

    const [evidence, setEvidence] = useState<EvidenceItem[]>(stepData?.evidence || []);
    const [urlInput, setUrlInput] = useState("");
    const [isDragging, setIsDragging] = useState(false);
    const [isSimulatingRecognition, setIsSimulatingRecognition] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Initial load animation
    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 8 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.1, ease: "power2.out" }
        );
    }, []);

    // Sync status with store - ULTRA LENIENT VALIDATION
    // Logic: If you uploaded *anything*, you can proceed. We don't block.
    useEffect(() => {
        const hasEvidence = evidence.length > 0;
        // Always set status based on presence. If present -> complete.
        // If not -> in-progress (so they can still see it, but sidebar might show incomplete)
        // Ideally, we want to allow them to "Continue" even if "in-progress" if they really want to,
        // but OnboardingShell blocks unless complete. So we mark complete if > 0.
        if (hasEvidence) {
            updateStepStatus(1, "complete");
        } else {
            updateStepStatus(1, "in-progress");
        }
    }, [evidence, updateStepStatus]);

    const saveToStore = useCallback((updated: EvidenceItem[]) => {
        setEvidence(updated);
        updateStepData(1, { evidence: updated });
    }, [updateStepData]);

    const classifyEvidence = async (itemId: string, fileName: string, fileType?: string) => {
        setIsSimulatingRecognition(itemId);

        try {
            // Call the backend classification API
            const authHeaders = await getAuthHeaders();
            const response = await fetch('/api/onboarding/classify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeaders },
                body: JSON.stringify({
                    session_id: session?.sessionId || 'demo',
                    evidence_data: {
                        name: fileName,
                        file_type: fileType,
                        item_id: itemId
                    }
                })
            });

            const result = await response.json();
            const category = result.classification?.category || 'other';

            setEvidence(prev => prev.map(e => e.id === itemId ? { ...e, status: "complete", matchedCategory: category } : e));
        } catch (error) {
            console.error('Classification error:', error);
            // Fallback to simple local heuristic only on complete API failure
            const lowerName = fileName.toLowerCase();
            let category = "other";
            if (lowerName.includes("manifesto") || lowerName.includes("brand")) category = "manifesto";
            else if (lowerName.includes("deck") || lowerName.includes("pitch")) category = "sales_deck";
            else if (fileType?.includes("image")) category = "product_screenshots";

            setEvidence(prev => prev.map(e => e.id === itemId ? { ...e, status: "complete", matchedCategory: category } : e));
        }

        setIsSimulatingRecognition(null);
    };

    const handleFiles = async (files: FileList | null) => {
        if (!files) return;
        const newItems: EvidenceItem[] = Array.from(files).map(file => ({
            id: `file-${Date.now()}-${file.name}`,
            type: "file",
            name: file.name,
            fileType: file.type,
            size: file.size,
            status: "processing",
            tags: [],
        }));

        const updated = [...evidence, ...newItems];
        saveToStore(updated);

        // Process sequentially
        for (const item of newItems) {
            await classifyEvidence(item.id, item.name, item.fileType);
        }
    };

    const handleUrl = () => {
        if (!urlInput.trim()) return;
        const newItem: EvidenceItem = {
            id: `url-${Date.now()}`,
            type: "url",
            name: urlInput,
            url: urlInput,
            status: "complete",
            tags: [],
            matchedCategory: "website"
        };

        const updated = [...evidence, newItem];
        saveToStore(updated);
        setUrlInput("");
    };

    return (
        <OnboardingStepLayout stepId={1}>
            <div ref={containerRef} className="max-w-[1200px] mx-auto space-y-6 pb-20">

                {/* Header */}
                <div data-animate className="flex items-end justify-between border-b border-[var(--border-subtle)] pb-4">
                    <div className="space-y-1">
                        <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Phase 01 / Foundation</span>
                        <h1 className="font-serif text-3xl text-[var(--ink)] tracking-tight">Evidence Vault</h1>
                        <p className="text-[var(--ink-secondary)] text-sm max-w-lg">
                            Upload your strategic assets. RaptorFlow automatically scans them for truth signatures.
                        </p>
                    </div>
                    {/* Status Dots */}
                    <div className="hidden md:block text-right">
                        <span className="block font-technical text-[10px] text-[var(--ink-muted)] uppercase tracking-wider mb-1">Vault Status</span>
                        <div className="flex gap-1 justify-end">
                            {[1, 2, 3, 4].map(i => (
                                <div key={i} className={cn("h-1.5 w-4 rounded-full transition-colors", evidence.length >= i ? "bg-[var(--blueprint)]" : "bg-[var(--border)]")} />
                            ))}
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-12 gap-8">

                    {/* Left: Inputs (5 cols) */}
                    <div data-animate className="col-span-12 lg:col-span-5 space-y-5">

                        {/* Drag & Drop Zone */}
                        <div
                            className={cn(
                                "relative group border-2 border-dashed rounded-xl bg-[var(--paper)] transition-all duration-300 cursor-pointer overflow-hidden",
                                isDragging
                                    ? "bg-[var(--blueprint-light)]/10 border-[var(--blueprint)] scale-[1.01]"
                                    : "border-[var(--border)] hover:border-[var(--ink-muted)] hover:shadow-sm"
                            )}
                            onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); }}
                            onDragLeave={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(false); }}
                            onDrop={(e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(false); handleFiles(e.dataTransfer.files); }}
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <div className="p-10 flex flex-col items-center justify-center text-center">
                                <div className={cn(
                                    "w-12 h-12 mb-4 rounded-full flex items-center justify-center transition-colors",
                                    isDragging ? "bg-[var(--blueprint)] text-white" : "bg-[var(--canvas)] text-[var(--ink-muted)] group-hover:bg-[var(--ink)] group-hover:text-white"
                                )}>
                                    <Upload size={20} />
                                </div>
                                <h3 className="text-sm font-semibold text-[var(--ink)]">Drop assets here</h3>
                                <p className="text-xs text-[var(--secondary)] mt-1.5">PDF, Slide Decks, Images</p>
                            </div>
                            <input ref={fileInputRef} type="file" multiple className="hidden" onChange={(e) => handleFiles(e.target.files)} />
                        </div>

                        {/* URL Input */}
                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                                    <LinkIcon size={14} className="text-[var(--muted)]" />
                                </div>
                                <input
                                    type="url"
                                    value={urlInput}
                                    onChange={(e) => setUrlInput(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && handleUrl()}
                                    placeholder="Add website or competitor link..."
                                    className="w-full h-10 pl-9 pr-4 bg-[var(--paper)] border border-[var(--border)] rounded-lg text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:outline-none focus:border-[var(--blueprint)] transition-colors"
                                />
                            </div>
                            <BlueprintButton
                                onClick={handleUrl}
                                disabled={!urlInput}
                                className="h-10 px-4"
                                variant="secondary"
                            >
                                <Plus size={16} />
                            </BlueprintButton>
                        </div>

                        {/* Inventory List */}
                        <div className="pt-2">
                            <div className="flex items-center justify-between px-1 mb-2">
                                <span className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider">Vault Inventory ({evidence.length})</span>
                            </div>
                            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                                {evidence.length === 0 && (
                                    <div className="text-center py-8 text-[var(--muted)] text-xs italic bg-[var(--canvas)] rounded-lg border border-dashed border-[var(--border)]">
                                        No assets uploaded yet.
                                    </div>
                                )}
                                {evidence.map((item) => (
                                    <div key={item.id} className="group flex items-center justify-between p-3 bg-[var(--paper)] border border-[var(--border-subtle)] rounded-lg shadow-sm hover:border-[var(--blueprint)] hover:shadow-md transition-all">
                                        <div className="flex items-center gap-3 overflow-hidden">
                                            <div className="shrink-0 text-[var(--blueprint)]">
                                                {item.status === "processing" ? <Loader2 size={16} className="animate-spin" /> :
                                                    item.type === "url" ? <LinkIcon size={16} /> : <FileText size={16} />}
                                            </div>
                                            <div className="flex flex-col min-w-0">
                                                <span className="text-sm font-medium text-[var(--ink)] truncate">{item.name}</span>
                                                <span className="text-[10px] text-[var(--secondary)] uppercase tracking-tight flex items-center gap-1">
                                                    {item.matchedCategory ? item.matchedCategory.replace("_", " ") : "Unclassified"}
                                                    {item.matchedCategory && <Check size={10} className="text-[var(--success)]" />}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); setEvidence(prev => prev.filter(p => p.id !== item.id)); }}
                                            className="opacity-0 group-hover:opacity-100 p-1.5 text-[var(--muted)] hover:text-[var(--error)] transition-colors"
                                        >
                                            <X size={14} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>

                    {/* Right: Goals (7 cols) */}
                    <div data-animate className="col-span-12 lg:col-span-7">
                        <div className="grid grid-cols-2 gap-4">
                            {RECOMMENDED_ITEMS.map((item) => {
                                const isSatisfied = evidence.some(e => e.matchedCategory === item.id || (item.id === 'website' && e.type === 'url'));

                                return (
                                    <div
                                        key={item.id}
                                        className={cn(
                                            "bg-[var(--paper)] p-4 rounded-xl border transition-all duration-300 relative overflow-hidden group",
                                            isSatisfied
                                                ? "border-[var(--success)] shadow-sm"
                                                : "border-[var(--border-subtle)] hover:border-[var(--blueprint)] opacity-100"
                                        )}
                                    >
                                        <div className="flex items-start justify-between mb-2">
                                            <div className={cn(
                                                "p-2 rounded-lg transition-colors",
                                                isSatisfied ? "bg-[var(--success)] text-white" : "bg-[var(--canvas)] text-[var(--muted)] group-hover:text-[var(--blueprint)]"
                                            )}>
                                                <item.icon size={18} />
                                            </div>
                                            {isSatisfied ? (
                                                <Check size={16} className="text-[var(--success)]" />
                                            ) : (
                                                item.required && <span className="text-[8px] font-bold text-[var(--muted)] border border-[var(--border)] px-1.5 py-0.5 rounded bg-[var(--canvas)]">REQ</span>
                                            )}
                                        </div>

                                        <h4 className="text-sm font-bold mb-1 text-[var(--ink)]">
                                            {item.label}
                                        </h4>
                                        <p className="text-xs text-[var(--secondary)] leading-tight">
                                            {item.description}
                                        </p>

                                        {/* Scan Effect if satisfied */}
                                        {isSatisfied && (
                                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12 translate-x-[-200%] animate-[shimmer_2s_infinite]" />
                                        )}
                                    </div>
                                );
                            })}
                        </div>

                        {/* AI Note */}
                        <div className="mt-6 p-4 rounded-xl border border-[var(--border-subtle)] bg-[var(--canvas)] flex items-start gap-3">
                            <Sparkles size={14} className="text-[var(--ink)] mt-0.5 flex-shrink-0" />
                            <div className="space-y-1">
                                <p className="text-[11px] font-medium text-[var(--ink)]">Autonomous Content Identification</p>
                                <p className="text-[10px] text-[var(--ink-secondary)] leading-relaxed">
                                    Our vision engine scans your files for key business identifiers. Uploading a PDF named "Brand Deck" or "Interface V1" will automatically satisfy the required slots.
                                </p>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </OnboardingStepLayout>
    );
}
