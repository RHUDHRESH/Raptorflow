import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Plus,
  Search,
  User,
  CheckCircle2,
  AlertTriangle,
  Calendar,
  ClipboardCheck,
  Send,
  X,
} from 'lucide-react'

import useRaptorflowStore from '@/store/raptorflowStore'
import { Modal } from '@/components/system/Modal'
import { HairlineTable } from '@/components/system/HairlineTable'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const STATUS_COLUMNS = [
  { id: 'backlog', label: 'Backlog' },
  { id: 'in_production', label: 'In Production' },
  { id: 'review', label: 'Needs Review' },
  { id: 'approval', label: 'Needs Approval' },
  { id: 'scheduled', label: 'Scheduled' },
  { id: 'shipped', label: 'Shipped' },
  { id: 'blocked', label: 'Blocked' },
]

const WORK_TYPES = [
  { id: 'post', label: 'Post' },
  { id: 'ad', label: 'Ad' },
  { id: 'landing_page', label: 'Landing page' },
  { id: 'email', label: 'Email' },
  { id: 'whatsapp_sequence', label: 'WhatsApp sequence' },
  { id: 'dm_script', label: 'DM script' },
  { id: 'video', label: 'Video' },
  { id: 'design', label: 'Design' },
  { id: 'other', label: 'Other' },
]

const RECEIPT_TYPES = [
  { id: 'url', label: 'URL' },
  { id: 'ad_id', label: 'Ad ID' },
  { id: 'screenshot', label: 'Screenshot' },
  { id: 'doc', label: 'Doc' },
  { id: 'other', label: 'Other' },
]

const OWNER_OPTIONS = [
  { id: 'me', label: 'You' },
  { id: 'reviewer', label: 'Reviewer' },
  { id: 'approver', label: 'Approver' },
]

const getStatusLabel = (status) => STATUS_COLUMNS.find((s) => s.id === status)?.label || status || 'Backlog'

const getStatusPill = (status) => {
  const base = 'px-2 py-0.5 rounded text-[11px] leading-none border'
  if (status === 'shipped') return `${base} bg-primary/10 text-primary border-primary/20`
  if (status === 'scheduled') return `${base} bg-paper-200 text-ink border-border-light`
  if (status === 'blocked') return `${base} bg-amber-50 text-amber-700 border-amber-200`
  if (status === 'approval') return `${base} bg-paper-200 text-ink border-border-light`
  if (status === 'review') return `${base} bg-paper text-ink border-border-light`
  return `${base} bg-paper text-ink-400 border-border-light`
}

const formatDate = (iso) => {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString()
  } catch {
    return ''
  }
}

const toIsoFromDateInput = (value) => {
  if (!value) return null
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return null
  return d.toISOString()
}

const FilterChip = ({ active, label, onClick }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg border text-body-xs transition-editorial ${active
        ? 'border-primary/20 bg-signal-muted text-primary'
        : 'border-border bg-paper text-ink-400 hover:bg-paper-200'
        }`}
    >
      {label}
    </button>
  )
}

const AddPipelineItemModal = ({ open, onClose, onCreate }) => {
  const [title, setTitle] = useState('')
  const [workType, setWorkType] = useState('post')
  const [channelId, setChannelId] = useState('linkedin')
  const [description, setDescription] = useState('')
  const [dueAt, setDueAt] = useState('')

  const reset = () => {
    setTitle('')
    setWorkType('post')
    setChannelId('linkedin')
    setDescription('')
    setDueAt('')
  }

  return (
    <Modal
      open={open}
      onOpenChange={(next) => {
        if (!next) {
          onClose()
          reset()
        }
      }}
      title="Add to Execution"
      description="Create a work item to ship in the real world."
      contentClassName="max-w-xl"
    >
      <div className="px-5 pb-5 space-y-4">
        <div>
          <label className="block text-body-xs text-ink-400 mb-2">Title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="LinkedIn post: proof-led angle"
            className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">Work type</label>
            <select
              value={workType}
              onChange={(e) => setWorkType(e.target.value)}
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            >
              {WORK_TYPES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-body-xs text-ink-400 mb-2">Channel</label>
            <input
              value={channelId}
              onChange={(e) => setChannelId(e.target.value)}
              placeholder="linkedin"
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label className="block text-body-xs text-ink-400 mb-2">Description</label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What needs to be done, what inputs, what approval required."
            className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
          />
        </div>

        <div>
          <label className="block text-body-xs text-ink-400 mb-2">Due date</label>
          <input
            type="date"
            value={dueAt}
            onChange={(e) => setDueAt(e.target.value)}
            className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        <div className="pt-2 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={() => {
              onClose()
              reset()
            }}
            className="px-4 py-2 border border-border bg-background rounded-xl text-body-sm hover:bg-muted transition-editorial"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => {
              const created = onCreate({
                title: title.trim() || 'Untitled work item',
                description: description.trim() || null,
                work_type: workType,
                channel_id: channelId.trim() || null,
                execution: {
                  due_at: toIsoFromDateInput(dueAt),
                },
              })
              if (created) {
                onClose()
                reset()
              }
            }}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial"
          >
            Add
          </button>
        </div>
      </div>
    </Modal>
  )
}

const PipelineItemModal = ({ open, onClose, item }) => {
  const {
    updatePipelineItem,
    assignPipelineItem,
    requestPipelineApproval,
    schedulePipelineItem,
    markPipelineItemShipped,
    logPipelineResult,
    setPipelineItemStatus,
  } = useRaptorflowStore()

  const [owner, setOwner] = useState(item?.execution?.owner_user_id || 'me')
  const [reviewer, setReviewer] = useState(item?.execution?.reviewer_user_id || '')
  const [approver, setApprover] = useState(item?.execution?.approver_user_id || '')
  const [approvalRequired, setApprovalRequired] = useState(Boolean(item?.approvals?.required))
  const [scheduledFor, setScheduledFor] = useState(item?.execution?.scheduled_for ? item.execution.scheduled_for.slice(0, 10) : '')
  const [receiptType, setReceiptType] = useState(item?.receipt?.type || 'url')
  const [receiptValue, setReceiptValue] = useState(item?.receipt?.value || '')
  const [metricName, setMetricName] = useState(item?.metrics_hook?.primary_metric || '')
  const [metricNote, setMetricNote] = useState('')

  const status = item?.execution?.status

  const close = () => {
    onClose()
  }

  if (!item) return null

  return (
    <Modal
      open={open}
      onOpenChange={(next) => {
        if (!next) close()
      }}
      title={item.title || 'Work item'}
      description="Execution work item"
      contentClassName="max-w-3xl"
    >
      <div className="px-5 pb-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className={getStatusPill(status)}>{getStatusLabel(status)}</span>
              <span className="px-2 py-0.5 rounded text-[11px] leading-none border bg-paper text-ink-400 border-border-light">
                {WORK_TYPES.find((t) => t.id === item.work_type)?.label || item.work_type}
              </span>
              {item.channel_id ? (
                <span className="px-2 py-0.5 rounded text-[11px] leading-none border bg-paper text-ink-400 border-border-light capitalize">
                  {item.channel_id}
                </span>
              ) : null}
            </div>
            {item.description ? (
              <div className="mt-3 text-body-sm text-ink whitespace-pre-wrap">{item.description}</div>
            ) : (
              <div className="mt-3 text-body-sm text-ink-400">No description yet.</div>
            )}
          </div>

          <button
            type="button"
            onClick={close}
            className="p-2 text-ink-400 hover:text-ink hover:bg-paper-200 rounded-lg transition-editorial"
          >
            <X className="w-5 h-5" strokeWidth={1.5} />
          </button>
        </div>

        <div className="mt-5 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="rounded-xl border border-border bg-card p-4">
              <div className="text-body-xs text-ink-400">Inputs</div>
              <div className="mt-2 text-body-sm text-ink">
                {item?.inputs?.asset_refs?.length ? `${item.inputs.asset_refs.length} assets` : 'No linked assets'}
              </div>
              <div className="mt-1 text-body-xs text-ink-400">
                {item?.inputs?.proof_claim_ids?.length ? `${item.inputs.proof_claim_ids.length} proof claims` : 'No proof claims'}
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-4">
              <div className="flex items-center justify-between">
                <div className="font-serif text-lg text-ink">Schedule</div>
                <div className="text-body-xs text-ink-400">Due: {formatDate(item?.execution?.due_at) || '—'}</div>
              </div>

              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-2">Scheduled for</label>
                  <input
                    type="date"
                    value={scheduledFor}
                    onChange={(e) => setScheduledFor(e.target.value)}
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    type="button"
                    onClick={() => {
                      schedulePipelineItem?.(item.pipeline_item_id, {
                        scheduled_for: toIsoFromDateInput(scheduledFor),
                      })
                    }}
                    className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 border border-border rounded-xl text-body-sm text-ink hover:bg-paper-200 transition-editorial"
                  >
                    <Calendar className="w-4 h-4" strokeWidth={1.5} />
                    Schedule
                  </button>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-4">
              <div className="font-serif text-lg text-ink">Receipt (required to mark shipped)</div>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-2">Type</label>
                  <select
                    value={receiptType}
                    onChange={(e) => setReceiptType(e.target.value)}
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    {RECEIPT_TYPES.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-body-xs text-ink-400 mb-2">Value</label>
                  <input
                    value={receiptValue}
                    onChange={(e) => setReceiptValue(e.target.value)}
                    placeholder="https://... or ad id"
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>
              </div>

              <div className="mt-3 flex items-center justify-end">
                <button
                  type="button"
                  onClick={() => {
                    markPipelineItemShipped?.(item.pipeline_item_id, {
                      type: receiptType,
                      value: receiptValue,
                    })
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial"
                >
                  <Send className="w-4 h-4" strokeWidth={1.5} />
                  Mark shipped
                </button>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-4">
              <div className="font-serif text-lg text-ink">Log result (links to Matrix later)</div>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-2">Primary metric</label>
                  <input
                    value={metricName}
                    onChange={(e) => setMetricName(e.target.value)}
                    placeholder="demo_requests"
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-body-xs text-ink-400 mb-2">Note</label>
                  <input
                    value={metricNote}
                    onChange={(e) => setMetricNote(e.target.value)}
                    placeholder="What happened (manual first)."
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>
              </div>

              <div className="mt-3 flex items-center justify-end">
                <button
                  type="button"
                  onClick={() => {
                    logPipelineResult?.(item.pipeline_item_id, {
                      primary_metric: metricName,
                      note: metricNote,
                    })
                    setMetricNote('')
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2 border border-border rounded-xl text-body-sm text-ink hover:bg-paper-200 transition-editorial"
                >
                  <ClipboardCheck className="w-4 h-4" strokeWidth={1.5} />
                  Log result
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-xl border border-border bg-card p-4">
              <div className="font-serif text-lg text-ink">Assignments</div>

              <div className="mt-3 space-y-3">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-2">Owner</label>
                  <select
                    value={owner}
                    onChange={(e) => setOwner(e.target.value)}
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    {OWNER_OPTIONS.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-body-xs text-ink-400 mb-2">Reviewer (optional)</label>
                  <select
                    value={reviewer}
                    onChange={(e) => setReviewer(e.target.value)}
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    <option value="">None</option>
                    {OWNER_OPTIONS.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-body-xs text-ink-400 mb-2">Approver (optional)</label>
                  <select
                    value={approver}
                    onChange={(e) => setApprover(e.target.value)}
                    className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    <option value="">None</option>
                    {OWNER_OPTIONS.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.label}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    assignPipelineItem?.(item.pipeline_item_id, {
                      owner_user_id: owner,
                      reviewer_user_id: reviewer || null,
                      approver_user_id: approver || null,
                    })
                  }}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 border border-border rounded-xl text-body-sm text-ink hover:bg-paper-200 transition-editorial"
                >
                  <User className="w-4 h-4" strokeWidth={1.5} />
                  Assign
                </button>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-4">
              <div className="font-serif text-lg text-ink">Approval</div>
              <div className="mt-3 flex items-center justify-between gap-3">
                <div className="text-body-sm text-ink">Required</div>
                <button
                  type="button"
                  onClick={() => setApprovalRequired((v) => !v)}
                  className={`px-3 py-1.5 rounded-lg border text-body-xs transition-editorial ${approvalRequired
                    ? 'border-primary/20 bg-signal-muted text-primary'
                    : 'border-border bg-paper text-ink-400 hover:bg-paper-200'
                    }`}
                >
                  {approvalRequired ? 'Yes' : 'No'}
                </button>
              </div>

              <button
                type="button"
                onClick={() => {
                  requestPipelineApproval?.(item.pipeline_item_id, {
                    required: approvalRequired,
                  })
                }}
                className="mt-3 w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial"
              >
                <CheckCircle2 className="w-4 h-4" strokeWidth={1.5} />
                Request approval
              </button>

              <div className="mt-3 text-body-xs text-ink-400">
                State: <span className="text-ink">{item?.approvals?.state || 'not_requested'}</span>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-4">
              <div className="font-serif text-lg text-ink">Status</div>
              <div className="mt-3 space-y-2">
                {STATUS_COLUMNS.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setPipelineItemStatus?.(item.pipeline_item_id, s.id)}
                    className={`w-full flex items-center justify-between gap-2 px-3 py-2 rounded-xl border text-body-sm transition-editorial ${s.id === status
                      ? 'border-primary/20 bg-signal-muted text-primary'
                      : 'border-border bg-paper text-ink hover:bg-paper-200'
                      }`}
                  >
                    <span>{s.label}</span>
                    {s.id === status ? (
                      <CheckCircle2 className="w-4 h-4" strokeWidth={1.5} />
                    ) : null}
                  </button>
                ))}
              </div>

              {status === 'blocked' ? (
                <div className="mt-3 flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-xl">
                  <AlertTriangle className="w-4 h-4 text-amber-700 mt-0.5" strokeWidth={1.5} />
                  <div>
                    <div className="text-body-sm text-amber-900 font-medium">Blocked</div>
                    <div className="text-body-xs text-amber-800 mt-0.5">Fix approvals, missing inputs, or scheduling conflicts.</div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </Modal>
  )
}

 const ExecutionPanel = () => {
  const { pipelineItems, addPipelineItem } = useRaptorflowStore()

  const [showAdd, setShowAdd] = useState(false)
  const [selectedId, setSelectedId] = useState(null)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [workTypeFilter, setWorkTypeFilter] = useState('all')
  const [ownerFilter, setOwnerFilter] = useState('all')

  const items = Array.isArray(pipelineItems) ? pipelineItems : []
  const selected = useMemo(() => items.find((i) => i.pipeline_item_id === selectedId), [items, selectedId])

  const visibleItems = useMemo(() => {
    const q = query.trim().toLowerCase()
    return items.filter((item) => {
      const status = item?.execution?.status || 'backlog'
      if (statusFilter !== 'all' && status !== statusFilter) return false

      const wt = item?.work_type || 'other'
      if (workTypeFilter !== 'all' && wt !== workTypeFilter) return false

      const owner = item?.execution?.owner_user_id || null
      if (ownerFilter === 'unassigned' && owner) return false
      if (ownerFilter !== 'all' && ownerFilter !== 'unassigned' && owner !== ownerFilter) return false

      if (!q) return true
      const title = (item?.title || '').toLowerCase()
      const desc = (item?.description || '').toLowerCase()
      const channel = (item?.channel_id || '').toLowerCase()
      return title.includes(q) || desc.includes(q) || channel.includes(q)
    })
  }, [items, ownerFilter, query, statusFilter, workTypeFilter])

  const queueRows = useMemo(() => {
    return visibleItems
      .slice()
      .sort((a, b) => {
        const aDue = new Date(a?.execution?.due_at || 0).getTime()
        const bDue = new Date(b?.execution?.due_at || 0).getTime()
        if (aDue !== bDue) return aDue - bDue
        return new Date(b?.updated_at || b?.created_at || 0).getTime() - new Date(a?.updated_at || a?.created_at || 0).getTime()
      })
  }, [visibleItems])

  const boardColumns = useMemo(() => {
    const byStatus = new Map(STATUS_COLUMNS.map((s) => [s.id, []]))
    visibleItems.forEach((item) => {
      const status = item?.execution?.status || 'backlog'
      if (!byStatus.has(status)) byStatus.set(status, [])
      byStatus.get(status).push(item)
    })
    return STATUS_COLUMNS.map((col) => ({ ...col, items: byStatus.get(col.id) || [] }))
  }, [visibleItems])

  const calendarGroups = useMemo(() => {
    const map = new Map()
    visibleItems
      .filter((i) => i?.execution?.scheduled_for)
      .forEach((i) => {
        const day = i.execution.scheduled_for.slice(0, 10)
        if (!map.has(day)) map.set(day, [])
        map.get(day).push(i)
      })
    const days = Array.from(map.keys()).sort()
    return days.map((day) => ({ day, items: map.get(day) }))
  }, [visibleItems])

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <div>
          <div className="font-serif text-headline-sm text-ink">Execution</div>
          <div className="text-body-sm text-ink-400 mt-1">Queue, approvals, schedule, receipts.</div>
        </div>
        <button
          type="button"
          onClick={() => setShowAdd(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          Add to Execution
        </button>
      </div>

      <Tabs defaultValue="queue">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="queue">Queue</TabsTrigger>
          <TabsTrigger value="board">Board</TabsTrigger>
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
        </TabsList>

        <TabsContent value="queue" className="mt-4">
          <div className="rounded-xl border border-border bg-card p-4 mb-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="md:col-span-2">
                <label className="block text-body-xs text-ink-400 mb-2">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search title, channel, description"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-body-xs text-ink-400 mb-2">Owner</label>
                <div className="flex flex-wrap gap-2">
                  <FilterChip active={ownerFilter === 'all'} label="All" onClick={() => setOwnerFilter('all')} />
                  <FilterChip active={ownerFilter === 'me'} label="You" onClick={() => setOwnerFilter('me')} />
                  <FilterChip
                    active={ownerFilter === 'unassigned'}
                    label="Unassigned"
                    onClick={() => setOwnerFilter('unassigned')}
                  />
                </div>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-body-xs text-ink-400 mb-2">Status</div>
                <div className="flex flex-wrap gap-2">
                  <FilterChip active={statusFilter === 'all'} label="All" onClick={() => setStatusFilter('all')} />
                  {STATUS_COLUMNS.map((s) => (
                    <FilterChip
                      key={s.id}
                      active={statusFilter === s.id}
                      label={s.label}
                      onClick={() => setStatusFilter(s.id)}
                    />
                  ))}
                </div>
              </div>

              <div>
                <div className="text-body-xs text-ink-400 mb-2">Work type</div>
                <div className="flex flex-wrap gap-2">
                  <FilterChip
                    active={workTypeFilter === 'all'}
                    label="All"
                    onClick={() => setWorkTypeFilter('all')}
                  />
                  {WORK_TYPES.map((t) => (
                    <FilterChip
                      key={t.id}
                      active={workTypeFilter === t.id}
                      label={t.label}
                      onClick={() => setWorkTypeFilter(t.id)}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          <HairlineTable
            data={queueRows}
            onRowClick={(row) => setSelectedId(row.pipeline_item_id)}
            emptyTitle="No work in Execution"
            emptyDescription="Add a work item from a Move, Campaign, or manual entry."
            emptyAction="Add to Execution"
            onEmptyAction={() => setShowAdd(true)}
            columns={[
              {
                key: 'title',
                header: 'Work item',
                render: (row) => (
                  <div>
                    <div className="text-ink">{row.title}</div>
                    <div className="text-xs text-ink-400 capitalize">{WORK_TYPES.find((t) => t.id === row.work_type)?.label || row.work_type}</div>
                  </div>
                ),
              },
              {
                key: 'status',
                header: 'Status',
                render: (row) => (
                  <span className={getStatusPill(row?.execution?.status)}>
                    {getStatusLabel(row?.execution?.status)}
                  </span>
                ),
              },
              {
                key: 'owner',
                header: 'Owner',
                render: (row) => (
                  <span className="text-body-sm text-ink-400">{row?.execution?.owner_user_id || '—'}</span>
                ),
              },
              {
                key: 'due',
                header: 'Due',
                align: 'right',
                render: (row) => (
                  <span className="text-body-sm text-ink">{formatDate(row?.execution?.due_at) || '—'}</span>
                ),
              },
              {
                key: 'scheduled',
                header: 'Scheduled',
                align: 'right',
                render: (row) => (
                  <span className="text-body-sm text-ink-400">{formatDate(row?.execution?.scheduled_for) || '—'}</span>
                ),
              },
            ]}
          />
        </TabsContent>

        <TabsContent value="board" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {boardColumns.map((col) => (
              <div key={col.id} className="rounded-xl border border-border bg-card p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-body-sm text-ink font-medium">{col.label}</div>
                  <span className="text-[11px] leading-none text-ink-400 px-2 py-1 rounded-full bg-paper border border-border-light">
                    {col.items.length}
                  </span>
                </div>
                <div className="space-y-2">
                  {col.items.length === 0 ? (
                    <div className="text-body-xs text-ink-400 p-2">Empty</div>
                  ) : (
                    col.items.map((item) => (
                      <motion.button
                        key={item.pipeline_item_id}
                        type="button"
                        onClick={() => setSelectedId(item.pipeline_item_id)}
                        whileHover={{ y: -1 }}
                        className="w-full text-left p-3 rounded-xl border border-border-light bg-paper hover:bg-paper-200 transition-editorial"
                      >
                        <div className="text-body-sm text-ink font-medium line-clamp-2">{item.title}</div>
                        <div className="text-body-xs text-ink-400 mt-1 capitalize">{item.work_type}</div>
                      </motion.button>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="calendar" className="mt-4">
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="text-body-sm text-ink font-medium">Scheduled items</div>
            <div className="text-body-xs text-ink-400 mt-1">Drag/drop later. Manual scheduling now.</div>

            <div className="mt-4 space-y-4">
              {calendarGroups.length === 0 ? (
                <div className="text-body-sm text-ink-400">Nothing scheduled yet.</div>
              ) : (
                calendarGroups.map((g) => (
                  <div key={g.day} className="p-3 rounded-xl border border-border-light bg-paper">
                    <div className="flex items-center justify-between">
                      <div className="text-body-sm text-ink font-medium">{new Date(g.day).toLocaleDateString()}</div>
                      <span className="text-[11px] leading-none text-ink-400 px-2 py-1 rounded-full bg-paper-200 border border-border-light">
                        {g.items.length}
                      </span>
                    </div>
                    <div className="mt-3 space-y-2">
                      {g.items.map((item) => (
                        <button
                          key={item.pipeline_item_id}
                          type="button"
                          onClick={() => setSelectedId(item.pipeline_item_id)}
                          className="w-full flex items-center justify-between gap-3 p-3 bg-card border border-border rounded-xl hover:border-border-dark transition-editorial"
                        >
                          <div className="text-left">
                            <div className="text-body-sm text-ink font-medium">{item.title}</div>
                            <div className="text-body-xs text-ink-400 capitalize">{item.work_type} • {item.channel_id || 'no channel'}</div>
                          </div>
                          <span className={getStatusPill(item?.execution?.status)}>{getStatusLabel(item?.execution?.status)}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>

      <AddPipelineItemModal
        open={showAdd}
        onClose={() => setShowAdd(false)}
        onCreate={(payload) => {
          const created = addPipelineItem?.(payload)
          if (created?.pipeline_item_id) {
            setSelectedId(created.pipeline_item_id)
            return created
          }
          return null
        }}
      />

      <PipelineItemModal
        open={Boolean(selectedId && selected)}
        onClose={() => setSelectedId(null)}
        item={selected}
      />
    </div>
  )
}

export default ExecutionPanel
