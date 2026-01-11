"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Upload, Link as LinkIcon, FileText, Image, Video, Plus, X, Check,
    AlertCircle, Loader2, ExternalLink, File, Scan, Tag, AlertTriangle,
    Package, RefreshCw
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { OnboardingStepLayout } from "../OnboardingStepLayout";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { StepLoadingState, StepErrorState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 1: Evidence Vault

   PURPOSE: Centralize all client materials for AI analysis
   - Upload files (PDF, DOC, PPTX, images) with OCR processing
   - Add URLs for website/competitor analysis
   - Tag and categorize evidence
   - Show present vs missing checklist
   - Detect multiple products/business lines
   ══════════════════════════════════════════════════════════════════════════════ */

// Types
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
    productLine?: string; // For multi-product detection
}

interface ProductLineWarning {
    detected: boolean;
    lines: string[];
    dismissed: boolean;
}

// Recommended evidence types with requirements
const RECOMMENDED_EVIDENCE = [
    { id: "website", label: "Company website", type: "url" as const, required: true, description: "Your main website URL" },
    { id: "pitchdeck", label: "Pitch deck / one-pager", type: "file" as const, required: true, description: "PDF or PPTX" },
    { id: "competitors", label: "Competitor websites (2-3)", type: "url" as const, required: false, description: "Top 2-3 competitors" },
    { id: "casestudies", label: "Case studies", type: "file" as const, required: false, description: "Success stories" },
    { id: "testimonials", label: "Customer testimonials", type: "file" as const, required: false, description: "Reviews, quotes" },
    { id: "screenshots", label: "Product screenshots", type: "file" as const, required: false, description: "UI/product visuals" },
    { id: "adsdata", label: "Ad performance data", type: "file" as const, required: false, description: "CSV, Excel exports" },
    { id: "transcripts", label: "Sales/support transcripts", type: "file" as const, required: false, description: "Call recordings, chats" },
];

// Tag categories
const TAG_OPTIONS = [
    { id: "website", label: "Website", color: "blueprint" },
    { id: "salesdeck", label: "Sales Deck", color: "success" },
    { id: "testimonial", label: "Testimonial", color: "warning" },
    { id: "competitor", label: "Competitor", color: "error" },
    { id: "casestudy", label: "Case Study", color: "blueprint" },
    { id: "screenshot", label: "Screenshot", color: "default" },
    { id: "dataexport", label: "Data Export", color: "default" },
];

export default function Step1EvidenceVault() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(1)?.data as {
        evidence?: EvidenceItem[];
        productLineWarning?: ProductLineWarning;
    } | undefined;

    // State
    const [evidence, setEvidence] = useState<EvidenceItem[]>(stepData?.evidence || []);
    const [urlInput, setUrlInput] = useState("");
    const [dragOver, setDragOver] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [productWarning, setProductWarning] = useState<ProductLineWarning>(
        stepData?.productLineWarning || { detected: false, lines: [], dismissed: false }
    );
    const [activeTagEditor, setActiveTagEditor] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Animation on mount
    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" }
        );
    }, []);

    // Auto-update step status
    useEffect(() => {
        const completedCount = evidence.filter(e => e.status === "complete").length;
        const hasMinimumEvidence = evidence.length >= 1;
        const hasRequiredItems = RECOMMENDED_EVIDENCE
            .filter(r => r.required)
            .every(req => evidence.some(e =>
                (req.type === "url" && e.type === "url") ||
                (req.type === "file" && e.type === "file")
            ));

        if (hasMinimumEvidence && completedCount === evidence.length && completedCount > 0) {
            updateStepStatus(1, "complete");
        } else if (evidence.length > 0) {
            updateStepStatus(1, "in-progress");
        }
    }, [evidence, updateStepStatus]);

    // Save evidence to store
    const saveEvidence = useCallback((updated: EvidenceItem[]) => {
        setEvidence(updated);
        updateStepData(1, { evidence: updated, productLineWarning: productWarning });
    }, [updateStepData, productWarning]);

    // Upload file to backend
    const uploadToBackend = async (file: File, itemId: string): Promise<boolean> => {
        if (!session?.sessionId) return false;

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            const formData = new FormData();
            formData.append("file", file);
            formData.append("item_id", itemId);

            const response = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/vault/upload`,
                {
                    method: "POST",
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                    body: formData,
                }
            );

            return response.ok;
        } catch (error) {
            console.error("Upload error:", error);
            return false;
        }
    };

    // Process URL via backend
    const processUrl = async (url: string, itemId: string): Promise<boolean> => {
        if (!session?.sessionId) return false;

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            const response = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/vault/url`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(token ? { Authorization: `Bearer ${token}` } : {}),
                    },
                    body: JSON.stringify({ url, item_id: itemId }),
                }
            );

            return response.ok;
        } catch (error) {
            console.error("URL processing error:", error);
            return false;
        }
    };

    // Add URL handler
    const addUrl = async () => {
        if (!urlInput.trim()) return;

        // Validate URL
        try {
            new URL(urlInput);
        } catch {
            setUploadError("Please enter a valid URL");
            return;
        }

        const newEvidence: EvidenceItem = {
            id: `url-${Date.now()}`,
            type: "url",
            name: urlInput,
            url: urlInput,
            status: "processing",
            tags: urlInput.includes("competitor") ? ["competitor"] : [],
        };

        const updated = [...evidence, newEvidence];
        saveEvidence(updated);
        setUrlInput("");
        setUploadError(null);

        // Process URL via backend
        const success = await processUrl(urlInput, newEvidence.id);

        setEvidence(prev => {
            const completed = prev.map(e =>
                e.id === newEvidence.id
                    ? { ...e, status: success ? "complete" as const : "error" as const, errorMessage: success ? undefined : "Failed to process URL" }
                    : e
            );
            updateStepData(1, { evidence: completed });
            return completed;
        });
    };

    // File upload handler
    const handleFileUpload = async (files: FileList | null) => {
        if (!files || files.length === 0) return;

        const MAX_SIZE = 50 * 1024 * 1024; // 50MB
        const validTypes = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "image/png",
            "image/jpeg",
            "image/gif",
            "video/mp4",
            "video/quicktime",
            "text/csv",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ];

        const newFiles: EvidenceItem[] = [];
        const errors: string[] = [];

        Array.from(files).forEach(file => {
            if (file.size > MAX_SIZE) {
                errors.push(`${file.name}: File too large (max 50MB)`);
                return;
            }
            if (!validTypes.includes(file.type)) {
                errors.push(`${file.name}: Unsupported file type`);
                return;
            }

            // Check for duplicates
            if (evidence.some(e => e.name === file.name && e.size === file.size)) {
                errors.push(`${file.name}: Already uploaded`);
                return;
            }

            newFiles.push({
                id: `file-${Date.now()}-${file.name}`,
                type: "file",
                name: file.name,
                fileType: file.type,
                size: file.size,
                status: "processing",
                tags: [],
                ocrProcessed: file.type.startsWith("image/"),
            });
        });

        if (errors.length > 0) {
            setUploadError(errors.join("; "));
        }

        if (newFiles.length === 0) return;

        const updated = [...evidence, ...newFiles];
        saveEvidence(updated);

        // Process each file
        for (let i = 0; i < newFiles.length; i++) {
            const item = newFiles[i];
            const file = Array.from(files).find(f => f.name === item.name);
            if (!file) continue;

            const success = await uploadToBackend(file, item.id);

            setEvidence(prev => {
                const completed = prev.map(e =>
                    e.id === item.id
                        ? { ...e, status: success ? "complete" as const : "error" as const, errorMessage: success ? undefined : "Upload failed" }
                        : e
                );
                updateStepData(1, { evidence: completed });
                return completed;
            });
        }
    };

    // Remove evidence
    const removeEvidence = (id: string) => {
        saveEvidence(evidence.filter(e => e.id !== id));
    };

    // Update tags
    const updateTags = (id: string, tags: string[]) => {
        const updated = evidence.map(e => e.id === id ? { ...e, tags } : e);
        saveEvidence(updated);
        setActiveTagEditor(null);
    };

    // Retry failed upload
    const retryUpload = async (id: string) => {
        const item = evidence.find(e => e.id === id);
        if (!item) return;

        setEvidence(prev => prev.map(e => e.id === id ? { ...e, status: "processing", errorMessage: undefined } : e));

        if (item.type === "url" && item.url) {
            const success = await processUrl(item.url, id);
            setEvidence(prev => {
                const completed = prev.map(e =>
                    e.id === id
                        ? { ...e, status: success ? "complete" as const : "error" as const, errorMessage: success ? undefined : "Failed to process URL" }
                        : e
                );
                updateStepData(1, { evidence: completed });
                return completed;
            });
        }
    };

    // Drop handlers
    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        handleFileUpload(e.dataTransfer.files);
    };

    // Get file icon
    const getFileIcon = (item: EvidenceItem) => {
        if (item.type === "url") return <LinkIcon size={14} strokeWidth={1.5} className="text-[var(--blueprint)]" />;
        if (item.fileType?.startsWith("image")) return <Image size={14} strokeWidth={1.5} className="text-[var(--blueprint)]" />;
        if (item.fileType?.startsWith("video")) return <Video size={14} strokeWidth={1.5} className="text-[var(--blueprint)]" />;
        if (item.fileType?.includes("pdf")) return <FileText size={14} strokeWidth={1.5} className="text-[var(--error)]" />;
        return <File size={14} strokeWidth={1.5} className="text-[var(--muted)]" />;
    };

    // Computed values
    const completedCount = evidence.filter(e => e.status === "complete").length;
    const processingCount = evidence.filter(e => e.status === "processing").length;
    const errorCount = evidence.filter(e => e.status === "error").length;

    const checklistStatus = RECOMMENDED_EVIDENCE.map(req => ({
        ...req,
        satisfied: evidence.some(e => {
            if (req.id === "website" && e.type === "url" && !e.tags?.includes("competitor")) return true;
            if (req.id === "competitors" && e.type === "url" && e.tags?.includes("competitor")) return true;
            if (req.id !== "website" && req.id !== "competitors" && req.type === "file" && e.type === "file") {
                if (req.id === "pitchdeck" && (e.fileType?.includes("pdf") || e.fileType?.includes("presentation"))) return true;
                if (req.id === "casestudies" && e.tags?.includes("casestudy")) return true;
                if (req.id === "testimonials" && e.tags?.includes("testimonial")) return true;
                if (req.id === "screenshots" && e.fileType?.startsWith("image")) return true;
            }
            return false;
        }),
    }));

    return (
        <OnboardingStepLayout stepId={1} moduleLabel="EVIDENCE-VAULT" itemCount={evidence.length}>
            <div ref={containerRef} className="space-y-6">
                {/* Progress Card */}
                {evidence.length > 0 && (
                    <BlueprintCard data-animate code="PROG" showCorners padding="md">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-sm font-medium text-[var(--ink)]">
                                {completedCount} of {evidence.length} items processed
                            </span>
                            {processingCount > 0 && (
                                <span className="flex items-center gap-1.5 font-technical text-[var(--blueprint)]">
                                    <Loader2 size={10} className="animate-spin" />PROCESSING
                                </span>
                            )}
                            {processingCount === 0 && completedCount > 0 && errorCount === 0 && (
                                <BlueprintBadge variant="success" dot>READY</BlueprintBadge>
                            )}
                            {errorCount > 0 && (
                                <BlueprintBadge variant="error" dot>{errorCount} ERROR{errorCount > 1 ? "S" : ""}</BlueprintBadge>
                            )}
                        </div>
                        <BlueprintProgress value={evidence.length > 0 ? (completedCount / evidence.length) * 100 : 0} />
                    </BlueprintCard>
                )}

                {/* Multi-Product Warning */}
                {productWarning.detected && !productWarning.dismissed && (
                    <BlueprintCard data-animate showCorners padding="md" className="border-[var(--warning)]/30 bg-[var(--warning-light)]">
                        <div className="flex items-start gap-3">
                            <Package size={18} className="text-[var(--warning)] mt-0.5" />
                            <div className="flex-1">
                                <h4 className="text-sm font-semibold text-[var(--ink)] mb-1">Multiple Products Detected</h4>
                                <p className="text-sm text-[var(--secondary)] mb-2">
                                    We noticed evidence for potentially different product lines: {productWarning.lines.join(", ")}.
                                    Consider splitting onboarding per product to avoid confusion.
                                </p>
                                <div className="flex gap-2">
                                    <SecondaryButton size="sm" onClick={() => setProductWarning(prev => ({ ...prev, dismissed: true }))}>
                                        Continue Anyway
                                    </SecondaryButton>
                                </div>
                            </div>
                        </div>
                    </BlueprintCard>
                )}

                {/* Error Display */}
                {uploadError && (
                    <BlueprintCard data-animate showCorners padding="sm" className="border-[var(--error)]/30 bg-[var(--error-light)]">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <AlertCircle size={14} className="text-[var(--error)]" />
                                <span className="text-sm text-[var(--error)]">{uploadError}</span>
                            </div>
                            <button onClick={() => setUploadError(null)} className="text-[var(--error)] hover:underline text-sm">
                                Dismiss
                            </button>
                        </div>
                    </BlueprintCard>
                )}

                {/* TWO-COLUMN LAYOUT: Upload + URL side by side */}
                <div data-animate className="grid md:grid-cols-2 gap-4">
                    {/* Left: Upload Zone */}
                    <BlueprintCard
                        code="UPLOAD"
                        showCorners
                        padding="none"
                        className={`transition-all h-full ${dragOver ? "border-[var(--blueprint)] bg-[var(--blueprint-light)]" : ""}`}
                    >
                        <div
                            className={`h-full p-6 border-2 border-dashed rounded-[var(--radius-md)] transition-all text-center flex flex-col items-center justify-center ${dragOver ? "border-[var(--blueprint)]" : "border-[var(--border)] hover:border-[var(--blueprint)]"
                                }`}
                            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                        >
                            <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center mb-3">
                                <Upload size={18} strokeWidth={1.5} className="text-[var(--muted)]" />
                            </div>
                            <p className="text-sm font-medium text-[var(--ink)] mb-1">Drop files here</p>
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="font-technical text-[var(--blueprint)] hover:underline mb-2"
                            >
                                BROWSE
                            </button>
                            <p className="font-technical text-[9px] text-[var(--muted)]">PDF, DOC, PPTX, IMAGES • 50MB MAX</p>
                            <input
                                ref={fileInputRef}
                                type="file"
                                multiple
                                className="hidden"
                                onChange={(e) => handleFileUpload(e.target.files)}
                                accept=".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg,.gif,.mp4,.mov,.csv,.xls,.xlsx"
                            />
                        </div>
                    </BlueprintCard>

                    {/* Right: Always-visible URL Input */}
                    <BlueprintCard code="URL" showCorners padding="md" className="h-full flex flex-col">
                        <div className="flex items-center gap-2 mb-3">
                            <LinkIcon size={14} strokeWidth={1.5} className="text-[var(--blueprint)]" />
                            <h3 className="text-sm font-semibold text-[var(--ink)]">Add Website URL</h3>
                            <span className="font-technical text-[8px] text-[var(--muted)] ml-auto">OPTIONAL</span>
                        </div>
                        <p className="text-xs text-[var(--secondary)] mb-3">
                            Add your website, competitor sites, or any relevant pages.
                        </p>
                        <div className="flex-1 flex flex-col gap-2">
                            <div className="relative">
                                <LinkIcon size={14} strokeWidth={1.5} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" />
                                <input
                                    type="url"
                                    value={urlInput}
                                    onChange={(e) => setUrlInput(e.target.value)}
                                    placeholder="https://yoursite.com"
                                    className="w-full h-10 pl-10 pr-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                                    onKeyDown={(e) => e.key === "Enter" && addUrl()}
                                />
                            </div>
                            <BlueprintButton size="sm" onClick={addUrl} disabled={!urlInput.trim()} className="w-full">
                                <Plus size={12} strokeWidth={1.5} />Add URL
                            </BlueprintButton>
                        </div>
                        <p className="font-technical text-[8px] text-[var(--muted)] mt-3 text-center">
                            You can add more URLs later from Settings
                        </p>
                    </BlueprintCard>
                </div>

                {/* Evidence List */}
                {evidence.length > 0 && (
                    <BlueprintCard data-animate code="LIST" showCorners padding="md">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-semibold text-[var(--ink)]">Your Evidence ({evidence.length})</h3>
                            <span className="font-technical text-[var(--success)]">{completedCount} READY</span>
                        </div>
                        <div className="space-y-2">
                            {evidence.map((item) => (
                                <div
                                    key={item.id}
                                    className={`flex items-center gap-3 p-3 rounded-[var(--radius-sm)] bg-[var(--canvas)] border ${item.status === "error" ? "border-[var(--error)]/30" : "border-[var(--border-subtle)]"
                                        }`}
                                >
                                    {getFileIcon(item)}
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-[var(--ink)] truncate">{item.name}</p>
                                        <div className="flex items-center gap-2">
                                            {item.type === "url" && (
                                                <a
                                                    href={item.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="font-technical text-[var(--blueprint)] hover:underline flex items-center gap-1"
                                                >
                                                    OPEN <ExternalLink size={8} />
                                                </a>
                                            )}
                                            {item.size && (
                                                <span className="font-technical text-[var(--muted)]">
                                                    {(item.size / 1024).toFixed(1)} KB
                                                </span>
                                            )}
                                            {item.ocrProcessed && (
                                                <span className="font-technical text-[var(--blueprint)] flex items-center gap-1">
                                                    <Scan size={8} />OCR
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    {/* Tags */}
                                    <div className="flex items-center gap-1">
                                        {(item.tags || []).slice(0, 2).map(tag => (
                                            <BlueprintBadge key={tag} variant="default" className="text-[9px]">
                                                {tag.toUpperCase()}
                                            </BlueprintBadge>
                                        ))}
                                        <button
                                            onClick={() => setActiveTagEditor(activeTagEditor === item.id ? null : item.id)}
                                            className="p-1 text-[var(--muted)] hover:text-[var(--blueprint)] rounded-[var(--radius-xs)] transition-colors"
                                        >
                                            <Tag size={10} strokeWidth={1.5} />
                                        </button>
                                    </div>

                                    {/* Status */}
                                    <div className="flex items-center gap-2">
                                        {item.status === "processing" && (
                                            <span className="flex items-center gap-1 font-technical text-[var(--blueprint)]">
                                                <Loader2 size={12} className="animate-spin" />ANALYZING
                                            </span>
                                        )}
                                        {item.status === "complete" && (
                                            <BlueprintBadge variant="success" dot>READY</BlueprintBadge>
                                        )}
                                        {item.status === "error" && (
                                            <div className="flex items-center gap-1">
                                                <BlueprintBadge variant="error" dot>ERROR</BlueprintBadge>
                                                <button
                                                    onClick={() => retryUpload(item.id)}
                                                    className="p-1 text-[var(--error)] hover:bg-[var(--error-light)] rounded-[var(--radius-xs)]"
                                                >
                                                    <RefreshCw size={10} strokeWidth={1.5} />
                                                </button>
                                            </div>
                                        )}
                                        <button
                                            onClick={() => removeEvidence(item.id)}
                                            className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] hover:bg-[var(--error-light)] rounded-[var(--radius-xs)] transition-colors"
                                        >
                                            <X size={12} strokeWidth={1.5} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </BlueprintCard>
                )}

                {/* Recommended Checklist - Compact horizontal pills */}
                <BlueprintCard data-animate figure="FIG. 01" title="Recommended Evidence" code="CHECK" showCorners padding="md">
                    <div className="flex flex-wrap gap-2">
                        {checklistStatus.map((item) => (
                            <div
                                key={item.id}
                                className={`inline-flex items-center gap-2 px-3 py-2 rounded-full border transition-all ${item.satisfied
                                    ? "bg-[var(--success-light)] border-[var(--success)]/30"
                                    : "bg-[var(--canvas)] border-[var(--border-subtle)]"
                                    }`}
                            >
                                {item.satisfied ? (
                                    <Check size={12} strokeWidth={1.5} className="text-[var(--success)]" />
                                ) : (
                                    <div className="w-3 h-3 rounded-full border-2 border-[var(--border)]" />
                                )}
                                <span className={`text-xs ${item.satisfied ? "text-[var(--ink)]" : "text-[var(--secondary)]"}`}>
                                    {item.label}
                                </span>
                                {item.required && !item.satisfied && (
                                    <span className="font-technical text-[8px] text-[var(--blueprint)]">REQ</span>
                                )}
                            </div>
                        ))}
                    </div>
                </BlueprintCard>

            </div>
        </OnboardingStepLayout>
    );
}
