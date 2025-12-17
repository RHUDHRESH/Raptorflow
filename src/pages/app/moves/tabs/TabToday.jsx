import { motion } from 'framer-motion'
import {
    Clock,
    Sparkles,
    Check,
    AlertCircle,
    SkipForward,
    ChevronRight
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'

/**
 * Today Tab - Single-Task Execution View
 * 
 * Shows ONE task with absolute clarity:
 * - The task
 * - Why it matters
 * - Time estimate
 * - Actions: Mark done, Generate draft, Skip, Blocked
 */

const TabToday = ({ move, framework, currentDay, totalDays }) => {
    const { toggleTaskDone, getMoveTasksForDay, openMuseDrawer } = useRaptorflowStore()

    // Get today's tasks
    const todayTasks = getMoveTasksForDay ? getMoveTasksForDay(move.id, currentDay) : []
    const allTasks = move.checklistItems || []

    // Find the current task (first incomplete task for today)
    const currentTask = todayTasks.find(t => !t.done) || allTasks.find(t => !t.done && t.day === currentDay)

    // Get framework action template for context
    const actionTemplate = framework?.dailyActions?.templates?.find(t => t.day === currentDay)

    // Count completed for today
    const todayCompleted = todayTasks.filter(t => t.done).length
    const todayTotal = todayTasks.length || 1

    if (!currentTask) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-12"
            >
                <div className="w-16 h-16 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mx-auto mb-4">
                    <Check className="w-8 h-8 text-emerald-600 dark:text-emerald-400" strokeWidth={2} />
                </div>
                <h2 className="font-serif text-xl text-foreground mb-2">
                    You're all done for today!
                </h2>
                <p className="text-muted-foreground max-w-md mx-auto">
                    Great work completing Day {currentDay}. Come back tomorrow for your next task,
                    or review your progress in the Plan tab.
                </p>
            </motion.div>
        )
    }

    const handleMarkDone = () => {
        toggleTaskDone(move.id, currentTask.id)
    }

    const handleGenerateDraft = () => {
        if (openMuseDrawer) {
            openMuseDrawer({
                context: currentTask.text,
                moveName: move.name
            })
        }
    }

    const isContentTask = currentTask.text.toLowerCase().includes('create') ||
        currentTask.text.toLowerCase().includes('write') ||
        currentTask.text.toLowerCase().includes('draft')

    return (
        <div className="max-w-2xl mx-auto">
            {/* Day progress */}
            <div className="flex items-center justify-between mb-6">
                <span className="text-sm text-muted-foreground">
                    Day {currentDay} of {totalDays}
                </span>
                <span className="text-sm text-muted-foreground">
                    {todayCompleted} of {todayTotal} tasks done
                </span>
            </div>

            {/* Main task card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-primary/5 border-2 border-primary/20 rounded-2xl p-8 mb-6"
            >
                {/* Task label */}
                <div className="flex items-center gap-2 mb-4">
                    <div className="px-3 py-1 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                        Today's Focus
                    </div>
                    {currentTask.duration && (
                        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                            <Clock className="w-4 h-4" strokeWidth={1.5} />
                            {currentTask.duration} min
                        </div>
                    )}
                </div>

                {/* Task text */}
                <h2 className="font-serif text-2xl text-foreground mb-4">
                    {currentTask.text}
                </h2>

                {/* Why it matters */}
                {actionTemplate && (
                    <div className="p-4 rounded-xl bg-background border border-border mb-6">
                        <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                            Why this matters
                        </h4>
                        <p className="text-sm text-foreground">
                            {getWhyItMatters(currentTask, framework, currentDay)}
                        </p>
                    </div>
                )}

                {/* Primary action */}
                <button
                    onClick={handleMarkDone}
                    className="w-full flex items-center justify-center gap-2 py-4 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity"
                >
                    <Check className="w-5 h-5" strokeWidth={2} />
                    Mark as Done
                </button>
            </motion.div>

            {/* Secondary actions */}
            <div className="grid grid-cols-3 gap-3">
                {/* Generate draft - only for content tasks */}
                {isContentTask && (
                    <button
                        onClick={handleGenerateDraft}
                        className="flex flex-col items-center gap-2 p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-colors"
                    >
                        <Sparkles className="w-5 h-5 text-primary" strokeWidth={1.5} />
                        <span className="text-xs text-foreground">Generate Draft</span>
                    </button>
                )}

                {/* I'm blocked */}
                <button className="flex flex-col items-center gap-2 p-4 rounded-xl bg-card border border-border hover:border-amber-500/30 transition-colors">
                    <AlertCircle className="w-5 h-5 text-amber-500" strokeWidth={1.5} />
                    <span className="text-xs text-foreground">I'm Blocked</span>
                </button>

                {/* Skip */}
                <button className="flex flex-col items-center gap-2 p-4 rounded-xl bg-card border border-border hover:border-muted-foreground/30 transition-colors">
                    <SkipForward className="w-5 h-5 text-muted-foreground" strokeWidth={1.5} />
                    <span className="text-xs text-foreground">Skip</span>
                </button>
            </div>

            {/* Other tasks for today */}
            {todayTasks.length > 1 && (
                <div className="mt-8">
                    <h3 className="text-sm font-medium text-foreground mb-3">Other tasks today</h3>
                    <div className="space-y-2">
                        {todayTasks.filter(t => t.id !== currentTask.id).map((task) => (
                            <div
                                key={task.id}
                                className={`
                  flex items-center gap-3 p-3 rounded-xl border transition-colors
                  ${task.done
                                        ? 'bg-muted/50 border-border'
                                        : 'bg-card border-border hover:border-primary/30'
                                    }
                `}
                            >
                                <button
                                    onClick={() => toggleTaskDone(move.id, task.id)}
                                    className={`
                    w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors
                    ${task.done
                                            ? 'border-primary bg-primary'
                                            : 'border-muted-foreground hover:border-primary'
                                        }
                  `}
                                >
                                    {task.done && <Check className="w-3 h-3 text-primary-foreground" strokeWidth={2} />}
                                </button>
                                <span className={`text-sm ${task.done ? 'text-muted-foreground line-through' : 'text-foreground'}`}>
                                    {task.text}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Quick tip */}
            <div className="mt-8 p-4 rounded-xl bg-muted/50 border border-border">
                <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-4 h-4 text-primary" strokeWidth={1.5} />
                    </div>
                    <div>
                        <h4 className="text-sm font-medium text-foreground mb-1">
                            Pro tip
                        </h4>
                        <p className="text-sm text-muted-foreground">
                            {getProTip(currentDay, totalDays)}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Helper: Generate contextual "why it matters" text
const getWhyItMatters = (task, framework, day) => {
    const reasons = {
        1: 'This foundation sets the tone for your entire move. Get this right.',
        2: 'Building on yesterday\'s work to create momentum.',
        3: 'Day 3 is the midpoint check - strong execution here predicts success.',
        7: 'Final sprint energy. The finish line is in sight.'
    }

    if (reasons[day]) return reasons[day]

    if (task.text.toLowerCase().includes('research')) {
        return 'Research-backed moves outperform gut-feel by 3x. This step builds your foundation.'
    }
    if (task.text.toLowerCase().includes('create') || task.text.toLowerCase().includes('write')) {
        return 'Content creation is where strategy becomes reality. Focus on quality over speed.'
    }
    if (task.text.toLowerCase().includes('launch') || task.text.toLowerCase().includes('publish')) {
        return 'Shipping is the only thing that generates feedback. Done is better than perfect.'
    }

    return 'Each task compounds. Complete this to unlock the next phase of your move.'
}

// Helper: Generate contextual pro tips
const getProTip = (currentDay, totalDays) => {
    const tips = [
        'Block 90 minutes of uninterrupted time for your main task today.',
        'If you\'re stuck, use the "Generate Draft" button to get AI assistance.',
        'Log your progress at the end of each day to track momentum.',
        'Don\'t skip tasks - they\'re sequenced for a reason.',
        'Review your KPI baseline before pushing content live.'
    ]

    if (currentDay === 1) {
        return 'Day 1 sets the pace. Give yourself extra time to understand the framework.'
    }
    if (currentDay === 3) {
        return 'Day 3 checkpoint: Ask yourself "Am I on track?" If not, adjust now.'
    }
    if (currentDay >= totalDays - 1) {
        return 'Final stretch! Focus on completion and logging your results.'
    }

    return tips[currentDay % tips.length]
}

export default TabToday
