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
import { useAuth } from "@/components/auth/AuthProvider";

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
    score?: number;
    intelligenceBrief?: string;
    visualPrompt?: string;
    engagementPrediction?: number;
    viralPotential?: number;
    followUpIdeas?: string[];
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
    const [isSurprising, setIsSurprising] = useState(false);
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

    const { user, profile } = useAuth();

    const generateWin = async (surprise: boolean = false) => {
        setIsGenerating(true);
        setIsSurprising(surprise);

        try {
            const workspaceId = profile?.workspace_id;
            if (!workspaceId) {
                throw new Error("No workspace ID");
            }

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/daily_wins/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    workspace_id: workspaceId,
                    user_id: user?.id,
                    force_refresh: surprise
                })
            });

            if (!response.ok) throw new Error("Failed to generate win");

            const data = await response.json();
            
            if (data.success && data.win) {
                const win = data.win;
                setContentWin({
                    id: win.id || `WIN-${Date.now()}`,
                    topic: win.topic || "Daily Insight",
                    angle: win.angle || "Strategic View",
                    hook: win.hook || win.content,
                    outline: win.hooks || (Array.isArray(win.outline) ? win.outline : ["Context", "Action", "Result"]),
                    platform: win.platform || "LinkedIn",
                    timeToPost: win.timeToPost || "~10 min",
                    score: win.score,
                    intelligenceBrief: win.content,
                    visualPrompt: win.visual_prompt,
                    engagementPrediction: win.engagement_prediction,
                    viralPotential: win.viral_potential,
                    followUpIdeas: win.follow_up_ideas
                });
            } else {
                throw new Error("No wins returned");
            }

        } catch (e) {
            console.error("Daily win generation failed, using fallback:", e);
            // Fallback logic
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
            }, 800);
        } finally {
            setIsGenerating(false);
            setIsSurprising(false);
        }
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

                            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                <button
                                    onClick={() => generateWin(false)}
                                    className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 bg-[var(--surface)] text-[var(--ink)] border border-[var(--border)] rounded-[var(--radius)] hover:bg-[var(--surface)]/80 transition-all font-medium"
                                >
                                    <Zap size={16} />
                                    Get Today's Win
                                </button>

                                <button
                                    onClick={() => generateWin(true)}
                                    className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 shadow-lg shadow-[var(--ink)]/10 transition-all font-medium group"
                                >
                                    <Sparkles size={16} className="group-hover:animate-pulse" />
                                    Surprise Me
                                </button>
                            </div>

                            <p className="mt-6 text-xs text-[var(--muted)]">
                                {isSurprising ? "Deep trend mapping in progress..." : "Quick, focused, satisfying."}
                            </p>
                        </div>
                    )}

                    {/* Loading State */}
                    {isGenerating && (
                        <div className="text-center py-16">
                            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                                <RefreshCw size={18} className="text-[var(--muted)] animate-spin" />
                            </div>
                            <p className="text-[var(--muted)] font-serif italic">
                                {isSurprising ? "Synthesizing market surprises..." : "Finding your win..."}
                            </p>
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
                                    {contentWin.score && (
                                        <span className="px-3 py-1 bg-amber-50 text-amber-700 text-xs font-bold rounded-full border border-amber-100 flex items-center gap-1">
                                            <Zap size={10} fill="currentColor" />
                                            {Math.round(contentWin.score * 100)} Surprise
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center gap-1 text-xs text-[var(--muted)]">
                                    <Clock size={12} />
                                    {contentWin.timeToPost}
                                </div>
                            </div>

                            {/* Main Card */}
                            <BlueprintCard showCorners padding="none">
                                {/* Hook / Post Content */}
                                <div className="p-6 border-b border-[var(--border)]">
                                    <p className="text-xs text-[var(--muted)] uppercase tracking-wide mb-2 font-medium">{contentWin.angle}</p>
                                    <div className="text-lg text-[var(--ink)] leading-relaxed font-serif whitespace-pre-wrap">
                                        {contentWin.hook}
                                    </div>
                                </div>

                                {/* Intelligence Brief (Narrative) if available */}
                                {contentWin.intelligenceBrief && contentWin.score && (
                                    <div className="p-6 bg-amber-50/30 border-b border-amber-100/50 space-y-6">
                                        <div>
                                            <p className="text-[10px] text-amber-700 uppercase tracking-[0.2em] mb-3 font-bold">Intelligence Brief</p>
                                            <div className="text-sm text-amber-900/80 leading-relaxed italic">
                                                "{contentWin.intelligenceBrief.split('\n')[0]}..." 
                                                <span className="text-[10px] ml-2 font-bold uppercase cursor-help" title={contentWin.intelligenceBrief}>[Full Logic]</span>
                                            </div>
                                        </div>

                                        {/* Strategic Forecast */}
                                        <div className="grid grid-cols-2 gap-6 pt-4 border-t border-amber-100/30">
                                            <div className="space-y-2">
                                                <div className="flex justify-between items-center text-[10px] text-amber-700 font-bold uppercase tracking-wider">
                                                    <span>Engagement</span>
                                                    <span>{Math.round((contentWin.engagementPrediction || 0) * 100)}%</span>
                                                </div>
                                                <div className="h-1 bg-amber-100 rounded-full overflow-hidden">
                                                    <div 
                                                        className="h-full bg-amber-500 rounded-full transition-all duration-1000" 
                                                        style={{ width: `${(contentWin.engagementPrediction || 0) * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                            <div className="space-y-2">
                                                <div className="flex justify-between items-center text-[10px] text-amber-700 font-bold uppercase tracking-wider">
                                                    <span>Viral Potential</span>
                                                    <span>{Math.round((contentWin.viralPotential || 0) * 100)}%</span>
                                                </div>
                                                <div className="h-1 bg-amber-100 rounded-full overflow-hidden">
                                                    <div 
                                                        className="h-full bg-orange-500 rounded-full transition-all duration-1000" 
                                                        style={{ width: `${(contentWin.viralPotential || 0) * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </div>

                                        {/* Follow-up Strategy */}
                                        {contentWin.followUpIdeas && contentWin.followUpIdeas.length > 0 && (
                                            <div className="pt-4 border-t border-amber-100/30">
                                                <p className="text-[10px] text-amber-700 uppercase tracking-wider mb-3 font-bold flex items-center gap-2">
                                                    <ArrowRight size={10} />
                                                    Momentum Strategy
                                                </p>
                                                <ul className="space-y-2">
                                                    {contentWin.followUpIdeas.map((idea, idx) => (
                                                        <li key={idx} className="text-xs text-amber-900/70 flex items-center gap-2">
                                                            <div className="w-1 h-1 rounded-full bg-amber-400" />
                                                            {idea}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Outline / Hooks */}
                                <div className="p-6 bg-[var(--surface)]">
                                    <p className="text-xs text-[var(--muted)] uppercase tracking-wide mb-4 font-medium">
                                        {contentWin.intelligenceBrief ? "Alternative Hooks" : "Structure"}
                                    </p>
                                    <div className="space-y-3">
                                        {contentWin.outline.map((step, i) => (
                                            <div key={i} className="flex items-start gap-3">
                                                <div className="w-5 h-5 rounded-full bg-[var(--ink)]/10 text-[var(--ink)] text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                                                    {i + 1}
                                                </div>
                                                <span className="text-sm text-[var(--ink)]/90 leading-snug">{step}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Visual Prompt if available */}
                                {contentWin.visualPrompt && (
                                    <div className="p-4 bg-[var(--canvas)] border-t border-[var(--border)]">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Sparkles size={12} className="text-amber-500" />
                                            <p className="text-[10px] text-[var(--muted)] uppercase tracking-wide font-medium">Visual Blueprint</p>
                                        </div>
                                        <p className="text-[11px] text-[var(--muted)] italic leading-relaxed">
                                            {contentWin.visualPrompt}
                                        </p>
                                    </div>
                                )}

                                {/* Actions */}
                                <div className="flex border-t border-[var(--border)]">
                                    <button
                                        onClick={copyToClipboard}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm text-[var(--muted)] hover:bg-[var(--surface)] hover:text-[var(--ink)] transition-colors border-r border-[var(--border)]"
                                    >
                                        {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                                        {copied ? "Copied" : "Copy Content"}
                                    </button>
                                    <button
                                        onClick={expandInMuse}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm text-[var(--blueprint)] hover:bg-[var(--blueprint)]/10 hover:text-[var(--blueprint)] transition-colors border-r border-[var(--border)] font-medium"
                                    >
                                        <Wand2 size={14} />
                                        Refine with Muse
                                    </button>
                                    <button
                                        onClick={() => markAsDone()}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium text-green-600 hover:bg-green-50 transition-colors"
                                    >
                                        <Check size={14} />
                                        Done & Posted
                                    </button>
                                </div>
                            </BlueprintCard>

                            {/* Try Another */}
                            <button
                                onClick={() => generateWin(contentWin.score ? true : false)}
                                className="w-full flex items-center justify-center gap-2 py-4 text-sm text-[var(--muted)] hover:text-[var(--ink)] transition-colors group"
                            >
                                <RefreshCw size={14} className="group-hover:rotate-180 transition-transform duration-500" />
                                {contentWin.score ? "Generate Another Surprise" : "Get another idea"}
                            </button>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}
