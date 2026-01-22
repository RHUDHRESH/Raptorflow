import React, { useState } from "react";
import { Check, Clock, Calendar, ChevronRight, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Progress } from "@radix-ui/react-progress";

interface Task {
    id: string;
    label: string;
    status: "pending" | "completed" | "locked";
    type: "action" | "decision" | "review";
    timeEstimate?: string;
}

interface ExecutionDay {
    day: number;
    date: string;
    theme: string;
    phase: string;
    clusterActions: Task[];
    networkAction: Task | null;
    status: "active" | "locked" | "completed";
}

// Mock Data
const MOCK_DAY: ExecutionDay = {
    day: 12,
    date: "Oct 24",
    theme: "Distribution Systems",
    phase: "Phase 2: Authority",
    status: "active",
    clusterActions: [
        { id: "t1", label: "Post 'The 3-Step Framework' on LinkedIn (Carousel)", status: "completed", type: "action", timeEstimate: "15m" },
        { id: "t2", label: "Engage with 5 founders in 'SaaS Growth' cluster", status: "pending", type: "action", timeEstimate: "20m" },
        { id: "t3", label: "Review analytics for yesterday's thread", status: "pending", type: "review", timeEstimate: "10m" },
    ],
    networkAction: { id: "n1", label: "Dm 3 potential partners", status: "locked", type: "action" },
};

export function DailyTaskBoard() {
    const [tasks, setTasks] = useState(MOCK_DAY.clusterActions);
    const completedCount = tasks.filter((t) => t.status === "completed").length;
    const progress = (completedCount / tasks.length) * 100;

    const toggleTask = (id: string) => {
        setTasks(tasks.map(t =>
            t.id === id ? { ...t, status: t.status === "completed" ? "pending" : "completed" } : t
        ));
    };

    return (
        <div className="card-diffused p-6 h-full flex flex-col relative overflow-hidden">
            {/* Header - Glassy & Vibrant */}
            <div className="flex items-start justify-between mb-6 relative z-10">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-primary bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100 dark:bg-indigo-900/20 dark:border-indigo-800">
                            Day {MOCK_DAY.day}
                        </span>
                        <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100 animate-pulse">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            LIVE
                        </span>
                    </div>
                    <h2 className="text-xl font-bold text-ink flex items-center gap-2">
                        {MOCK_DAY.theme}
                    </h2>
                    <p className="text-xs text-ink-muted font-medium mt-1">{MOCK_DAY.phase}</p>
                </div>

                {/* Calendar Icon - Decorative */}
                <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl text-white shadow-lg shadow-indigo-500/20 rotate-3 transform hover:rotate-0 transition-transform duration-300">
                    <Calendar className="w-5 h-5" />
                </div>
            </div>

            {/* Progress Bar - Vibrant Gradient */}
            <div className="mb-8 space-y-2">
                <div className="flex justify-between text-xs font-medium">
                    <span className="text-ink-secondary">Daily Progress</span>
                    <span className="text-primary font-bold">{Math.round(progress)}%</span>
                </div>
                <Progress.Root className="progress-modern w-full" value={progress}>
                    <Progress.Indicator
                        className="progress-modern-bar w-full"
                        style={{ transform: `translateX(-${100 - progress}%)` }}
                    />
                </Progress.Root>
            </div>

            {/* Tasks List */}
            <div className="space-y-3 flex-1 overflow-y-auto pr-1 custom-scrollbar relative z-10">
                {tasks.map((task) => (
                    <div
                        key={task.id}
                        onClick={() => task.status !== "locked" && toggleTask(task.id)}
                        className={cn(
                            "group flex items-start gap-4 p-4 rounded-xl border transition-all duration-300 cursor-pointer relative overflow-hidden",
                            task.status === "completed"
                                ? "bg-surface/50 border-transparent opacity-60 hover:opacity-100"
                                : "bg-surface hover:bg-white hover:shadow-modern-md border-border-subtle hover:border-primary/20 hover:-translate-y-0.5"
                        )}
                    >
                        {/* Checkbox */}
                        <div className={cn(
                            "mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors duration-300 z-10",
                            task.status === "completed"
                                ? "bg-emerald-500 border-emerald-500 text-white"
                                : "bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-600"
                        )}>
                            {task.status === "completed" && <Check className="w-3 h-3" strokeWidth={3} />}
                        </div>

                        <div className="flex-1 z-10">
                            <p className={cn(
                                "text-sm font-medium transition-all duration-300",
                                task.status === "completed" ? "text-ink-muted line-through" : "text-ink"
                            )}>
                                {task.label}
                            </p>
                            <div className="flex items-center gap-3 mt-2">
                                <span className={cn(
                                    "text-[10px] uppercase font-bold px-1.5 py-0.5 rounded",
                                    task.type === "action" ? "bg-blue-50 text-blue-600" :
                                        task.type === "decision" ? "bg-purple-50 text-purple-600" :
                                            "bg-amber-50 text-amber-600"
                                )}>
                                    {task.type}
                                </span>
                                {task.timeEstimate && (
                                    <span className="flex items-center gap-1 text-[10px] text-ink-muted">
                                        <Clock className="w-3 h-3" />
                                        {task.timeEstimate}
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Locked Item Example */}
                <div className="flex items-center gap-4 p-4 rounded-xl border border-dashed border-gray-200 bg-gray-50/50 opacity-70">
                    <div className="w-5 h-5 rounded-full border-2 border-gray-200 flex items-center justify-center">
                        <Lock className="w-3 h-3 text-gray-400" />
                    </div>
                    <div className="flex-1">
                        <p className="text-sm font-medium text-gray-400">Bonus: Network Outreach</p>
                        <p className="text-[10px] text-gray-400 mt-1">Updates available at 5PM</p>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-6 pt-4 border-t border-border-subtle relative z-10">
                <button className="w-full py-2.5 rounded-lg btn-modern-ghost text-xs font-bold uppercase tracking-wider hover:bg-indigo-50 hover:text-indigo-600 transition-colors flex items-center justify-center gap-2">
                    View Full Calendar <ChevronRight className="w-3 h-3" />
                </button>
            </div>

            {/* Background Blob */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 blur-3xl rounded-full pointer-events-none -mr-16 -mt-16" />
            <div className="absolute bottom-0 left-0 w-40 h-40 bg-emerald-500/5 blur-2xl rounded-full pointer-events-none -ml-10 -mb-10" />
        </div>
    );
}
