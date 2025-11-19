import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Clock, Scale, Tweak, X, CheckCircle2, TrendingUp, AlertCircle } from 'lucide-react'
import { cn } from '../utils/cn'

const moves = [
  {
    id: 1,
    name: 'Launch Product Beta',
    progress: 75,
    velocity: 8.5,
    blockers: 2,
    recommendation: 'scale',
  },
  {
    id: 2,
    name: 'Acquire 100 Customers',
    progress: 45,
    velocity: 4.2,
    blockers: 5,
    recommendation: 'tweak',
  },
  {
    id: 3,
    name: 'Build ICP Database',
    progress: 90,
    velocity: 9.1,
    blockers: 0,
    recommendation: 'scale',
  },
  {
    id: 4,
    name: 'Implement Analytics Dashboard',
    progress: 60,
    velocity: 6.8,
    blockers: 1,
    recommendation: 'scale',
  },
]

export default function WeeklyReview() {
  const [selectedMoves, setSelectedMoves] = useState({})
  const [reviewNotes, setReviewNotes] = useState({})

  const handleDecision = (moveId, decision) => {
    setSelectedMoves({ ...selectedMoves, [moveId]: decision })
  }

  const handleComplete = () => {
    // Handle review completion
    alert('Weekly review completed!')
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900 p-12 text-white"
      >
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
              <Clock className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-4xl font-display font-bold mb-2">Weekly Review</h1>
              <p className="text-neutral-300 text-lg">
                Review your moves and make strategic decisions
              </p>
            </div>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-accent-500/20 rounded-full blur-3xl" />
      </motion.div>

      {/* Instructions */}
      <div className="glass rounded-2xl p-6 bg-primary-50 border-primary-200">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-neutral-900 mb-2">Review Process</h3>
            <p className="text-neutral-700">
              For each move, review the metrics and decide: <strong>Scale</strong> (double down), 
              <strong> Tweak</strong> (adjust approach), or <strong>Kill</strong> (stop and redirect resources).
            </p>
          </div>
        </div>
      </div>

      {/* Moves Review */}
      <div className="space-y-6">
        {moves.map((move, index) => {
          const decision = selectedMoves[move.id]
          const notes = reviewNotes[move.id] || ''

          return (
            <motion.div
              key={move.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-8"
            >
              {/* Move Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-neutral-900 mb-2">{move.name}</h3>
                  <div className="flex items-center gap-6 text-sm text-neutral-600">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      Progress: {move.progress}%
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      Velocity: {move.velocity}
                    </div>
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      Blockers: {move.blockers}
                    </div>
                  </div>
                </div>
                {decision && (
                  <div className={cn(
                    "px-4 py-2 rounded-xl font-medium",
                    decision === 'scale' 
                      ? "bg-green-100 text-green-700"
                      : decision === 'tweak'
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                  )}>
                    {decision === 'scale' ? 'Scale' : decision === 'tweak' ? 'Tweak' : 'Kill'}
                  </div>
                )}
              </div>

              {/* Progress Bar */}
              <div className="mb-6">
                <div className="w-full h-3 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${move.progress}%` }}
                    transition={{ duration: 1, delay: index * 0.2 }}
                    className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
                  />
                </div>
              </div>

              {/* Decision Buttons */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                {[
                  { id: 'scale', label: 'Scale', icon: TrendingUp, color: 'green' },
                  { id: 'tweak', label: 'Tweak', icon: Scale, color: 'yellow' },
                  { id: 'kill', label: 'Kill', icon: X, color: 'red' },
                ].map((option) => {
                  const Icon = option.icon
                  const isSelected = decision === option.id
                  return (
                    <motion.button
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleDecision(move.id, option.id)}
                      className={cn(
                        "p-6 rounded-xl border-2 font-semibold transition-all flex flex-col items-center gap-3",
                        isSelected
                          ? option.color === 'green'
                            ? "border-green-500 bg-green-50 text-green-700"
                            : option.color === 'yellow'
                            ? "border-yellow-500 bg-yellow-50 text-yellow-700"
                            : "border-red-500 bg-red-50 text-red-700"
                          : "border-neutral-200 hover:border-neutral-300 text-neutral-700"
                      )}
                    >
                      <Icon className="w-8 h-8" />
                      <span>{option.label}</span>
                    </motion.button>
                  )
                })}
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Review Notes
                </label>
                <textarea
                  rows={3}
                  placeholder="Add your thoughts and reasoning for this decision..."
                  value={notes}
                  onChange={(e) => setReviewNotes({ ...reviewNotes, [move.id]: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                />
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Complete Review */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-end"
      >
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleComplete}
          disabled={Object.keys(selectedMoves).length !== moves.length}
          className={cn(
            "flex items-center gap-2 px-8 py-4 rounded-xl font-semibold transition-all",
            Object.keys(selectedMoves).length === moves.length
              ? "bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/20"
              : "bg-neutral-200 text-neutral-400 cursor-not-allowed"
          )}
        >
          <CheckCircle2 className="w-5 h-5" />
          Complete Weekly Review
        </motion.button>
      </motion.div>
    </div>
  )
}

