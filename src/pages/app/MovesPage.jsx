import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  Zap,
  Clock,
  Target,
  ChevronRight,
  Play,
  BarChart3,
  Sparkles,
  BookOpen
} from 'lucide-react'
import useRaptorflowStore from '../../store/raptorflowStore'
import { PROBLEM_TYPES, FRAMEWORK_CONFIGS } from '../../data/frameworkConfigs'
import { BrandIcon } from '@/components/brand/BrandSystem'
import MoveDetail from './moves/MoveDetail'

/**
 * MovesPage - Home for the Moves section
 * 
 * Shows:
 * - Today's priority task card
 * - Active moves grid
 * - Quick start templates
 */

// Status badge component
const StatusBadge = ({ status }) => {
  const styles = {
    active: 'bg-emerald-50 text-emerald-600 border border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800 dark:text-emerald-400',
    generating: 'bg-amber-50 text-amber-600 border border-amber-200 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-400',
    pending: 'bg-muted text-muted-foreground border border-border',
    completed: 'bg-primary/5 text-primary border border-primary/20',
    paused: 'bg-muted text-muted-foreground border border-border'
  }

  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wider font-semibold ${styles[status] || styles.pending}`}>
      {status}
    </span>
  )
}

// Move card for the grid
const MoveCard = ({ move, onClick }) => {
  const { getMoveDayNumber, getCampaign } = useRaptorflowStore()

  const completedTasks = (move.checklistItems || []).filter(t => t.done).length
  const totalTasks = (move.checklistItems || []).length
  const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
  const currentDay = getMoveDayNumber ? getMoveDayNumber(move.id) : 1
  const totalDays = move.durationDays || 14

  const problem = move.problemType ? PROBLEM_TYPES[move.problemType] : null
  const framework = move.frameworkId ? FRAMEWORK_CONFIGS[move.frameworkId] : null

  return (
    <motion.button
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.99 }}
      onClick={onClick}
      className="w-full text-left p-6 bg-card border border-border/60 rounded-2xl hover:border-primary/40 hover:shadow-glow transition-all group relative overflow-hidden"
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none group-hover:bg-primary/10 transition-colors" />

      <div className="flex items-start justify-between mb-4 relative z-10">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/10 flex items-center justify-center flex-shrink-0 shadow-sm">
            <BrandIcon name="speed" size={22} className="text-primary" />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-serif text-lg text-foreground leading-tight mb-1 group-hover:text-primary transition-colors line-clamp-2">
              {move.name || 'Untitled Move'}
            </h3>
            {framework && (
              <p className="text-xs text-muted-foreground truncate font-medium">
                {framework.name}
              </p>
            )}
          </div>
        </div>
        <div className="flex-shrink-0 ml-3">
          <StatusBadge status={move.status} />
        </div>
      </div>

      {/* Target/Goal section */}
      {problem && (
        <div className="mb-5 relative z-10">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/50 border border-border/50">
            <Target className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-xs text-foreground/80 font-medium truncate max-w-[200px]">
              {problem.statement}
            </span>
          </div>
        </div>
      )}

      {/* Stats row */}
      <div className="flex items-center justify-between text-xs text-muted-foreground mb-3 relative z-10">
        <div className="flex items-center gap-1.5 font-medium">
          <Clock className="w-3.5 h-3.5" strokeWidth={2} />
          <span>Day {currentDay}</span>
          <span className="text-muted-foreground/50">/</span>
          <span>{totalDays}</span>
        </div>
        <div className="font-medium">
          {progress}% complete
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-muted/60 rounded-full overflow-hidden relative z-10">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          className="h-full bg-gradient-to-r from-primary to-primary/80 rounded-full"
        />
      </div>
    </motion.button>
  )
}

// Today's task card
const TodayCard = ({ move, task }) => {
  const navigate = useNavigate()
  const framework = move.frameworkId ? FRAMEWORK_CONFIGS[move.frameworkId] : null

  if (!task) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="group relative overflow-hidden rounded-3xl border border-primary/20 bg-gradient-to-b from-primary/5 to-transparent p-1"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />

      <div className="relative bg-card/50 backdrop-blur-sm rounded-[22px] p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider shadow-sm border border-primary/10">
                <Sparkles className="w-3 h-3" strokeWidth={2} />
                Today's Focus
              </span>
              <span className="text-xs text-muted-foreground font-medium px-2 py-0.5 rounded bg-muted/50 border border-border">
                {move.name}
              </span>
            </div>

            <h2 className="font-serif text-3xl md:text-4xl text-foreground mb-4 leading-tight">
              {task.text}
            </h2>

            <div className="flex items-center gap-6 text-sm">
              {task.duration && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                    <Clock className="w-4 h-4" />
                  </div>
                  <span className="font-medium">{task.duration} min</span>
                </div>
              )}
              {framework && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                    <Zap className="w-4 h-4" />
                  </div>
                  <span className="font-medium">{framework.name}</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex-shrink-0">
            <button
              onClick={() => navigate(`/app/moves/${move.id}/today`)}
              className="group/btn relative flex items-center gap-3 px-8 py-4 bg-primary text-primary-foreground rounded-2xl text-base font-semibold hover:shadow-lg hover:shadow-primary/25 transition-all w-full md:w-auto overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover/btn:translate-x-[100%] transition-transform duration-700" />
              <span>Start Task</span>
              <ChevronRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" strokeWidth={2} />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// Quick start templates
const QUICK_TEMPLATES = [
  {
    id: 'conversion',
    name: 'Convert More Leads',
    description: '7-day conversion blitz',
    problem: 'conversion',
    icon: 'results'
  },
  {
    id: 'awareness',
    name: 'Build Awareness',
    description: '14-day authority play',
    problem: 'awareness',
    icon: 'target'
  },
  {
    id: 'launch',
    name: 'Launch Something',
    description: '7-day launch sprint',
    problem: 'launch',
    icon: 'launch'
  }
]

// Moves home (list view)
const MovesHome = () => {
  const navigate = useNavigate()
  const { moves, getMoveDayNumber, getMoveTasksForDay } = useRaptorflowStore()

  const activeMoves = moves.filter(m => m.status === 'active')
  const completedMoves = moves.filter(m => m.status === 'completed')

  // Find today's #1 task from the highest priority move
  const todayTask = activeMoves.length > 0 ? (() => {
    const move = activeMoves[0]
    const currentDay = getMoveDayNumber ? getMoveDayNumber(move.id) : 1
    const tasks = getMoveTasksForDay ? getMoveTasksForDay(move.id, currentDay) : []
    const incompleteTask = tasks.find(t => !t.done) || (move.checklistItems || []).find(t => !t.done)
    return incompleteTask ? { move, task: incompleteTask } : null
  })() : null

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="font-serif text-3xl text-foreground mb-2">Moves</h1>
          <p className="text-muted-foreground">
            One problem. One outcome. 7–30 days.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/app/moves/library')}
            className="flex items-center gap-2 px-4 py-2.5 text-sm text-muted-foreground hover:text-foreground border border-border rounded-xl hover:border-primary/30 transition-colors"
          >
            <BookOpen className="w-4 h-4" strokeWidth={1.5} />
            Library
          </button>
          <button
            onClick={() => navigate('/app/moves/new/1')}
            className="flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" strokeWidth={1.5} />
            New Move
          </button>
        </div>
      </div>

      {/* Today's task */}
      {todayTask && (
        <TodayCard move={todayTask.move} task={todayTask.task} />
      )}

      {/* Active moves */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-serif text-lg text-foreground">Active Moves</h2>
          <span className="text-sm text-muted-foreground">{activeMoves.length} running</span>
        </div>

        {activeMoves.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeMoves.map((move, idx) => (
              <motion.div
                key={move.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <MoveCard
                  move={move}
                  onClick={() => navigate(`/app/moves/${move.id}`)}
                />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-muted/30 border border-dashed border-border rounded-2xl">
            <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center mx-auto mb-4">
              <Zap className="w-8 h-8 text-muted-foreground" strokeWidth={1.5} />
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">No active moves</h3>
            <p className="text-sm text-muted-foreground mb-4 max-w-md mx-auto">
              Create your first move to start executing with focus.
            </p>
            <button
              onClick={() => navigate('/app/moves/new/1')}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity"
            >
              <Plus className="w-4 h-4" strokeWidth={1.5} />
              Create Move
            </button>
          </div>
        )}
      </section>

      {/* Quick start templates */}
      <section className="mb-10">
        <h2 className="font-serif text-lg text-foreground mb-4">Quick Start</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {QUICK_TEMPLATES.map((template, idx) => (
            <motion.button
              key={template.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => navigate(`/app/moves/new/1?problem=${template.problem}`)}
              className="flex items-center gap-4 p-5 bg-card border border-border rounded-2xl text-left hover:border-primary/30 transition-colors group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
                <BrandIcon name={template.icon} size={24} className="text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-foreground group-hover:text-primary transition-colors">
                  {template.name}
                </h3>
                <p className="text-sm text-muted-foreground">{template.description}</p>
              </div>
              <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" strokeWidth={1.5} />
            </motion.button>
          ))}
        </div>
      </section>

      {/* Completed moves */}
      {completedMoves.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-serif text-lg text-foreground">Completed</h2>
            <span className="text-sm text-muted-foreground">{completedMoves.length} finished</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedMoves.slice(0, 6).map((move) => (
              <MoveCard
                key={move.id}
                move={move}
                onClick={() => navigate(`/app/moves/${move.id}`)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

// Main MovesPage with routing
const MovesPage = () => {
  const { id, tab } = useParams()

  // If we have an ID, show the detail view
  if (id && id !== 'new' && id !== 'library') {
    return <MoveDetail />
  }

  // Otherwise show the home view
  return <MovesHome />
}

export default MovesPage
