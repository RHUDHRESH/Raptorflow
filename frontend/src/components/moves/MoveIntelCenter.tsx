
"use client";

import { useState } from "react";
import { Move, ExecutionDay, TaskItem } from "./types";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { BlueprintTooltip } from "@/components/ui/BlueprintTooltip";
import { BlueprintTabs, TabContent } from "@/components/ui/BlueprintTabs";
import { Check, Circle, Zap, Share2, MessageSquare, Clock, ArrowRight, User, Layout, Activity, Calendar, Info, Layers, Mail, Linkedin, Twitter, Instagram } from "lucide-react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE INTEL CENTER
   The central "Headquarters" for a single move.
   Now separates Strategy (Research) from Execution (The Plan) to reduce cognitive load.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MoveIntelCenterProps {
    move: Move;
}

export function MoveIntelCenter({ move }: MoveIntelCenterProps) {
    const [activeTab, setActiveTab] = useState("execution");

    const tabs = [
        { id: "strategy", label: "Strategy & Intel", icon: <Layout size={14} />, code: "STR-01" },
        { id: "execution", label: "Execution Plan", icon: <Activity size={14} />, code: "EXE-07" },
    ];

    return (
        <div className="space-y-6">
            <BlueprintTabs
                tabs={tabs}
                activeTab={activeTab}
                onChange={setActiveTab}
                className="mb-4"
            />

            <TabContent className="min-h-[400px]">
                {activeTab === "strategy" ? (
                    <StrategyView move={move} />
                ) : (
                    <ExecutionView move={move} />
                )}
            </TabContent>
        </div>
    );
}

// --- SUB-COMPONENTS ---

function StrategyView({ move }: { move: Move }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Context & Goal */}
            <div className="space-y-6">
                <BlueprintCard className="p-6 h-full border-l-4 border-l-[var(--blueprint)]">
                    <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Strategic Context</h3>
                    <div className="space-y-4">
                        <div>
                            <span className="text-xs font-mono text-[var(--muted)] uppercase tracking-wider block mb-1">core objective</span>
                            <p className="text-[var(--ink)] text-lg leading-relaxed">{move.goal}</p>
                        </div>
                        <div className="h-px bg-[var(--border-subtle)]" />
                        <div>
                            <span className="text-xs font-mono text-[var(--muted)] uppercase tracking-wider block mb-1">the "why" (context)</span>
                            <p className="text-[var(--ink-secondary)] text-sm leading-relaxed">{move.context}</p>
                        </div>
                    </div>
                </BlueprintCard>
            </div>

            {/* Intel & Configuration */}
            <div className="space-y-6">
                <BlueprintCard className="p-6">
                    <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Intel & targeting</h3>
                    <dl className="grid grid-cols-1 gap-y-5">
                        <div>
                            <dt className="text-xs font-mono text-[var(--muted)] uppercase tracking-wider mb-1">Target Audience (ICP)</dt>
                            <dd className="flex items-center gap-2 text-[var(--ink)] font-medium">
                                <User size={16} className="text-[var(--blueprint)]" />
                                {move.icp || "General Audience"}
                            </dd>
                        </div>
                        <div>
                            <dt className="text-xs font-mono text-[var(--muted)] uppercase tracking-wider mb-1">Linked Campaign</dt>
                            <dd className="text-[var(--ink)]">
                                {move.campaignId ? (
                                    <span className="flex items-center gap-2">
                                        <Layers size={16} className="text-[var(--success)]" />
                                        Linked Campaign {move.campaignId}
                                    </span>
                                ) : (
                                    <span className="text-[var(--muted)] italic">No linked campaign</span>
                                )}
                            </dd>
                        </div>
                        <div>
                            <dt className="text-xs font-mono text-[var(--muted)] uppercase tracking-wider mb-1">Tone of Voice</dt>
                            <dd className="inline-flex items-center px-2.5 py-1 rounded-full border border-[var(--border)] bg-[var(--surface)] text-xs text-[var(--ink-secondary)]">
                                {move.tone}
                            </dd>
                        </div>
                    </dl>
                </BlueprintCard>

                {/* Stats / Progress Summary */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-[var(--radius)] bg-[var(--surface-subtle)] border border-[var(--border)] text-center">
                        <div className="text-2xl font-bold text-[var(--ink)]">{move.duration}</div>
                        <div className="text-[10px] uppercase text-[var(--muted)] font-mono">Days to Execute</div>
                    </div>
                    <div className="p-4 rounded-[var(--radius)] bg-[var(--surface-subtle)] border border-[var(--border)] text-center">
                        <div className="text-2xl font-bold text-[var(--ink)]">{(move.execution || []).length * 3}+</div>
                        <div className="text-[10px] uppercase text-[var(--muted)] font-mono">Touchpoints</div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ExecutionView({ move }: { move: Move }) {
    return (
        <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-serif text-lg text-[var(--ink)]">7-Day Battle Plan</h3>
                <div className="flex items-center gap-4 text-[10px] text-[var(--muted)] uppercase tracking-wider font-mono">
                    <span className="flex items-center gap-1.5"><Zap size={10} /> Pillar</span>
                    <span className="flex items-center gap-1.5"><Share2 size={10} /> Cluster</span>
                    <span className="flex items-center gap-1.5"><MessageSquare size={10} /> Network</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {(move.execution || []).map((day, idx) => (
                    <DayCard key={idx} day={day} index={idx} totalDays={move.duration} />
                ))}
                {(move.execution || []).length === 0 && (
                    <div className="col-span-full w-full text-center py-12 text-[var(--muted)] italic">
                        No execution data generated yet.
                    </div>
                )}
            </div>
        </div>
    );
}

function DayCard({ day, index, totalDays }: { day: ExecutionDay, index: number, totalDays: number }) {
    const isToday = false; // logic for today highlight could be passed down, assuming false for generic view

    return (
        <div className="w-full h-full flex flex-col rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] overflow-hidden hover:shadow-lg transition-shadow">
            {/* Header */}
            <div className="p-3 border-b border-[var(--border)] bg-[var(--surface-subtle)] flex items-center justify-between">
                <div>
                    <span className="text-[10px] font-mono text-[var(--muted)] uppercase">Day {day.day.toString().padStart(2, '0')}</span>
                    <h4 className="font-bold text-sm text-[var(--ink)] uppercase tracking-wide">{day.phase} Phase</h4>
                </div>
                {day.pillarTask.status === 'done' && (
                    <div className="w-6 h-6 rounded-full bg-[var(--success)] flex items-center justify-center text-white">
                        <Check size={14} strokeWidth={3} />
                    </div>
                )}
            </div>

            {/* Tasks */}
            <div className="p-4 flex-1 space-y-4">
                {/* Pillar */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-[var(--blueprint)]">
                            <Zap size={14} />
                            <span className="text-[10px] font-bold uppercase">Pillar Task</span>
                        </div>
                        <span className="text-[10px] text-[var(--muted)] border border-[var(--border)] px-1.5 rounded bg-[var(--surface)]">
                            45-60 min
                        </span>
                    </div>

                    <div className="group">
                        <div className="flex items-start gap-2">
                            <p className={cn(
                                "text-sm font-medium leading-tight flex-1",
                                day.pillarTask.status === 'done' ? "line-through text-[var(--muted)]" : "text-[var(--ink)]"
                            )}>
                                {day.pillarTask.title}
                            </p>
                            {day.pillarTask.description && (
                                <BlueprintTooltip content={day.pillarTask.description}>
                                    <Info size={12} className="text-[var(--muted)] opacity-0 group-hover:opacity-100 transition-opacity mt-0.5 cursor-help" />
                                </BlueprintTooltip>
                            )}
                        </div>

                        {day.pillarTask.channel && (
                            <div className="mt-2">
                                <ChannelBadge channel={day.pillarTask.channel} />
                            </div>
                        )}
                    </div>
                </div>

                <div className="h-px bg-[var(--border-subtle)]" />

                {/* Cluster */}
                <div className="space-y-2">
                    <div className="flex items-center gap-1.5 text-[var(--ink-secondary)] mb-1">
                        <Share2 size={14} />
                        <span className="text-[10px] font-bold uppercase">Cluster ({day.clusterActions.length})</span>
                    </div>
                    <ul className="space-y-2">
                        {day.clusterActions.map((task, i) => (
                            <li key={i} className="group flex items-start justify-between gap-2">
                                <div className={cn(
                                    "text-xs font-medium flex items-start gap-1.5 flex-1 min-w-0",
                                    task.status === 'done' ? "text-[var(--muted)] line-through" : "text-[var(--ink)]"
                                )}>
                                    <span className="mt-1.5 w-1 h-1 rounded-full bg-[var(--border)] shrink-0" />
                                    <span className="truncate">{task.title}</span>
                                </div>

                                <div className="flex items-center gap-1.5 shrink-0">
                                    {task.channel && <ChannelIcon channel={task.channel} />}
                                    {task.description && (
                                        <BlueprintTooltip content={task.description}>
                                            <Info size={10} className="text-[var(--muted)] opacity-0 group-hover:opacity-100 transition-opacity cursor-help" />
                                        </BlueprintTooltip>
                                    )}
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="h-px bg-[var(--border-subtle)]" />

                {/* Network */}
                <div className="space-y-2">
                    <div className="flex items-center gap-1.5 text-[var(--success)] mb-1">
                        <MessageSquare size={14} />
                        <span className="text-[10px] font-bold uppercase">Network</span>
                    </div>
                    <div className="group flex items-start justify-between gap-2">
                        <p className={cn(
                            "text-xs font-medium truncate flex-1",
                            day.networkAction.status === 'done' ? "line-through text-[var(--muted)]" : "text-[var(--ink)]"
                        )}>
                            {day.networkAction.title}
                        </p>
                        {day.networkAction.description && (
                            <BlueprintTooltip content={day.networkAction.description}>
                                <Info size={10} className="text-[var(--muted)] opacity-0 group-hover:opacity-100 transition-opacity cursor-help shrink-0" />
                            </BlueprintTooltip>
                        )}
                    </div>
                </div>
            </div>

            {/* Footer Status */}
            <div className="p-2 border-t border-[var(--border-subtle)] bg-[var(--surface)] text-[10px] text-center text-[var(--muted)]">
                Status: <span className="uppercase font-medium">{day.pillarTask.status}</span>
            </div>
        </div>
    );
}

// --- HELPER COMPONENTS ---

function getChannelIcon(channel: string) {
    const c = channel.toLowerCase();
    if (c.includes('link') || c.includes('li')) return <Linkedin size={10} />;
    if (c.includes('twitter') || c.includes('x')) return <Twitter size={10} />;
    if (c.includes('insta') || c.includes('ig')) return <Instagram size={10} />;
    if (c.includes('mail') || c.includes('sub')) return <Mail size={10} />;
    if (c.includes('multi')) return <Layers size={10} />;
    if (c.includes('dm')) return <MessageSquare size={10} />;
    return <Circle size={8} />;
}


function ChannelBadge({ channel }: { channel: string }) {
    const c = channel.toLowerCase();
    let icon = <Activity size={10} />;

    if (c.includes('link') || c.includes('li')) icon = <Linkedin size={10} />;
    else if (c.includes('twitter') || c.includes('x')) icon = <Twitter size={10} />;
    else if (c.includes('insta') || c.includes('ig')) icon = <Instagram size={10} />;
    else if (c.includes('mail') || c.includes('sub')) icon = <Mail size={10} />;
    else if (c.includes('multi')) icon = <Layers size={10} />;
    else if (c.includes('dm')) icon = <MessageSquare size={10} />;

    return (
        <span className="inline-flex items-center gap-1.5 text-[9px] font-mono text-[var(--ink-secondary)] px-1.5 py-0.5 rounded border border-[var(--border)] bg-[var(--surface)]">
            {icon}
            <span className="capitalize">{channel}</span>
        </span>
    );
}

function ChannelIcon({ channel }: { channel: string }) {
    return (
        <div className="text-[var(--muted)]" title={channel}>
            {getChannelIcon(channel)}
        </div>
    );
}
