import { useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Calendar, 
  CheckCircle2, 
  Clock, 
  Target,
  ArrowRight,
  PlayCircle
} from 'lucide-react'
import { cn } from '../utils/cn'
import { MoveStatus } from '../utils/moveSystemTypes'

// Mock daily tasks grouped by Move
const mockDailyTasks = [
  {
    move_id: 'move-1',
    move_name: 'Authority Sprint – Enterprise CTOs',
    move_status: MoveStatus.OODA_ACT,
    sprint_dates: '12–26 Apr',
    day_progress: 'Day 3/14',
    tasks: [
      { id: 'task-1', text: 'Approve LI post #1 draft', status: 'pending', due: 'Today' },
      { id: 'task-2', text: 'Record 90s security risk video', status: 'pending', due: 'Today' },
      { id: 'task-3', text: 'Review analytics snapshot', status: 'complete', due: 'Today' }
    ]
  },
  {
    move_id: 'move-2',
    move_name: 'Garrison – High-Value Accounts',
    move_status: MoveStatus.OODA_ACT,
    sprint_dates: '12–26 Apr',
    day_progress: 'Triggered',
    tasks: [
      { id: 'task-4', text: 'Review 4 at-risk accounts flagged yesterday', status: 'pending', due: 'Today' },
      { id: 'task-5', text: 'Send personal loom to ACME Corp', status: 'pending', due: 'Today' }
    ]
  },
  {
    move_id: 'move-3',
    move_name: 'Asset Forge – Security Proof Pack',
    move_status: MoveStatus.OODA_DECIDE,
    sprint_dates: '12–26 Apr',
    day_progress: 'Day 5/7',
    tasks: [
      { id: 'task-6', text: 'Upload latest uptime graph', status: 'pending', due: 'Today' },
      { id: 'task-7', text: 'Tag asset to this Move', status: 'pending', due: 'Today' }
    ]
  }
]

export default function Today() {
  const [tasks] = useState(mockDailyTasks)

  const totalTasks = tasks.reduce((sum, move) => sum + move.tasks.length, 0)
  const completedTasks = tasks.reduce((sum, move) => 
    sum + move.tasks.filter(t => t.status === 'complete').length, 0
  )

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <span className="micro-label tracking-[0.5em]">Daily Ops</span>
            <span className="h-px w-16 bg-neutral-200" />
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-400">Today's Checklist</span>
          </div>
          <div className="space-y-4">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              What do I do today?
            </h1>
            <p className="font-sans text-base text-neutral-600 max-w-2xl leading-relaxed">
              Every checkbox rolls up into some Move in some Line. Grouped by Move, not random tasks.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="runway-card p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 border-2 border-neutral-200 bg-white flex items-center justify-center">
              <Target className="w-6 h-6 text-neutral-900" />
            </div>
            <div>
              <div className="text-3xl font-bold text-neutral-900">{tasks.length}</div>
              <div className="text-sm text-neutral-600">Moves in Play</div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="runway-card p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 border-2 border-neutral-200 bg-white flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <div className="text-3xl font-bold text-neutral-900">
                {completedTasks} / {totalTasks}
              </div>
              <div className="text-sm text-neutral-600">Tasks Complete</div>
            </div>
          </div>
          <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(completedTasks / totalTasks) * 100}%` }}
              transition={{ duration: 1, delay: 0.3 }}
              className="h-full bg-green-600 rounded-full"
            />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="runway-card p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 border-2 border-neutral-200 bg-white flex items-center justify-center">
              <Clock className="w-6 h-6 text-neutral-900" />
            </div>
            <div>
              <div className="text-3xl font-bold text-neutral-900">
                {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </div>
              <div className="text-sm text-neutral-600">Today</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Moves with Tasks */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-neutral-900">Today's Operations</h2>
        
        {tasks.map((moveGroup, moveIndex) => (
          <motion.div
            key={moveGroup.move_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: moveIndex * 0.1 }}
            className="runway-card p-6"
          >
            {/* Move Header */}
            <div className="flex items-start justify-between mb-4 pb-4 border-b border-neutral-200">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <PlayCircle className="w-5 h-5 text-blue-600" />
                  <Link
                    to={`/moves/${moveGroup.move_id}`}
                    className="text-lg font-bold text-neutral-900 hover:underline"
                  >
                    {moveGroup.move_name}
                  </Link>
                </div>
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <span>Sprint: {moveGroup.sprint_dates}</span>
                  <span>•</span>
                  <span>{moveGroup.day_progress}</span>
                </div>
              </div>
              <span className={cn(
                "px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border rounded",
                moveGroup.move_status === MoveStatus.OODA_ACT
                  ? "bg-blue-100 text-blue-900 border-blue-200"
                  : "bg-yellow-100 text-yellow-900 border-yellow-200"
              )}>
                {moveGroup.move_status}
              </span>
            </div>

            {/* Tasks */}
            <div className="space-y-3">
              {moveGroup.tasks.map((task, taskIndex) => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: (moveIndex * 0.1) + (taskIndex * 0.05) }}
                  className={cn(
                    "flex items-start gap-3 p-4 rounded-lg border transition-colors",
                    task.status === 'complete'
                      ? "bg-green-50 border-green-200"
                      : "bg-neutral-50 border-neutral-200 hover:bg-neutral-100"
                  )}
                >
                  <button className={cn(
                    "w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors",
                    task.status === 'complete'
                      ? "bg-green-600 border-green-600"
                      : "border-neutral-300 hover:border-neutral-900"
                  )}>
                    {task.status === 'complete' && (
                      <CheckCircle2 className="w-4 h-4 text-white" />
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className={cn(
                      "text-sm font-medium",
                      task.status === 'complete'
                        ? "text-green-900 line-through"
                        : "text-neutral-900"
                    )}>
                      {task.text}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <Clock className="w-3 h-3 text-neutral-400" />
                      <span className="text-xs text-neutral-600">{task.due}</span>
                    </div>
                  </div>
                  <Link
                    to={`/moves/${moveGroup.move_id}`}
                    className="text-neutral-400 hover:text-neutral-900 transition-colors"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {tasks.length === 0 && (
        <div className="runway-card p-12 text-center">
          <Calendar className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-neutral-900 mb-2">No tasks for today</h3>
          <p className="text-sm text-neutral-600 mb-6">
            All caught up! Check the War Room to see upcoming moves.
          </p>
          <Link
            to="/moves/war-room"
            className="inline-flex items-center gap-2 border border-neutral-900 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-colors"
          >
            Go to War Room
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}
    </div>
  )
}


