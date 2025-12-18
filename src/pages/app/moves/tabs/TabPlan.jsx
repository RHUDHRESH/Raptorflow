import { motion } from 'framer-motion'
import {
    Check,
    Calendar,
    Flag,
    ChevronRight,
    MapPin,
    Milestone
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'

/**
 * Plan Tab - Timeline + Checkpoints
 */

const TabPlan = ({ move, framework, currentDay, totalDays }) => {
    const { toggleTaskDone } = useRaptorflowStore()

    const tasks = move.checklistItems || []

    // Group tasks by phase
    const getPhase = (day) => {
        const ratio = day / totalDays
        if (ratio <= 0.25) return { name: 'Build', color: 'blue' }
        if (ratio <= 0.6) return { name: 'Launch', color: 'emerald' }
        if (ratio <= 0.85) return { name: 'Optimize', color: 'amber' }
        return { name: 'Review', color: 'purple' }
    }

    // Group tasks by day
    const tasksByDay = tasks.reduce((acc, task) => {
        const day = task.day || 1
        if (!acc[day]) acc[day] = []
        acc[day].push(task)
        return acc
    }, {})

    // Get checkpoints
    const checkpoints = [
        { day: 3, name: 'Day 3 Check', description: 'Early pulse check - are we on track?', type: 'day3' },
        { day: Math.ceil(totalDays / 2), name: 'Midpoint Review', description: 'Halfway review & adjustments', type: 'midpoint' },
        { day: totalDays, name: 'Final Review', description: 'After-action report & playbook save', type: 'end' }
    ].filter(c => c.day <= totalDays)

    return (
        <div className="max-w-3xl mx-auto pb-12">

            {/* Header */}
            <div className="mb-8 p-4 rounded-xl bg-muted/30 border border-border/60 flex items-center gap-4">
                <MapPin className="w-5 h-5 text-muted-foreground" />
                <div>
                    <h3 className="text-sm font-medium text-foreground">Mission Timeline</h3>
                    <div className="text-xs text-muted-foreground">
                        {totalDays} Day Campaign • {tasks.length} Actions • 3 Checkpoints
                    </div>
                </div>
            </div>

            {/* Timeline */}
            <div className="relative pl-4">
                {/* Vertical line - tactical dash */}
                <div className="absolute left-[31px] top-4 bottom-0 w-px bg-border border-l border-dashed border-muted-foreground/30" />

                {/* Days */}
                {Array.from({ length: totalDays }, (_, i) => i + 1).map((day) => {
                    const dayTasks = tasksByDay[day] || []
                    const phase = getPhase(day)
                    const isToday = day === currentDay
                    const isPast = day < currentDay
                    const checkpoint = checkpoints.find(c => c.day === day)
                    const allDone = dayTasks.length > 0 && dayTasks.every(t => t.done)
                    const someDone = dayTasks.some(t => t.done)

                    return (
                        <motion.div
                            key={day}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: Math.min(day * 0.05, 0.5) }}
                            className={`relative pl-12 pb-8 ${isPast && !isToday ? 'opacity-70' : 'opacity-100'}`}
                        >
                            {/* Day Node */}
                            <div className={`
                                absolute left-[19px] top-0 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold z-10 border-2 transition-all
                                ${isToday
                                    ? 'bg-primary text-primary-foreground border-primary scale-110 shadow-lg shadow-primary/20'
                                    : allDone
                                        ? 'bg-emerald-500 border-emerald-500 text-white'
                                        : isPast
                                            ? 'bg-muted border-muted-foreground/30 text-muted-foreground'
                                            : 'bg-background border-border text-muted-foreground'
                                }
                            `}>
                                {allDone ? <Check size={12} strokeWidth={3} /> : day}
                            </div>

                            {/* Content Card */}
                            <div className={`
                                rounded-xl border transition-all duration-300 group
                                ${isToday
                                    ? 'bg-card border-primary/40 shadow-md ring-1 ring-primary/10'
                                    : 'bg-card/50 border-border hover:border-primary/20 hover:bg-card'
                                }
                            `}>
                                {/* Day Header */}
                                <div className="flex items-center justify-between p-3 border-b border-border/50">
                                    <div className="flex items-center gap-3">
                                        <div className="text-sm font-bold text-foreground">Day {day}</div>
                                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase tracking-wider font-bold bg-${phase.color}-100 text-${phase.color}-700 dark:bg-${phase.color}-900/30 dark:text-${phase.color}-400`}>
                                            {phase.name}
                                        </span>
                                    </div>
                                    {isToday && <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full">CURRENT</span>}
                                </div>

                                {/* Task List */}
                                <div className="p-2 space-y-1">
                                    {dayTasks.length > 0 ? (
                                        dayTasks.map((task) => (
                                            <div
                                                key={task.id}
                                                className={`
                                                    flex items-start gap-3 p-2 rounded-lg transition-colors cursor-pointer group/task
                                                    ${task.done ? 'opacity-60' : 'hover:bg-muted/50'}
                                                `}
                                                onClick={() => toggleTaskDone(move.id, task.id)}
                                            >
                                                <div className={`
                                                    mt-0.5 w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 transition-colors
                                                    ${task.done
                                                        ? 'bg-primary border-primary text-primary-foreground'
                                                        : 'border-muted-foreground/40 group-hover/task:border-primary'
                                                    }
                                                `}>
                                                    {task.done && <Check size={10} strokeWidth={3} />}
                                                </div>
                                                <div className={`text-sm leading-snug ${task.done ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                                                    {task.text}
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="p-2 text-xs text-muted-foreground italic">Rest & Optimize</div>
                                    )}
                                </div>

                                {/* Checkpoint Marker */}
                                {checkpoint && (
                                    <div className="px-3 pb-3 pt-1">
                                        <div className="flex items-start gap-3 p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
                                            <Milestone className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5" />
                                            <div>
                                                <div className="text-xs font-bold text-amber-700 dark:text-amber-300 uppercase tracking-wide">
                                                    Checkpoint: {checkpoint.name}
                                                </div>
                                                <div className="text-xs text-amber-600/80 dark:text-amber-400/80 mt-0.5">
                                                    {checkpoint.description}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )
                })}
            </div>
        </div>
    )
}

export default TabPlan
