import { useState } from 'react'
import { motion } from 'framer-motion'
import {
    TrendingUp,
    TrendingDown,
    Target,
    Plus,
    BarChart3
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'

/**
 * Scoreboard Tab - Results That Matter
 * 
 * Shows:
 * - Primary KPI big number with delta
 * - Leading indicators with trends
 * - Daily log input for manual tracking
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
        <div className="max-w-3xl mx-auto">
            {/* Primary KPI */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-primary/5 border-2 border-primary/20 rounded-2xl p-8 mb-6"
            >
                <div className="flex items-start justify-between mb-4">
                    <div>
                        <div className="text-sm text-muted-foreground mb-1">Primary KPI</div>
                        <h2 className="font-serif text-xl text-foreground">
                            {tracking.metric || framework?.metrics?.primary?.name || 'Win Condition'}
                        </h2>
                    </div>

                    <div className={`
            flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium
            ${isPositive
                            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                            : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                        }
          `}>
                        {isPositive ? (
                            <TrendingUp className="w-4 h-4" strokeWidth={1.5} />
                        ) : (
                            <TrendingDown className="w-4 h-4" strokeWidth={1.5} />
                        )}
                        {isPositive ? '+' : ''}{deltaPercent}%
                    </div>
                </div>

                {/* Big number */}
                <div className="flex items-end gap-4 mb-6">
                    <div className="text-6xl font-bold text-foreground">
                        {currentValue}
                    </div>
                    <div className="pb-2">
                        <span className="text-muted-foreground">/ </span>
                        <span className="text-2xl text-muted-foreground">{target}</span>
                        <span className="text-sm text-muted-foreground ml-1">target</span>
                    </div>
                </div>

                {/* Progress bar */}
                <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-muted-foreground">Progress to target</span>
                        <span className="font-medium text-foreground">{progress}%</span>
                    </div>
                    <div className="h-3 bg-muted rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            className="h-full bg-primary rounded-full"
                        />
                    </div>
                </div>

                {/* Baseline vs Current */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-primary/20">
                    <div>
                        <div className="text-xs text-muted-foreground mb-1">Baseline</div>
                        <div className="text-lg font-medium text-foreground">{baseline}</div>
                    </div>
                    <div>
                        <div className="text-xs text-muted-foreground mb-1">Current</div>
                        <div className="text-lg font-medium text-foreground">{currentValue}</div>
                    </div>
                    <div>
                        <div className="text-xs text-muted-foreground mb-1">Change</div>
                        <div className={`text-lg font-medium ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                            {isPositive ? '+' : ''}{delta}
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Log update */}
            <div className="bg-card border border-border rounded-xl p-4 mb-6">
                <h3 className="text-sm font-medium text-foreground mb-3">Log today's number</h3>
                <div className="flex gap-3">
                    <input
                        type="number"
                        value={newValue}
                        onChange={(e) => setNewValue(e.target.value)}
                        placeholder={`Enter ${tracking.metric || 'value'}`}
                        className="flex-1 px-4 py-2.5 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    />
                    <button
                        onClick={handleLogUpdate}
                        disabled={!newValue}
                        className="flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                    >
                        <Plus className="w-4 h-4" strokeWidth={1.5} />
                        Log
                    </button>
                </div>
            </div>

            {/* Leading indicators */}
            <div className="mb-6">
                <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                    Leading Indicators
                </h3>
                <div className="grid grid-cols-2 gap-3">
                    {leadingIndicators.map((indicator, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="p-4 bg-card border border-border rounded-xl"
                        >
                            <div className="text-sm text-foreground mb-1">{indicator.name}</div>
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-muted-foreground">Target: {indicator.target}</span>
                                <span className="text-xs text-muted-foreground">--</span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Update history */}
            {updates.length > 0 && (
                <div>
                    <h3 className="text-sm font-medium text-foreground mb-3">History</h3>
                    <div className="space-y-2">
                        {updates.slice().reverse().slice(0, 7).map((update, idx) => (
                            <div
                                key={idx}
                                className="flex items-center justify-between p-3 bg-muted/50 border border-border rounded-xl"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="text-sm text-foreground font-medium">{update.value}</div>
                                    <div className="text-xs text-muted-foreground">
                                        Day {update.day}
                                    </div>
                                </div>
                                <div className="text-xs text-muted-foreground">
                                    {new Date(update.date).toLocaleDateString()}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Empty state for no updates */}
            {updates.length === 0 && (
                <div className="text-center py-8 text-sm text-muted-foreground">
                    No updates logged yet. Start tracking your progress above.
                </div>
            )}
        </div>
    )
}

export default TabScoreboard
