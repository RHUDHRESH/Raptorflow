"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, ArrowUp, ArrowDown, GripVertical, MessageSquare, Megaphone, Target, Eye, Layers } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 19: Message Hierarchy

   Visual hierarchy builder with live preview
   Arrange messages by importance: headlines → subheads → body
   ══════════════════════════════════════════════════════════════════════════════ */

interface HierarchyItem {
    id: string;
    level: number;
    type: "headline" | "subhead" | "body";
    content: string;
    code: string;
}

const INITIAL_HIERARCHY: HierarchyItem[] = [
    { id: "1", level: 1, type: "headline", content: "Marketing. Finally under control.", code: "MSG-01" },
    { id: "2", level: 2, type: "subhead", content: "RaptorFlow extracts and validates your positioning in hours, not months.", code: "MSG-02" },
    { id: "3", level: 3, type: "body", content: "For founders scaling their first marketing team, we provide the system to build validated positioning from your existing evidence.", code: "MSG-03" },
    { id: "4", level: 2, type: "subhead", content: "AI-powered extraction from your existing content", code: "MSG-04" },
    { id: "5", level: 3, type: "body", content: "Upload your website, pitch deck, and content. We extract claims, validate facts, and surface contradictions automatically.", code: "MSG-05" },
];

const typeConfig = {
    headline: {
        icon: Megaphone,
        label: "HEADLINE",
        color: "text-[var(--blueprint)]",
        bg: "bg-[var(--blueprint)]",
        lightBg: "bg-[var(--blueprint-light)]",
        previewClass: "text-2xl font-serif text-[var(--ink)]"
    },
    subhead: {
        icon: Target,
        label: "SUBHEAD",
        color: "text-[var(--warning)]",
        bg: "bg-[var(--warning)]",
        lightBg: "bg-[var(--warning-light)]",
        previewClass: "text-lg font-semibold text-[var(--ink)]"
    },
    body: {
        icon: MessageSquare,
        label: "BODY",
        color: "text-[var(--muted)]",
        bg: "bg-[var(--canvas)]",
        lightBg: "bg-[var(--canvas)]",
        previewClass: "text-sm text-[var(--secondary)]"
    },
};

// Hierarchy item with visual level indicator
function HierarchyRow({
    item,
    index,
    total,
    onMove
}: {
    item: HierarchyItem;
    index: number;
    total: number;
    onMove: (direction: "up" | "down") => void;
}) {
    const config = typeConfig[item.type];
    const ConfigIcon = config.icon;

    return (
        <div
            className={`
                flex items-start gap-3 p-4 rounded-xl transition-all
                bg-[var(--paper)] border-2 border-[var(--border)]
                hover:border-[var(--blueprint)]/50 hover:shadow-sm
            `}
            style={{ marginLeft: `${(item.level - 1) * 20}px` }}
        >
            {/* Level indicator */}
            <div className="flex flex-col items-center gap-1">
                <div className={`w-8 h-8 rounded-lg ${config.bg} flex items-center justify-center`}>
                    <ConfigIcon size={14} strokeWidth={1.5} className={item.type === "body" ? "text-[var(--muted)]" : "text-[var(--paper)]"} />
                </div>
                <span className="font-technical text-[8px] text-[var(--muted)]">L{item.level}</span>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <span className="font-technical text-[9px] text-[var(--blueprint)]">{item.code}</span>
                    <BlueprintBadge
                        variant={item.type === "headline" ? "blueprint" : item.type === "subhead" ? "warning" : "default"}
                        className="text-[8px]"
                    >
                        {config.label}
                    </BlueprintBadge>
                </div>
                <p className={`${item.type === "headline" ? "text-base font-semibold" : item.type === "subhead" ? "text-sm font-medium" : "text-sm"} text-[var(--ink)]`}>
                    {item.content}
                </p>
            </div>

            {/* Reorder controls */}
            <div className="flex flex-col gap-1">
                <button
                    onClick={() => onMove("up")}
                    disabled={index === 0}
                    className="p-1.5 rounded-lg hover:bg-[var(--canvas)] disabled:opacity-20 transition-all"
                    title="Move up"
                >
                    <ArrowUp size={14} strokeWidth={1.5} className="text-[var(--muted)]" />
                </button>
                <button
                    onClick={() => onMove("down")}
                    disabled={index === total - 1}
                    className="p-1.5 rounded-lg hover:bg-[var(--canvas)] disabled:opacity-20 transition-all"
                    title="Move down"
                >
                    <ArrowDown size={14} strokeWidth={1.5} className="text-[var(--muted)]" />
                </button>
            </div>
        </div>
    );
}

export default function Step19MessageHierarchy() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(19)?.data as { hierarchy?: HierarchyItem[]; confirmed?: boolean } | undefined;
    const [hierarchy, setHierarchy] = useState<HierarchyItem[]>(stepData?.hierarchy || INITIAL_HIERARCHY);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [showPreview, setShowPreview] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    const saveData = (items: HierarchyItem[]) => {
        setHierarchy(items);
        updateStepData(19, { hierarchy: items });
    };

    const moveItem = (id: string, direction: "up" | "down") => {
        const idx = hierarchy.findIndex((h) => h.id === id);
        if (idx === -1) return;
        if (direction === "up" && idx === 0) return;
        if (direction === "down" && idx === hierarchy.length - 1) return;

        const newHierarchy = [...hierarchy];
        const swapIdx = direction === "up" ? idx - 1 : idx + 1;
        [newHierarchy[idx], newHierarchy[swapIdx]] = [newHierarchy[swapIdx], newHierarchy[idx]];
        saveData(newHierarchy);
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(19, { hierarchy, confirmed: true });
        updateStepStatus(19, "complete");
    };

    // Stats
    const headlines = hierarchy.filter(h => h.type === "headline").length;
    const subheads = hierarchy.filter(h => h.type === "subhead").length;
    const bodyItems = hierarchy.filter(h => h.type === "body").length;

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Header */}
            <div data-animate className="text-center py-4">
                <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">Message Hierarchy</h2>
                <p className="text-sm text-[var(--secondary)] max-w-lg mx-auto">
                    Great messaging follows a hierarchy: lead with headlines, support with subheads, explain with body.
                    Arrange your messages in order of importance.
                </p>
            </div>

            {/* Stats */}
            <div data-animate className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30 text-center">
                    <Megaphone size={16} className="mx-auto mb-1 text-[var(--blueprint)]" />
                    <span className="text-2xl font-serif text-[var(--blueprint)]">{headlines}</span>
                    <p className="font-technical text-[8px] text-[var(--blueprint)]">HEADLINES</p>
                </div>
                <div className="p-4 rounded-xl bg-[var(--warning-light)] border border-[var(--warning)]/30 text-center">
                    <Target size={16} className="mx-auto mb-1 text-[var(--warning)]" />
                    <span className="text-2xl font-serif text-[var(--warning)]">{subheads}</span>
                    <p className="font-technical text-[8px] text-[var(--warning)]">SUBHEADS</p>
                </div>
                <div className="p-4 rounded-xl bg-[var(--canvas)] border border-[var(--border)] text-center">
                    <MessageSquare size={16} className="mx-auto mb-1 text-[var(--muted)]" />
                    <span className="text-2xl font-serif text-[var(--ink)]">{bodyItems}</span>
                    <p className="font-technical text-[8px] text-[var(--muted)]">BODY</p>
                </div>
            </div>

            {/* Toggle Preview */}
            <div data-animate className="flex justify-end">
                <button
                    onClick={() => setShowPreview(!showPreview)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-technical text-[10px] transition-all ${showPreview
                        ? "bg-[var(--blueprint)] text-[var(--paper)]"
                        : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)]"
                        }`}
                >
                    <Eye size={12} />{showPreview ? "HIDE PREVIEW" : "SHOW PREVIEW"}
                </button>
            </div>

            {/* Preview Panel */}
            {showPreview && (
                <BlueprintCard data-animate figure="PREVIEW" title="How It Looks" code="PREV" showCorners padding="lg" className="bg-[var(--paper)]">
                    <div className="space-y-4 max-w-xl">
                        {hierarchy.map((item) => {
                            const config = typeConfig[item.type];
                            return (
                                <p key={item.id} className={config.previewClass}>
                                    {item.content}
                                </p>
                            );
                        })}
                    </div>
                </BlueprintCard>
            )}

            {/* Hierarchy Builder */}
            <BlueprintCard data-animate figure="FIG. 01" title="Arrange Your Messages" code="HIER" showCorners padding="md">
                <p className="text-xs text-[var(--secondary)] mb-4">
                    Use the arrows to reorder. Messages at the top are most important.
                </p>
                <div className="space-y-3">
                    {hierarchy.map((item, idx) => (
                        <HierarchyRow
                            key={item.id}
                            item={item}
                            index={idx}
                            total={hierarchy.length}
                            onMove={(direction) => moveItem(item.id, direction)}
                        />
                    ))}
                </div>
            </BlueprintCard>

            {/* Confirm */}
            {!confirmed && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                    <Layers size={14} strokeWidth={1.5} />Lock Message Hierarchy
                </BlueprintButton>
            )}

            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                            <Layers size={20} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="text-base font-serif text-[var(--ink)]">Hierarchy Locked</span>
                            <p className="font-technical text-[10px] text-[var(--secondary)]">{hierarchy.length} messages arranged</p>
                        </div>
                        <BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">MESSAGE-HIERARCHY • STEP 18/24</span>
            </div>
        </div>
    );
}
