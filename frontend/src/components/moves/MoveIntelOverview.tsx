"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { useMovesStore } from "@/stores/movesStore";
import { TrendingUp, Zap, Target, Clock, CheckCircle2, Activity } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE INTEL OVERVIEW
   A summary view for the Moves page - shows aggregate intel across all moves.
   Does not require a specific move prop.
   ══════════════════════════════════════════════════════════════════════════════ */

export function MoveIntelOverview() {
    const { moves } = useMovesStore();

    const activeMoves = moves.filter(m => m.status === "active");
    const completedMoves = moves.filter(m => m.status === "completed");
    const totalTasks = moves.reduce((acc, m) => {
        return acc + (m.execution?.length || 0) * 3; // pillar + cluster + network per day
    }, 0);

    const completedTasks = moves.reduce((acc, m) => {
        let count = 0;
        m.execution?.forEach(day => {
            if (day.pillarTask?.status === "done") count++;
            day.clusterActions?.forEach(a => { if (a.status === "done") count++; });
            if (day.networkAction?.status === "done") count++;
        });
        return acc + count;
    }, 0);

    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    // Category distribution
    const categoryCount: Record<string, number> = {};
    moves.forEach(m => {
        categoryCount[m.category] = (categoryCount[m.category] || 0) + 1;
    });
    const topCategory = Object.entries(categoryCount).sort((a, b) => b[1] - a[1])[0];

    return (
        <BlueprintCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-[var(--blueprint)]/10 rounded-lg">
                    <Activity size={20} className="text-[var(--blueprint)]" />
                </div>
                <div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">Intel Overview</h3>
                    <p className="text-xs text-[var(--ink-secondary)]">Strategic summary across all moves</p>
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)]">
                    <div className="flex items-center gap-2 mb-2">
                        <Zap size={16} className="text-[var(--blueprint)]" />
                        <span className="text-[10px] font-mono text-[var(--muted)] uppercase">Active</span>
                    </div>
                    <div className="text-2xl font-bold text-[var(--ink)]">{activeMoves.length}</div>
                    <div className="text-xs text-[var(--ink-secondary)]">moves in flight</div>
                </div>

                <div className="p-4 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)]">
                    <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 size={16} className="text-[var(--success)]" />
                        <span className="text-[10px] font-mono text-[var(--muted)] uppercase">Completed</span>
                    </div>
                    <div className="text-2xl font-bold text-[var(--ink)]">{completedMoves.length}</div>
                    <div className="text-xs text-[var(--ink-secondary)]">moves finished</div>
                </div>

                <div className="p-4 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)]">
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp size={16} className="text-[var(--warning)]" />
                        <span className="text-[10px] font-mono text-[var(--muted)] uppercase">Task Rate</span>
                    </div>
                    <div className="text-2xl font-bold text-[var(--ink)]">{completionRate}%</div>
                    <div className="text-xs text-[var(--ink-secondary)]">{completedTasks}/{totalTasks} tasks</div>
                </div>

                <div className="p-4 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)]">
                    <div className="flex items-center gap-2 mb-2">
                        <Target size={16} className="text-[var(--ink)]" />
                        <span className="text-[10px] font-mono text-[var(--muted)] uppercase">Top Focus</span>
                    </div>
                    <div className="text-lg font-bold text-[var(--ink)] capitalize truncate">
                        {topCategory ? topCategory[0] : "—"}
                    </div>
                    <div className="text-xs text-[var(--ink-secondary)]">
                        {topCategory ? `${topCategory[1]} moves` : "no data"}
                    </div>
                </div>
            </div>

            {moves.length === 0 && (
                <div className="mt-6 text-center py-8 border border-dashed border-[var(--border)] rounded-[var(--radius)]">
                    <Clock size={24} className="mx-auto text-[var(--muted)] mb-2" />
                    <p className="text-[var(--ink-secondary)]">No moves created yet</p>
                    <p className="text-xs text-[var(--muted)]">Create your first move to see intel here</p>
                </div>
            )}
        </BlueprintCard>
    );
}
