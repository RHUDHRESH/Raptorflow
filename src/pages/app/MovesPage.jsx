import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  CheckCircle2,
  Circle,
  ChevronRight,
  Sparkles,
  Box,
  Zap,
  Clock,
  Target,
  FileText,
  Trash2,
  Play,
  Pause,
  MoreHorizontal,
  Link2,
  Unlink2,
  Send
} from 'lucide-react'
import { BrandIcon } from '@/components/brand/BrandSystem'
import useRaptorflowStore from '../../store/raptorflowStore'
import { Modal } from '@/components/system/Modal'
import PreFlightChecklistModal from '../../components/activity/PreFlightChecklistModal'

// Move status badge
const StatusBadge = ({ status }) => {
  const styles = {
    active: 'bg-emerald-50 text-emerald-600',
    generating: 'bg-paper-200 text-ink',
    pending: 'bg-amber-50 text-amber-600',
    completed: 'bg-primary/10 text-primary',
    paused: 'bg-ink-100 text-ink-400'
  }

  return (
    <span className={`px-2 py-1 rounded text-body-xs capitalize ${styles[status] || styles.pending}`}>
      {status}
    </span>
  )
}

const CreateStandaloneMoveModal = ({ open, onOpenChange, onCreate, initialValues }) => {
  const { campaigns } = useRaptorflowStore()
  const [name, setName] = useState('')
  const [campaignId, setCampaignId] = useState('')
  const [cohort, setCohort] = useState('')
  const [channel, setChannel] = useState('linkedin')
  const [durationDays, setDurationDays] = useState(7)
  const [metric, setMetric] = useState('engagement')

  useEffect(() => {
    if (!open) {
      setName('')
      setCampaignId('')
      setCohort('')
      setChannel('linkedin')
      setDurationDays(7)
      setMetric('engagement')
      return
    }

    if (!initialValues) return

    if (typeof initialValues.name === 'string') setName(initialValues.name)
    if (typeof initialValues.campaignId === 'string') setCampaignId(initialValues.campaignId)
    if (typeof initialValues.cohort === 'string') setCohort(initialValues.cohort)
    if (typeof initialValues.channel === 'string') setChannel(initialValues.channel)
    if (typeof initialValues.durationDays === 'number') setDurationDays(initialValues.durationDays)
    if (typeof initialValues.metric === 'string') setMetric(initialValues.metric)
  }, [initialValues, open])

  const handleCreate = () => {
    const trimmed = name.trim()
    if (!trimmed) return
    onCreate({
      name: trimmed,
      campaignId: campaignId || null,
      cohort: cohort || null,
      channel,
      durationDays: Number(durationDays || 7),
      metric,
    })
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="New move"
      description="Create a standalone move, or attach it to a campaign."
      contentClassName="max-w-xl"
    >
      <div className="p-6 space-y-4">
        <div>
          <label className="block text-body-xs text-ink-400 mb-1">Move name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Founder outreach sprint"
            className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        <div>
          <label className="block text-body-xs text-ink-400 mb-1">Attach to campaign (optional)</label>
          <select
            value={campaignId}
            onChange={(e) => setCampaignId(e.target.value)}
            className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          >
            <option value="">Standalone</option>
            {(campaigns || []).map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-body-xs text-ink-400 mb-1">Channel</label>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            >
              <option value="linkedin">LinkedIn</option>
              <option value="email">Email</option>
              <option value="twitter">X / Twitter</option>
              <option value="instagram">Instagram</option>
              <option value="youtube">YouTube</option>
            </select>
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-1">Duration (days)</label>
            <input
              type="number"
              value={durationDays}
              onChange={(e) => setDurationDays(Number(e.target.value || 7))}
              className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label className="block text-body-xs text-ink-400 mb-1">Success metric</label>
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          >
            <option value="engagement">Engagement</option>
            <option value="replies">Replies</option>
            <option value="leads">Leads</option>
            <option value="calls">Booked calls</option>
          </select>
        </div>

        <button
          onClick={handleCreate}
          disabled={!name.trim()}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial disabled:opacity-50"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          Create move
        </button>
      </div>
    </Modal>
  )
}

// Move card for list view
const MoveCard = ({ move, campaign, onClick }) => {
  const completedTasks = move.checklistItems.filter(t => t.done).length
  const totalTasks = move.checklistItems.length
  const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      onClick={onClick}
      className="p-5 bg-card border border-border rounded-xl cursor-pointer hover:border-border-dark transition-editorial group"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-signal-muted rounded-xl flex items-center justify-center">
            <BrandIcon name="speed" className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-serif text-lg text-ink group-hover:text-primary transition-editorial">
              {move.name}
            </h3>
            <p className="text-body-xs text-ink-400">{campaign?.name || 'No campaign'}</p>
          </div>
        </div>
        <StatusBadge status={move.status} />
      </div>

      {/* Meta info */}
      <div className="flex items-center gap-3 mb-4">
        <span className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400 capitalize">
          {move.channel}
        </span>
        <span className="flex items-center gap-1 text-body-xs text-ink-400">
          <Clock className="w-3.5 h-3.5" strokeWidth={1.5} />
          {move.durationDays}d
        </span>
        <span className="flex items-center gap-1 text-body-xs text-ink-400">
          <FileText className="w-3.5 h-3.5" strokeWidth={1.5} />
          {move.assets?.length || 0} assets
        </span>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-body-xs text-ink-400">{completedTasks}/{totalTasks} tasks</span>
          <span className="text-body-xs text-ink font-mono">{progress}%</span>
        </div>
        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="mt-4 flex items-center justify-end">
        <ChevronRight className="w-4 h-4 text-ink-400 opacity-0 group-hover:opacity-100 transition-editorial" strokeWidth={1.5} />
      </div>
    </motion.div>
  )
}

// Task item
const TaskItem = ({ task, onToggle, onDelete }) => (
  <motion.div
    initial={{ opacity: 0, x: -10 }}
    animate={{ opacity: 1, x: 0 }}
    className="flex items-start gap-3 p-3 bg-paper hover:bg-paper-200 rounded-xl border border-border-light transition-editorial group"
  >
    <button onClick={onToggle} className="mt-0.5 flex-shrink-0">
      {task.done ? (
        <CheckCircle2 className="w-5 h-5 text-primary" strokeWidth={1.5} />
      ) : (
        <Circle className="w-5 h-5 text-ink-300 group-hover:text-ink-400" strokeWidth={1.5} />
      )}
    </button>
    <span className={`flex-1 text-body-sm ${task.done ? 'text-ink-400 line-through' : 'text-ink'}`}>
      {task.text}
    </span>
    <button
      onClick={onDelete}
      className="opacity-0 group-hover:opacity-100 p-1 text-ink-400 hover:text-red-500 transition-editorial"
    >
      <Trash2 className="w-4 h-4" strokeWidth={1.5} />
    </button>
  </motion.div>
)

// Asset card
const AssetCard = ({ asset, onOpenMuse }) => (
  <div className="p-4 bg-paper-200 rounded-xl">
    <div className="flex items-center justify-between mb-2">
      <span className="text-body-xs text-ink-400 capitalize">{asset.type} • {asset.channel}</span>
      <span className="text-body-xs text-ink-400">
        {new Date(asset.createdAt).toLocaleDateString()}
      </span>
    </div>
    <pre className="whitespace-pre-wrap text-body-sm text-ink font-sans line-clamp-4 mb-3">
      {asset.content}
    </pre>
    <button
      onClick={onOpenMuse}
      className="text-body-xs text-primary hover:underline"
    >
      Edit in Muse →
    </button>
  </div>
)

// Move Detail View
const MoveDetail = ({ move }) => {
  const navigate = useNavigate()
  const {
    getCampaign,
    campaigns,
    toggleTaskDone,
    addTaskToMove,
    updateMove,
    getMoveDayNumber,
    getMoveTasksForDay,
    setTaskDay,
    attachProofToTask,
    addTrackingUpdate,
    completeMove,
    getAssetsByMove,
    openMuseDrawer,
    deleteMove,
    attachMoveToCampaign,
    detachMoveFromCampaign,
    addPipelineItem
  } = useRaptorflowStore()

  const campaign = getCampaign(move.campaignId)
  const assets = getAssetsByMove(move.id)
  const [newTask, setNewTask] = useState('')
  const [showMenu, setShowMenu] = useState(false)
  const [proofTaskId, setProofTaskId] = useState(null)
  const [proofUrl, setProofUrl] = useState('')
  const [proofNote, setProofNote] = useState('')
  const [trackingValue, setTrackingValue] = useState('')
  const [completionOutcome, setCompletionOutcome] = useState(move.result?.outcome || 'won')
  const [completionLearning, setCompletionLearning] = useState(move.result?.learning || '')
  const [preflightOpen, setPreflightOpen] = useState(false)
  const [attachCampaignId, setAttachCampaignId] = useState('')

  const completedTasks = move.checklistItems.filter(t => t.done).length
  const totalTasks = move.checklistItems.length
  const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  const durationDays = move.plan?.durationDays || move.durationDays || 7
  const dayNumber = getMoveDayNumber?.(move.id) || 1
  const todayTasks = getMoveTasksForDay?.(move.id, dayNumber) || []
  const tasksByDay = Array.from({ length: Math.max(durationDays, 1) }, (_, i) => i + 1)
    .map(day => ({ day, tasks: getMoveTasksForDay?.(move.id, day) || [] }))

  const dayOptions = Array.from({ length: Math.max(durationDays, 1) }, (_, i) => i + 1)

  const handleAddTask = (e) => {
    e.preventDefault()
    if (!newTask.trim()) return
    addTaskToMove(move.id, newTask.trim())
    setNewTask('')
  }

  const handleToggleStatus = () => {
    if (move.status === 'active') {
      updateMove(move.id, { status: 'paused' })
      return
    }
    if (move.status === 'generating') return
    if (move.status === 'completed') return
    setPreflightOpen(true)
  }

  const handleAttachProof = (taskId) => {
    setProofTaskId(taskId)
    const existing = (move.tasks || []).find(t => t.id === taskId)?.proof
    setProofUrl(existing?.url || '')
    setProofNote(existing?.note || '')
  }

  const handleSaveProof = () => {
    if (!proofTaskId) return
    attachProofToTask(move.id, proofTaskId, { url: proofUrl, note: proofNote })
    setProofTaskId(null)
    setProofUrl('')
    setProofNote('')
  }

  const handleLogTracking = () => {
    if (!trackingValue) return
    addTrackingUpdate(move.id, { value: Number(trackingValue) })
    setTrackingValue('')
  }

  const handleCompleteMove = () => {
    completeMove(move.id, { outcome: completionOutcome, learning: completionLearning })
  }

  const handleSetTaskDay = (taskId, day) => {
    setTaskDay?.(move.id, taskId, day)
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this move?')) {
      deleteMove(move.id)
      navigate('/app/moves')
    }
  }

  const handleOpenMuse = () => {
    openMuseDrawer({ moveId: move.id, campaignId: move.campaignId })
  }

  const handleAttachToCampaign = () => {
    if (!attachCampaignId) return
    attachMoveToCampaign?.(move.id, attachCampaignId)
    setAttachCampaignId('')
  }

  const handleDetach = () => {
    detachMoveFromCampaign?.(move.id)
  }

  const handleAddToExecution = () => {
    const created = addPipelineItem?.({
      title: move?.name || 'Move execution item',
      description: move?.cta ? `CTA: ${move.cta}` : null,
      work_type: 'other',
      channel_id: move?.channel || null,
      linked: {
        move_id: move.id,
        campaign_id: move.campaignId || null,
      },
      inputs: {
        asset_refs: Array.isArray(move?.assets) ? move.assets.map((id) => ({ type: 'asset', id })) : [],
      },
    })

    if (created?.pipeline_item_id) {
      navigate('/app/trail')
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/app/moves')}
          className="text-body-xs text-ink-400 hover:text-ink mb-2 flex items-center gap-1"
        >
          ← Back to moves
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-serif text-headline-md text-ink">{move.name}</h1>
            {campaign ? (
              <div className="mt-1 flex items-center gap-2">
                <button
                  onClick={() => navigate(`/app/campaigns/${campaign.id}`)}
                  className="text-body-sm text-ink-400 hover:text-primary"
                >
                  {campaign.name} →
                </button>
                <button
                  onClick={handleDetach}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-paper-200 rounded-lg text-body-xs text-ink-400 hover:text-ink transition-editorial"
                  title="Detach from campaign"
                >
                  <Unlink2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Detach
                </button>
              </div>
            ) : (
              <div className="mt-1 flex items-center gap-2">
                <span className="text-body-sm text-ink-400">Standalone move</span>
                <div className="flex items-center gap-2">
                  <select
                    value={attachCampaignId}
                    onChange={(e) => setAttachCampaignId(e.target.value)}
                    className="px-2 py-1 bg-paper border border-border rounded-lg text-body-xs text-ink"
                  >
                    <option value="">Attach to campaign…</option>
                    {(campaigns || []).map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                  <button
                    onClick={handleAttachToCampaign}
                    disabled={!attachCampaignId}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-paper-200 rounded-lg text-body-xs text-ink-400 hover:text-ink transition-editorial disabled:opacity-50"
                  >
                    <Link2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Attach
                  </button>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleToggleStatus}
              disabled={move.status === 'generating'}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-body-sm transition-editorial ${move.status === 'active'
                ? 'bg-amber-50 text-amber-600 hover:bg-amber-100'
                : move.status === 'generating'
                  ? 'bg-paper-200 text-ink-400'
                  : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'
                }`}
            >
              {move.status === 'active' ? (
                <>
                  <Pause className="w-4 h-4" strokeWidth={1.5} />
                  Pause
                </>
              ) : move.status === 'generating' ? (
                <>
                  <Clock className="w-4 h-4" strokeWidth={1.5} />
                  Generating…
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" strokeWidth={1.5} />
                  Activate
                </>
              )}
            </button>
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="p-2 text-ink-400 hover:text-ink hover:bg-paper-200 rounded-lg transition-editorial"
              >
                <MoreHorizontal className="w-5 h-5" strokeWidth={1.5} />
              </button>
              <AnimatePresence>
                {showMenu && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
                    <motion.div
                      initial={{ opacity: 0, y: -5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -5 }}
                      className="absolute right-0 top-full mt-1 w-40 bg-card border border-border rounded-lg shadow-lg z-20 py-1"
                    >
                      <button
                        onClick={handleDelete}
                        className="w-full flex items-center gap-2 px-3 py-2 text-body-sm text-red-500 hover:bg-red-50 transition-editorial"
                      >
                        <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                        Delete Move
                      </button>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-serif text-lg text-ink">Today</h2>
                <p className="text-body-xs text-ink-400">Day {dayNumber} of {durationDays}</p>
              </div>
              {move.status === 'generating' ? (
                <span className="text-body-xs text-ink-400">Generating…</span>
              ) : move.status !== 'active' ? (
                <button
                  onClick={() => setPreflightOpen(true)}
                  className="px-3 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
                >
                  Run pre-flight
                </button>
              ) : (
                <span className="text-body-xs text-ink-400">Running</span>
              )}
            </div>

            {todayTasks.length ? (
              <div className="space-y-2">
                {todayTasks.map(task => (
                  <div key={task.id} className="p-3 bg-paper rounded-xl border border-border-light">
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() => toggleTaskDone(move.id, task.id)}
                        className="mt-0.5"
                      >
                        {task.status === 'done' ? (
                          <CheckCircle2 className="w-5 h-5 text-primary" strokeWidth={1.5} />
                        ) : (
                          <Circle className="w-5 h-5 text-ink-300" strokeWidth={1.5} />
                        )}
                      </button>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-3">
                          <div className="text-body-sm text-ink">{task.text}</div>
                          <div className="flex items-center gap-2">
                            <select
                              value={task.day || 1}
                              onChange={(e) => handleSetTaskDay(task.id, Number(e.target.value))}
                              className="px-2 py-1 bg-paper border border-border rounded-lg text-body-xs text-ink focus:outline-none"
                            >
                              {dayOptions.map(d => (
                                <option key={`today_day_${d}`} value={d}>Day {d}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                        <div className="mt-2 flex items-center gap-2">
                          <button
                            onClick={() => handleAttachProof(task.id)}
                            className="px-2.5 py-1 bg-paper-200 rounded-lg text-body-xs text-ink-400 hover:text-ink transition-editorial"
                          >
                            {task.proof?.url ? 'Edit proof' : 'Attach proof'}
                          </button>
                          <button
                            onClick={() => handleSetTaskDay(task.id, dayNumber)}
                            className="px-2.5 py-1 bg-paper-200 rounded-lg text-body-xs text-ink-400 hover:text-ink transition-editorial"
                          >
                            Move to today
                          </button>
                          {task.proof?.url && (
                            <a
                              href={task.proof.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-body-xs text-primary hover:underline"
                            >
                              View →
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" strokeWidth={1.5} />
                <p className="text-body-sm text-ink-400">No tasks scheduled for today.</p>
              </div>
            )}
          </motion.div>

          {/* Progress */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-lg text-ink">Progress</h2>
              <span className="text-2xl font-mono text-ink">{progress}%</span>
            </div>
            <div className="h-3 bg-muted rounded-full overflow-hidden mb-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                className="h-full bg-primary rounded-full"
              />
            </div>
            <p className="text-body-xs text-ink-400">{completedTasks} of {totalTasks} tasks complete</p>
          </motion.div>

          {/* Checklist */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <h2 className="font-serif text-lg text-ink mb-4">This move</h2>

            <div className="space-y-4 mb-4">
              {tasksByDay.map(({ day, tasks }) => (
                <div key={`day_${day}`} className="p-4 bg-paper-200 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-body-sm text-ink font-medium">Day {day}</div>
                    <div className="text-body-xs text-ink-400">{tasks.length} tasks</div>
                  </div>
                  {tasks.length ? (
                    <div className="space-y-2">
                      {tasks.map(task => (
                        <div key={task.id} className="p-3 bg-paper rounded-xl border border-border-light">
                          <div className="flex items-start gap-3">
                            <button
                              onClick={() => toggleTaskDone(move.id, task.id)}
                              className="mt-0.5"
                            >
                              {task.status === 'done' ? (
                                <CheckCircle2 className="w-5 h-5 text-primary" strokeWidth={1.5} />
                              ) : (
                                <Circle className="w-5 h-5 text-ink-300" strokeWidth={1.5} />
                              )}
                            </button>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-3">
                                <div className="text-body-sm text-ink">{task.text}</div>
                                <div className="flex items-center gap-2">
                                  <select
                                    value={task.day || 1}
                                    onChange={(e) => handleSetTaskDay(task.id, Number(e.target.value))}
                                    className="px-2 py-1 bg-paper border border-border rounded-lg text-body-xs text-ink focus:outline-none"
                                  >
                                    {dayOptions.map(d => (
                                      <option key={`move_day_${task.id}_${d}`} value={d}>Day {d}</option>
                                    ))}
                                  </select>
                                </div>
                              </div>
                              <div className="mt-2 flex items-center gap-2">
                                <button
                                  onClick={() => handleAttachProof(task.id)}
                                  className="px-2.5 py-1 bg-paper-200 rounded-lg text-body-xs text-ink-400 hover:text-ink transition-editorial"
                                >
                                  {task.proof?.url ? 'Edit proof' : 'Attach proof'}
                                </button>
                                <button
                                  onClick={() => handleSetTaskDay(task.id, dayNumber)}
                                  className="px-2.5 py-1 bg-paper-200 rounded-lg text-body-xs text-ink-400 hover:text-ink transition-editorial"
                                >
                                  Move to today
                                </button>
                                {task.proof?.url && (
                                  <a
                                    href={task.proof.url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-body-xs text-primary hover:underline"
                                  >
                                    View →
                                  </a>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-body-xs text-ink-400">No tasks yet.</div>
                  )}
                </div>
              ))}
            </div>

            <form onSubmit={handleAddTask} className="flex gap-2">
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="Add a task..."
                className="flex-1 px-4 py-2.5 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
              <button
                type="submit"
                disabled={!newTask.trim()}
                className="px-4 py-2.5 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial disabled:opacity-50"
              >
                Add
              </button>
            </form>
          </motion.div>

          {/* Assets */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-lg text-ink">Assets</h2>
              <button
                onClick={handleOpenMuse}
                className="flex items-center gap-1 px-3 py-1.5 text-body-sm text-primary hover:bg-signal-muted rounded-lg transition-editorial"
              >
                <Sparkles className="w-4 h-4" strokeWidth={1.5} />
                Generate Asset
              </button>
            </div>

            {assets.length > 0 ? (
              <div className="space-y-3">
                {assets.map(asset => (
                  <AssetCard
                    key={asset.id}
                    asset={asset}
                    onOpenMuse={handleOpenMuse}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-ink-300 mx-auto mb-3" strokeWidth={1.5} />
                <p className="text-body-sm text-ink-400 mb-4">No assets yet</p>
                <button
                  onClick={handleOpenMuse}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
                >
                  Generate your first asset
                </button>
              </div>
            )}
          </motion.div>

          {/* Tracking & Completion */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <h2 className="font-serif text-lg text-ink mb-4">Tracking</h2>
            <div className="p-4 bg-paper-200 rounded-xl mb-4">
              <div className="flex items-center justify-between">
                <div className="text-body-xs text-ink-400">Metric</div>
                <div className="text-body-xs text-ink font-mono">{move.tracking?.metric || move.metric || '—'}</div>
              </div>
              <div className="mt-3 flex gap-2">
                <input
                  type="number"
                  value={trackingValue}
                  onChange={(e) => setTrackingValue(e.target.value)}
                  placeholder="Add today's number"
                  className="flex-1 px-4 py-2.5 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
                <button
                  type="button"
                  onClick={handleLogTracking}
                  disabled={!trackingValue}
                  className="px-4 py-2.5 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial disabled:opacity-50"
                >
                  Log
                </button>
              </div>
              {(move.tracking?.updates || []).length > 0 && (
                <div className="mt-3 text-body-xs text-ink-400">
                  Updates: {(move.tracking?.updates || []).length}
                </div>
              )}
            </div>

            <h2 className="font-serif text-lg text-ink mb-3">Complete</h2>
            <div className="p-4 bg-paper-200 rounded-xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                <select
                  value={completionOutcome}
                  onChange={(e) => setCompletionOutcome(e.target.value)}
                  className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                >
                  <option value="won">Won</option>
                  <option value="meh">Meh</option>
                  <option value="failed">Failed</option>
                </select>
                <button
                  type="button"
                  onClick={handleCompleteMove}
                  className="w-full px-4 py-3 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial"
                >
                  Mark complete
                </button>
              </div>
              <textarea
                value={completionLearning}
                onChange={(e) => setCompletionLearning(e.target.value)}
                rows={3}
                placeholder="What did we learn? What changes next time?"
                className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
              />
            </div>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Move details */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <h3 className="font-serif text-lg text-ink mb-4">Details</h3>
            <div className="space-y-3 text-body-sm">
              <div className="flex items-center justify-between">
                <span className="text-ink-400">Channel</span>
                <span className="text-ink capitalize">{move.channel}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-400">CTA</span>
                <span className="text-ink">{move.cta}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-400">Metric</span>
                <span className="text-ink capitalize">{move.metric}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-400">Duration</span>
                <span className="text-ink">{move.durationDays} days</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-400">Status</span>
                <StatusBadge status={move.status} />
              </div>
            </div>
          </motion.div>

          {/* Quick actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-3"
          >
            <button
              onClick={handleAddToExecution}
              className="w-full flex items-center gap-3 p-4 bg-card border border-border rounded-xl text-left hover:border-border-dark transition-editorial"
            >
              <div className="w-10 h-10 bg-paper-200 rounded-xl flex items-center justify-center">
                <Send className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
              </div>
              <div>
                <div className="text-body-sm text-ink font-medium">Add to Execution</div>
                <div className="text-body-xs text-ink-400">Create a shippable work item</div>
              </div>
            </button>

            <button
              onClick={handleOpenMuse}
              className="w-full flex items-center gap-3 p-4 bg-signal-muted border border-primary/20 rounded-xl text-left hover:bg-primary/20 transition-editorial"
            >
              <div className="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary" strokeWidth={1.5} />
              </div>
              <div>
                <div className="text-body-sm text-ink font-medium">Generate Asset</div>
                <div className="text-body-xs text-ink-400">Create content with Muse</div>
              </div>
            </button>

            <button
              onClick={() => navigate('/app/black-box/new')}
              className="w-full flex items-center gap-3 p-4 bg-card border border-border rounded-xl text-left hover:border-border-dark transition-editorial"
            >
              <div className="w-10 h-10 bg-paper-200 rounded-xl flex items-center justify-center">
                <Box className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
              </div>
              <div>
                <div className="text-body-sm text-ink font-medium">Start Duel</div>
                <div className="text-body-xs text-ink-400">Test asset variants</div>
              </div>
            </button>
          </motion.div>
        </div>
      </div>

      {proofTaskId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/40" onClick={() => setProofTaskId(null)} />
          <div className="relative w-full max-w-lg bg-card border border-border rounded-2xl p-5 shadow-xl">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="font-serif text-lg text-ink">Attach proof</div>
                <div className="text-body-xs text-ink-400">Paste a URL or add a quick note.</div>
              </div>
              <button
                onClick={() => setProofTaskId(null)}
                className="px-3 py-1.5 text-body-xs text-ink-400 hover:text-ink"
              >
                Close
              </button>
            </div>
            <div className="space-y-3">
              <input
                value={proofUrl}
                onChange={(e) => setProofUrl(e.target.value)}
                placeholder="https://..."
                className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
              <textarea
                value={proofNote}
                onChange={(e) => setProofNote(e.target.value)}
                rows={3}
                placeholder="Optional note"
                className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
              />
              <div className="flex items-center justify-end gap-2">
                <button
                  onClick={() => setProofTaskId(null)}
                  className="px-4 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveProof}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
                >
                  Save proof
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <PreFlightChecklistModal
        open={preflightOpen}
        onOpenChange={setPreflightOpen}
        moveId={move.id}
      />
    </div>
  )
}

// Main Moves Page
const MovesPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { moves, getMove, getCampaign, createMove, attachMoveToCampaign, linkSignalToMove } = useRaptorflowStore()
  const [createOpen, setCreateOpen] = useState(false)

  const createRequest = useMemo(() => {
    const params = new URLSearchParams(location.search)
    const newFlag = params.get('new')
    const name = params.get('name')
    const campaignId = params.get('campaignId')
    const cohort = params.get('cohort')
    const channel = params.get('channel')
    const metric = params.get('metric')
    const durationDaysRaw = params.get('durationDays')
    const signalId = params.get('signalId')

    const shouldOpen = newFlag === '1' || Boolean(name) || Boolean(campaignId) || Boolean(signalId)
    if (!shouldOpen) return null

    const durationDays = durationDaysRaw ? Number(durationDaysRaw) : undefined

    return {
      initialValues: {
        name: name || undefined,
        campaignId: campaignId || undefined,
        cohort: cohort || undefined,
        channel: channel || undefined,
        metric: metric || undefined,
        durationDays: Number.isFinite(durationDays) ? durationDays : undefined,
      },
      signalId: signalId || null,
    }
  }, [location.search])

  useEffect(() => {
    if (!createRequest) return
    setCreateOpen(true)
  }, [createRequest])

  // If viewing a specific move
  if (id) {
    const move = getMove(id)
    if (move) {
      return <MoveDetail move={move} />
    }
  }

  // Group moves by status
  const activeMoves = moves.filter(m => m.status === 'active')
  const pendingMoves = moves.filter(m => m.status === 'pending')
  const completedMoves = moves.filter(m => m.status === 'completed')

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-serif text-headline-md text-ink">Moves</h1>
          <p className="text-body-sm text-ink-400 mt-1">Your tactical marketing strikes</p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={() => setCreateOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          New Move
        </motion.button>
      </div>

      {/* Active moves */}
      {activeMoves.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <h2 className="font-serif text-lg text-ink mb-4">Active ({activeMoves.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeMoves.map(move => (
              <MoveCard
                key={move.id}
                move={move}
                campaign={getCampaign(move.campaignId)}
                onClick={() => navigate(`/app/moves/${move.id}`)}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* Pending moves */}
      {pendingMoves.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <h2 className="font-serif text-lg text-ink mb-4">Pending ({pendingMoves.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pendingMoves.map(move => (
              <MoveCard
                key={move.id}
                move={move}
                campaign={getCampaign(move.campaignId)}
                onClick={() => navigate(`/app/moves/${move.id}`)}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* Completed moves */}
      {completedMoves.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="font-serif text-lg text-ink mb-4">Completed ({completedMoves.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedMoves.map(move => (
              <MoveCard
                key={move.id}
                move={move}
                campaign={getCampaign(move.campaignId)}
                onClick={() => navigate(`/app/moves/${move.id}`)}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* Empty state */}
      {moves.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <Zap className="w-16 h-16 text-ink-300 mx-auto mb-4" strokeWidth={1.5} />
          <h2 className="font-serif text-xl text-ink mb-2">No moves yet</h2>
          <p className="text-body-sm text-ink-400 mb-6">Create your first move (standalone or attached to a campaign)</p>
          <button
            onClick={() => setCreateOpen(true)}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial"
          >
            Create a Move
          </button>
        </motion.div>
      )}

      <CreateStandaloneMoveModal
        open={createOpen}
        onOpenChange={setCreateOpen}
        initialValues={createRequest?.initialValues}
        onCreate={({ name, campaignId, cohort, channel, durationDays, metric }) => {
          const now = Date.now()
          const move = createMove({
            name,
            cohort: cohort || '',
            channel,
            metric,
            durationDays,
            cta: 'Take action',
            campaignId: null,
            checklistItems: [
              { id: `${now}_0`, text: 'Confirm objective + success metric', done: false },
              { id: `${now}_1`, text: 'Plan the first execution day', done: false },
              { id: `${now}_2`, text: 'Ship Day 1', done: false },
            ],
          })

          if (campaignId) {
            attachMoveToCampaign?.(move.id, campaignId)
          }

          if (createRequest?.signalId) {
            linkSignalToMove?.(createRequest.signalId, move.id)
          }

          setCreateOpen(false)
          if (createRequest) {
            navigate(`/app/moves/${move.id}`, { replace: true })
            return
          }
          navigate(`/app/moves/${move.id}`)
        }}
      />
    </div>
  )
}

export default MovesPage
