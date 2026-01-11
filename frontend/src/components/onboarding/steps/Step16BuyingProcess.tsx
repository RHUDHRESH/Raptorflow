"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, ArrowRight, ArrowLeft, Users, Search, Scale, CreditCard, Heart, Lightbulb, Target, Zap, MessageSquare } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { OnboardingStepLayout } from "../OnboardingStepLayout";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 16: Buying Process

   Educational content explaining buyer journey stages
   Shows how your ICPs move through each stage with specific behaviors
   ══════════════════════════════════════════════════════════════════════════════ */

interface BuyingStage {
    id: string;
    name: string;
    icon: React.ElementType;
    description: string;
    mindset: string;
    questions: string[];
    content: string[];
    triggers: string[];
    icpBehavior: string;
    keyInsight: string;
    code: string;
}

const BUYING_STAGES: BuyingStage[] = [
    {
        id: "1",
        name: "Problem Aware",
        icon: Users,
        description: "The buyer realizes they have a problem but may not know solutions exist.",
        mindset: "\"Something isn't working. This is frustrating.\"",
        questions: ["Why is this happening to me?", "Is this a real problem or just me?", "How urgent is this?"],
        content: ["Blog posts validating the pain", "Social proof that others feel this too", "Content about the cost of inaction"],
        triggers: ["Frustration event", "Competitor failure", "Team complaint", "Missed goal"],
        icpBehavior: "Your ICPs are likely in this stage when they're venting on social media, asking questions in communities, or searching for \"why is X so hard\"",
        keyInsight: "At this stage, DON'T sell your product. Validate their problem and build trust.",
        code: "STG-01"
    },
    {
        id: "2",
        name: "Solution Aware",
        icon: Search,
        description: "The buyer knows solutions exist and is exploring options.",
        mindset: "\"There must be a better way. What are my options?\"",
        questions: ["What solutions exist?", "How do others solve this?", "What are the approaches?"],
        content: ["Comparison guides", "\"How to\" educational content", "Solution frameworks"],
        triggers: ["Google search", "Peer recommendation", "Industry report", "Podcast mention"],
        icpBehavior: "Your ICPs are researching categories, reading reviews, and comparing approaches (not products yet)",
        keyInsight: "Position your APPROACH as the best solution type, not your product specifically.",
        code: "STG-02"
    },
    {
        id: "3",
        name: "Product Aware",
        icon: Scale,
        description: "The buyer knows your product exists and is evaluating fit.",
        mindset: "\"This looks interesting. Is it right for me?\"",
        questions: ["Is this right for my situation?", "What's the ROI?", "Can I trust this company?"],
        content: ["Case studies matching their profile", "Demo videos", "Product tours", "ROI calculators"],
        triggers: ["Website visit", "Content download", "Webinar attendance", "Social follow"],
        icpBehavior: "Your ICPs are on your website, watching demos, and looking for proof it works for companies like theirs",
        keyInsight: "Show them THEMSELVES in your case studies and examples. Mirror their situation.",
        code: "STG-03"
    },
    {
        id: "4",
        name: "Evaluation",
        icon: CreditCard,
        description: "The buyer is actively comparing you against alternatives.",
        mindset: "\"How does this compare? Can we afford it?\"",
        questions: ["How do you compare to X?", "What's the total cost?", "How hard is implementation?"],
        content: ["Pricing page", "Feature comparisons", "Implementation guides", "FAQ"],
        triggers: ["Demo request", "Free trial signup", "Pricing page visit", "Contact form"],
        icpBehavior: "Your ICPs are in spreadsheet mode—comparing features, prices, and implementation effort across options",
        keyInsight: "Make it EASY to compare. Hide nothing. Reduce friction in their evaluation.",
        code: "STG-04"
    },
    {
        id: "5",
        name: "Decision",
        icon: Heart,
        description: "The buyer is ready to commit but needs final reassurance.",
        mindset: "\"Am I making the right choice? What if this fails?\"",
        questions: ["What's the risk?", "What if it doesn't work?", "Can I get out if needed?"],
        content: ["Guarantees", "Success stories", "Testimonials from similar companies", "Support details"],
        triggers: ["Final objections", "Contract review", "Manager approval", "Legal review"],
        icpBehavior: "Your ICPs are seeking reassurance—they want to feel confident they won't look bad for choosing you",
        keyInsight: "Address fear, not features. Reduce perceived risk with guarantees and social proof.",
        code: "STG-05"
    },
];

// Progress indicator component
function JourneyProgress({ currentStage, totalStages }: { currentStage: number; totalStages: number }) {
    return (
        <div className="flex items-center gap-1">
            {Array.from({ length: totalStages }).map((_, i) => (
                <div
                    key={i}
                    className={`h-1.5 flex-1 rounded-full transition-all ${i <= currentStage ? "bg-[var(--blueprint)]" : "bg-[var(--border)]"
                        }`}
                />
            ))}
        </div>
    );
}

export default function Step16BuyingProcess() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(16)?.data as { reviewed?: boolean } | undefined;
    const [activeStage, setActiveStage] = useState(0);
    const [reviewed, setReviewed] = useState(stepData?.reviewed || false);
    const containerRef = useRef<HTMLDivElement>(null);
    const stageRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    // Animate stage change
    useEffect(() => {
        if (stageRef.current) {
            gsap.fromTo(stageRef.current,
                { opacity: 0, x: 20 },
                { opacity: 1, x: 0, duration: 0.3, ease: "power2.out" }
            );
        }
    }, [activeStage]);

    const handleConfirm = () => {
        setReviewed(true);
        updateStepData(16, { reviewed: true });
        updateStepStatus(16, "complete");
    };

    const stage = BUYING_STAGES[activeStage];
    const StageIcon = stage.icon;

    return (
        <OnboardingStepLayout stepId={16} moduleLabel="BUYING-PROCESS">
            <div ref={containerRef} className="space-y-6">
                {/* Educational Header */}
                <div data-animate className="text-center py-4">
                    <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">The Buyer's Journey</h2>
                    <p className="text-sm text-[var(--secondary)] max-w-lg mx-auto">
                        Your customers go through 5 distinct stages before purchasing. Understanding these stages
                        helps you create the right content and messaging for each moment.
                    </p>
                </div>

                {/* Stage Navigation */}
                <div data-animate>
                    <JourneyProgress currentStage={activeStage} totalStages={BUYING_STAGES.length} />
                    <div className="flex items-center gap-2 overflow-x-auto py-4 -mx-4 px-4">
                        {BUYING_STAGES.map((s, i) => {
                            const SIcon = s.icon;
                            return (
                                <button
                                    key={s.id}
                                    onClick={() => setActiveStage(i)}
                                    className={`
                                    flex items-center gap-2 px-4 py-2.5 font-technical text-[10px] rounded-lg
                                    whitespace-nowrap transition-all flex-shrink-0
                                    ${activeStage === i
                                            ? "bg-[var(--blueprint)] text-[var(--paper)] shadow-lg"
                                            : i < activeStage
                                                ? "bg-[var(--blueprint-light)] text-[var(--blueprint)] border border-[var(--blueprint)]/30"
                                                : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)] hover:border-[var(--blueprint)]"
                                        }
                                `}
                                >
                                    <SIcon size={14} strokeWidth={1.5} />{s.name}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Stage Content */}
                <div ref={stageRef}>
                    <BlueprintCard data-animate figure={`FIG. ${String(activeStage + 1).padStart(2, "0")}`} title={stage.name} code={stage.code} showCorners padding="lg">
                        {/* Stage Header */}
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-14 h-14 rounded-xl bg-[var(--blueprint)] flex items-center justify-center shadow-lg">
                                <StageIcon size={24} strokeWidth={1.5} className="text-[var(--paper)]" />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-serif text-[var(--ink)]">{stage.name}</h3>
                                <p className="text-sm text-[var(--secondary)]">{stage.description}</p>
                            </div>
                            <BlueprintBadge variant="blueprint">STAGE {activeStage + 1}/{BUYING_STAGES.length}</BlueprintBadge>
                        </div>

                        {/* Buyer Mindset */}
                        <div className="p-4 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)] mb-6">
                            <div className="flex items-center gap-2 mb-2">
                                <MessageSquare size={12} className="text-[var(--blueprint)]" />
                                <span className="font-technical text-[9px] text-[var(--muted)]">BUYER MINDSET</span>
                            </div>
                            <p className="text-base italic text-[var(--ink)]">{stage.mindset}</p>
                        </div>

                        {/* ICP Behavior - The "aha" moment */}
                        <div className="p-4 rounded-lg bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30 mb-6">
                            <div className="flex items-start gap-3">
                                <div className="w-8 h-8 rounded-lg bg-[var(--blueprint)] flex items-center justify-center flex-shrink-0">
                                    <Target size={14} className="text-[var(--paper)]" />
                                </div>
                                <div>
                                    <span className="font-technical text-[9px] text-[var(--blueprint)] block mb-1">YOUR ICP AT THIS STAGE</span>
                                    <p className="text-sm text-[var(--ink)]">{stage.icpBehavior}</p>
                                </div>
                            </div>
                        </div>

                        {/* Three Column Grid */}
                        <div className="grid md:grid-cols-3 gap-4 mb-6">
                            <div className="p-4 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                <span className="font-technical text-[9px] text-[var(--warning)] block mb-3">QUESTIONS THEY ASK</span>
                                <ul className="space-y-2">
                                    {stage.questions.map((q, i) => (
                                        <li key={i} className="text-sm text-[var(--secondary)] flex items-start gap-2">
                                            <span className="text-[var(--warning)]">?</span>{q}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="p-4 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                <span className="font-technical text-[9px] text-[var(--success)] block mb-3">CONTENT THEY NEED</span>
                                <ul className="space-y-2">
                                    {stage.content.map((c, i) => (
                                        <li key={i} className="text-sm text-[var(--secondary)] flex items-start gap-2">
                                            <Check size={12} className="text-[var(--success)] mt-0.5 flex-shrink-0" />{c}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="p-4 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                <span className="font-technical text-[9px] text-[var(--error)] block mb-3">WHAT TRIGGERS THEM</span>
                                <ul className="space-y-2">
                                    {stage.triggers.map((t, i) => (
                                        <li key={i} className="text-sm text-[var(--secondary)] flex items-start gap-2">
                                            <Zap size={12} className="text-[var(--error)] mt-0.5 flex-shrink-0" />{t}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Key Insight */}
                        <div className="p-4 rounded-lg bg-[var(--warning-light)] border border-[var(--warning)]/30">
                            <div className="flex items-start gap-3">
                                <Lightbulb size={18} className="text-[var(--warning)] flex-shrink-0 mt-0.5" />
                                <div>
                                    <span className="font-technical text-[9px] text-[var(--warning)] block mb-1">KEY INSIGHT</span>
                                    <p className="text-sm text-[var(--ink)]">{stage.keyInsight}</p>
                                </div>
                            </div>
                        </div>

                        {/* Navigation */}
                        <div className="flex justify-between mt-6 pt-4 border-t border-[var(--border-subtle)]">
                            <SecondaryButton
                                size="sm"
                                onClick={() => setActiveStage(Math.max(0, activeStage - 1))}
                                disabled={activeStage === 0}
                            >
                                <ArrowLeft size={12} strokeWidth={1.5} />Previous Stage
                            </SecondaryButton>
                            <SecondaryButton
                                size="sm"
                                onClick={() => setActiveStage(Math.min(BUYING_STAGES.length - 1, activeStage + 1))}
                                disabled={activeStage === BUYING_STAGES.length - 1}
                            >
                                Next Stage<ArrowRight size={12} strokeWidth={1.5} />
                            </SecondaryButton>
                        </div>
                    </BlueprintCard>
                </div>

                {/* Confirm */}
                {!reviewed && activeStage === BUYING_STAGES.length - 1 && (
                    <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                        <Check size={14} strokeWidth={1.5} />I Understand the Buyer's Journey
                    </BlueprintButton>
                )}

                {reviewed && (
                    <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                                <Check size={24} strokeWidth={2} className="text-[var(--paper)]" />
                            </div>
                            <div>
                                <span className="text-base font-serif text-[var(--ink)]">Buyer's Journey Mapped</span>
                                <p className="font-technical text-[10px] text-[var(--secondary)]">5 stages reviewed</p>
                            </div>
                            <BlueprintBadge variant="success" dot className="ml-auto">COMPLETE</BlueprintBadge>
                        </div>
                    </BlueprintCard>
                )}

            </div>
        </OnboardingStepLayout>
    );
}
