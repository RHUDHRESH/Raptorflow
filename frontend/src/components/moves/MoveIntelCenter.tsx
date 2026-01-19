"use client";

import { useState, useMemo } from "react";
import { Move, ExecutionDay, TaskItem, MOVE_CATEGORIES } from "./types";
import { useMovesStore } from "@/stores/movesStore"; // Import store
import { MoveCategoryIcon } from "@/components/moves/MoveCategoryIcon";
import { Check, Zap, Share2, MessageSquare, Layout, Activity, Calendar, Layers, ChevronDown, ChevronRight, Target, Lightbulb, Users, Megaphone, ArrowRight, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE INTEL CENTER — QUIET LUXURY REDESIGN
   Rich, detailed view of Strategy & Execution
   ══════════════════════════════════════════════════════════════════════════════ */

interface MoveIntelCenterProps {
    move: Move;
}

export function MoveIntelCenter({ move }: MoveIntelCenterProps) {
    const { updateMove } = useMovesStore(); // Connect to store
    const [activeTab, setActiveTab] = useState<"strategy" | "execution" | "reasoning">("strategy");
    const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([1]));
    const [reasoning, setReasoning] = useState<any[]>([]);
    const [loadingReasoning, setLoadingReasoning] = useState(false);

    // --- ABSOLUTE INFINITY: FETCH REASONING ---
    useEffect(() => {
        if (activeTab === "reasoning" && move.id) {
            async function loadReasoning() {
                setLoadingReasoning(true);
                const response = await apiClient.getExpertReasoning(move.id);
                setReasoning(response.data || []);
                setLoadingReasoning(false);
            }
            loadReasoning();
        }
    }, [activeTab, move.id]);

    const category = MOVE_CATEGORIES[move.category];

    const toggleDay = (day: number) => {
        setExpandedDays(prev => {
            const next = new Set(prev);
            if (next.has(day)) next.delete(day);
            else next.add(day);
            return next;
        });
    };

    // Calculate progress
    const progress = useMemo(() => {
        if (!move.execution?.length) return { completed: 0, total: 0, percentage: 0 };
        let total = 0;
        let completed = 0;
        move.execution.forEach(day => {
            total += 1 + (day.clusterActions?.length || 0) + 1;
            if (day.pillarTask?.status === 'done') completed++;
            day.clusterActions?.forEach(t => { if (t.status === 'done') completed++; });
            if (day.networkAction?.status === 'done') completed++;
        });
        return { completed, total, percentage: total > 0 ? Math.round((completed / total) * 100) : 0 };
    }, [move.execution]);

    const handleCompleteMove = () => {
        setIsCompleting(true);

        // Optimistic update styling
        setTimeout(() => {
            updateMove(move.id, { status: 'completed', progress: 100 });
            setIsCompleting(false);
            // Trigger confetti if we had it, or just rely on the UI transition
        }, 600);
    };

    // Move is eligible for completion if progress > 90% or user decides to force it
    const canComplete = progress.percentage >= 90 || move.status === 'completed';

    return (
        <div className="space-y-6 relative">
            {isCompleting && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/50 backdrop-blur-sm rounded-lg animate-in fade-in">
                    <div className="text-center">
                        <Trophy className="w-16 h-16 text-[var(--blueprint)] mx-auto mb-2 animate-bounce" />
                        <h3 className="text-xl font-bold text-[var(--ink)]">Move Complete!</h3>
                    </div>
                </div>
            )}

            {/* Move Header Summary */}
            <div className="flex items-start justify-between gap-5 p-6 bg-[var(--surface-subtle)] rounded-[var(--radius-lg)] border border-[var(--border)]">
                <div className="flex items-start gap-5 flex-1 min-w-0">
                    <div className="w-16 h-16 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center text-3xl shrink-0 shadow-sm">
                        <MoveCategoryIcon category={move.category} size={32} />
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                            <span className="text-xs font-mono text-[var(--muted)] uppercase tracking-wider">{category?.name}</span>
                            {move.campaignId && (
                                <span className="flex items-center gap-1 text-[10px] text-[var(--success)] font-medium border border-[var(--success)]/20 bg-[var(--success)]/5 px-1.5 py-0.5 rounded">
                                    <Layers size={10} />
                                    Campaign Linked
                                </span>
                            )}
                        </div>
                        <h2 className="font-serif text-2xl text-[var(--ink)] mb-2 leading-tight">{move.name}</h2>
                        <div className="flex items-center gap-6 text-sm text-[var(--muted)]">
                            <span className="flex items-center gap-1.5">
                                <Calendar size={14} />
                                {move.duration} Days
                            </span>
                            <span className="flex items-center gap-1.5">
                                <Activity size={14} />
                                {progress.percentage}% Complete
                            </span>
                            <span className={cn(
                                "px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wide",
                                move.status === 'active' && "bg-[var(--success)]/10 text-[var(--success)]",
                                move.status === 'draft' && "bg-[var(--warning)]/10 text-[var(--warning)]",
                                move.status === 'completed' && "bg-[var(--blueprint)]/10 text-[var(--blueprint)]",
                                move.status === 'paused' && "bg-[var(--muted)]/10 text-[var(--muted)]"
                            )}>
                                {move.status}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Main Action Button */}
                <div className="flex flex-col items-end gap-2">
                    {move.status !== 'completed' ? (
                        <button
                            onClick={handleCompleteMove}
                            className={cn(
                                "flex items-center gap-2 px-5 py-2.5 rounded-[var(--radius)] font-medium transition-all shadow-sm",
                                canComplete
                                    ? "bg-[var(--ink)] text-white hover:bg-[var(--ink)]/90 hover:shadow-md"
                                    : "bg-[var(--paper)] border border-[var(--border)] text-[var(--muted)] hover:text-[var(--ink)] hover:border-[var(--ink)]"
                            )}
                        >
                            {canComplete ? <><Trophy size={16} /> Complete Move</> : "Mark as Complete"}
                        </button>
                    ) : (
                        <div className="flex items-center gap-2 px-5 py-2.5 rounded-[var(--radius)] bg-[var(--success)]/10 text-[var(--success)] font-bold border border-[var(--success)]/20">
                            <Check size={18} strokeWidth={3} />
                            Completed
                        </div>
                    )}
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex items-center gap-8 border-b border-[var(--border)] px-2">
                <button
                    onClick={() => setActiveTab("strategy")}
                    className={cn(
                        "flex items-center gap-2 pb-3 text-sm font-medium border-b-2 transition-all -mb-px",
                        activeTab === "strategy"
                            ? "border-[var(--ink)] text-[var(--ink)]"
                            : "border-transparent text-[var(--muted)] hover:text-[var(--ink)] hover:border-[var(--border-subtle)]"
                    )}
                >
                    <Layout size={14} />
                    Strategy & Intel
                </button>
                <button
                    onClick={() => setActiveTab("execution")}
                    className={cn(
                        "flex items-center gap-2 pb-3 text-sm font-medium border-b-2 transition-all -mb-px",
                        activeTab === "execution"
                            ? "border-[var(--ink)] text-[var(--ink)]"
                            : "border-transparent text-[var(--muted)] hover:text-[var(--ink)] hover:border-[var(--border-subtle)]"
                    )}
                >
                    <Activity size={14} />
                    Execution Plan
                </button>
                <button
                    onClick={() => setActiveTab("reasoning")}
                    className={cn(
                        "flex items-center gap-2 pb-3 text-sm font-medium border-b-2 transition-all -mb-px",
                        activeTab === "reasoning"
                            ? "border-[var(--ink)] text-[var(--ink)]"
                            : "border-transparent text-[var(--muted)] hover:text-[var(--ink)] hover:border-[var(--border-subtle)]"
                    )}
                >
                    <Lightbulb size={14} />
                    Expert Reasoning
                </button>
            </div>

            {/* CONTENT AREA */}
            <div className="min-h-[400px]">
                {/* ... existing strategy and execution tabs ... */}
                {activeTab === "reasoning" && (
                    <div className="space-y-4 animate-in fade-in duration-300">
                        {loadingReasoning ? (
                            <div className="p-12 text-center text-[var(--muted)] italic">Decrypting specialist thought logs...</div>
                        ) : reasoning.length === 0 ? (
                            <div className="p-12 text-center text-[var(--muted)]">No reasoning logs available for this move.</div>
                        ) : (
                            <div className="space-y-6">
                                {reasoning.map((log, i) => (
                                    <div key={i} className="p-4 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)]">
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                <div className="w-6 h-6 rounded-full bg-[var(--ink)] text-white flex items-center justify-center text-[10px] font-bold">
                                                    {log.agent_name[0]}
                                                </div>
                                                <span className="text-xs font-bold uppercase tracking-wider text-[var(--ink)]">{log.agent_name}</span>
                                            </div>
                                            <span className="text-[10px] text-[var(--muted)]">{new Date(log.created_at).toLocaleTimeString()}</span>
                                        </div>
                                        <p className="text-sm text-[var(--ink-secondary)] leading-relaxed italic">"{log.thought_process}"</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
                {/* STRATEGY TAB */}
                {activeTab === "strategy" && (
                    <div className="space-y-6 animate-in fade-in duration-300">
                        {/* Core Objective */}
                        <div className="p-6 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--paper)] shadow-sm">
                            <div className="flex items-center gap-2 mb-3">
                                <Target size={16} className="text-[var(--blueprint)]" />
                                <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--blueprint)]">Core Objective</h3>
                            </div>
                            <p className="text-lg text-[var(--ink)] font-serif leading-relaxed">{move.goal}</p>
                        </div>

                        {/* Context & Rationale */}
                        {move.context && (
                            <div className="p-6 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--paper)]">
                                <div className="flex items-center gap-2 mb-3">
                                    <Lightbulb size={16} className="text-[var(--warning-dark)]" />
                                    <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--warning-dark)]">Context & Rationale</h3>
                                </div>
                                <p className="text-[var(--ink-secondary)] leading-relaxed">{move.context}</p>
                            </div>
                        )}

                        {/* Strategy Details Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Target ICP */}
                            <div className="p-5 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-center hover:border-[var(--blueprint)] transition-colors">
                                <Users size={20} className="mx-auto mb-2 text-[var(--secondary)]" />
                                <div className="text-[10px] font-bold uppercase text-[var(--muted)] mb-1">Target ICP</div>
                                <div className="font-medium text-[var(--ink)]">{move.icp || "General Audience"}</div>
                            </div>

                            {/* Tone */}
                            <div className="p-5 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-center hover:border-[var(--blueprint)] transition-colors">
                                <Megaphone size={20} className="mx-auto mb-2 text-[var(--secondary)]" />
                                <div className="text-[10px] font-bold uppercase text-[var(--muted)] mb-1">Tone</div>
                                <div className="font-medium text-[var(--ink)]">{move.tone}</div>
                            </div>

                            {/* Category */}
                            <div className="p-5 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-center hover:border-[var(--blueprint)] transition-colors">
                                <Zap size={20} className="mx-auto mb-2 text-[var(--secondary)]" />
                                <div className="text-[10px] font-bold uppercase text-[var(--muted)] mb-1">Category</div>
                                <div className="font-medium text-[var(--ink)]">{category?.name}</div>
                            </div>
                        </div>

                        {/* Metrics */}
                        <div className="p-5 rounded-[var(--radius-lg)] bg-[var(--surface-subtle)] border border-[var(--border)]">
                            <div className="mb-3 text-[10px] font-bold uppercase text-[var(--muted)]">Success Metrics</div>
                            <div className="flex flex-wrap gap-2">
                                {move.metrics?.map((m, i) => (
                                    <span key={i} className="px-3 py-1.5 rounded-full bg-[var(--paper)] border border-[var(--border)] text-xs font-medium text-[var(--ink)] shadow-sm">
                                        {m}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* EXECUTION TAB */}
                {activeTab === "execution" && (
                    <div className="space-y-4 animate-in fade-in duration-300">
                        {move.execution?.map((day) => {
                            const isExpanded = expandedDays.has(day.day);
                            return (
                                <div
                                    key={day.day}
                                    className={cn(
                                        "border rounded-[var(--radius-lg)] overflow-hidden transition-all duration-300",
                                        isExpanded
                                            ? "bg-[var(--paper)] border-[var(--blueprint)] shadow-md"
                                            : "bg-[var(--surface)] border-[var(--border)] hover:border-[var(--blueprint)]"
                                    )}
                                >
                                    {/* Day Header */}
                                    <button
                                        onClick={() => toggleDay(day.day)}
                                        className="w-full flex items-center justify-between p-4 bg-transparent"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={cn(
                                                "w-10 h-10 rounded-full flex items-center justify-center font-serif text-lg font-bold border",
                                                day.day === 1 ? "bg-[var(--blueprint)] text-white border-transparent" : "bg-[var(--paper)] text-[var(--ink)] border-[var(--border)]"
                                            )}>
                                                {day.day}
                                            </div>
                                            <div className="text-left">
                                                <div className="text-xs text-[var(--muted)] font-mono uppercase tracking-wider mb-0.5">{day.phase} Phase</div>
                                                <div className="font-medium text-[var(--ink)]">{day.pillarTask.title}</div>
                                            </div>
                                        </div>
                                        {isExpanded ? <ChevronDown size={18} className="text-[var(--muted)]" /> : <ChevronRight size={18} className="text-[var(--muted)]" />}
                                    </button>

                                    {/* Detailed Execution Content */}
                                    {isExpanded && (
                                        <div className="p-4 pt-0 border-t border-[var(--border-subtle)] bg-[var(--paper)]">
                                            <div className="grid grid-cols-1 gap-4 mt-4 relative">
                                                {/* Left structural line */}
                                                <div className="absolute top-2 bottom-2 left-5 w-px bg-[var(--border-subtle)]" />

                                                {/* PILLAR TASK (Main Focus) */}
                                                <div className="relative pl-12 group">
                                                    <div className="absolute left-3 top-2 w-4 h-4 rounded-full border-2 border-[var(--blueprint)] bg-[var(--paper)] flex items-center justify-center z-10">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-[var(--blueprint)]" />
                                                    </div>
                                                    <div className="p-4 rounded-[var(--radius)] border border-[var(--blueprint)]/30 bg-[var(--blueprint)]/5">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <Zap size={14} className="text-[var(--blueprint)]" />
                                                            <span className="text-xs font-bold uppercase tracking-wider text-[var(--blueprint)]">Core Focus</span>
                                                        </div>
                                                        <p className="text-sm text-[var(--ink)] font-medium mb-1">{day.pillarTask.title}</p>
                                                        <p className="text-xs text-[var(--ink-secondary)]">{day.pillarTask.description || "Execute this core action to drive momentum."}</p>
                                                    </div>
                                                </div>

                                                {/* CLUSTER ACTIONS (Supporting) */}
                                                {day.clusterActions?.map((action, i) => (
                                                    <div key={i} className="relative pl-12 group">
                                                        <div className="absolute left-3 top-3 w-4 h-4 rounded-full border border-[var(--border)] bg-[var(--surface-subtle)] z-10" />
                                                        <div className="p-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] hover:bg-[var(--surface-hover)] transition-colors">
                                                            <div className="flex items-center justify-between mb-1">
                                                                <div className="flex items-center gap-2">
                                                                    <Share2 size={12} className="text-[var(--ink-secondary)]" />
                                                                    <span className="text-xs font-bold uppercase tracking-wider text-[var(--muted)]">Support</span>
                                                                </div>
                                                                {action.channel && (
                                                                    <span className="text-[10px] text-[var(--muted)] bg-[var(--paper)] px-1.5 py-0.5 rounded uppercase border border-[var(--border)]">
                                                                        {action.channel}
                                                                    </span>
                                                                )}
                                                            </div>
                                                            <p className="text-sm text-[var(--ink)]">{action.title}</p>
                                                        </div>
                                                    </div>
                                                ))}

                                                {/* NETWORK ACTION (Outreach) */}
                                                <div className="relative pl-12 group">
                                                    <div className="absolute left-3 top-3 w-4 h-4 rounded-full border border-[var(--success)] bg-[var(--success-light)] z-10" />
                                                    <div className="p-3 rounded-[var(--radius)] border border-[var(--success)]/20 bg-[var(--success)]/5">
                                                        <div className="flex items-center justify-between mb-1">
                                                            <div className="flex items-center gap-2">
                                                                <MessageSquare size={12} className="text-[var(--success)]" />
                                                                <span className="text-xs font-bold uppercase tracking-wider text-[var(--success)]">Outreach</span>
                                                            </div>
                                                        </div>
                                                        <p className="text-sm text-[var(--ink)]">{day.networkAction.title}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
