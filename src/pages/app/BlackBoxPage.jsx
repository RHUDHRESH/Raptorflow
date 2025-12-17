import { useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Box, 
  Plus, 
  Trophy, 
  Zap, 
  TrendingUp,
  Crown,
  ChevronRight,
  X,
  Loader2,
  Copy,
  Pause,
  Play,
  Search,
  SlidersHorizontal,
  Share2,
  Archive,
  Info,
  MousePointer,
  Users
} from 'lucide-react'
import useRaptorflowStore from '../../store/raptorflowStore'
import { Modal } from '@/components/system/Modal'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

// Duel variable options
const DUEL_VARIABLES = [
  { id: 'hook', name: 'Hook', description: 'Opening line that grabs attention' },
  { id: 'headline', name: 'Headline', description: 'Main headline angle' },
  { id: 'cta', name: 'CTA', description: 'Call to action text' },
  { id: 'offer', name: 'Offer Frame', description: 'How the offer is presented' },
  { id: 'proof', name: 'Proof Order', description: 'Lead with proof vs insight' }
]

// Goal options
const DUEL_GOALS = [
  { id: 'clicks', name: 'Clicks', icon: MousePointer, description: 'Optimize for click-through' },
  { id: 'leads', name: 'Leads', icon: Users, description: 'Optimize for conversions' }
]

const CHANNEL_OPTIONS = [
  { id: 'linkedin', name: 'LinkedIn' },
  { id: 'email', name: 'Email' },
  { id: 'twitter', name: 'X / Twitter' },
  { id: 'website', name: 'Website' }
]

const STATUS_CHIPS = [
  { id: 'all', name: 'All' },
  { id: 'draft', name: 'Draft' },
  { id: 'running', name: 'Running' },
  { id: 'ready', name: 'Ready to Crown' },
  { id: 'winner', name: 'Winner' },
  { id: 'archived', name: 'Archived' }
]

const getDuelMetricTotal = (duel) =>
  duel.goal === 'clicks'
    ? duel.variants.reduce((sum, v) => sum + (v.clicks || 0), 0)
    : duel.variants.reduce((sum, v) => sum + (v.leads || 0), 0)

const getDuelThreshold = (duel) => (duel.goal === 'clicks' ? 100 : 25)

const getDuelLeader = (duel) => {
  const metricKey = duel.goal === 'clicks' ? 'clicks' : 'leads'
  return duel.variants.reduce((best, v) => ((v?.[metricKey] || 0) > (best?.[metricKey] || 0) ? v : best), duel.variants[0])
}

const getDaysSince = (iso) => {
  if (!iso) return null
  const ms = Date.now() - new Date(iso).getTime()
  if (!Number.isFinite(ms) || ms < 0) return null
  return Math.max(0, Math.floor(ms / (24 * 60 * 60 * 1000)))
}

const getDuelStatusLabel = (duel, isReadyToCrown) => {
  if (duel.status === 'archived') return 'Archived'
  if (duel.status === 'winner' || duel.status === 'completed') return 'Winner'
  if (duel.status === 'paused') return 'Paused'
  if (isReadyToCrown) return 'Ready to Crown'
  if (duel.status === 'running') return 'Running'
  return duel.status || 'Draft'
}

const getStatusPillClasses = (statusLabel) => {
  if (statusLabel === 'Ready to Crown') return 'bg-primary/10 text-primary'
  if (statusLabel === 'Winner') return 'bg-primary/10 text-primary'
  if (statusLabel === 'Running') return 'bg-emerald-50 text-emerald-700'
  if (statusLabel === 'Paused') return 'bg-muted text-ink-400'
  if (statusLabel === 'Archived') return 'bg-paper-200 text-ink-400'
  return 'bg-muted text-ink-400'
}

// Duel Card
const DuelCard = ({ duel, onOpen, onPauseToggle, onDuplicate, onCrown, isPulsing, cohortLabel }) => {
  const totalMetric = getDuelMetricTotal(duel)
  const threshold = getDuelThreshold(duel)
  const readiness = Math.min(1, threshold > 0 ? totalMetric / threshold : 0)
  const isReadyToCrown = duel.status === 'running' && readiness >= 1
  const statusLabel = getDuelStatusLabel(duel, isReadyToCrown)
  const leader = getDuelLeader(duel)
  const winner = duel.winner ? duel.variants.find(v => v.id === duel.winner) : null
  const daysRunning = getDaysSince(duel.createdAt)
  const leaderIsWinner = winner?.id && leader?.id && winner.id === leader.id
  const leaderMetric = duel.goal === 'clicks' ? leader?.clicks || 0 : leader?.leads || 0
  const statusTone = statusLabel === 'Ready to Crown' || statusLabel === 'Winner' ? 'text-primary' : 'text-ink-400'
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onOpen}
      className={`px-2 md:px-3 py-3 cursor-pointer transition-editorial group ${
        isPulsing ? 'bg-primary/5' : 'bg-transparent hover:bg-paper/30'
      }`}
      {...(isPulsing
        ? {
            animate: { opacity: 1, y: 0, scale: [1, 1.015, 1] },
            transition: { duration: 0.75, ease: 'easeOut' }
          }
        : {})}
    >
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-serif text-base text-ink truncate group-hover:text-primary transition-editorial">
              {duel.name || `${duel.variable} Duel`}
            </h3>
            <span className={`px-2 py-0.5 rounded text-[11px] leading-none ${getStatusPillClasses(statusLabel)}`}>
              {statusLabel}
            </span>
            <span className="px-2 py-0.5 rounded text-[11px] leading-none bg-paper-200 text-ink-400 capitalize">
              {duel.goal}
            </span>
          </div>
          <div className="mt-1 text-[11px] leading-none text-ink-400 capitalize">
            {duel.channel}{cohortLabel ? ` • ${cohortLabel}` : ''}{daysRunning !== null ? ` • ${daysRunning}d` : ''}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <div className="text-right">
            <div className="text-[11px] leading-none text-ink-400">Primary</div>
            <div className="mt-1 font-mono text-sm text-ink">
              {totalMetric}
              <span className="ml-1 text-[11px] font-sans text-ink-400">
                {duel.goal === 'clicks' ? 'clicks' : 'leads'}
              </span>
            </div>
          </div>

          <div className="text-right">
            <div className="text-[11px] leading-none text-ink-400 flex items-center justify-end gap-1">
              Leader
              {leaderIsWinner && <Crown className="w-3 h-3 text-primary" strokeWidth={1.5} />}
            </div>
            <div className="mt-1 font-mono text-sm text-ink">
              {leader?.label || '—'}
              <span className="ml-1 text-[11px] font-sans text-ink-400">{leaderMetric}</span>
            </div>
          </div>

          <div className="hidden lg:block w-36">
            <div className="flex items-center justify-between text-[11px] leading-none text-ink-400 mb-1">
              <span>Readiness</span>
              <span>{Math.round(readiness * 100)}%</span>
            </div>
            <div className="h-1.5 bg-paper-200 rounded-full overflow-hidden">
              <div className="h-full bg-primary/60" style={{ width: `${Math.round(readiness * 100)}%` }} />
            </div>
          </div>

          <div className="flex items-center gap-1.5 md:opacity-0 md:group-hover:opacity-100 transition-editorial">
            {isReadyToCrown && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onCrown?.()
                }}
                className="px-2.5 py-1 text-[11px] border border-primary/20 rounded-md text-primary bg-primary/10 hover:bg-primary/15 transition-editorial"
              >
                Crown
              </button>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation()
                onOpen()
              }}
              className="px-2.5 py-1 text-[11px] border border-border rounded-md text-ink hover:bg-paper-200 transition-editorial"
            >
              Open
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onPauseToggle()
              }}
              disabled={statusLabel === 'Winner' || statusLabel === 'Archived'}
              className="px-2.5 py-1 text-[11px] border border-border rounded-md text-ink hover:bg-paper-200 transition-editorial disabled:opacity-50"
            >
              {duel.status === 'paused' ? 'Resume' : 'Pause'}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDuplicate()
              }}
              className="px-2.5 py-1 text-[11px] border border-border rounded-md text-ink hover:bg-paper-200 transition-editorial"
            >
              Duplicate
            </button>
            <ChevronRight className="w-4 h-4 text-ink-400 opacity-0 group-hover:opacity-100 transition-editorial" strokeWidth={1.5} />
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// Create Duel Modal
const CreateDuelModal = ({ isOpen, onClose, presetVariable, signalId }) => {
  const navigate = useNavigate()
  const { cohorts, createDuel, canUseBlackBox, usage, getPlanLimits, getSignal, linkSignalToDuel } = useRaptorflowStore()
  const planLimits = getPlanLimits()
  
  const [step, setStep] = useState(1)
  const signal = signalId ? getSignal?.(signalId) : null
  const [formData, setFormData] = useState({
    goal: 'clicks',
    variable: 'hook',
    cohort: cohorts[0]?.id || '',
    channel: 'linkedin',
    variants: [
      { content: '', notes: '' },
      { content: '', notes: '' }
    ]
  })
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    if (!isOpen) return

    const initialCohort = signal?.cohortIds?.[0] || cohorts[0]?.id || ''
    const variable = presetVariable || 'hook'
    const recommendedVariants = variable === 'hook' || variable === 'headline' ? 3 : 2
    const initialChannel = signal?.channelIds?.[0] || 'linkedin'

    setStep(presetVariable ? 2 : 1)
    setFormData({
      goal: 'clicks',
      variable,
      cohort: initialCohort,
      channel: initialChannel,
      variants: Array.from({ length: recommendedVariants }).map(() => ({ content: '', notes: '' }))
    })
  }, [cohorts, isOpen, presetVariable, signal?.channelIds, signal?.cohortIds])

  const canCreate = canUseBlackBox()

  const addVariant = () => {
    if (formData.variants.length < 4) {
      setFormData(prev => ({
        ...prev,
        variants: [...prev.variants, { content: '', notes: '' }]
      }))
    }
  }

  const updateVariant = (index, content) => {
    setFormData(prev => ({
      ...prev,
      variants: prev.variants.map((v, i) => (i === index ? { ...v, content } : v))
    }))
  }

  const updateVariantNotes = (index, notes) => {
    setFormData(prev => ({
      ...prev,
      variants: prev.variants.map((v, i) => (i === index ? { ...v, notes } : v))
    }))
  }

  const removeVariant = (index) => {
    if (formData.variants.length > 2) {
      setFormData(prev => ({
        ...prev,
        variants: prev.variants.filter((_, i) => i !== index)
      }))
    }
  }

  const handleCreate = async () => {
    if (!canCreate) return
    
    setIsCreating(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newDuel = createDuel({
      goal: formData.goal,
      variable: formData.variable,
      cohort: formData.cohort,
      channel: formData.channel,
      signalId: signalId || null,
      name: `${DUEL_VARIABLES.find(v => v.id === formData.variable)?.name || 'Custom'} Duel — ${CHANNEL_OPTIONS.find(c => c.id === formData.channel)?.name || formData.channel}`,
      variants: formData.variants.filter(v => v.content.trim())
    })
    
    setIsCreating(false)
    onClose()
    if (newDuel) {
      if (signalId) {
        linkSignalToDuel?.(signalId, newDuel.id)
      }
      navigate(`/app/black-box/${newDuel.id}`)
    }
  }

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => !open && onClose()}
      title="Start a Duel"
      description={`Step ${step} of 3`}
      contentClassName="max-w-xl"
    >
      {!canCreate && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-body-sm text-amber-700">
          You've reached your duel limit ({usage.blackBoxDuelsThisMonth}/{planLimits.blackBoxDuelsPerMonth} this month)
        </div>
      )}

      {/* Step 1: Goal */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block text-body-sm text-ink mb-3">Pick a Black Move</label>
            <div className="space-y-2">
              {DUEL_VARIABLES.map(variable => (
                <button
                  key={variable.id}
                  onClick={() => {
                    const recommendedVariants = variable.id === 'hook' || variable.id === 'headline' ? 3 : 2
                    setFormData(prev => ({
                      ...prev,
                      variable: variable.id,
                      variants: Array.from({ length: recommendedVariants }).map(() => ({ content: '', notes: '' }))
                    }))
                  }}
                  className={`w-full flex items-center justify-between p-4 rounded-xl border transition-editorial ${
                    formData.variable === variable.id
                      ? 'border-primary bg-signal-muted'
                      : 'border-border hover:border-border-dark'
                  }`}
                >
                  <div className="text-left">
                    <div className="text-body-sm text-ink font-medium">{variable.name} Duel</div>
                    <div className="text-body-xs text-ink-400">{variable.description}</div>
                  </div>
                  {formData.variable === variable.id && (
                    <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => setStep(2)}
            className="w-full px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial"
          >
            Next: Context
          </button>
        </div>
      )}

      {/* Step 2: Variable */}
      {step === 2 && (
        <div className="space-y-4">
          <div>
            <label className="block text-body-sm text-ink mb-3">Context</label>
            <div className="grid grid-cols-2 gap-3">
              {DUEL_GOALS.map(goal => (
                <button
                  key={goal.id}
                  onClick={() => setFormData(prev => ({ ...prev, goal: goal.id }))}
                  className={`flex items-center gap-3 p-4 rounded-xl border transition-editorial ${
                    formData.goal === goal.id
                      ? 'border-primary bg-signal-muted'
                      : 'border-border hover:border-border-dark'
                  }`}
                >
                  <goal.icon className={`w-5 h-5 ${formData.goal === goal.id ? 'text-primary' : 'text-ink-400'}`} strokeWidth={1.5} />
                  <div className="text-left">
                    <div className="text-body-sm text-ink font-medium">{goal.name}</div>
                    <div className="text-body-xs text-ink-400">{goal.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-body-xs text-ink-400 mb-2">Cohort</label>
              <select
                value={formData.cohort}
                onChange={(e) => setFormData(prev => ({ ...prev, cohort: e.target.value }))}
                className="w-full px-3 py-2 bg-paper border border-border rounded-lg text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              >
                {cohorts.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-body-xs text-ink-400 mb-2">Channel</label>
              <select
                value={formData.channel}
                onChange={(e) => setFormData(prev => ({ ...prev, channel: e.target.value }))}
                className="w-full px-3 py-2 bg-paper border border-border rounded-lg text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              >
                {CHANNEL_OPTIONS.map(ch => (
                  <option key={ch.id} value={ch.id}>
                    {ch.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="flex-1 px-4 py-3 border border-border rounded-xl text-ink hover:bg-paper-200 transition-editorial"
            >
              Back
            </button>
            <button
              onClick={() => setStep(3)}
              className="flex-1 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial"
            >
              Next: Variants
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Variants */}
      {step === 3 && (
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-body-sm text-ink">Generate variants</label>
              {formData.variants.length < 4 && (
                <button
                  onClick={addVariant}
                  className="text-body-xs text-primary hover:underline"
                >
                  + Add variant
                </button>
              )}
            </div>
            <div className="space-y-3">
              {formData.variants.map((variant, index) => (
                <div key={index} className="relative">
                  <div className="absolute left-3 top-3 w-6 h-6 bg-paper-200 rounded-full flex items-center justify-center">
                    <span className="text-body-xs font-medium text-ink">
                      {String.fromCharCode(65 + index)}
                    </span>
                  </div>
                  <textarea
                    value={variant.content}
                    onChange={(e) => updateVariant(index, e.target.value)}
                    placeholder={`Variant ${String.fromCharCode(65 + index)} ${formData.variable}...`}
                    rows={2}
                    className="w-full pl-12 pr-10 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
                  />
                  <input
                    value={variant.notes || ''}
                    onChange={(e) => updateVariantNotes(index, e.target.value)}
                    placeholder="Notes (why this variant exists)"
                    className="mt-2 w-full px-3 py-2 bg-paper border border-border rounded-xl text-body-sm text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                  {formData.variants.length > 2 && (
                    <button
                      onClick={() => removeVariant(index)}
                      className="absolute right-3 top-3 p-1 text-ink-400 hover:text-ink"
                    >
                      <X className="w-4 h-4" strokeWidth={1.5} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(2)}
              className="flex-1 px-4 py-3 border border-border rounded-xl text-ink hover:bg-paper-200 transition-editorial"
            >
              Back
            </button>
            <button
              onClick={handleCreate}
              disabled={!canCreate || isCreating || formData.variants.filter(v => v.content.trim()).length < 2}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial disabled:opacity-50"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} />
                  Creating...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" strokeWidth={1.5} />
                  Start Duel
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </Modal>
  )
}

// Duel Detail View
const DuelDetail = ({ duel }) => {
  const navigate = useNavigate()
  const { simulateClicks, crownWinner, promoteWinner, toggleDuelPaused, archiveDuel, cohorts } = useRaptorflowStore()
  const [simulating, setSimulating] = useState(false)
  const [trendMode, setTrendMode] = useState('cumulative')
  const [showPromoteModal, setShowPromoteModal] = useState(false)
  const [shareCopied, setShareCopied] = useState(false)
  
  const cohort = cohorts.find(c => c.id === duel.cohort)
  const winner = duel.winner ? duel.variants.find(v => v.id === duel.winner) : null
  const totalClicks = duel.variants.reduce((sum, v) => sum + v.clicks, 0)
  const totalLeads = duel.variants.reduce((sum, v) => sum + v.leads, 0)
  const totalMetric = getDuelMetricTotal(duel)
  const threshold = getDuelThreshold(duel)
  const readiness = Math.min(1, threshold > 0 ? totalMetric / threshold : 0)
  const isReadyToCrown = duel.status === 'running' && readiness >= 1

  const metricKey = duel.goal === 'clicks' ? 'clicks' : 'leads'
  const metricLabel = duel.goal === 'clicks' ? 'Clicks' : 'Leads'
  const leader = getDuelLeader(duel)
  const control = duel.variants.find(v => v.label === 'A') || duel.variants[0]

  const confidence = readiness >= 1 ? 'High' : readiness >= 0.6 ? 'Medium' : 'Low'
  const upliftVsControl = (() => {
    if (!control || !leader) return 0
    const base = control?.[metricKey] || 0
    const lead = leader?.[metricKey] || 0
    if (base <= 0) return lead > 0 ? 1 : 0
    return (lead - base) / base
  })()

  const leaderboardRows = useMemo(() => {
    const total = duel.variants.reduce((sum, v) => sum + (v?.[metricKey] || 0), 0)
    const base = control?.[metricKey] || 0
    return duel.variants
      .map(v => {
        const value = v?.[metricKey] || 0
        const uplift = base > 0 ? (value - base) / base : 0
        const probability = total > 0 ? value / total : 0
        return { ...v, value, uplift, probability }
      })
      .sort((a, b) => b.value - a.value)
  }, [control, duel.variants, metricKey])

  const trendSeries = useMemo(() => {
    const days = 7
    const labels = Array.from({ length: days }, (_, i) => {
      const d = new Date(Date.now() - (days - 1 - i) * 24 * 60 * 60 * 1000)
      return d.toLocaleDateString([], { weekday: 'short' })
    })

    const variants = duel.variants.map((v, idx) => {
      const total = v?.[metricKey] || 0
      const weights = Array.from({ length: days }, (_, i) => 0.8 + (i + 1) * (0.25 + idx * 0.07))
      const sumW = weights.reduce((s, w) => s + w, 0)
      const daily = weights.map(w => Math.max(0, Math.round((total * w) / sumW)))
      if (trendMode === 'daily') return { variant: v, values: daily }

      const cumulative = daily.reduce((acc, cur) => {
        const prev = acc.length ? acc[acc.length - 1] : 0
        acc.push(prev + cur)
        return acc
      }, [])
      return { variant: v, values: cumulative }
    })

    const max = Math.max(1, ...variants.flatMap(s => s.values))
    return { labels, variants, max }
  }, [duel.variants, metricKey, trendMode])

  const handleSimulate = async (variantId) => {
    setSimulating(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const clicks = Math.floor(Math.random() * 15) + 5
    const leads = Math.floor(Math.random() * 3)
    simulateClicks(duel.id, variantId, clicks, leads)
    
    setSimulating(false)
  }

  const handleCrownWinner = () => {
    crownWinner(duel.id)
  }

  const handlePromote = () => {
    setShowPromoteModal(true)
  }

  const handleConfirmPromote = () => {
    promoteWinner(duel.id)
    setShowPromoteModal(false)
  }

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setShareCopied(true)
      window.setTimeout(() => setShareCopied(false), 1200)
    } catch {
      setShareCopied(false)
    }
  }

  const copySmartLink = (link) => {
    navigator.clipboard.writeText(`https://${link}`)
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="sticky top-0 z-10 -mx-4 px-4 py-4 bg-paper/90 backdrop-blur border-b border-border-light">
        <div className="flex items-start justify-between gap-4">
          <div>
            <button
              onClick={() => navigate('/app/black-box')}
              className="text-body-xs text-ink-400 hover:text-ink mb-2 flex items-center gap-1"
            >
              ← Back to Black Box
            </button>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="font-serif text-headline-md text-ink">{duel.name || `${duel.variable} Duel`}</h1>
              <span className={`px-3 py-1.5 rounded-lg text-body-sm ${getStatusPillClasses(getDuelStatusLabel(duel, isReadyToCrown))}`}>
                {getDuelStatusLabel(duel, isReadyToCrown)}
              </span>
            </div>
            <div className="flex items-center gap-2 flex-wrap mt-2">
              <span className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400">Goal: {metricLabel}</span>
              <span className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400">Cohort: {cohort?.name || 'All'}</span>
              <span className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400 capitalize">Channel: {duel.channel}</span>
              {getDaysSince(duel.createdAt) !== null && (
                <span className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400">Started {getDaysSince(duel.createdAt)}d ago</span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap justify-end">
            {duel.status !== 'winner' && duel.status !== 'archived' && (
              <button
                onClick={() => toggleDuelPaused(duel.id)}
                className="inline-flex items-center gap-2 px-3 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
              >
                {duel.status === 'paused' ? (
                  <Play className="w-4 h-4" strokeWidth={1.5} />
                ) : (
                  <Pause className="w-4 h-4" strokeWidth={1.5} />
                )}
                {duel.status === 'paused' ? 'Resume' : 'Pause'}
              </button>
            )}

            {duel.status === 'running' && (
              <button
                onClick={handleCrownWinner}
                disabled={!isReadyToCrown}
                className="inline-flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm font-medium hover:opacity-95 transition-editorial disabled:opacity-50"
              >
                <Trophy className="w-4 h-4" strokeWidth={1.5} />
                Crown Winner
              </button>
            )}

            {(duel.status === 'winner' || duel.status === 'completed') && !duel.promotedAt && (
              <button
                onClick={handlePromote}
                className="inline-flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm font-medium hover:opacity-95 transition-editorial"
              >
                <TrendingUp className="w-4 h-4" strokeWidth={1.5} />
                Promote Winner
              </button>
            )}

            {(duel.status === 'winner' || duel.status === 'completed') && duel.promotedAt && (
              <span className="px-3 py-2 rounded-lg text-body-sm text-primary bg-primary/10 border border-primary/20">
                Champion promoted
              </span>
            )}

            <button
              onClick={handleShare}
              className="inline-flex items-center gap-2 px-3 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
            >
              <Share2 className="w-4 h-4" strokeWidth={1.5} />
              {shareCopied ? 'Copied' : 'Share'}
            </button>

            <button
              onClick={() => archiveDuel(duel.id)}
              disabled={duel.status === 'archived'}
              className="inline-flex items-center gap-2 px-3 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial disabled:opacity-50"
            >
              <Archive className="w-4 h-4" strokeWidth={1.5} />
              Archive
            </button>
          </div>
        </div>
      </div>

      {/* Winner banner */}
      {winner && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-primary/10 border border-primary/20 rounded-xl flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <Crown className="w-5 h-5 text-white" strokeWidth={1.5} />
            </div>
            <div>
              <div className="text-body-sm text-ink font-medium">
                Variant {winner.label} is crowned.
              </div>
              <div className="text-body-xs text-ink-400">
                {metricLabel}: {winner?.[metricKey] || 0}
              </div>
            </div>
          </div>
          {!duel.promotedAt && (
            <button
              onClick={handlePromote}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
            >
              <TrendingUp className="w-4 h-4" strokeWidth={1.5} />
              Promote Winner
            </button>
          )}
          {duel.promotedAt && (
            <span className="text-body-sm text-primary">✓ Promoted to defaults</span>
          )}
        </motion.div>
      )}

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Variants */}
          <div className="p-5 bg-card border border-border rounded-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-body-sm text-ink font-medium">
                  Variant {leader?.label || '—'} is leading.
                </div>
                <div className="text-body-xs text-ink-400 mt-1">
                  Confidence: {confidence} • Estimated uplift: {Math.round(upliftVsControl * 100)}%
                </div>
                <div className="text-body-xs text-ink-400 mt-1">
                  Data collected: {totalMetric} {duel.goal}
                </div>
              </div>

              <div className="min-w-[180px]">
                <div className="flex items-center justify-between text-body-xs text-ink-400 mb-2">
                  <span>Decision readiness</span>
                  <span>{Math.round(readiness * 100)}%</span>
                </div>
                <div className="h-2 bg-paper-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary/60"
                    style={{ width: `${Math.round(readiness * 100)}%` }}
                  />
                </div>
                <div className="text-body-xs text-ink-400 mt-2">
                  {isReadyToCrown ? 'Ready to crown' : `Need ${Math.max(0, threshold - totalMetric)} more ${duel.goal}`}
                </div>
              </div>
            </div>
          </div>

          <div className="p-5 bg-card border border-border rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-lg text-ink">Leaderboard</h2>
              <span className="text-body-xs text-ink-400">Metric: {metricLabel}</span>
            </div>

            <div className="overflow-hidden rounded-lg border border-border">
              <table className="w-full text-left">
                <thead className="bg-paper-200">
                  <tr className="text-body-xs text-ink-400">
                    <th className="px-3 py-2 font-medium">Variant</th>
                    <th className="px-3 py-2 font-medium">Value</th>
                    <th className="px-3 py-2 font-medium">Uplift vs A</th>
                    <th className="px-3 py-2 font-medium">Prob. best</th>
                  </tr>
                </thead>
                <tbody className="bg-card">
                  {leaderboardRows.map((row) => (
                    <tr key={row.id} className="border-t border-border">
                      <td className="px-3 py-2 text-body-sm text-ink">
                        <span className="font-mono">{row.label}</span>
                        {winner?.id === row.id && (
                          <span className="ml-2 text-body-xs text-primary">Winner</span>
                        )}
                      </td>
                      <td className="px-3 py-2 text-body-sm text-ink font-mono">{row.value}</td>
                      <td className="px-3 py-2 text-body-sm text-ink font-mono">{Math.round(row.uplift * 100)}%</td>
                      <td className="px-3 py-2 text-body-sm text-ink font-mono">{Math.round(row.probability * 100)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="p-5 bg-card border border-border rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-lg text-ink">Trend</h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setTrendMode('cumulative')}
                  className={`px-3 py-1.5 rounded-lg text-body-xs border transition-editorial ${
                    trendMode === 'cumulative'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border bg-card text-ink hover:bg-paper-200'
                  }`}
                >
                  Cumulative
                </button>
                <button
                  onClick={() => setTrendMode('daily')}
                  className={`px-3 py-1.5 rounded-lg text-body-xs border transition-editorial ${
                    trendMode === 'daily'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border bg-card text-ink hover:bg-paper-200'
                  }`}
                >
                  Daily
                </button>
              </div>
            </div>

            <div className="w-full overflow-x-auto">
              <svg viewBox="0 0 640 220" className="w-full h-[220px]">
                {trendSeries.labels.map((_, i) => {
                  const x = 40 + (i * 560) / (trendSeries.labels.length - 1)
                  return (
                    <line
                      key={`grid-${i}`}
                      x1={x}
                      x2={x}
                      y1={20}
                      y2={190}
                      stroke="rgba(0,0,0,0.06)"
                      strokeWidth="1"
                    />
                  )
                })}

                {trendSeries.variants.map((s, seriesIndex) => {
                  const color = seriesIndex === 0 ? 'rgba(255,177,98,0.85)' : seriesIndex === 1 ? 'rgba(44,59,77,0.65)' : 'rgba(44,59,77,0.35)'
                  const points = s.values
                    .map((v, i) => {
                      const x = 40 + (i * 560) / (trendSeries.labels.length - 1)
                      const y = 190 - (v / trendSeries.max) * 170
                      return `${x},${y}`
                    })
                    .join(' ')
                  return (
                    <polyline
                      key={s.variant.id}
                      fill="none"
                      stroke={color}
                      strokeWidth={seriesIndex === 0 ? 3 : 2}
                      points={points}
                      strokeLinejoin="round"
                      strokeLinecap="round"
                    />
                  )
                })}

                {trendSeries.labels.map((label, i) => {
                  const x = 40 + (i * 560) / (trendSeries.labels.length - 1)
                  return (
                    <text
                      key={`label-${i}`}
                      x={x}
                      y={212}
                      textAnchor="middle"
                      fontSize="12"
                      fill="rgba(44,59,77,0.55)"
                      fontFamily="Inter, system-ui"
                    >
                      {label}
                    </text>
                  )
                })}
              </svg>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {/* Stats */}
          {duel.variants.map((variant, index) => {
            const isCurrentLeader = leader?.id === variant.id
            const isWinner = winner?.id === variant.id
            const clickShare = totalClicks > 0 ? Math.round((variant.clicks / totalClicks) * 100) : 0
            const leadShare = totalLeads > 0 ? Math.round((variant.leads / totalLeads) * 100) : 0

            const card = (
              <motion.div
                key={variant.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`p-5 bg-card border rounded-xl ${
                  isWinner ? 'border-primary bg-primary/5' : isCurrentLeader ? 'border-border-dark' : 'border-border'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      isWinner ? 'bg-primary text-white' : isCurrentLeader ? 'bg-signal-muted text-ink' : 'bg-paper-200 text-ink'
                    }`}>
                      <span className="font-medium">{variant.label}</span>
                    </div>
                    {(isWinner || isCurrentLeader) && (
                      <span className={`px-2 py-1 rounded text-body-xs flex items-center gap-1 ${
                        isWinner ? 'bg-primary/10 text-primary' : 'bg-paper-200 text-ink-400'
                      }`}>
                        <Crown className="w-3 h-3" strokeWidth={1.5} />
                        {isWinner ? 'Winner' : 'Leading'}
                      </span>
                    )}
                  </div>

                  {/* Smart link */}
                  <div className="flex items-center gap-2">
                    <code className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400 font-mono">
                      {variant.smartLink}
                    </code>
                    <button
                      onClick={() => copySmartLink(variant.smartLink)}
                      className="p-1.5 text-ink-400 hover:text-ink hover:bg-paper-200 rounded transition-editorial"
                    >
                      <Copy className="w-4 h-4" strokeWidth={1.5} />
                    </button>
                  </div>
                </div>

                {/* Content */}
                <div className="p-4 bg-paper-200 rounded-lg mb-4">
                  <pre className="whitespace-pre-wrap text-body-sm text-ink font-sans">
                    {variant.content}
                  </pre>
                </div>

                <div className="p-4 bg-paper-200 rounded-lg mb-4">
                  <div className="text-body-xs text-ink-400 mb-2">Notes</div>
                  <div className="text-body-sm text-ink">
                    {variant.notes || '—'}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-body-xs text-ink-400 mb-1">Clicks</div>
                    <div className="text-xl font-mono text-ink">{variant.clicks}</div>
                    <div className="text-body-xs text-ink-400">{clickShare}% share</div>
                  </div>
                  <div>
                    <div className="text-body-xs text-ink-400 mb-1">Leads</div>
                    <div className="text-xl font-mono text-ink">{variant.leads}</div>
                    <div className="text-body-xs text-ink-400">{leadShare}% share</div>
                  </div>
                  <div>
                    <div className="text-body-xs text-ink-400 mb-1">CVR</div>
                    <div className="text-xl font-mono text-ink">
                      {variant.clicks > 0 ? ((variant.leads / variant.clicks) * 100).toFixed(1) : '0'}%
                    </div>
                  </div>
                </div>

                {duel.status === 'running' && (
                  <div className="mt-4">
                    <button
                      onClick={() => handleSimulate(variant.id)}
                      disabled={simulating}
                      className="w-full px-3 py-2 text-body-xs text-primary border border-primary/20 rounded-lg hover:bg-signal-muted transition-editorial disabled:opacity-50"
                    >
                      {simulating ? 'Simulating...' : 'Simulate traffic'}
                    </button>
                  </div>
                )}
              </motion.div>
            )

            if (!isCurrentLeader) return card
            return (
              <div
                key={variant.id}
                className="p-[1px] rounded-xl bg-gradient-to-r from-primary/30 via-primary/10 to-primary/30"
              >
                {card}
              </div>
            )
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="mt-8 p-5 bg-card border border-border rounded-xl">
        <h2 className="font-serif text-lg text-ink mb-2">Learnings & Story</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-paper-200 rounded-lg">
            <div className="text-body-xs text-ink-400 mb-2">Hypothesis</div>
            <div className="text-body-sm text-ink">—</div>
          </div>
          <div className="p-4 bg-paper-200 rounded-lg">
            <div className="text-body-xs text-ink-400 mb-2">What changed</div>
            <div className="text-body-sm text-ink">{DUEL_VARIABLES.find(v => v.id === duel.variable)?.name || duel.variable}</div>
          </div>
          <div className="p-4 bg-paper-200 rounded-lg">
            <div className="text-body-xs text-ink-400 mb-2">Result interpretation</div>
            <div className="text-body-sm text-ink">—</div>
          </div>
          <div className="p-4 bg-paper-200 rounded-lg">
            <div className="text-body-xs text-ink-400 mb-2">What to test next</div>
            <div className="text-body-sm text-ink">—</div>
          </div>
        </div>
      </div>

      <Modal
        open={showPromoteModal}
        onOpenChange={(open) => !open && setShowPromoteModal(false)}
        title="Promote winner"
        description="Push the champion into defaults"
        contentClassName="max-w-lg"
      >
        <div className="space-y-4">
          <div className="p-4 bg-paper-200 rounded-lg">
            <div className="text-body-sm text-ink font-medium mb-1">Promote to</div>
            <div className="text-body-xs text-ink-400">Muse defaults • Strategy preferences • Campaign suggestions</div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setShowPromoteModal(false)}
              className="flex-1 px-4 py-3 border border-border rounded-xl text-ink hover:bg-paper-200 transition-editorial"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmPromote}
              className="flex-1 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial"
            >
              Promote
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

// Main Black Box Page
const BlackBoxPage = () => {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const { duels, getDuel, usage, getPlanLimits } = useRaptorflowStore()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createPresetVariable, setCreatePresetVariable] = useState(null)
  const planLimits = getPlanLimits()

  const signalId = useMemo(() => {
    try {
      const params = new URLSearchParams(location.search)
      return params.get('signalId')
    } catch {
      return null
    }
  }, [location.search])

  const isNewRoute = id === 'new' || location.pathname.endsWith('/black-box/new')

  // If viewing a specific duel
  if (id && id !== 'new') {
    const duel = getDuel(id)
    if (duel) {
      return <DuelDetail duel={duel} />
    }
  }

  // Show create modal if /new
  if (isNewRoute) {
    return (
      <>
        <BlackBoxListView 
          duels={duels} 
          onNavigate={navigate} 
          onOpenCreate={(presetVariable) => {
            setCreatePresetVariable(presetVariable || null)
            setShowCreateModal(true)
          }}
          usage={usage}
          planLimits={planLimits}
        />
        <CreateDuelModal
          isOpen={true}
          presetVariable={null}
          signalId={signalId}
          onClose={() => {
            setCreatePresetVariable(null)
            navigate('/app/black-box')
          }}
        />
      </>
    )
  }

  return (
    <>
      <BlackBoxListView 
        duels={duels} 
        onNavigate={navigate} 
        onOpenCreate={(presetVariable) => {
          setCreatePresetVariable(presetVariable || null)
          setShowCreateModal(true)
        }}
        usage={usage}
        planLimits={planLimits}
      />
      <CreateDuelModal
        isOpen={showCreateModal}
        presetVariable={createPresetVariable}
        signalId={signalId}
        onClose={() => {
          setCreatePresetVariable(null)
          setShowCreateModal(false)
        }}
      />
    </>
  )
}

// List view
const BlackBoxListView = ({ duels, onNavigate, onOpenCreate, usage, planLimits }) => {
  const { cohorts, toggleDuelPaused, duplicateDuel, crownWinner } = useRaptorflowStore()
  const blackMovesRef = useRef(null)
  const [statusFilter, setStatusFilter] = useState('all')
  const [channelFilter, setChannelFilter] = useState('all')
  const [cohortFilter, setCohortFilter] = useState('all')
  const [goalFilter, setGoalFilter] = useState('all')
  const [variableFilter, setVariableFilter] = useState('all')
  const [query, setQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [pulsingDuelId, setPulsingDuelId] = useState(null)
  const pulsedReadyRef = useRef(new Set())

  const cohortNameById = useMemo(() => {
    const map = new Map()
    cohorts.forEach(c => map.set(c.id, c.name))
    return map
  }, [cohorts])

  const enrichedDuels = useMemo(() => {
    return duels.map(d => {
      const totalMetric = getDuelMetricTotal(d)
      const threshold = getDuelThreshold(d)
      const readiness = Math.min(1, threshold > 0 ? totalMetric / threshold : 0)
      const isReadyToCrown = d.status === 'running' && readiness >= 1
      const statusLabel = getDuelStatusLabel(d, isReadyToCrown)
      return { duel: d, statusLabel, isReadyToCrown }
    })
  }, [duels])

  useEffect(() => {
    const newlyReady = enrichedDuels.find(({ duel, isReadyToCrown }) =>
      isReadyToCrown && !pulsedReadyRef.current.has(duel.id)
    )
    if (!newlyReady) return

    pulsedReadyRef.current.add(newlyReady.duel.id)
    setPulsingDuelId(newlyReady.duel.id)
    const t = window.setTimeout(() => setPulsingDuelId(null), 900)
    return () => window.clearTimeout(t)
  }, [enrichedDuels])

  const filteredDuels = useMemo(() => {
    const q = query.trim().toLowerCase()

    const statusRank = ({ duel, isReadyToCrown }) => {
      if (isReadyToCrown) return 0
      if (duel.status === 'running') return 1
      if (duel.status === 'paused') return 2
      if (duel.status === 'draft') return 3
      if (duel.status === 'winner' || duel.status === 'completed') return 4
      if (duel.status === 'archived') return 5
      return 6
    }

    return enrichedDuels
      .filter(({ duel, statusLabel, isReadyToCrown }) => {
        if (statusFilter === 'all') return true
        if (statusFilter === 'ready') return isReadyToCrown
        if (statusFilter === 'winner') return duel.status === 'winner' || duel.status === 'completed'
        if (statusFilter === 'archived') return duel.status === 'archived'
        if (statusFilter === 'running') return duel.status === 'running'
        if (statusFilter === 'draft') return duel.status === 'draft'
        return statusLabel.toLowerCase() === statusFilter
      })
      .filter(({ duel }) => (channelFilter === 'all' ? true : duel.channel === channelFilter))
      .filter(({ duel }) => (cohortFilter === 'all' ? true : duel.cohort === cohortFilter))
      .filter(({ duel }) => (goalFilter === 'all' ? true : duel.goal === goalFilter))
      .filter(({ duel }) => (variableFilter === 'all' ? true : duel.variable === variableFilter))
      .filter(({ duel }) => {
        if (!q) return true
        const cohortName = cohortNameById.get(duel.cohort) || ''
        const haystack = [
          duel.name || '',
          duel.variable || '',
          duel.channel || '',
          duel.goal || '',
          cohortName
        ]
          .join(' ')
          .toLowerCase()
        return haystack.includes(q)
      })
      .sort((a, b) => {
        const ra = statusRank(a)
        const rb = statusRank(b)
        if (ra !== rb) return ra - rb
        return new Date(b.duel.createdAt || 0).getTime() - new Date(a.duel.createdAt || 0).getTime()
      })
      .map(({ duel }) => duel)
  }, [channelFilter, cohortFilter, cohortNameById, enrichedDuels, goalFilter, query, statusFilter, variableFilter])

  const hasActiveFilters =
    statusFilter !== 'all' ||
    channelFilter !== 'all' ||
    cohortFilter !== 'all' ||
    goalFilter !== 'all' ||
    variableFilter !== 'all' ||
    query.trim().length > 0

  const activeFilterCount =
    (statusFilter !== 'all' ? 1 : 0) +
    (channelFilter !== 'all' ? 1 : 0) +
    (cohortFilter !== 'all' ? 1 : 0) +
    (goalFilter !== 'all' ? 1 : 0) +
    (variableFilter !== 'all' ? 1 : 0) +
    (query.trim().length > 0 ? 1 : 0)

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-serif text-headline-md text-ink">Black Box</h1>
          <p className="text-body-sm text-ink-400 mt-1">
            Run duels. Crown winners. Promote patterns.
          </p>
        </motion.div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-body-xs text-ink-400">
              {usage.blackBoxDuelsThisMonth}/{planLimits.blackBoxDuelsPerMonth} duels this month
            </span>
            <TooltipProvider delayDuration={120}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    aria-label="Black Box usage info"
                    className="w-6 h-6 inline-flex items-center justify-center rounded-full border border-border text-ink-400 hover:text-ink hover:bg-paper-200 transition-editorial"
                  >
                    <Info className="w-3.5 h-3.5" strokeWidth={1.5} />
                  </button>
                </TooltipTrigger>
                <TooltipContent
                  side="bottom"
                  sideOffset={8}
                  className="bg-card text-ink border border-border shadow-md rounded-xl px-3 py-2"
                >
                  <div className="text-body-sm text-ink font-medium">Black Box usage</div>
                  <div className="text-body-xs text-ink-400 mt-1">
                    Your plan allows {planLimits.blackBoxDuelsPerMonth} duels per month.
                  </div>
                  <div className="text-body-xs text-ink-400 mt-2">
                    Start Duel increments usage. Duplicates also count.
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <button
            onClick={() => blackMovesRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
            className="px-3 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
          >
            Black Moves
          </button>
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => onOpenCreate()}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial"
          >
            <Plus className="w-4 h-4" strokeWidth={1.5} />
            Start Duel
          </motion.button>
        </div>
      </div>

      <div className="sticky top-0 z-10 mb-5">
        <div className="-mx-4 px-4 py-2 bg-paper/85 backdrop-blur">
          <div className="rounded-xl border border-border bg-card/80 backdrop-blur px-3 py-2">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-1.5 flex-wrap md:flex-nowrap md:overflow-x-auto md:whitespace-nowrap">
                {STATUS_CHIPS.map(chip => (
                  <button
                    key={chip.id}
                    onClick={() => setStatusFilter(chip.id)}
                    className={`px-2.5 py-1 rounded-md text-body-xs border transition-editorial ${
                      statusFilter === chip.id
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border bg-card text-ink hover:bg-paper-200'
                    }`}
                  >
                    {chip.name}
                  </button>
                ))}
              </div>

              <div className="flex flex-wrap items-center gap-2 w-full">
                <div className="relative w-full md:w-72">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search"
                    className="w-full pl-9 pr-3 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => setShowFilters(v => !v)}
                  className="md:hidden inline-flex items-center gap-2 px-3 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink hover:bg-paper-200 transition-editorial"
                >
                  <SlidersHorizontal className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Filters
                  {activeFilterCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 rounded-full bg-primary/10 text-primary text-[11px] leading-none">
                      {activeFilterCount}
                    </span>
                  )}
                </button>

                <div className="hidden md:flex items-center gap-2 ml-auto">
                  <div className="text-[11px] leading-none text-ink-400 px-2">
                    {filteredDuels.length} shown
                  </div>

                  {hasActiveFilters && (
                    <button
                      type="button"
                      onClick={() => {
                        setStatusFilter('all')
                        setChannelFilter('all')
                        setCohortFilter('all')
                        setGoalFilter('all')
                        setVariableFilter('all')
                        setQuery('')
                        setShowFilters(false)
                      }}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink hover:bg-paper-200 transition-editorial"
                    >
                      <X className="w-3.5 h-3.5" strokeWidth={1.5} />
                      Reset
                    </button>
                  )}

                  <select
                    value={channelFilter}
                    onChange={(e) => setChannelFilter(e.target.value)}
                    className="px-3 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    <option value="all">Channel</option>
                    {CHANNEL_OPTIONS.map(ch => (
                      <option key={ch.id} value={ch.id}>
                        {ch.name}
                      </option>
                    ))}
                  </select>

                  <select
                    value={cohortFilter}
                    onChange={(e) => setCohortFilter(e.target.value)}
                    className="px-3 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    <option value="all">Cohort</option>
                    {cohorts.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>

                  <select
                    value={goalFilter}
                    onChange={(e) => setGoalFilter(e.target.value)}
                    className="px-3 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    <option value="all">Goal</option>
                    {DUEL_GOALS.map(g => (
                      <option key={g.id} value={g.id}>
                        {g.name}
                      </option>
                    ))}
                  </select>

                  <select
                    value={variableFilter}
                    onChange={(e) => setVariableFilter(e.target.value)}
                    className="px-3 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  >
                    <option value="all">Variable</option>
                    {DUEL_VARIABLES.map(v => (
                      <option key={v.id} value={v.id}>
                        {v.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {showFilters && (
                <div className="md:hidden mt-2 p-2 rounded-xl border border-border-light bg-card/60">
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      value={channelFilter}
                      onChange={(e) => setChannelFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="all">Channel</option>
                      {CHANNEL_OPTIONS.map(ch => (
                        <option key={ch.id} value={ch.id}>
                          {ch.name}
                        </option>
                      ))}
                    </select>

                    <select
                      value={cohortFilter}
                      onChange={(e) => setCohortFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="all">Cohort</option>
                      {cohorts.map(c => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>

                    <select
                      value={goalFilter}
                      onChange={(e) => setGoalFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="all">Goal</option>
                      {DUEL_GOALS.map(g => (
                        <option key={g.id} value={g.id}>
                          {g.name}
                        </option>
                      ))}
                    </select>

                    <select
                      value={variableFilter}
                      onChange={(e) => setVariableFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="all">Variable</option>
                      {DUEL_VARIABLES.map(v => (
                        <option key={v.id} value={v.id}>
                          {v.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="mt-2 flex items-center justify-between gap-2">
                    <div className="text-[11px] leading-none text-ink-400 px-1">
                      {filteredDuels.length} shown
                    </div>
                    <div className="flex items-center gap-2">
                      {hasActiveFilters && (
                        <button
                          type="button"
                          onClick={() => {
                            setStatusFilter('all')
                            setChannelFilter('all')
                            setCohortFilter('all')
                            setGoalFilter('all')
                            setVariableFilter('all')
                            setQuery('')
                            setShowFilters(false)
                          }}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink hover:bg-paper-200 transition-editorial"
                        >
                          <X className="w-3.5 h-3.5" strokeWidth={1.5} />
                          Reset
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() => setShowFilters(false)}
                        className="inline-flex items-center px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-body-xs font-medium hover:opacity-95 transition-editorial"
                      >
                        Done
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Black Moves - Preset experiments */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-8"
        ref={blackMovesRef}
      >
        <h2 className="font-serif text-lg text-ink mb-4">Black Moves</h2>
        <div className="rounded-xl border border-border bg-card/60 px-4 py-3">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-body-sm text-ink font-medium">Pick a fight</div>
              <div className="text-body-xs text-ink-400 mt-1">Choose one variable. We generate 2–4 variants.</div>
            </div>
            <Zap className="w-4 h-4 text-ink-300" strokeWidth={1.5} />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {DUEL_VARIABLES.map((variable) => (
              <button
                key={variable.id}
                title={variable.description}
                onClick={() => onOpenCreate(variable.id)}
                className="px-3 py-1.5 rounded-full border border-border bg-paper text-body-xs text-ink hover:bg-paper-200 transition-editorial"
              >
                {variable.name}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Running duels */}
      {/* Completed duels */}
      {filteredDuels.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <h2 className="font-serif text-lg text-ink mb-4">Arena Lobby</h2>
          <div className="rounded-xl border border-border bg-card/60 overflow-hidden divide-y divide-border-light">
            {filteredDuels.map(duel => (
              <DuelCard
                key={duel.id}
                duel={duel}
                isPulsing={pulsingDuelId === duel.id}
                onOpen={() => onNavigate(`/app/black-box/${duel.id}`)}
                onCrown={() => {
                  crownWinner(duel.id)
                  onNavigate(`/app/black-box/${duel.id}`)
                }}
                onPauseToggle={() => toggleDuelPaused(duel.id)}
                onDuplicate={() => {
                  const duplicated = duplicateDuel(duel.id)
                  if (duplicated) onNavigate(`/app/black-box/${duplicated.id}`)
                }}
                cohortLabel={cohortNameById.get(duel.cohort) || duel.cohort || ''}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* Empty state */}
      {duels.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <Box className="w-16 h-16 text-ink-300 mx-auto mb-4" strokeWidth={1.5} />
          <h2 className="font-serif text-xl text-ink mb-2">No duels yet</h2>
          <p className="text-body-sm text-ink-400 mb-6">Start your first duel to test which variants win</p>
          <button
            onClick={onOpenCreate}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial"
          >
            Start your first duel
          </button>
        </motion.div>
      )}

      {duels.length > 0 && filteredDuels.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <Box className="w-16 h-16 text-ink-300 mx-auto mb-4" strokeWidth={1.5} />
          <h2 className="font-serif text-xl text-ink mb-2">No duels match your filters</h2>
          <p className="text-body-sm text-ink-400 mb-6">Try widening your status or search</p>
          <button
            onClick={() => {
              setStatusFilter('all')
              setChannelFilter('all')
              setCohortFilter('all')
              setGoalFilter('all')
              setVariableFilter('all')
              setQuery('')
            }}
            className="px-6 py-3 border border-border rounded-lg font-medium text-ink hover:bg-paper-200 transition-editorial"
          >
            Reset filters
          </button>
        </motion.div>
      )}
    </div>
  )
}

export default BlackBoxPage
