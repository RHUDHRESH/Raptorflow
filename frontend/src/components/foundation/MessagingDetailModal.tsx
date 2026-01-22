"use client";

import { useState } from "react";
import { X, ChevronDown, ChevronUp, MessageSquare, Target, Volume2, BookOpen, CheckCircle2, AlertCircle, Check, AlertTriangle, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { CoreMessaging } from "@/types/foundation";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   MESSAGING DETAIL MODAL ΓÇö Core Messaging & StoryBrand Framework
   One-liner, Positioning, Value Props, Brand Voice, StoryBrand
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface MessagingDetailModalProps {
    messaging: CoreMessaging;
    isOpen: boolean;
    onClose: () => void;
    onUpdate?: (updates: Partial<CoreMessaging>) => void;
}

export function MessagingDetailModal({ messaging, isOpen, onClose, onUpdate }: MessagingDetailModalProps) {
    const [expandedSections, setExpandedSections] = useState<string[]>(["oneliner", "positioning", "storybrand"]);

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
                        <div className="w-14 h-14 rounded-[var(--radius)] bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30 flex items-center justify-center">
                            <MessageSquare size={24} className="text-[var(--blueprint)]" />
                        </div>
                        <div>
                            <h2 className="font-serif text-2xl text-[var(--ink)]">Core Messaging</h2>
                            <p className="text-sm text-[var(--ink-secondary)]">Your brand's voice and positioning</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        {messaging.confidence && (
                            <div className="px-3 py-1 bg-[var(--surface)] border border-[var(--structure)] rounded-full">
                                <span className="text-xs text-[var(--ink-muted)]">Confidence: </span>
                                <span className="font-data text-sm text-[var(--ink)]">{messaging.confidence}%</span>
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

                    {/* One-Liner Section */}
                    <CollapsibleSection
                        title="One-Liner"
                        icon={Target}
                        isExpanded={isExpanded("oneliner")}
                        onToggle={() => toggleSection("oneliner")}
                        badge="Essential"
                    >
                        <div className="p-6 bg-[var(--ink)] rounded-xl text-center">
                            <p className="font-serif text-2xl text-[var(--paper)] leading-relaxed">
                                "{messaging.oneLiner}"
                            </p>
                        </div>
                        <p className="text-xs text-[var(--ink-muted)] mt-3 text-center">
                            The single sentence that explains what you do.
                        </p>
                    </CollapsibleSection>

                    {/* Positioning Statement Section */}
                    <CollapsibleSection
                        title="Positioning Statement"
                        icon={Target}
                        isExpanded={isExpanded("positioning")}
                        onToggle={() => toggleSection("positioning")}
                    >
                        <div className="p-5 bg-[var(--surface)] rounded-xl border border-[var(--structure-subtle)]">
                            <p className="text-lg text-[var(--ink)] leading-relaxed">
                                For <HighlightSpan>{messaging.positioningStatement.target}</HighlightSpan>{" "}
                                who <HighlightSpan>{messaging.positioningStatement.situation}</HighlightSpan>,{" "}
                                <HighlightSpan variant="brand">{messaging.positioningStatement.product}</HighlightSpan>{" "}
                                is the <HighlightSpan>{messaging.positioningStatement.category}</HighlightSpan>{" "}
                                that <HighlightSpan variant="success">{messaging.positioningStatement.keyBenefit}</HighlightSpan>{" "}
                                unlike <HighlightSpan variant="muted">{messaging.positioningStatement.alternatives}</HighlightSpan>{" "}
                                because <HighlightSpan variant="success">{messaging.positioningStatement.differentiator}</HighlightSpan>.
                            </p>
                        </div>
                    </CollapsibleSection>

                    {/* Value Props Section */}
                    <CollapsibleSection
                        title="Value Propositions"
                        icon={CheckCircle2}
                        isExpanded={isExpanded("valueprops")}
                        onToggle={() => toggleSection("valueprops")}
                        badge={`${messaging.valueProps.length}/3`}
                    >
                        <div className="space-y-4">
                            {messaging.valueProps.map((prop, i) => (
                                <div key={i} className="flex gap-4 p-4 bg-[var(--surface)] rounded-xl border border-[var(--structure-subtle)]">
                                    <div className="w-10 h-10 rounded-xl bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center font-bold shrink-0">
                                        {i + 1}
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-semibold text-[var(--ink)] mb-1">{prop.title}</h4>
                                        <p className="text-sm text-[var(--ink-secondary)] mb-2">{prop.description}</p>
                                        {prop.proof && (
                                            <div className="flex items-center gap-2 text-xs text-green-600">
                                                <CheckCircle2 size={12} />
                                                <span>Proof: {prop.proof}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CollapsibleSection>

                    {/* Brand Voice Section */}
                    <CollapsibleSection
                        title="Brand Voice Guidelines"
                        icon={Volume2}
                        isExpanded={isExpanded("voice")}
                        onToggle={() => toggleSection("voice")}
                    >
                        {/* Tone */}
                        <div className="mb-6">
                            <h4 className="text-xs font-bold text-[var(--ink-muted)] uppercase tracking-wide mb-3">Tone</h4>
                            <div className="flex flex-wrap gap-2">
                                {messaging.brandVoice.tone.map((t, i) => (
                                    <span key={i} className="px-3 py-1.5 bg-[var(--ink)] text-[var(--paper)] text-sm font-medium rounded-lg">
                                        {t}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Do / Don't */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
                                <h4 className="flex items-center gap-2 text-sm font-bold text-green-700 mb-3">
                                    <CheckCircle2 size={16} />
                                    Do
                                </h4>
                                <ul className="space-y-2">
                                    {messaging.brandVoice.doList.map((item, i) => (
                                        <li key={i} className="text-sm text-green-600 flex items-start gap-2">
                                            <Check className="text-green-500 mt-0.5" size={14} />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                                <h4 className="flex items-center gap-2 text-sm font-bold text-red-700 mb-3">
                                    <AlertCircle size={16} />
                                    Don't
                                </h4>
                                <ul className="space-y-2">
                                    {messaging.brandVoice.dontList.map((item, i) => (
                                        <li key={i} className="text-sm text-red-600 flex items-start gap-2">
                                            <X className="text-red-500 mt-0.5" size={14} />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </CollapsibleSection>

                    {/* StoryBrand Section */}
                    <CollapsibleSection
                        title="StoryBrand Framework"
                        icon={BookOpen}
                        isExpanded={isExpanded("storybrand")}
                        onToggle={() => toggleSection("storybrand")}
                        badge="7 Elements"
                    >
                        <p className="text-sm text-[var(--ink-secondary)] mb-6">
                            Your customer is the hero. Your brand is the guide that helps them succeed.
                        </p>

                        <div className="space-y-4">
                            {/* Character */}
                            <StoryBrandStep
                                number={1}
                                title="Character"
                                subtitle="The Hero"
                                content={messaging.storyBrand.character}
                                color="blue"
                            />

                            {/* Problem */}
                            <StoryBrandStep
                                number={2}
                                title="Problem"
                                subtitle="What They Face"
                                color="red"
                            >
                                <div className="space-y-2">
                                    <div className="flex gap-2">
                                        <span className="text-xs font-bold text-[var(--ink-muted)] w-20 shrink-0">External:</span>
                                        <span className="text-sm text-[var(--ink)]">{messaging.storyBrand.problemExternal}</span>
                                    </div>
                                    <div className="flex gap-2">
                                        <span className="text-xs font-bold text-[var(--ink-muted)] w-20 shrink-0">Internal:</span>
                                        <span className="text-sm text-[var(--ink)]">{messaging.storyBrand.problemInternal}</span>
                                    </div>
                                    <div className="flex gap-2">
                                        <span className="text-xs font-bold text-[var(--ink-muted)] w-20 shrink-0">Philosophical:</span>
                                        <span className="text-sm text-[var(--ink)]">{messaging.storyBrand.problemPhilosophical}</span>
                                    </div>
                                </div>
                            </StoryBrandStep>

                            {/* Guide */}
                            <StoryBrandStep
                                number={3}
                                title="Guide"
                                subtitle="Your Brand"
                                content={messaging.storyBrand.guide}
                                color="purple"
                            />

                            {/* Plan */}
                            <StoryBrandStep
                                number={4}
                                title="Plan"
                                subtitle="Clear Steps"
                                color="green"
                            >
                                <div className="flex flex-wrap gap-2">
                                    {messaging.storyBrand.plan.map((step, i) => (
                                        <span key={i} className="flex items-center gap-2 px-3 py-1.5 bg-green-100 text-green-700 text-sm rounded-lg">
                                            <span className="w-5 h-5 rounded-full bg-green-600 text-white text-xs flex items-center justify-center">{i + 1}</span>
                                            {step}
                                        </span>
                                    ))}
                                </div>
                            </StoryBrandStep>

                            {/* Call to Action */}
                            <StoryBrandStep
                                number={5}
                                title="Call to Action"
                                subtitle="Direct & Transitional"
                                color="orange"
                            >
                                <div className="flex gap-4">
                                    <div className="flex-1 p-3 bg-[var(--ink)] text-[var(--paper)] rounded-lg text-center">
                                        <span className="text-xs text-[var(--paper)]/60 block mb-1">Direct CTA</span>
                                        <span className="font-medium">{messaging.storyBrand.callToAction}</span>
                                    </div>
                                    {messaging.storyBrand.transitionalCTA && (
                                        <div className="flex-1 p-3 bg-[var(--surface)] border border-[var(--structure)] rounded-lg text-center">
                                            <span className="text-xs text-[var(--ink-muted)] block mb-1">Transitional CTA</span>
                                            <span className="font-medium text-[var(--ink)]">{messaging.storyBrand.transitionalCTA}</span>
                                        </div>
                                    )}
                                </div>
                            </StoryBrandStep>

                            {/* Avoid Failure */}
                            <StoryBrandStep
                                number={6}
                                title="Avoid Failure"
                                subtitle="What If They Don't Act"
                                color="red"
                            >
                                <div className="flex flex-wrap gap-2">
                                    {messaging.storyBrand.avoidFailure.map((item, i) => (
                                        <span key={i} className="px-3 py-1.5 bg-red-100 text-red-700 text-sm rounded-lg flex items-center gap-1.5">
                                            <AlertTriangle size={14} /> {item}
                                        </span>
                                    ))}
                                </div>
                            </StoryBrandStep>

                            {/* Success */}
                            <StoryBrandStep
                                number={7}
                                title="Success"
                                subtitle="The Transformation"
                                color="green"
                            >
                                <div className="flex flex-wrap gap-2">
                                    {messaging.storyBrand.success.map((item, i) => (
                                        <span key={i} className="px-3 py-1.5 bg-green-100 text-green-700 text-sm rounded-lg flex items-center gap-1.5">
                                            <Sparkles size={14} /> {item}
                                        </span>
                                    ))}
                                </div>
                            </StoryBrandStep>
                        </div>
                    </CollapsibleSection>

                </div>
            </div>
        </div>
    );
}

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   HELPER COMPONENTS
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface CollapsibleSectionProps {
    title: string;
    icon: React.ElementType;
    isExpanded: boolean;
    onToggle: () => void;
    children: React.ReactNode;
    badge?: string;
}

function CollapsibleSection({ title, icon: Icon, isExpanded, onToggle, children, badge }: CollapsibleSectionProps) {
    return (
        <div className="border border-[var(--structure)] rounded-xl overflow-hidden">
            <button
                onClick={onToggle}
                className="w-full flex items-center justify-between p-4 bg-[var(--surface)] hover:bg-[var(--surface)]/80 transition-colors"
            >
                <div className="flex items-center gap-3">
                    <Icon size={18} className="text-[var(--ink-muted)]" />
                    <span className="font-medium text-[var(--ink)]">{title}</span>
                    {badge && (
                        <span className="px-2 py-0.5 text-[10px] font-bold bg-[var(--blueprint-light)] text-[var(--blueprint)] rounded-full">
                            {badge}
                        </span>
                    )}
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

interface HighlightSpanProps {
    children: React.ReactNode;
    variant?: "default" | "brand" | "success" | "muted";
}

function HighlightSpan({ children, variant = "default" }: HighlightSpanProps) {
    const styles = {
        default: "bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded",
        brand: "bg-[var(--blueprint-light)] text-[var(--blueprint)] px-1.5 py-0.5 rounded font-semibold",
        success: "bg-green-100 text-green-700 px-1.5 py-0.5 rounded",
        muted: "bg-[var(--surface)] text-[var(--ink-muted)] px-1.5 py-0.5 rounded line-through",
    };
    return <span className={styles[variant]}>{children}</span>;
}

interface StoryBrandStepProps {
    number: number;
    title: string;
    subtitle: string;
    content?: string;
    color: "blue" | "red" | "purple" | "green" | "orange";
    children?: React.ReactNode;
}

function StoryBrandStep({ number, title, subtitle, content, color, children }: StoryBrandStepProps) {
    const colorStyles = {
        blue: "bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/30",
        red: "bg-[var(--error-light)] text-[var(--error)] border-[var(--error)]/30",
        purple: "bg-[var(--accent-light)] text-[var(--accent)] border-[var(--accent)]/30",
        green: "bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]/30",
        orange: "bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]/30",
    };

    return (
        <div className={cn("p-4 rounded-xl border", colorStyles[color])}>
            <div className="flex items-center gap-3 mb-2">
                <span className="w-6 h-6 rounded-full bg-current/20 flex items-center justify-center text-xs font-bold">
                    {number}
                </span>
                <div>
                    <span className="font-semibold">{title}</span>
                    <span className="text-xs opacity-70 ml-2">{subtitle}</span>
                </div>
            </div>
            {content && <p className="text-sm ml-9">{content}</p>}
            {children && <div className="ml-9">{children}</div>}
        </div>
    );
}

export default MessagingDetailModal;
