import { useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Plus,
  ArrowLeft,
  ChevronRight,
  Box,
  Zap,
  Radio,
  Trash2,
  ExternalLink,
} from 'lucide-react'

import useRaptorflowStore from '@/store/raptorflowStore'
import { Modal } from '@/components/system/Modal'
import { HairlineTable } from '@/components/system/HairlineTable'

const STATUS_OPTIONS = [
  { id: 'triage', label: 'Triage' },
  { id: 'shaped', label: 'Shaped' },
  { id: 'prioritized', label: 'Prioritized' },
  { id: 'in_test', label: 'In test' },
  { id: 'resolved', label: 'Resolved' },
  { id: 'archived', label: 'Archived' },
]

const EFFORT_OPTIONS = [
  { id: 'low', label: 'Low' },
  { id: 'medium', label: 'Medium' },
  { id: 'high', label: 'High' },
]

const getStatusLabel = (status) => {
  return STATUS_OPTIONS.find((s) => s.id === status)?.label || status || 'Triage'
}

const getStatusPill = (status) => {
  const base = 'px-2 py-0.5 rounded text-[11px] leading-none border'
  if (status === 'prioritized') return `${base} bg-primary/10 text-primary border-primary/20`
  if (status === 'in_test') return `${base} bg-paper-200 text-ink border-border-light`
  if (status === 'resolved') return `${base} bg-paper-200 text-ink border-border-light`
  if (status === 'archived') return `${base} bg-paper-200 text-ink-400 border-border-light`
  if (status === 'shaped') return `${base} bg-paper text-ink border-border-light`
  return `${base} bg-paper text-ink-400 border-border-light`
}

const scoreSignalICE = (signal) => {
  const ice = signal?.ice || {}
  const impact = Number(ice.impact || 0)
  const confidence = Number(ice.confidence || 0)
  const ease = Number(ice.ease || 0)
  return impact * confidence * ease
}

const EvidenceRow = ({ ev, onOpen }) => {
  const label = ev?.type === 'matrix_metric'
    ? 'Matrix'
    : ev?.type === 'radar_scan'
      ? 'Radar'
      : ev?.type === 'duel'
        ? 'Black Box'
        : ev?.type === 'move'
          ? 'Move'
          : 'Evidence'

  return (
    <button
      type="button"
      onClick={onOpen}
      className="w-full flex items-center justify-between gap-3 p-3 bg-paper rounded-xl border border-border-light hover:bg-paper-200 transition-editorial"
    >
      <div className="text-left">
        <div className="text-body-sm text-ink font-medium">{label}</div>
        <div className="text-body-xs text-ink-400 mt-0.5">{ev?.label || ev?.id || ''}</div>
      </div>
      <ExternalLink className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
    </button>
  )
}

const CreateSignalModal = ({ open, onClose, onCreate }) => {
  const { cohorts } = useRaptorflowStore()

  const [title, setTitle] = useState('')
  const [statement, setStatement] = useState('')
  const [zone, setZone] = useState('activation')
  const [effort, setEffort] = useState('medium')
  const [status, setStatus] = useState('triage')
  const [cohortId, setCohortId] = useState(cohorts?.[0]?.id || '')
  const [impact, setImpact] = useState(2)
  const [confidence, setConfidence] = useState(2)
  const [ease, setEase] = useState(2)

  const reset = () => {
    setTitle('')
    setStatement('')
    setZone('activation')
    setEffort('medium')
    setStatus('triage')
    setCohortId(cohorts?.[0]?.id || '')
    setImpact(2)
    setConfidence(2)
    setEase(2)
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
      title="New Signal"
      description="Capture a leverage point with evidence."
      contentClassName="max-w-2xl"
    >
      <div className="px-5 pb-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Activation friction: Week-1 dropoff"
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">Zone</label>
            <input
              value={zone}
              onChange={(e) => setZone(e.target.value)}
              placeholder="activation"
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-body-xs text-ink-400 mb-2">Signal statement</label>
            <textarea
              value={statement}
              onChange={(e) => setStatement(e.target.value)}
              rows={3}
              placeholder="Users who do X don’t do Y because Z."
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
            />
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">Effort</label>
            <select
              value={effort}
              onChange={(e) => setEffort(e.target.value)}
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            >
              {EFFORT_OPTIONS.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">Primary cohort</label>
            <select
              value={cohortId}
              onChange={(e) => setCohortId(e.target.value)}
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            >
              <option value="">None</option>
              {(cohorts || []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">ICE: Impact</label>
            <input
              type="number"
              min={0}
              max={5}
              value={impact}
              onChange={(e) => setImpact(e.target.value)}
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">ICE: Confidence</label>
            <input
              type="number"
              min={0}
              max={5}
              value={confidence}
              onChange={(e) => setConfidence(e.target.value)}
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-body-xs text-ink-400 mb-2">ICE: Ease</label>
            <input
              type="number"
              min={0}
              max={5}
              value={ease}
              onChange={(e) => setEase(e.target.value)}
              className="w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
        </div>

        <div className="mt-5 flex items-center justify-end gap-3">
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
              const payload = {
                title: title.trim() || 'Untitled Signal',
                statement: statement.trim(),
                zone: zone.trim() || 'activation',
                effort,
                status,
                cohortIds: cohortId ? [cohortId] : [],
                ice: {
                  impact: Number(impact || 0),
                  confidence: Number(confidence || 0),
                  ease: Number(ease || 0),
                },
              }
              const created = onCreate(payload)
              if (created) {
                onClose()
                reset()
              }
            }}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial"
          >
            Create Signal
          </button>
        </div>
      </div>
    </Modal>
  )
}

const SignalDetail = ({ signal }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    cohorts,
    updateSignal,
    deleteSignal,
    linkSignalToDuel,
  } = useRaptorflowStore()

  const cohortNameById = useMemo(() => {
    const map = new Map()
    ;(cohorts || []).forEach((c) => map.set(c.id, c.name))
    return map
  }, [cohorts])

  const cohortLabel = (signal?.cohortIds || []).map((id) => cohortNameById.get(id) || id).join(', ')

  const linkedDuelIds = signal?.linked?.duelIds || []
  const linkedMoveIds = signal?.linked?.moveIds || []

  const evidence = signal?.evidenceRefs || []

  const openEvidence = (ev) => {
    if (!ev) return
    if (ev.type === 'radar_scan') navigate('/app/radar')
    if (ev.type === 'matrix_metric') navigate('/app/matrix')
    if (ev.type === 'duel' && ev.id) navigate(`/app/black-box/${ev.id}`)
    if (ev.type === 'move' && ev.id) navigate(`/app/moves/${ev.id}`)
  }

  const setStatus = (next) => {
    updateSignal(signal.id, { status: next })
  }

  const handleStartDuel = () => {
    const params = new URLSearchParams(location.search)
    params.set('signalId', signal.id)
    navigate(`/app/black-box/new?${params.toString()}`)
  }

  const handleCreateMove = () => {
    const params = new URLSearchParams(location.search)
    params.set('new', '1')
    params.set('signalId', signal.id)
    params.set('name', signal.title || 'Signal move')
    params.set('durationDays', '7')

    const cohort = signal?.cohortIds?.[0]
    const channel = signal?.channelIds?.[0]
    const metric = signal?.primaryMetric?.name || signal?.primaryMetric?.id

    if (cohort) params.set('cohort', cohort)
    if (channel) params.set('channel', channel)
    if (metric) params.set('metric', metric)

    navigate(`/app/moves?${params.toString()}`)
  }

  const showStatusOptions = STATUS_OPTIONS.filter((s) => s.id !== signal.status)

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <button
            type="button"
            onClick={() => navigate('/app/signals')}
            className="text-body-xs text-ink-400 hover:text-ink mb-2 flex items-center gap-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} />
            Back to Signals
          </button>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="font-serif text-headline-md text-ink">{signal.title}</h1>
            <span className={getStatusPill(signal.status)}>{getStatusLabel(signal.status)}</span>
          </div>
          <div className="mt-2 text-body-sm text-ink-400">
            {signal.zone ? <span className="capitalize">{signal.zone}</span> : null}
            {cohortLabel ? <span> • {cohortLabel}</span> : null}
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap justify-end">
          <button
            type="button"
            onClick={handleStartDuel}
            className="inline-flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm font-medium hover:opacity-95 transition-editorial"
          >
            <Box className="w-4 h-4" strokeWidth={1.5} />
            Start Duel
          </button>
          <button
            type="button"
            onClick={handleCreateMove}
            className="inline-flex items-center gap-2 px-3 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
          >
            <Zap className="w-4 h-4" strokeWidth={1.5} />
            Create Move
          </button>
          <button
            type="button"
            onClick={() => {
              deleteSignal(signal.id)
              navigate('/app/signals')
            }}
            className="inline-flex items-center gap-2 px-3 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
          >
            <Trash2 className="w-4 h-4" strokeWidth={1.5} />
            Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="text-body-xs text-ink-400">Signal statement</div>
            <div className="mt-2 text-body-sm text-ink whitespace-pre-wrap">
              {signal.statement || 'No statement yet.'}
            </div>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 bg-paper rounded-xl border border-border-light">
                <div className="text-[11px] leading-none text-ink-400">Primary metric</div>
                <div className="mt-1 text-body-sm text-ink">{signal?.primaryMetric?.name || '—'}</div>
              </div>
              <div className="p-3 bg-paper rounded-xl border border-border-light">
                <div className="text-[11px] leading-none text-ink-400">Baseline</div>
                <div className="mt-1 text-body-sm text-ink font-mono">{signal?.baseline?.value ?? '—'}</div>
              </div>
              <div className="p-3 bg-paper rounded-xl border border-border-light">
                <div className="text-[11px] leading-none text-ink-400">ICE score</div>
                <div className="mt-1 text-body-sm text-ink font-mono">{Math.round(scoreSignalICE(signal) * 10) / 10}</div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-5">
            <div className="flex items-center justify-between">
              <div className="font-serif text-lg text-ink">Evidence</div>
              <span className="text-[11px] leading-none text-ink-400 px-2 py-1 rounded-full bg-paper border border-border-light">
                {evidence.length}
              </span>
            </div>
            <div className="mt-4 space-y-2">
              {evidence.length === 0 ? (
                <div className="p-4 bg-paper border border-border-light rounded-xl text-body-sm text-ink-400">
                  No evidence linked.
                </div>
              ) : (
                evidence.map((ev, idx) => (
                  <EvidenceRow key={`${ev.type || 'ev'}-${ev.id || idx}`} ev={ev} onOpen={() => openEvidence(ev)} />
                ))
              )}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-5">
            <div className="font-serif text-lg text-ink">Linked work</div>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 bg-paper rounded-xl border border-border-light">
                <div className="text-[11px] leading-none text-ink-400">Duels</div>
                <div className="mt-2 space-y-2">
                  {linkedDuelIds.length === 0 ? (
                    <div className="text-body-xs text-ink-400">None</div>
                  ) : (
                    linkedDuelIds.map((id) => (
                      <button
                        key={id}
                        type="button"
                        onClick={() => navigate(`/app/black-box/${id}`)}
                        className="w-full flex items-center justify-between gap-2 px-3 py-2 bg-paper-200 rounded-lg text-body-xs text-ink hover:bg-paper-200/70 transition-editorial"
                      >
                        <span className="truncate">{id}</span>
                        <ChevronRight className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                      </button>
                    ))
                  )}
                </div>
              </div>
              <div className="p-3 bg-paper rounded-xl border border-border-light">
                <div className="text-[11px] leading-none text-ink-400">Moves</div>
                <div className="mt-2 space-y-2">
                  {linkedMoveIds.length === 0 ? (
                    <div className="text-body-xs text-ink-400">None</div>
                  ) : (
                    linkedMoveIds.map((id) => (
                      <button
                        key={id}
                        type="button"
                        onClick={() => navigate(`/app/moves/${id}`)}
                        className="w-full flex items-center justify-between gap-2 px-3 py-2 bg-paper-200 rounded-lg text-body-xs text-ink hover:bg-paper-200/70 transition-editorial"
                      >
                        <span className="truncate">{id}</span>
                        <ChevronRight className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                      </button>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="font-serif text-lg text-ink">Status</div>
            <div className="mt-3 space-y-2">
              <div className="text-body-xs text-ink-400">Current</div>
              <div className="flex items-center gap-2">
                <Radio className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                <span className="text-body-sm text-ink">{getStatusLabel(signal.status)}</span>
              </div>

              <div className="mt-4 text-body-xs text-ink-400">Move to</div>
              <div className="space-y-2">
                {showStatusOptions.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setStatus(s.id)}
                    className="w-full flex items-center justify-between gap-2 px-3 py-2 bg-paper border border-border-light rounded-xl text-body-sm text-ink hover:bg-paper-200 transition-editorial"
                  >
                    <span>{s.label}</span>
                    <ChevronRight className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-5">
            <div className="font-serif text-lg text-ink">Notes</div>
            <textarea
              value={signal.notes || ''}
              onChange={(e) => updateSignal(signal.id, { notes: e.target.value })}
              rows={6}
              placeholder="Decision notes, mechanism, follow-ups."
              className="mt-3 w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

const SignalsListView = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const { signals, createSignal, deleteSignal } = useRaptorflowStore()

  const [statusFilter, setStatusFilter] = useState('all')
  const [showCreate, setShowCreate] = useState(false)

  const filtered = useMemo(() => {
    const list = Array.isArray(signals) ? signals : []
    return list
      .filter((s) => (statusFilter === 'all' ? true : s.status === statusFilter))
      .map((s) => ({ ...s, iceScore: scoreSignalICE(s) }))
      .sort((a, b) => {
        if ((b.iceScore || 0) !== (a.iceScore || 0)) return (b.iceScore || 0) - (a.iceScore || 0)
        return new Date(b.updatedAt || b.createdAt || 0).getTime() - new Date(a.updatedAt || a.createdAt || 0).getTime()
      })
  }, [signals, statusFilter])

  const handleCreate = (payload) => {
    const created = createSignal(payload)
    if (created?.id) {
      navigate(`/app/signals/${created.id}`)
      return created
    }
    return null
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-serif text-headline-md text-ink">Signals</h1>
          <p className="text-body-sm text-ink-400 mt-1">Rank leverage. Turn signals into tests and moves.</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-card border border-border rounded-lg text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          >
            <option value="all">All statuses</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial"
          >
            <Plus className="w-4 h-4" strokeWidth={1.5} />
            New Signal
          </button>
        </div>
      </div>

      <HairlineTable
        loading={false}
        data={filtered}
        onRowClick={(row) => navigate(`/app/signals/${row.id}`)}
        emptyTitle="No signals yet"
        emptyDescription="Create your first Signal or promote from Radar/Matrix."
        emptyAction="New Signal"
        onEmptyAction={() => setShowCreate(true)}
        columns={[
          {
            key: 'title',
            header: 'Signal',
            render: (row) => (
              <div>
                <div className="text-ink">{row.title}</div>
                <div className="text-xs text-ink-400 capitalize">{row.zone || 'signal'}</div>
              </div>
            ),
          },
          {
            key: 'metric',
            header: 'Primary metric',
            render: (row) => (
              <div>
                <div className="text-ink">{row?.primaryMetric?.name || '—'}</div>
                <div className="text-xs text-ink-400">baseline {row?.baseline?.value ?? '—'}</div>
              </div>
            ),
          },
          {
            key: 'ice',
            header: 'ICE',
            align: 'right',
            render: (row) => <span className="font-mono text-ink">{Math.round((row.iceScore || 0) * 10) / 10}</span>,
          },
          {
            key: 'status',
            header: 'Status',
            align: 'right',
            render: (row) => (
              <span className={getStatusPill(row.status)}>{getStatusLabel(row.status)}</span>
            ),
          },
          {
            key: 'actions',
            header: '',
            align: 'right',
            render: (row) => (
              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    const params = new URLSearchParams(location.search)
                    params.set('signalId', row.id)
                    navigate(`/app/black-box/new?${params.toString()}`)
                  }}
                  className="px-2.5 py-1 text-[11px] border border-primary/20 rounded-md text-primary bg-primary/10 hover:bg-primary/15 transition-editorial"
                >
                  Start Duel
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteSignal(row.id)
                  }}
                  className="px-2.5 py-1 text-[11px] border border-border rounded-md text-ink hover:bg-paper-200 transition-editorial"
                >
                  Delete
                </button>
              </div>
            ),
          },
        ]}
      />

      <CreateSignalModal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreate={handleCreate}
      />
    </div>
  )
}

const SignalsPage = () => {
  const { id } = useParams()
  const { getSignal } = useRaptorflowStore()

  if (id) {
    const signal = getSignal(id)
    if (signal) return <SignalDetail signal={signal} />
  }

  return <SignalsListView />
}

export default SignalsPage
