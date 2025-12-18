import { useState } from 'react'
import { motion } from 'framer-motion'
import {
    TrendingUp,
    TrendingDown,
    Target,
    Plus,
    BarChart3,
    Activity,
    CalendarClock
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'

/**
 * Scoreboard Tab - Results That Matter
 */

const TabScoreboard = ({ move, framework, currentDay, totalDays }) => {
    const { addTrackingUpdate } = useRaptorflowStore()
    const [newValue, setNewValue] = useState('')

    const tracking = move.tracking || {}
    const updates = tracking.updates || []
    const baseline = parseFloat(tracking.baseline) || 0
    const target = tracking.target || framework?.metrics?.primary?.target || 0

    // Calculate current value (latest update or baseline)
    const currentValue = updates.length > 0
        ? updates[updates.length - 1].value
        : baseline

    // Calculate delta from baseline
    const delta = currentValue - baseline
    const deltaPercent = baseline > 0 ? Math.round((delta / baseline) * 100) : 0
    const isPositive = delta >= 0

    // Progress towards target
    const targetValue = typeof target === 'string'
        ? parseFloat(target.replace(/[^0-9.-]/g, ''))
        : target
    const progress = targetValue > 0 && baseline < targetValue
        ? Math.min(100, Math.round(((currentValue - baseline) / (targetValue - baseline)) * 100))
        : 0

    const handleLogUpdate = () => {
        if (newValue && addTrackingUpdate) {
            addTrackingUpdate(move.id, {
                value: parseFloat(newValue),
                date: new Date().toISOString(),
                day: currentDay
            })
            setNewValue('')
        }
    }

    // Get leading indicators from framework
    const leadingIndicators = framework?.metrics?.leading || []

    return (
        <div className="max-w-3xl mx-auto pb-12">

            {/* Primary KPI Card */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-card border-2 border-primary/20 rounded-2xl p-6 mb-8 shadow-lg shadow-primary/5 relative overflow-hidden"
            >
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Target size={120} />
                </div>

                <div className="relative z-10">
                    <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                            <Activity className="w-4 h-4 text-primary" />
                            <h2 className="text-sm font-bold text-primary uppercase tracking-widest">
                                Primary Objective
                            </h2>
                        </div>
                        <div className={`
                            flex items-center gap-1 px-2 py-1 rounded text-xs font-bold uppercase
                            ${isPositive
                                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                                : 'bg-red-500/10 text-red-600 dark:text-red-400'
                            }
                        `}>
                            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                            {isPositive ? '+' : ''}{deltaPercent}%
                        </div>
                    </div>

                    <h1 className="text-4xl sm:text-6xl font-black text-foreground mb-1 tracking-tighter">
                        {tracking.metric || framework?.metrics?.primary?.name || 'Win Condition'}
                    </h1>
                </div>

                {/* Score Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8 pt-6 border-t border-border/50 relative z-10">
                    <div>
                        <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">Baseline</div>
                        <div className="text-2xl font-bold text-muted-foreground/70">{baseline}</div>
                    </div>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">Target</div>
                        <div className="text-2xl font-bold text-foreground">{target}</div>
                    </div>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">Current</div>
                        <div className="text-2xl font-bold text-primary">{currentValue}</div>
                    </div>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">Delta</div>
                        <div className={`text-2xl font-bold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
                            {isPositive ? '+' : ''}{delta}
                        </div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-6 relative z-10">
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 1, ease: 'easeOut' }}
                            className="h-full bg-primary relative"
                        >
                            <div className="absolute right-0 top-0 bottom-0 w-px bg-white/50 animate-pulse" />
                        </motion.div>
                    </div>
                    <div className="flex justify-between mt-1.5">
                        <span className="text-[10px] font-bold text-muted-foreground">0%</span>
                        <span className="text-[10px] font-bold text-primary">{progress}% COMPLETE</span>
                        <span className="text-[10px] font-bold text-muted-foreground">100%</span>
                    </div>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Update Logger */}
                <div>
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Plus size={14} /> Log Progress
                    </h3>
                    <div className="p-4 bg-muted/30 border border-border/60 rounded-xl">
                        <label className="text-xs font-medium text-foreground mb-2 block">
                            New Value for Day {currentDay}
                        </label>
                        <div className="flex gap-2">
                            <input
                                type="number"
                                value={newValue}
                                onChange={(e) => setNewValue(e.target.value)}
                                placeholder="0.00"
                                className="flex-1 bg-background border border-border rounded-lg px-3 py-2 text-sm font-mono focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                            />
                            <button
                                onClick={handleLogUpdate}
                                disabled={!newValue}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-xs font-bold uppercase disabled:opacity-50"
                            >
                                Submit
                            </button>
                        </div>
                    </div>

                    {/* Leading Indicators */}
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 mt-8 flex items-center gap-2">
                        <BarChart3 size={14} /> Signals
                    </h3>
                    <div className="space-y-2">
                        {leadingIndicators.map((indicator, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-card border border-border rounded-xl">
                                <span className="text-sm font-medium text-foreground">{indicator.name}</span>
                                <span className="text-xs font-mono text-muted-foreground">Target: {indicator.target}</span>
                            </div>
                        ))}
                        {leadingIndicators.length === 0 && (
                            <div className="text-xs text-muted-foreground italic p-2">No leading indicators defined.</div>
                        )}
                    </div>
                </div>

                {/* History Feed */}
                <div>
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                        <CalendarClock size={14} /> Data Stream
                    </h3>
                    <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                        {updates.length > 0 ? (
                            updates.slice().reverse().map((update, idx) => (
                                <div
                                    key={idx}
                                    className="flex items-center justify-between p-3 bg-muted/20 border border-border/50 rounded-xl hover:bg-muted/40 transition-colors"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                                            {update.day}d
                                        </div>
                                        <div className="font-mono font-bold text-foreground">
                                            {update.value}
                                        </div>
                                    </div>
                                    <div className="text-[10px] text-muted-foreground font-medium uppercase">
                                        {new Date(update.date).toLocaleDateString()}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="p-8 text-center border-2 border-dashed border-border/50 rounded-xl">
                                <Activity className="w-8 h-8 text-muted-foreground mx-auto mb-2 opacity-50" />
                                <div className="text-xs text-muted-foreground">No data points recorded yet.</div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default TabScoreboard
