"use client";

import { useRef, useEffect, useState } from "react";
import gsap from "gsap";
import { Zap, Check, X, Trophy, RefreshCw, Radar, Play } from "lucide-react";
import { cn } from "@/lib/utils";
import { Confetti } from "@/components/ui/confetti";

/* ══════════════════════════════════════════════════════════════════════════════
   DAILY WINS SIDEBAR — Quick Dopamine Hits
   "Platform, ICP, Wipe" — Minimalist Tactical Deck
   ══════════════════════════════════════════════════════════════════════════════ */

interface MicroTask {
    id: string;
    platform: string; // The "WHERE"
    icp: string;      // The "WHO"
    wipe: string;     // The "WHAT" (Action)
    energy: "High" | "Med" | "Low";
}

const WIN_CARDS: MicroTask[] = [
    {
        id: "1",
        platform: "LinkedIn",
        icp: "Enterprise CTOs",
        wipe: "Post: 'Why serverless is expensive' chart.",
        energy: "High"
    },
    {
        id: "2",
        platform: "Twitter/X",
        icp: "SaaS Founders",
        wipe: "Reply to @paulg with contrarian take.",
        energy: "Med"
    },
    {
        id: "3",
        platform: "Email",
        icp: "Lost Leads (Q4)",
        wipe: "Send: 'One last idea' sequence.",
        energy: "High"
    },
    {
        id: "4",
        platform: "Slack",
        icp: "Top 10 Users",
        wipe: "DM: 'Can I feature you?'",
        energy: "Low"
    }
];

export function DailyWinsSidebar() {
    const containerRef = useRef<HTMLDivElement>(null);
    const cardsRef = useRef<HTMLDivElement>(null);
    const [winsCount, setWinsCount] = useState(0);
    const [maxWins] = useState(10);
    const [state, setState] = useState<"idle" | "scanning" | "active">("idle");
    const [tasks, setTasks] = useState<MicroTask[]>([]);
    const [showConfetti, setShowConfetti] = useState(false);

    // Load persisted state
    useEffect(() => {
        const today = new Date().toDateString();
        const savedDate = localStorage.getItem("daily_wins_date");
        const savedCount = localStorage.getItem("daily_wins_count");

        if (savedDate === today && savedCount) {
            setTimeout(() => setWinsCount(parseInt(savedCount, 10)), 0);
        } else {
            setTimeout(() => {
                setWinsCount(0);
                localStorage.setItem("daily_wins_date", today);
                localStorage.setItem("daily_wins_count", "0");
            }, 0);
        }
    }, []);

    // Persist count
    useEffect(() => {
        if (winsCount > 0) {
            localStorage.setItem("daily_wins_count", winsCount.toString());
            localStorage.setItem("daily_wins_date", new Date().toDateString());
        }
    }, [winsCount]);

    // Entry animation
    useEffect(() => {
        if (containerRef.current) {
            gsap.fromTo(
                containerRef.current,
                { x: 50, opacity: 0 },
                { x: 0, opacity: 1, duration: 0.4, ease: "power2.out", delay: 0.3 }
            );
        }
    }, []);

    // Card stacking animation
    useEffect(() => {
        if (tasks.length > 0 && cardsRef.current) {
            const cards = cardsRef.current.querySelectorAll("[data-win-card]");
            gsap.fromTo(
                cards,
                { y: 40, opacity: 0, scale: 0.9 },
                {
                    y: 0,
                    opacity: 1,
                    scale: 1,
                    duration: 0.4,
                    stagger: 0.1,
                    ease: "back.out(1.2)"
                }
            );
        }
    }, [tasks]);

    const handleScout = () => {
        if (state !== "idle") return;
        setState("scanning");

        setTimeout(() => {
            const shuffled = [...WIN_CARDS].sort(() => 0.5 - Math.random());
            const selected = shuffled.slice(0, Math.min(3, shuffled.length));
            setTasks(selected);
            setState("active");
        }, 1200);
    };

    const handleDismiss = (taskId: string) => {
        const cardEl = cardsRef.current?.querySelector(`[data-win-card="${taskId}"]`);
        if (cardEl) {
            gsap.to(cardEl, {
                x: 100,
                opacity: 0,
                rotate: 5,
                duration: 0.2,
                ease: "power2.in",
                onComplete: () => {
                    setTasks((prev) => prev.filter((t) => t.id !== taskId));
                    if (tasks.length <= 1) setState("idle");
                }
            });
        }
    };

    const handleExecute = (taskId: string) => {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 2000);
        setWinsCount((prev) => Math.min(prev + 1, maxWins));

        const cardEl = cardsRef.current?.querySelector(`[data-win-card="${taskId}"]`);
        if (cardEl) {
            // Dopaminergic "Crunch" Animation
            const tl = gsap.timeline({
                onComplete: () => {
                    setTasks((prev) => prev.filter((t) => t.id !== taskId));
                    if (tasks.length <= 1) setState("idle");
                }
            });

            // 1. Scale down slightly (anticipation)
            tl.to(cardEl, { scale: 0.95, duration: 0.1, ease: "power1.out" })
                // 2. Flash white and expand borders (impact)
                .to(cardEl, {
                    scale: 1.05,
                    backgroundColor: "var(--success)",
                    borderColor: "var(--success)",
                    boxShadow: "0 0 30px var(--success)",
                    opacity: 0,
                    duration: 0.3,
                    ease: "power2.in"
                });
        }
    };

    return (
        <div
            ref={containerRef}
            className="w-72 bg-[var(--paper)] border-l border-[var(--structure)] flex flex-col relative overflow-hidden"
            style={{ opacity: 0 }}
        >
            <Confetti isActive={showConfetti} pieceCount={70} duration={2500} />

            {/* Header */}
            <div className="p-4 border-b border-[var(--structure)] bg-[var(--surface)]">
                <div className="flex items-center justify-between mb-3">
                    <div>
                        <span className="label text-[10px] tracking-widest">TACTICAL DECK</span>
                        <h3 className="font-editorial text-lg text-[var(--ink)] leading-tight">Daily Wins</h3>
                    </div>
                    <div className="flex items-center gap-1.5 bg-[var(--paper)] px-2 py-1 rounded-[var(--radius-sm)] border border-[var(--structure)]">
                        <Trophy size={12} className="text-[var(--warning)]" />
                        <span className="font-data text-base text-[var(--ink)]">{winsCount}</span>
                    </div>
                </div>
                <div className="h-1 w-full bg-[var(--structure-subtle)] rounded-[var(--radius)] overflow-hidden">
                    <div
                        className="h-full bg-[var(--ink)] rounded-[var(--radius)] transition-all duration-500 will-change-transform"
                        style={{ width: `${(winsCount / maxWins) * 100}%` }}
                    />
                </div>
            </div>

            {/* Deck Area */}
            <div className="flex-1 p-4 overflow-y-auto bg-[var(--canvas)]">
                {state === "idle" && (
                    <div className="h-full flex flex-col items-center justify-center space-y-4">
                        <div className="w-16 h-16 rounded-full border-2 border-[var(--structure)] flex items-center justify-center bg-[var(--surface)] animate-pulse">
                            <Radar size={24} className="text-[var(--ink-muted)]" />
                        </div>
                        <p className="text-xs text-[var(--ink-secondary)] text-center font-mono uppercase tracking-wide">
                            Sector Scan Ready
                        </p>
                        <button
                            onClick={handleScout}
                            className="bg-[var(--ink)] text-[var(--paper)] px-6 py-2 rounded-[var(--radius-sm)] text-xs font-bold hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
                        >
                            <Play size={10} fill="currentColor" /> INITIATE SCAN
                        </button>
                    </div>
                )}

                {state === "scanning" && (
                    <div className="h-full flex flex-col items-center justify-center space-y-4">
                        <div className="relative w-20 h-20">
                            <div className="absolute inset-0 border border-[var(--structure)] rounded-full animate-ping opacity-20" />
                            <div className="absolute inset-0 border-t-2 border-[var(--ink)] rounded-full animate-spin" />
                            <div className="absolute inset-3 bg-[var(--ink)]/5 rounded-full" />
                        </div>
                        <p className="text-xs font-mono text-[var(--ink)] animate-pulse">ACQUIRING TARGETS...</p>
                    </div>
                )}

                {state === "active" && (
                    <div ref={cardsRef} className="space-y-4 perspective-1000">
                        {tasks.map((task) => (
                            <div
                                key={task.id}
                                data-win-card={task.id}
                                className="bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] p-4 shadow-sm hover:translate-y-[-2px] hover:shadow-md transition-all group relative overflow-hidden"
                                style={{ opacity: 0 }}
                            >
                                {/* Platform Tag */}
                                <div className="absolute top-0 right-0 p-2 opacity-50">
                                    <span className="text-[10px] font-mono text-[var(--ink-muted)] uppercase border border-[var(--structure)] px-1.5 py-0.5 rounded-[var(--radius-sm)]">
                                        {task.platform}
                                    </span>
                                </div>

                                <div className="space-y-3 relative z-10">
                                    {/* 1. ICP */}
                                    <div>
                                        <span className="text-[9px] font-bold text-[var(--ink-muted)] uppercase tracking-wider block mb-1">TARGET (ICP)</span>
                                        <p className="text-sm font-semibold text-[var(--ink)]">{task.icp}</p>
                                    </div>

                                    {/* 2. Wipe (Action) */}
                                    <div>
                                        <span className="text-[9px] font-bold text-[var(--ink-muted)] uppercase tracking-wider block mb-1">EXECUTION (WIPE)</span>
                                        <p className="text-sm text-[var(--ink-secondary)] leading-snug">{task.wipe}</p>
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex gap-2 mt-4 pt-3 border-t border-[var(--structure-subtle)]">
                                    <button
                                        onClick={() => handleDismiss(task.id)}
                                        className="p-2 text-[var(--ink-muted)] hover:text-[var(--error)] hover:bg-[var(--error-light)] rounded-[var(--radius-sm)] transition-colors"
                                    >
                                        <X size={14} />
                                    </button>
                                    <button
                                        onClick={() => handleExecute(task.id)}
                                        className="flex-1 bg-[var(--ink)] text-[var(--paper)] text-xs font-bold py-2 rounded-[var(--radius-sm)] hover:bg-[var(--ink)]/90 flex items-center justify-center gap-2 group-hover:scale-[1.02] transition-transform"
                                    >
                                        <Zap size={12} fill="currentColor" />
                                        EXECUTE
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
