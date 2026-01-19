"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
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
    Zap,
    Plus,
    Wand2
} from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { cn } from "@/lib/utils";
import { openPlatform } from "@/lib/external-links";

/* ══════════════════════════════════════════════════════════════════════════════
   DAILY WINS — Quick Content Wins
   Quiet Luxury Redesign — Matches Moves page styling
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
    const router = useRouter();
    const pageRef = useRef<HTMLDivElement>(null);
    const cardRef = useRef<HTMLDivElement>(null);
    const [contentWin, setContentWin] = useState<ContentWin | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [copied, setCopied] = useState(false);
    const [streak, setStreak] = useState(0);
    const [totalWins, setTotalWins] = useState(0);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        const savedStreak = localStorage.getItem("daily_wins_streak");
        const savedTotal = localStorage.getItem("daily_wins_total");
        if (savedStreak) setStreak(parseInt(savedStreak, 10));
        if (savedTotal) setTotalWins(parseInt(savedTotal, 10));
    }, []);

    useEffect(() => {
        if (!pageRef.current || !mounted) return;
        gsap.fromTo(pageRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
    }, [mounted]);

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
                { opacity: 0, y: 16, scale: 0.98 },
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

    const expandInMuse = () => {
        if (!contentWin) return;
        const context = encodeURIComponent(JSON.stringify({
            topic: contentWin.topic,
            angle: contentWin.angle,
            hook: contentWin.hook,
            outline: contentWin.outline,
            platform: contentWin.platform
        }));
        router.push(`/muse?context=${context}`);
    };

    if (!mounted) return null;

    return (
        <div ref={pageRef} className="min-h-screen bg-[var(--canvas)]" style={{ opacity: 0 }}>
            {/* Page Header - Quiet Luxury */}
            <div className="border-b border-[var(--border)] bg-[var(--paper)]">
                <div className="max-w-3xl mx-auto px-6 py-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="font-serif text-3xl text-[var(--ink)]">
                                Daily Wins
                            </h1>
                            <p className="text-sm text-[var(--muted)] mt-1">
                                Quick content inspiration for busy days
                            </p>
                        </div>

                        {/* Stats Badges */}
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)]">
                                <Flame size={14} className="text-orange-500" />
                                <span className="text-sm font-medium text-[var(--ink)]">{streak} streak</span>
                            </div>
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)]">
                                <Trophy size={14} className="text-amber-500" />
                                <span className="text-sm font-medium text-[var(--ink)]">{totalWins} wins</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-3xl mx-auto px-6 py-8">
                <div className="max-w-xl mx-auto">

                    {/* Empty State - Generate Button */}
                    {!contentWin && !isGenerating && (
                        <div className="text-center py-16">
                            <div className="w-16 h-16 mx-auto mb-6 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                                <Sparkles size={24} className="text-[var(--muted)]" />
                            </div>
                            <h2 className="font-serif text-xl text-[var(--ink)] mb-2">Ready to post something?</h2>
                            <p className="text-[var(--muted)] max-w-sm mx-auto mb-8">
                                Get a quick content idea you can write and post in 10 minutes or less.
                            </p>

                            <button
                                onClick={generateWin}
                                className="flex items-center gap-2 px-6 py-3 mx-auto bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all font-medium"
                            >
                                <Zap size={16} />
                                Get Today's Win
                            </button>

                            <p className="mt-4 text-xs text-[var(--muted)]">
                                Quick, focused, satisfying.
                            </p>
                        </div>
                    )}

                    {/* Loading State */}
                    {isGenerating && (
                        <div className="text-center py-16">
                            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                                <RefreshCw size={18} className="text-[var(--muted)] animate-spin" />
                            </div>
                            <p className="text-[var(--muted)]">Finding your win...</p>
                        </div>
                    )}

                    {/* Content Win Card */}
                    {contentWin && !isGenerating && (
                        <div ref={cardRef} className="space-y-4" style={{ opacity: 0 }}>
                            {/* Topic Badge Row */}
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <span className="px-3 py-1 bg-[var(--ink)] text-white text-xs font-medium rounded-full">
                                        {contentWin.topic}
                                    </span>
                                    <span className="px-3 py-1 bg-[var(--surface)] text-[var(--muted)] text-xs rounded-full border border-[var(--border)]">
                                        {contentWin.platform}
                                    </span>
                                </div>
                                <div className="flex items-center gap-1 text-xs text-[var(--muted)]">
                                    <Clock size={12} />
                                    {contentWin.timeToPost}
                                </div>
                            </div>

                            {/* Main Card */}
                            <BlueprintCard showCorners padding="none">
                                {/* Hook */}
                                <div className="p-6 border-b border-[var(--border)]">
                                    <p className="text-xs text-[var(--muted)] uppercase tracking-wide mb-2 font-medium">{contentWin.angle}</p>
                                    <p className="text-lg text-[var(--ink)] leading-relaxed font-medium">
                                        "{contentWin.hook}"
                                    </p>
                                </div>

                                {/* Outline */}
                                <div className="p-6 bg-[var(--surface)]">
                                    <p className="text-xs text-[var(--muted)] uppercase tracking-wide mb-4 font-medium">Structure</p>
                                    <div className="space-y-3">
                                        {contentWin.outline.map((step, i) => (
                                            <div key={i} className="flex items-center gap-3">
                                                <div className="w-6 h-6 rounded-full bg-[var(--ink)] text-white text-xs font-bold flex items-center justify-center shrink-0">
                                                    {i + 1}
                                                </div>
                                                <span className="text-sm text-[var(--ink)]">{step}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex border-t border-[var(--border)]">
                                    <button
                                        onClick={copyToClipboard}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm text-[var(--muted)] hover:bg-[var(--surface)] hover:text-[var(--ink)] transition-colors border-r border-[var(--border)]"
                                    >
                                        {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                                        {copied ? "Copied" : "Copy"}
                                    </button>
                                    <button
                                        onClick={expandInMuse}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm text-[var(--blueprint)] hover:bg-[var(--blueprint)]/10 hover:text-[var(--blueprint)] transition-colors border-r border-[var(--border)] font-medium"
                                    >
                                        <Wand2 size={14} />
                                        Expand in Muse
                                    </button>
                                    <button
                                        onClick={() => openPlatform(contentWin.platform)}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm text-[var(--muted)] hover:bg-[var(--surface)] hover:text-[var(--ink)] transition-colors border-r border-[var(--border)]"
                                    >
                                        <ExternalLink size={14} />
                                        {contentWin.platform}
                                    </button>
                                    <button
                                        onClick={markAsDone}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium text-green-600 hover:bg-green-50 transition-colors"
                                    >
                                        <Check size={14} />
                                        Posted!
                                    </button>
                                </div>
                            </BlueprintCard>

                            {/* Try Another */}
                            <button
                                onClick={generateWin}
                                className="w-full flex items-center justify-center gap-2 py-3 text-sm text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
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
