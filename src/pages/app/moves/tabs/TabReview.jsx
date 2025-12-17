import { useState } from 'react'
import { motion } from 'framer-motion'
import {
    Flag,
    CheckCircle,
    AlertTriangle,
    ChevronRight,
    MessageSquare,
    FileText,
    Save
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'

/**
 * Review Tab - Checkpoints + After-Action Review
 * 
 * Shows:
 * - Day 3 checkpoint (mandatory)
 * - Midpoint checkpoint
 * - End-of-move AAR report
 */

const CheckpointCard = ({ checkpoint, move, onComplete }) => {
    const [answers, setAnswers] = useState({
        onTrack: null,
        blocker: '',
        fix: ''
    })

    const isComplete = checkpoint.data?.completed

    return (
        <div className={`
      p-6 rounded-2xl border-2 transition-all
      ${isComplete
                ? 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800'
                : 'bg-card border-border'
            }
    `}>
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`
            w-10 h-10 rounded-xl flex items-center justify-center
            ${isComplete
                            ? 'bg-emerald-500 text-white'
                            : 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400'
                        }
          `}>
                        {isComplete ? (
                            <CheckCircle className="w-5 h-5" strokeWidth={2} />
                        ) : (
                            <Flag className="w-5 h-5" strokeWidth={1.5} />
                        )}
                    </div>
                    <div>
                        <h3 className="font-medium text-foreground">{checkpoint.name}</h3>
                        <p className="text-sm text-muted-foreground">Day {checkpoint.day}</p>
                    </div>
                </div>

                {isComplete && (
                    <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 text-xs font-medium">
                        Complete
                    </span>
                )}
            </div>

            {!isComplete && (
                <div className="space-y-4">
                    {/* On track question */}
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                            Are we on track?
                        </label>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setAnswers({ ...answers, onTrack: true })}
                                className={`
                  flex-1 py-3 rounded-xl text-sm font-medium transition-all
                  ${answers.onTrack === true
                                        ? 'bg-emerald-500 text-white'
                                        : 'bg-muted text-muted-foreground hover:bg-muted/80'
                                    }
                `}
                            >
                                Yes
                            </button>
                            <button
                                onClick={() => setAnswers({ ...answers, onTrack: false })}
                                className={`
                  flex-1 py-3 rounded-xl text-sm font-medium transition-all
                  ${answers.onTrack === false
                                        ? 'bg-amber-500 text-white'
                                        : 'bg-muted text-muted-foreground hover:bg-muted/80'
                                    }
                `}
                            >
                                Not quite
                            </button>
                        </div>
                    </div>

                    {/* Blocker question */}
                    {answers.onTrack === false && (
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                What's the biggest blocker?
                            </label>
                            <select
                                value={answers.blocker}
                                onChange={(e) => setAnswers({ ...answers, blocker: e.target.value })}
                                className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                            >
                                <option value="">Select...</option>
                                <option value="time">Not enough time</option>
                                <option value="content">Content not ready</option>
                                <option value="unclear">Strategy unclear</option>
                                <option value="technical">Technical issues</option>
                                <option value="other">Something else</option>
                            </select>
                        </div>
                    )}

                    {/* Fix */}
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                            One change to make now
                        </label>
                        <input
                            type="text"
                            value={answers.fix}
                            onChange={(e) => setAnswers({ ...answers, fix: e.target.value })}
                            placeholder="What will you adjust?"
                            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                        />
                    </div>

                    <button
                        onClick={() => onComplete(checkpoint.type, answers)}
                        disabled={answers.onTrack === null}
                        className="w-full py-3 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                    >
                        Complete Checkpoint
                    </button>
                </div>
            )}

            {isComplete && checkpoint.data && (
                <div className="space-y-3 pt-4 border-t border-emerald-200 dark:border-emerald-800">
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Status:</span>
                        <span className={`text-sm font-medium ${checkpoint.data.onTrack ? 'text-emerald-600' : 'text-amber-600'}`}>
                            {checkpoint.data.onTrack ? 'On Track' : 'Adjusting'}
                        </span>
                    </div>
                    {checkpoint.data.fix && (
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">Action:</span>
                            <span className="text-sm text-foreground">{checkpoint.data.fix}</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

const AARForm = ({ move, onComplete }) => {
    const [aar, setAAR] = useState({
        outcome: '',
        whatWorked: '',
        whatDidnt: '',
        bestChannel: '',
        bestAsset: '',
        nextMove: ''
    })

    return (
        <div className="p-6 bg-card border border-border rounded-2xl">
            <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-purple-600 dark:text-purple-400" strokeWidth={1.5} />
                </div>
                <div>
                    <h3 className="font-medium text-foreground">After-Action Review</h3>
                    <p className="text-sm text-muted-foreground">End-of-move analysis</p>
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                        Overall outcome
                    </label>
                    <select
                        value={aar.outcome}
                        onChange={(e) => setAAR({ ...aar, outcome: e.target.value })}
                        className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                    >
                        <option value="">Select...</option>
                        <option value="exceeded">Exceeded target</option>
                        <option value="met">Met target</option>
                        <option value="close">Close to target</option>
                        <option value="missed">Missed target</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                        What worked best?
                    </label>
                    <textarea
                        value={aar.whatWorked}
                        onChange={(e) => setAAR({ ...aar, whatWorked: e.target.value })}
                        placeholder="Describe what drove results"
                        rows={3}
                        className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                        What didn't work?
                    </label>
                    <textarea
                        value={aar.whatDidnt}
                        onChange={(e) => setAAR({ ...aar, whatDidnt: e.target.value })}
                        placeholder="What would you skip next time?"
                        rows={3}
                        className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                            Best channel
                        </label>
                        <input
                            type="text"
                            value={aar.bestChannel}
                            onChange={(e) => setAAR({ ...aar, bestChannel: e.target.value })}
                            placeholder="e.g., LinkedIn"
                            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                            Best asset
                        </label>
                        <input
                            type="text"
                            value={aar.bestAsset}
                            onChange={(e) => setAAR({ ...aar, bestAsset: e.target.value })}
                            placeholder="e.g., Case study"
                            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                        What's the next move?
                    </label>
                    <input
                        type="text"
                        value={aar.nextMove}
                        onChange={(e) => setAAR({ ...aar, nextMove: e.target.value })}
                        placeholder="What would you run next?"
                        className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                    />
                </div>

                <button
                    onClick={() => onComplete(aar)}
                    className="w-full flex items-center justify-center gap-2 py-3 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity"
                >
                    <Save className="w-4 h-4" strokeWidth={1.5} />
                    Save to Playbook
                </button>
            </div>
        </div>
    )
}

const TabReview = ({ move, framework, currentDay, totalDays }) => {
    const { updateMoveCheckpoint, completeMove } = useRaptorflowStore()

    const checkpoints = move.checkpoints || {}

    // Define checkpoint schedule
    const checkpointSchedule = [
        {
            type: 'day3',
            name: 'Day 3 Check',
            day: 3,
            data: checkpoints.day3,
            description: 'Early pulse check - are we on track?'
        },
        {
            type: 'midpoint',
            name: 'Midpoint Review',
            day: Math.floor(totalDays / 2),
            data: checkpoints.midpoint,
            description: 'Halfway through - time to adjust'
        }
    ].filter(c => c.day <= totalDays)

    const showAAR = currentDay >= totalDays || move.status === 'completed'

    const handleCheckpointComplete = (type, answers) => {
        if (updateMoveCheckpoint) {
            updateMoveCheckpoint(move.id, type, {
                ...answers,
                completed: true,
                completedAt: new Date().toISOString()
            })
        }
    }

    const handleAARComplete = (aar) => {
        if (completeMove) {
            completeMove(move.id, {
                aar,
                completedAt: new Date().toISOString()
            })
        }
    }

    return (
        <div className="max-w-2xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <h2 className="text-lg font-medium text-foreground mb-1">Reviews & Checkpoints</h2>
                <p className="text-sm text-muted-foreground">
                    Mandatory checkpoints to keep your move on track
                </p>
            </div>

            {/* Checkpoints */}
            <div className="space-y-4 mb-8">
                {checkpointSchedule.map((checkpoint, idx) => {
                    const isUnlocked = currentDay >= checkpoint.day

                    if (!isUnlocked) {
                        return (
                            <div
                                key={checkpoint.type}
                                className="p-6 rounded-2xl border border-dashed border-border bg-muted/30"
                            >
                                <div className="flex items-center gap-3 opacity-50">
                                    <div className="w-10 h-10 rounded-xl bg-muted flex items-center justify-center">
                                        <Flag className="w-5 h-5 text-muted-foreground" strokeWidth={1.5} />
                                    </div>
                                    <div>
                                        <h3 className="font-medium text-foreground">{checkpoint.name}</h3>
                                        <p className="text-sm text-muted-foreground">
                                            Unlocks on Day {checkpoint.day}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )
                    }

                    return (
                        <motion.div
                            key={checkpoint.type}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                        >
                            <CheckpointCard
                                checkpoint={checkpoint}
                                move={move}
                                onComplete={handleCheckpointComplete}
                            />
                        </motion.div>
                    )
                })}
            </div>

            {/* After-Action Review */}
            {showAAR && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <AARForm move={move} onComplete={handleAARComplete} />
                </motion.div>
            )}

            {!showAAR && (
                <div className="p-6 rounded-2xl border border-dashed border-border bg-muted/30 text-center">
                    <FileText className="w-8 h-8 text-muted-foreground mx-auto mb-2" strokeWidth={1.5} />
                    <h3 className="font-medium text-foreground mb-1">After-Action Review</h3>
                    <p className="text-sm text-muted-foreground">
                        Available when the move is complete
                    </p>
                </div>
            )}
        </div>
    )
}

export default TabReview
