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
import {
  HeroSection,
  LuxeCard,
  LuxeBadge,
  EmptyState,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI'

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

const getPhaseLabel = (status) => {
  const phase = status.replace('OODA_', '').toLowerCase()
  if (phase === 'act') return 'Act'
  if (phase === 'decide') return 'Decide'
  if (phase === 'orient') return 'Orient'
  return phase.charAt(0).toUpperCase() + phase.slice(1)
}

export default function Today() {
  const [tasks] = useState(mockDailyTasks)

  const totalTasks = tasks.reduce((sum, move) => sum + move.tasks.length, 0)
  const completedTasks = tasks.reduce((sum, move) =>
    sum + move.tasks.filter(t => t.status === 'complete').length, 0
  )

  return (
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {/* Header */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Today's Operations"
          subtitle="Every task rolls up into a Move. Grouped by Move, not random tasks."
          metrics={[
            { label: 'Moves Active', value: tasks.length.toString() },
            { label: 'Tasks', value: `${completedTasks}/${totalTasks}` },
            { label: 'Date', value: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }
          ]}
        />
      </motion.div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-neutral-100 flex items-center justify-center">
                <Target className="w-6 h-6 text-neutral-900" />
              </div>
              <div>
                <div className="text-3xl font-display font-medium text-neutral-900">{tasks.length}</div>
                <div className="text-sm text-neutral-600">Moves in Play</div>
              </div>
            </div>
          </LuxeCard>
        </motion.div>

        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <div className="text-3xl font-display font-medium text-neutral-900">
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
                className="h-full bg-emerald-600 rounded-full"
              />
            </div>
          </LuxeCard>
        </motion.div>

        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <div className="text-3xl font-display font-medium text-neutral-900">
                  {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <div className="text-sm text-neutral-600">Today</div>
              </div>
            </div>
          </LuxeCard>
        </motion.div>
      </div>

      {/* Moves with Tasks */}
      {tasks.length > 0 ? (
        <div className="space-y-6">
          <h2 className="font-display text-xl font-medium text-neutral-900">Active Moves</h2>

          {tasks.map((moveGroup, moveIndex) => {
            const phaseLabel = getPhaseLabel(moveGroup.move_status)
            return (
              <motion.div
                key={moveGroup.move_id}
                variants={fadeInUp}
              >
                <LuxeCard className="p-6">
                  {/* Move Header */}
                  <div className="flex items-start justify-between mb-4 pb-4 border-b border-neutral-200">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <PlayCircle className="w-5 h-5 text-blue-600" />
                        <Link
                          to={`/moves/${moveGroup.move_id}`}
                          className="font-display text-lg font-medium text-neutral-900 hover:underline"
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
                    <LuxeBadge
                      variant={phaseLabel === 'Act' ? 'info' : 'warning'}
                      className="uppercase tracking-wider"
                    >
                      {phaseLabel}
                    </LuxeBadge>
                  </div>

                  {/* Tasks */}
                  <div className="space-y-3">
                    {moveGroup.tasks.map((task) => (
                      <div
                        key={task.id}
                        className={cn(
                          "flex items-start gap-3 p-4 rounded-xl border transition-colors",
                          task.status === 'complete'
                            ? "bg-emerald-50 border-emerald-200"
                            : "bg-neutral-50 border-neutral-200 hover:bg-neutral-100"
                        )}
                      >
                        <button className={cn(
                          "w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors",
                          task.status === 'complete'
                            ? "bg-emerald-600 border-emerald-600"
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
                              ? "text-emerald-900 line-through"
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
                      </div>
                    ))}
                  </div>
                </LuxeCard>
              </motion.div>
            )
          })}
        </div>
      ) : (
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-12">
            <EmptyState
              icon={Calendar}
              title="No tasks for today"
              description="All caught up! Check Moves to see upcoming work."
              action={
                <Link to="/moves">
                  <button className="inline-flex items-center gap-2 px-6 py-3 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 transition-colors">
                    Open Moves
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </Link>
              }
            />
          </LuxeCard>
        </motion.div>
      )}
    </motion.div>
  )
}
