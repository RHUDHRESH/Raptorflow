import { motion } from 'framer-motion'
import {
    Check,
    Calendar,
    Flag,
    ChevronRight
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'

/**
 * Plan Tab - Timeline + Checkpoints
 * 
 * Shows:
 * - Vertical timeline by day
 * - Phase groupings (Build, Launch, Optimize, Review)
 * - Checkpoint cards (Day 3, Midpoint, End)
 */

const TabPlan = ({ move, framework, currentDay, totalDays }) => {
    const { toggleTaskDone } = useRaptorflowStore()

    const tasks = move.checklistItems || []

    // Group tasks by phase
    const getPhase = (day) => {
        const ratio = day / totalDays
        if (ratio <= 0.25) return 'Build'
        if (ratio <= 0.5) return 'Launch'
        if (ratio <= 0.75) return 'Optimize'
        return 'Review'
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
        { day: 3, name: 'Day 3 Check', description: 'Are we on track?' },
        { day: Math.floor(totalDays / 2), name: 'Midpoint', description: 'Halfway review' },
        { day: totalDays, name: 'Final Review', description: 'After-action report' }
    ].filter(c => c.day <= totalDays)

    return (
        <div className="max-w-3xl mx-auto">
            {/* Phase legend */}
            <div className="flex items-center gap-4 mb-6 pb-4 border-b border-border">
                {['Build', 'Launch', 'Optimize', 'Review'].map((phase, idx) => (
                    <div key={phase} className="flex items-center gap-2">
                        <div className={`
              w-3 h-3 rounded-full
              ${idx === 0 ? 'bg-blue-500' : idx === 1 ? 'bg-emerald-500' : idx === 2 ? 'bg-amber-500' : 'bg-purple-500'}
            `} />
                        <span className="text-xs text-muted-foreground">{phase}</span>
                    </div>
                ))}
            </div>

            {/* Timeline */}
            <div className="relative">
                {/* Vertical line */}
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />

                {/* Days */}
                {Array.from({ length: totalDays }, (_, i) => i + 1).map((day) => {
                    const dayTasks = tasksByDay[day] || []
                    const phase = getPhase(day)
                    const isToday = day === currentDay
                    const isPast = day < currentDay
                    const checkpoint = checkpoints.find(c => c.day === day)
                    const allDone = dayTasks.length > 0 && dayTasks.every(t => t.done)

                    const phaseColor = phase === 'Build' ? 'blue' : phase === 'Launch' ? 'emerald' : phase === 'Optimize' ? 'amber' : 'purple'

                    return (
                        <motion.div
                            key={day}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: day * 0.03 }}
                            className="relative pl-16 pb-6"
                        >
                            {/* Day marker */}
                            <div className={`
                absolute left-3 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium z-10
                ${isToday
                                    ? 'bg-primary text-primary-foreground ring-4 ring-primary/20'
                                    : allDone
                                        ? 'bg-emerald-500 text-white'
                                        : isPast
                                            ? 'bg-muted text-muted-foreground'
                                            : 'bg-card border-2 border-border text-foreground'
                                }
              `}>
                                {allDone ? <Check className="w-3 h-3" strokeWidth={2} /> : day}
                            </div>

                            {/* Content */}
                            <div className={`
                rounded-xl border transition-colors
                ${isToday
                                    ? 'bg-primary/5 border-primary/30'
                                    : 'bg-card border-border'
                                }
              `}>
                                {/* Day header */}
                                <div className="flex items-center justify-between p-4 border-b border-border">
                                    <div className="flex items-center gap-3">
                                        <span className={`text-sm font-medium ${isToday ? 'text-primary' : 'text-foreground'}`}>
                                            Day {day}
                                        </span>
                                        <span className={`
                      px-2 py-0.5 rounded-full text-xs
                      bg-${phaseColor}-100 text-${phaseColor}-700 dark:bg-${phaseColor}-900/30 dark:text-${phaseColor}-400
                    `}>
                                            {phase}
                                        </span>
                                        {isToday && (
                                            <span className="px-2 py-0.5 rounded-full bg-primary text-primary-foreground text-xs">
                                                Today
                                            </span>
                                        )}
                                    </div>

                                    {dayTasks.length > 0 && (
                                        <span className="text-xs text-muted-foreground">
                                            {dayTasks.filter(t => t.done).length}/{dayTasks.length} done
                                        </span>
                                    )}
                                </div>

                                {/* Tasks */}
                                {dayTasks.length > 0 ? (
                                    <div className="p-4 space-y-2">
                                        {dayTasks.map((task) => (
                                            <div
                                                key={task.id}
                                                className={`
                          flex items-center gap-3 p-3 rounded-lg transition-colors
                          ${task.done
                                                        ? 'bg-muted/50'
                                                        : 'bg-background hover:bg-muted/30'
                                                    }
                        `}
                                            >
                                                <button
                                                    onClick={() => toggleTaskDone(move.id, task.id)}
                                                    className={`
                            w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors
                            ${task.done
                                                            ? 'border-emerald-500 bg-emerald-500'
                                                            : isPast
                                                                ? 'border-amber-500'
                                                                : 'border-muted-foreground hover:border-primary'
                                                        }
                          `}
                                                >
                                                    {task.done && <Check className="w-3 h-3 text-white" strokeWidth={2} />}
                                                </button>
                                                <span className={`text-sm flex-1 ${task.done ? 'text-muted-foreground line-through' : 'text-foreground'}`}>
                                                    {task.text}
                                                </span>
                                                {task.duration && (
                                                    <span className="text-xs text-muted-foreground">
                                                        {task.duration}m
                                                    </span>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="p-4 text-sm text-muted-foreground">
                                        No tasks scheduled
                                    </div>
                                )}

                                {/* Checkpoint */}
                                {checkpoint && (
                                    <div className="mx-4 mb-4 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
                                        <div className="flex items-center gap-2">
                                            <Flag className="w-4 h-4 text-amber-600 dark:text-amber-400" strokeWidth={1.5} />
                                            <span className="text-sm font-medium text-amber-700 dark:text-amber-300">
                                                {checkpoint.name}
                                            </span>
                                        </div>
                                        <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                                            {checkpoint.description}
                                        </p>
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
