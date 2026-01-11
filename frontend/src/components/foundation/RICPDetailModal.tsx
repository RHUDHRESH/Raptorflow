"use client";

import { useState } from "react";
import { X, ChevronDown, ChevronUp, Users, Brain, Target, MessageSquare, Clock, Zap, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { RICP, MARKET_SOPHISTICATION_LABELS, MarketSophisticationStage } from "@/types/foundation";

/* ══════════════════════════════════════════════════════════════════════════════
   RICP DETAIL MODAL — Rich Ideal Customer Profile View
   Full breakdown: Demographics, Psychographics, Market Sophistication, Usage
   ══════════════════════════════════════════════════════════════════════════════ */

interface RICPDetailModalProps {
    ricp: RICP;
    isOpen: boolean;
    onClose: () => void;
    onUpdate?: (updates: Partial<RICP>) => void;
}

export function RICPDetailModal({ ricp, isOpen, onClose, onUpdate }: RICPDetailModalProps) {
    const [expandedSections, setExpandedSections] = useState<string[]>(["demographics", "psychographics"]);

    if (!isOpen) return null;

    const toggleSection = (section: string) => {
        setExpandedSections((prev) =>
            prev.includes(section) ? prev.filter((s) => s !== section) : [...prev, section]
        );
    };

    const isExpanded = (section: string) => expandedSections.includes(section);

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center p-4 overflow-y-auto">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

            {/* Modal */}
            <div className="relative w-full max-w-4xl my-8 bg-[var(--paper)] rounded-[var(--radius)] border border-[var(--structure)] shadow-2xl overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-4 duration-300">
                {/* Header */}
                <div className="sticky top-0 z-10 flex items-center justify-between p-8 border-b border-[var(--structure)] bg-[var(--paper)]">
                    <div className="flex items-center gap-5">
                        <div className="w-14 h-14 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--structure)] flex items-center justify-center text-3xl">
                            {ricp.avatar || "👤"}
                        </div>
                        <div>
                            <h2 className="font-serif text-2xl text-[var(--ink)]">{ricp.name}</h2>
                            {ricp.personaName && (
                                <p className="text-sm text-[var(--ink-secondary)]">Persona: {ricp.personaName}</p>
                            )}
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        {ricp.confidence && (
                            <div className="px-3 py-1 bg-[var(--surface)] border border-[var(--structure)] rounded-full">
                                <span className="text-xs text-[var(--ink-muted)]">Confidence: </span>
                                <span className="font-data text-sm text-[var(--ink)]">{ricp.confidence}%</span>
                            </div>
                        )}
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-[var(--surface)] rounded-lg transition-colors"
                        >
                            <X size={20} className="text-[var(--ink-muted)]" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-8 space-y-8">

                    {/* Demographics Section */}
                    <CollapsibleSection
                        title="Demographics"
                        icon={Users}
                        isExpanded={isExpanded("demographics")}
                        onToggle={() => toggleSection("demographics")}
                    >
                        <div className="grid grid-cols-2 gap-4">
                            <InfoField label="Age Range" value={ricp.demographics.ageRange} />
                            <InfoField label="Income" value={ricp.demographics.income} />
                            <InfoField label="Location" value={ricp.demographics.location} />
                            <InfoField label="Role" value={ricp.demographics.role} />
                            <InfoField label="Stage" value={ricp.demographics.stage} className="col-span-2" />
                        </div>
                    </CollapsibleSection>

                    {/* Psychographics Section */}
                    <CollapsibleSection
                        title="Psychographics"
                        icon={Brain}
                        isExpanded={isExpanded("psychographics")}
                        onToggle={() => toggleSection("psychographics")}
                    >
                        {/* Mindset */}
                        <div className="mb-6">
                            <h4 className="text-xs font-bold text-[var(--ink-muted)] uppercase tracking-wide mb-3">Mindset</h4>
                            <div className="space-y-3">
                                <InfoField label="Beliefs" value={ricp.psychographics.beliefs} />
                                <InfoField label="Identity" value={ricp.psychographics.identity} />
                                <InfoField label="Becoming" value={ricp.psychographics.becoming} />
                                <InfoField label="Fears" value={ricp.psychographics.fears} highlight="warning" />
                                <TagList label="Values" items={ricp.psychographics.values} />
                            </div>
                        </div>

                        {/* Behaviors */}
                        <div className="mb-6">
                            <h4 className="text-xs font-bold text-[var(--ink-muted)] uppercase tracking-wide mb-3">Behaviors</h4>
                            <div className="space-y-3">
                                <TagList label="Hangouts" items={ricp.psychographics.hangouts} variant="surface" />
                                <TagList label="Content Consumed" items={ricp.psychographics.contentConsumed} variant="surface" />
                                <TagList label="Who They Follow" items={ricp.psychographics.whoTheyFollow} variant="surface" />
                            </div>
                        </div>

                        {/* Triggers & Timing */}
                        <div>
                            <h4 className="text-xs font-bold text-[var(--ink-muted)] uppercase tracking-wide mb-3">Triggers & Timing</h4>
                            <div className="space-y-3">
                                <TagList label="Language" items={ricp.psychographics.language} variant="code" />
                                <TagList label="Timing" items={ricp.psychographics.timing} icon={Clock} />
                                <TagList label="Triggers" items={ricp.psychographics.triggers} icon={Zap} variant="accent" />
                            </div>
                        </div>
                    </CollapsibleSection>

                    {/* Market Sophistication Section */}
                    <CollapsibleSection
                        title="Market Sophistication"
                        icon={Target}
                        isExpanded={isExpanded("sophistication")}
                        onToggle={() => toggleSection("sophistication")}
                    >
                        <p className="text-sm text-[var(--ink-secondary)] mb-4">
                            Which stage of awareness is this customer at? This affects your messaging strategy.
                        </p>
                        <div className="space-y-2">
                            {([1, 2, 3, 4, 5] as MarketSophisticationStage[]).map((stage) => {
                                const info = MARKET_SOPHISTICATION_LABELS[stage];
                                const isSelected = ricp.marketSophistication === stage;
                                return (
                                    <button
                                        key={stage}
                                        onClick={() => onUpdate?.({ marketSophistication: stage })}
                                        className={cn(
                                            "w-full flex items-center gap-4 p-4 rounded-xl border transition-all text-left",
                                            isSelected
                                                ? "border-[var(--ink)] bg-[var(--ink)] text-[var(--paper)]"
                                                : "border-[var(--structure)] bg-[var(--paper)] hover:border-[var(--structure-strong)]"
                                        )}
                                    >
                                        <div className={cn(
                                            "w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm",
                                            isSelected ? "bg-[var(--paper)] text-[var(--ink)]" : "bg-[var(--surface)] text-[var(--ink)]"
                                        )}>
                                            {stage}
                                        </div>
                                        <div className="flex-1">
                                            <h5 className={cn("font-medium", isSelected ? "text-[var(--paper)]" : "text-[var(--ink)]")}>
                                                {info.name}
                                            </h5>
                                            <p className={cn("text-sm", isSelected ? "text-[var(--paper)]/70" : "text-[var(--ink-muted)]")}>
                                                {info.description}
                                            </p>
                                        </div>
                                        {isSelected && <CheckCircle2 size={20} />}
                                    </button>
                                );
                            })}
                        </div>
                    </CollapsibleSection>

                    {/* Usage Guidance Section */}
                    <CollapsibleSection
                        title="How to Use This RICP"
                        icon={MessageSquare}
                        isExpanded={isExpanded("usage")}
                        onToggle={() => toggleSection("usage")}
                    >
                        <div className="space-y-4">
                            <UsageCard
                                title="Content Creation"
                                emoji="✍️"
                                description={`Write every post, email, and ad as if speaking directly to ${ricp.personaName || 'this person'}. Use their language and address their fears.`}
                            />
                            <UsageCard
                                title="Channel Selection"
                                emoji="📍"
                                description={`Only show up where ${ricp.personaName || 'they'} hang${ricp.personaName ? 's' : ''} out. If they're not on a platform, neither are you.`}
                            />
                            <UsageCard
                                title="Product Decisions"
                                emoji="🎯"
                                description={`Every feature should solve ${ricp.personaName || 'their'}'s problems. Every price point should match their willingness to pay.`}
                            />
                        </div>
                    </CollapsibleSection>

                </div>
            </div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   HELPER COMPONENTS
   ══════════════════════════════════════════════════════════════════════════════ */

interface CollapsibleSectionProps {
    title: string;
    icon: React.ElementType;
    isExpanded: boolean;
    onToggle: () => void;
    children: React.ReactNode;
}

function CollapsibleSection({ title, icon: Icon, isExpanded, onToggle, children }: CollapsibleSectionProps) {
    return (
        <div className="border border-[var(--structure)] rounded-xl overflow-hidden">
            <button
                onClick={onToggle}
                className="w-full flex items-center justify-between p-4 bg-[var(--surface)] hover:bg-[var(--surface)]/80 transition-colors"
            >
                <div className="flex items-center gap-3">
                    <Icon size={18} className="text-[var(--ink-muted)]" />
                    <span className="font-medium text-[var(--ink)]">{title}</span>
                </div>
                {isExpanded ? (
                    <ChevronUp size={18} className="text-[var(--ink-muted)]" />
                ) : (
                    <ChevronDown size={18} className="text-[var(--ink-muted)]" />
                )}
            </button>
            {isExpanded && (
                <div className="p-4 bg-[var(--paper)] animate-in slide-in-from-top-2 duration-200">
                    {children}
                </div>
            )}
        </div>
    );
}

interface InfoFieldProps {
    label: string;
    value: string;
    className?: string;
    highlight?: "warning" | "success";
}

function InfoField({ label, value, className, highlight }: InfoFieldProps) {
    return (
        <div className={cn("p-3 bg-[var(--surface)] rounded-lg border border-[var(--structure-subtle)]", className)}>
            <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase tracking-wide block mb-1">{label}</span>
            <span className={cn(
                "text-sm text-[var(--ink)]",
                highlight === "warning" && "text-orange-600",
                highlight === "success" && "text-green-600"
            )}>
                {value}
            </span>
        </div>
    );
}

interface TagListProps {
    label: string;
    items: string[];
    variant?: "default" | "surface" | "code" | "accent";
    icon?: React.ElementType;
}

function TagList({ label, items, variant = "default", icon: Icon }: TagListProps) {
    const tagStyles = {
        default: "bg-[var(--paper)] border-[var(--structure)]",
        surface: "bg-[var(--surface)] border-[var(--structure-subtle)]",
        code: "bg-[var(--ink)] text-[var(--paper)] border-transparent font-mono text-[10px]",
        accent: "bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/30",
    };

    return (
        <div>
            <div className="flex items-center gap-2 mb-2">
                {Icon && <Icon size={12} className="text-[var(--ink-muted)]" />}
                <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase tracking-wide">{label}</span>
            </div>
            <div className="flex flex-wrap gap-2">
                {items.map((item, i) => (
                    <span
                        key={i}
                        className={cn(
                            "px-2.5 py-1 text-xs rounded-lg border",
                            tagStyles[variant]
                        )}
                    >
                        {item}
                    </span>
                ))}
            </div>
        </div>
    );
}

interface UsageCardProps {
    title: string;
    emoji: string;
    description: string;
}

function UsageCard({ title, emoji, description }: UsageCardProps) {
    return (
        <div className="flex gap-4 p-4 bg-[var(--surface)] rounded-xl border border-[var(--structure-subtle)]">
            <span className="text-2xl">{emoji}</span>
            <div>
                <h5 className="font-medium text-[var(--ink)] mb-1">{title}</h5>
                <p className="text-sm text-[var(--ink-secondary)]">{description}</p>
            </div>
        </div>
    );
}

export default RICPDetailModal;
