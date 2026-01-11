"use client";

import { useState, useEffect, useRef } from "react";
import gsap from "gsap";
import {
    Sparkles,
    Copy,
    ExternalLink,
    Check,
    RefreshCw,
    Flame,
    Trophy,
    Clock,
    ArrowRight,
    MessageSquare
} from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { openPlatform } from "@/lib/external-links";

/* ══════════════════════════════════════════════════════════════════════════════
   DAILY WINS — Quick Content Wins
   For when you've had a long day but still want to post something meaningful.
   Calm, focused, satisfying. One-click content inspiration.
   ══════════════════════════════════════════════════════════════════════════════ */

interface ContentWin {
    id: string;
    topic: string;
    angle: string;
    hook: string;
    outline: string[];
    platform: string;
    timeToPost: string;
}

const CONTENT_IDEAS = [
    {
        topic: "Founder Lessons",
        angle: "What nobody tells you about...",
        hooks: [
            "The hardest part of building isn't the product. It's the waiting.",
            "I used to think more features = more customers. I was wrong.",
            "The best marketing decision I made? Talking to 50 customers before writing a single line of copy."
        ],
        outline: ["Opening hook", "The lesson", "What I do now", "Your takeaway"],
        platforms: ["LinkedIn", "X (Twitter)"]
    },
    {
        topic: "Industry Insight",
        angle: "A contrarian take on...",
        hooks: [
            "Everyone's chasing AI. The real opportunity? The boring problems nobody wants to solve.",
            "Hot take: Your competitors aren't your competition. Inertia is.",
            "The SaaS playbook from 2020 doesn't work anymore. Here's what does."
        ],
        outline: ["The common belief", "Why it's wrong", "The evidence", "The better way"],
        platforms: ["LinkedIn", "X (Twitter)"]
    },
    {
        topic: "Behind the Scenes",
        angle: "Real talk about...",
        hooks: [
            "This week's revenue: $0. This week's learnings: Priceless.",
            "Shipped a feature nobody asked for. Here's why it was the right call.",
            "Our biggest mistake this quarter (and what we're doing about it)."
        ],
        outline: ["The situation", "What happened", "The decision", "What's next"],
        platforms: ["LinkedIn", "X (Twitter)", "Newsletter"]
    },
    {
        topic: "Quick Tips",
        angle: "One thing that changed everything...",
        hooks: [
            "Stop scheduling posts for 9am. Here's when your audience actually reads.",
            "The 2-minute exercise that 10x'd our content engagement.",
            "Forget the algorithm. Focus on this one metric instead."
        ],
        outline: ["The problem", "The solution", "How to apply it", "Results you'll see"],
        platforms: ["X (Twitter)", "LinkedIn"]
    }
];

export default function DailyWinsPage() {
    const pageRef = useRef<HTMLDivElement>(null);
    const cardRef = useRef<HTMLDivElement>(null);
    const [contentWin, setContentWin] = useState<ContentWin | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [copied, setCopied] = useState(false);
    const [streak, setStreak] = useState(0);
    const [totalWins, setTotalWins] = useState(0);

    useEffect(() => {
        const savedStreak = localStorage.getItem("daily_wins_streak");
        const savedTotal = localStorage.getItem("daily_wins_total");
        if (savedStreak) setStreak(parseInt(savedStreak, 10));
        if (savedTotal) setTotalWins(parseInt(savedTotal, 10));
    }, []);

    useEffect(() => {
        if (!pageRef.current) return;
        gsap.fromTo(pageRef.current, { opacity: 0 }, { opacity: 1, duration: 0.4 });
    }, []);

    const generateWin = () => {
        setIsGenerating(true);

        setTimeout(() => {
            const category = CONTENT_IDEAS[Math.floor(Math.random() * CONTENT_IDEAS.length)];
            const hook = category.hooks[Math.floor(Math.random() * category.hooks.length)];
            const platform = category.platforms[Math.floor(Math.random() * category.platforms.length)];

            setContentWin({
                id: `WIN-${Date.now()}`,
                topic: category.topic,
                angle: category.angle,
                hook,
                outline: category.outline,
                platform,
                timeToPost: "~10 min"
            });

            setIsGenerating(false);
        }, 800);
    };

    useEffect(() => {
        if (contentWin && !isGenerating && cardRef.current) {
            gsap.fromTo(cardRef.current,
                { opacity: 0, y: 20, scale: 0.98 },
                { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power2.out" }
            );
        }
    }, [contentWin, isGenerating]);

    const markAsDone = () => {
        const newStreak = streak + 1;
        const newTotal = totalWins + 1;
        setStreak(newStreak);
        setTotalWins(newTotal);
        localStorage.setItem("daily_wins_streak", newStreak.toString());
        localStorage.setItem("daily_wins_total", newTotal.toString());
        setContentWin(null);
    };

    const copyToClipboard = async () => {
        if (!contentWin) return;
        const text = `${contentWin.hook}\n\n${contentWin.outline.map((s, i) => `${i + 1}. ${s}`).join("\n")}`;
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div ref={pageRef} className="min-h-[calc(100vh-80px)] flex flex-col" style={{ opacity: 0 }}>
            {/* Header */}
            <div className="px-8 py-6 border-b border-[var(--structure)]">
                <div className="max-w-2xl mx-auto align-between gap-4">
                    <div>
                        <div className="align-start gap-3 mb-1">
                            <span className="font-technical text-[var(--blueprint)]">SYS.WINS</span>
                            <div className="h-px w-8 bg-[var(--structure)]" />
                            <span className="font-technical text-[var(--ink-muted)]">DAILY</span>
                        </div>
                        <h1 className="font-serif text-2xl text-[var(--ink)]">Daily Wins</h1>
                        <p className="text-sm text-[var(--ink-secondary)]">Quick content wins for busy days</p>
                    </div>
                    <div className="align-center gap-4">
                        <div className="align-center gap-2 px-3 py-1.5 bg-[var(--warning-light)] border border-[var(--warning)]/30 rounded-[var(--radius-sm)]">
                            <Flame size={14} className="text-[var(--warning)]" />
                            <span className="text-sm font-medium text-[var(--warning)]">{streak} day streak</span>
                        </div>
                        <div className="align-center gap-2 px-3 py-1.5 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)]">
                            <Trophy size={14} className="text-[var(--blueprint)]" />
                            <span className="text-sm font-medium text-[var(--ink)]">{totalWins} wins</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 align-center p-8">
                <div className="w-full max-w-xl">

                    {/* Empty State - Generate Button */}
                    {!contentWin && !isGenerating && (
                        <div className="text-center">
                            <div className="mb-6">
                                <div className="inline-flex align-center justify-center w-20 h-20 rounded-[var(--radius)] bg-[var(--blueprint-light)] border border-[var(--blueprint)]/20 mb-4">
                                    <MessageSquare size={32} className="text-[var(--blueprint)]" />
                                </div>
                                <h2 className="font-serif text-xl text-[var(--ink)] mb-2">Ready to post something?</h2>
                                <p className="text-[var(--ink-secondary)] max-w-sm mx-auto">
                                    Get a quick content idea you can write and post in 10 minutes or less.
                                </p>
                            </div>

                            <BlueprintButton
                                size="lg"
                                onClick={generateWin}
                            >
                                <Sparkles size={20} />
                                Get Today's Win
                            </BlueprintButton>

                            <p className="mt-4 text-xs text-[var(--ink-muted)]">
                                Quick, focused, satisfying.
                            </p>
                        </div>
                    )}

                    {/* Loading State */}
                    {isGenerating && (
                        <div className="text-center py-12">
                            <div className="inline-flex align-center justify-center w-16 h-16 rounded-full bg-[var(--surface)] border border-[var(--structure)] mb-4">
                                <RefreshCw size={24} className="text-[var(--blueprint)] animate-spin" />
                            </div>
                            <p className="text-[var(--ink-secondary)]">Finding your win...</p>
                        </div>
                    )}

                    {/* Content Win Card */}
                    {contentWin && !isGenerating && (
                        <div ref={cardRef} className="space-y-4" style={{ opacity: 0 }}>
                            {/* Topic Badge */}
                            <div className="align-between gap-2">
                                <div className="align-center gap-2">
                                    <span className="px-3 py-1 bg-[var(--blueprint-light)] text-[var(--blueprint)] text-xs font-bold rounded-full">
                                        {contentWin.topic}
                                    </span>
                                    <span className="px-3 py-1 bg-[var(--surface)] text-[var(--ink-secondary)] text-xs rounded-full">
                                        {contentWin.platform}
                                    </span>
                                </div>
                                <div className="align-center gap-1 text-xs text-[var(--ink-muted)]">
                                    <Clock size={12} />
                                    {contentWin.timeToPost}
                                </div>
                            </div>

                            {/* Main Card */}
                            <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] overflow-hidden shadow-sm">
                                {/* Hook */}
                                <div className="p-6 border-b border-[var(--structure-subtle)]">
                                    <p className="text-xs text-[var(--ink-muted)] uppercase tracking-wide mb-2">{contentWin.angle}</p>
                                    <p className="text-lg text-[var(--ink)] leading-relaxed font-medium">
                                        "{contentWin.hook}"
                                    </p>
                                </div>

                                {/* Outline */}
                                <div className="p-6 bg-[var(--surface)]/50">
                                    <p className="text-xs text-[var(--ink-muted)] uppercase tracking-wide mb-3">Structure</p>
                                    <div className="space-y-2">
                                        {contentWin.outline.map((step, i) => (
                                            <div key={i} className="justify-start gap-3">
                                                <div className="w-6 h-6 rounded-full bg-[var(--ink)] text-[var(--paper)] text-xs font-bold flex items-center justify-center shrink-0">
                                                    {i + 1}
                                                </div>
                                                <span className="text-sm text-[var(--ink-secondary)]">{step}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex border-t border-[var(--structure)]">
                                    <button
                                        onClick={copyToClipboard}
                                        className="flex-1 align-center justify-center gap-2 py-3 text-sm text-[var(--ink-secondary)] hover:bg-[var(--surface)] transition-colors border-r border-[var(--structure)]"
                                    >
                                        {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                                        {copied ? "Copied" : "Copy"}
                                    </button>
                                    <button
                                        onClick={() => openPlatform(contentWin.platform)}
                                        className="flex-1 align-center justify-center gap-2 py-3 text-sm text-[var(--ink-secondary)] hover:bg-[var(--surface)] transition-colors border-r border-[var(--structure)]"
                                    >
                                        <ExternalLink size={16} />
                                        Open {contentWin.platform}
                                    </button>
                                    <button
                                        onClick={markAsDone}
                                        className="flex-1 align-center justify-center gap-2 py-3 text-sm font-medium text-green-600 hover:bg-green-50 transition-colors"
                                    >
                                        <Check size={16} />
                                        Posted!
                                    </button>
                                </div>
                            </div>

                            {/* Try Another */}
                            <button
                                onClick={generateWin}
                                className="w-full align-center justify-center gap-2 py-3 text-sm text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
                            >
                                <RefreshCw size={14} />
                                Get another idea
                            </button>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}
