import { motion } from 'framer-motion'
import {
    Clock,
    Check,
    AlertCircle,
    ChevronRight,
    Map,
    Target,
    Zap,
    Briefcase
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'
import { PROBLEM_TYPES } from '../../../../data/frameworkConfigs'

const TabToday = ({ move, framework, currentDay, totalDays }) => {
    const { toggleTaskDone, getMoveTasksForDay, openMuseDrawer } = useRaptorflowStore()

    // Get today's tasks
    const todayTasks = getMoveTasksForDay ? getMoveTasksForDay(move.id, currentDay) : []
    const sortedTasks = todayTasks.sort((a, b) => a.done === b.done ? 0 : a.done ? 1 : -1)

    // Find urgency (first incomplete)
    const currentTask = sortedTasks.find(t => !t.done)
    const isAllDone = !currentTask && todayTasks.length > 0

    // Context Data
    const problem = move.problemType ? PROBLEM_TYPES[move.problemType] : null
    const frameworkName = move.frameworkName || framework?.name || 'Custom Framework'
    const inputs = move.slots?.inputs || {}
    const tracking = move.tracking || {}
    const kpi = tracking.metric || 'Goal'
    const target = tracking.target || '?'
    const current = tracking.updates?.[tracking.updates.length - 1]?.value || tracking.baseline || 0

    // --- Helpers ---

    const getWhyItMatters = (task, day) => {
        // Truer context based on task content
        const t = task.text.toLowerCase()
        if (t.includes('research')) return "Research-backed moves outperform gut attempts by 3x. This sets your foundation."
        if (t.includes('draft') || t.includes('write')) return "Content is where strategy hits reality. Focus on clarity over cleverness."
        if (t.includes('publish') || t.includes('post')) return "Shipping is the only way to generate data. Don't overthink it."
        if (t.includes('review') || t.includes('measure')) return "You can't improve what you don't measure. Honesty here saves money later."

        // Fallback to day logic
        if (day === 1) return "Momentum starts here. Crushing day 1 predicts move success."
        if (day === 3) return "The crucial pivot point. Early feedback determines the next 10 days."
        if (day === totalDays) return "Finish strong. Capture the learnings for your playbook."

        return "This task unlocks the next step in your sequence."
    }

    // --- Render ---

    if (isAllDone) {
        return (
            <div className="max-w-3xl mx-auto py-12 text-center animate-in fade-in slide-in-from-bottom-4">
                <div className="w-20 h-20 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mx-auto mb-6">
                    <Check className="w-10 h-10 text-emerald-600 dark:text-emerald-400" strokeWidth={3} />
                </div>
                <h2 className="font-serif text-3xl text-foreground mb-3">You won today.</h2>
                <p className="text-muted-foreground text-lg max-w-md mx-auto mb-8">
                    Day {currentDay} complete. You're one step closer to {kpi}.
                </p>
                <div className="flex justify-center gap-4">
                    <div className="p-4 rounded-xl bg-muted/50 border border-border">
                        <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Current {kpi}</div>
                        <div className="text-xl font-bold text-foreground">{current}</div>
                    </div>
                </div>
            </div>
        )
    }

    if (!currentTask) {
        return <div className="text-center py-12 text-muted-foreground">No tasks scheduled for today. Check the Plan tab.</div>
    }

    return (
        <div className="max-w-3xl mx-auto pb-12 animate-in fade-in slide-in-from-bottom-2 duration-500">

            {/* 1. STRATEGY HEADER (Context) */}
            <div className="mb-8 p-4 rounded-xl bg-muted/30 border border-border/60">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 text-sm">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                            <Briefcase size={16} strokeWidth={2} />
                        </div>
                        <div>
                            <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Buying Back Focus</div>
                            <div className="font-medium text-foreground">Solving "{problem?.statement || 'Unknown Problem'}"</div>
                        </div>
                    </div>
                    <div className="hidden md:block w-px h-8 bg-border" />
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center text-orange-500">
                            <Map size={16} strokeWidth={2} />
                        </div>
                        <div>
                            <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Using Framework</div>
                            <div className="font-medium text-foreground">{frameworkName}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 2. FOCUS CARD (The "One Thing") */}
            <div className="relative overflow-hidden rounded-2xl border-2 border-primary/20 bg-card shadow-lg mb-8">
                {/* Status Strip */}
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-primary to-primary/50" />

                <div className="p-6 md:p-8">
                    <div className="flex items-center justify-between mb-6">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wide">
                            <Zap size={12} className="fill-current" />
                            Today's Single Task
                        </div>
                        <div className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground bg-muted/50 px-3 py-1 rounded-lg">
                            <Clock size={14} />
                            {currentTask.duration || 60} min
                        </div>
                    </div>

                    <h1 className="font-serif text-3xl md:text-4xl text-foreground leading-tight mb-6">
                        {currentTask.text}
                    </h1>

                    <div className="grid md:grid-cols-2 gap-8 mb-8">
                        {/* WHY */}
                        <div>
                            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-3">
                                Why This Matters
                            </h4>
                            <p className="text-sm leading-relaxed text-foreground/80">
                                {getWhyItMatters(currentTask, currentDay)}
                            </p>
                        </div>

                        {/* INPUTS */}
                        <div>
                            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-3">
                                Inputs You Have
                            </h4>
                            {Object.keys(inputs).length > 0 ? (
                                <ul className="space-y-2">
                                    {Object.entries(inputs).slice(0, 3).map(([key, val]) => (
                                        <li key={key} className="flex items-start gap-2 text-sm text-foreground/80">
                                            <div className="mt-1.5 w-1 h-1 rounded-full bg-primary flex-shrink-0" />
                                            <span className="line-clamp-1 italic text-muted-foreground">{val || 'Not defined'}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="text-sm text-muted-foreground italic">No specific inputs defined.</div>
                            )}
                        </div>
                    </div>

                    {/* BIG CTA */}
                    <button
                        onClick={() => toggleTaskDone(move.id, currentTask.id)}
                        className="w-full flex items-center justify-center gap-3 py-4 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl text-base font-bold shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all active:translate-y-0"
                    >
                        <Check className="w-5 h-5" strokeWidth={3} />
                        COMPLETE THIS TASK
                    </button>

                    <div className="mt-4 flex justify-center gap-6 text-xs font-medium text-muted-foreground">
                        <button onClick={() => openMuseDrawer({ context: currentTask.text, moveName: move.name })} className="hover:text-primary transition-colors">
                            Generate Draft (AI)
                        </button>
                        <button className="hover:text-foreground transition-colors">
                            Skip for now
                        </button>
                    </div>
                </div>
            </div>

            {/* 3. PACE (Scoreboard Context) */}
            <div className="bg-muted/20 border border-border rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                    <Target className="w-5 h-5 text-foreground" strokeWidth={2} />
                    <h3 className="font-bold text-foreground">Your Pace (Day {currentDay} of {totalDays})</h3>
                </div>

                <div className="flex items-center justify-between bg-card p-4 rounded-lg border border-border shadow-sm">
                    <div>
                        <div className="text-xs text-muted-foreground uppercase font-bold mb-1">Target Goal</div>
                        <div className="text-lg font-bold text-foreground">
                            {target} <span className="text-sm font-medium text-muted-foreground">{kpi}</span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-xs text-muted-foreground uppercase font-bold mb-1">Current Reality</div>
                        <div className="text-lg font-bold text-primary">
                            {current} <span className="text-sm font-medium text-muted-foreground">{kpi}</span>
                        </div>
                    </div>
                </div>
                <div className="mt-3 text-xs text-center text-muted-foreground">
                    Next task unlocks when you complete today's focus.
                </div>
            </div>

        </div>
    )
}

export default TabToday
