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
import { apiClient } from "@/lib/api/client";
import { useAuth } from "@/components/auth/AuthProvider";
import { useDashboardStore } from "@/stores/dashboardStore";
import { supabase } from "@/lib/supabaseClient";
import { toast } from "sonner";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   DAILY WINS ΓÇö Quick Content Wins
   Quiet Luxury Redesign ΓÇö Matches Moves page styling
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface ContentWin {
    id: string;
    topic: string;
    angle: string;
    hook: string;
    body: string;
    visual_prompt: string;
    platform: string;
    timeToPost: string;
    score: number;
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

    const { workspace } = useAuth();
    const { summary } = useDashboardStore();

    useEffect(() => {
        setMounted(true);
        if (summary) {
            setStreak(summary.daily_wins_streak);
            setTotalWins(summary.workspace_stats.total_wins);
        }
    }, [summary]);

    useEffect(() => {
        if (!pageRef.current || !mounted) return;
        gsap.fromTo(pageRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
    }, [mounted]);

    const generateWin = async () => {
        setIsGenerating(true);
        try {
            const { data: { user } } = await supabase.auth.getUser();
            if (!user) {
                toast.error("You must be logged in to generate a win.");
                setIsGenerating(false);
                return;
            }

            if (!workspace?.workspaceId) {
                toast.error("No active workspace found.");
                setIsGenerating(false);
                return;
            }

            const response = await apiClient.generateDailyWin({
                workspace_id: workspace.workspaceId,
                user_id: user.id,
                platform: "LinkedIn"
            });

            if (response.success && response.data?.final_win) {
                const win = response.data.final_win;
                setContentWin({
                    id: `WIN-${Date.now()}`,
                    topic: "SOTA Insight",
                    angle: "MasterClass Polish",
                    hook: win.hooks?.[0] || "No hook generated.",
                    body: win.content,
                    visual_prompt: win.visual_prompt,
                    platform: "LinkedIn",
                    timeToPost: "~5 min",
                    score: win.score
                });
                toast.success("Intelligence Brief ready.");
            } else {
                toast.error((response.error as string) || "Failed to generate win. The editor rejected the quality.");
            }
        } catch (error) {
            console.error("Failed to generate win:", error);
            toast.error("An unexpected error occurred.");
        } finally {
            setIsGenerating(false);
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

    const markAsDone = async () => {
        if (!contentWin) return;

        try {
            if (!workspace?.workspaceId) return;

            const response = await apiClient.markWinAsPosted(contentWin.id, {
                workspace_id: workspace.workspaceId,
                user_id: "current-user", // Backend gets it from token
                platform: contentWin.platform
            });

            if (response.success) {
                setStreak(response.new_streak as number);
                toast.success(`Consistency rewarded! Current streak: ${response.new_streak as number}`);
                setContentWin(null);
            }
        } catch (error) {
            toast.error("Failed to mark win as posted on server.");
        }
    };

    const copyToClipboard = async () => {
        if (!contentWin) return;
        const text = `${contentWin.hook}\n\n${contentWin.body}`;
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
            body: contentWin.body,
            visual_prompt: contentWin.visual_prompt,
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
                                    <Zap size={12} className="text-amber-500" />
                                    {contentWin.score * 100}% Surprise
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

                                {/* Body */}
                                <div className="p-6 bg-[var(--surface)] border-b border-[var(--border)]">
                                    <p className="text-xs text-[var(--muted)] uppercase tracking-wide mb-4 font-medium">Editorial Brief</p>
                                    <div className="prose prose-sm text-[var(--ink)] leading-relaxed whitespace-pre-wrap">
                                        {contentWin.body}
                                    </div>
                                </div>

                                {/* Visual Prompt */}
                                <div className="p-6 bg-[var(--canvas)]">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Sparkles size={14} className="text-[var(--blueprint)]" />
                                        <p className="text-xs text-[var(--muted)] uppercase tracking-wide font-medium">Visual Direction</p>
                                    </div>
                                    <p className="text-sm text-[var(--muted)] italic">
                                        "{contentWin.visual_prompt}"
                                    </p>
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
