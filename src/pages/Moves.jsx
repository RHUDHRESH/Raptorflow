import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Target,
  Plus,
  Search,
  Filter,
  ArrowRight,
  Clock,
  Users,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  X,
  Loader2,
  Flame,
  Compass
} from 'lucide-react'
import { cn } from '../utils/cn'

// --- Universal goal catalogue (primary + optional secondary) ---
const UNIVERSAL_GOALS = [
  { id: 'reach', label: 'Reach', desc: 'Get in front of more of the right people.' },
  { id: 'attention', label: 'Attention & Engagement', desc: 'Make them notice and interact.' },
  { id: 'conversion', label: 'Conversion & Pipeline', desc: 'Turn attention into sign-ups/requests.' },
  { id: 'revenue', label: 'Revenue & Upsell', desc: 'Turn existing interest/users into cash.' },
  { id: 'retention', label: 'Retention & Reactivation', desc: 'Keep people from drifting away.' },
  { id: 'authority', label: 'Authority & Brand Positioning', desc: 'Become the default choice in their head.' },
  { id: 'insight', label: 'Insight & Learning', desc: 'Learn what actually works so everything else gets smarter.' }
]

// --- Mock cohorts (universal language) ---
const MOCK_COHORTS = [
  { id: 'c1', name: 'Corporate Operators', tags: ['ROI-first', 'Time-scarce', 'Predictability'], avatar: '🏢' },
  { id: 'c2', name: 'Early Adopters', tags: ['Speed', 'Novelty', 'High Tolerance'], avatar: '🚀' },
  { id: 'c3', name: 'Local Regulars', tags: ['Habit', 'Trust', 'Word-of-mouth'], avatar: '📍' },
  { id: 'c4', name: 'Creators', tags: ['Authenticity', 'Engagement', 'Collabs'], avatar: '🎙️' }
]

// --- Mock existing moves with universal schema ---
const INITIAL_MOVES = [
  {
    id: 'm1',
    name: '14-Day Conversion Sprint',
    status: 'active',
    primaryGoal: 'conversion',
    secondaryGoals: ['attention'],
    primaryCohort: 'c1',
    secondaryCohorts: ['c2'],
    timeframe: 14,
    intensity: 'Standard',
    progress: 48,
    daysElapsed: 5
  },
  {
    id: 'm2',
    name: 'Authority Proof Loop',
    status: 'planning',
    primaryGoal: 'authority',
    secondaryGoals: ['reach'],
    primaryCohort: 'c4',
    secondaryCohorts: [],
    timeframe: 28,
    intensity: 'Light',
    progress: 0,
    daysElapsed: 0
  },
  {
    id: 'm3',
    name: 'Retention + Reactivation Pulse',
    status: 'completed',
    primaryGoal: 'retention',
    secondaryGoals: ['insight'],
    primaryCohort: 'c3',
    secondaryCohorts: [],
    timeframe: 14,
    intensity: 'Standard',
    progress: 100,
    daysElapsed: 14
  }
]

const STATUS_META = {
  planning: { label: 'Planning', className: 'bg-amber-50 text-amber-900 border-amber-200' },
  active: { label: 'Active', className: 'bg-green-50 text-green-900 border-green-200' },
  paused: { label: 'Paused', className: 'bg-neutral-100 text-neutral-800 border-neutral-200' },
  completed: { label: 'Completed', className: 'bg-blue-50 text-blue-900 border-blue-200' },
  killed: { label: 'Killed', className: 'bg-rose-50 text-rose-900 border-rose-200' }
}

const TIMEFRAMES = [
  { value: 7, label: '7 days', helper: 'Quick push' },
  { value: 14, label: '14 days', helper: 'Standard sprint' },
  { value: 28, label: '28 days', helper: 'Deep campaign' }
]

const INTENSITIES = [
  { value: 'Light', label: 'Light', helper: '1–2 focused actions / week' },
  { value: 'Standard', label: 'Standard', helper: '3–5 actions / week' },
  { value: 'Aggressive', label: 'Aggressive', helper: 'Daily, multi-channel' }
]

const compatibilityNote = (primaryId, secondaryIds) => {
  if (!primaryId || secondaryIds.length === 0) return null
  if (secondaryIds.length > 2) return { tone: 'warning', text: 'Multiple secondary cohorts selected. Keep messaging distinct.' }
  return { tone: 'ok', text: 'Cohorts share enough overlap. Build variations in Muse.' }
}

export default function Moves() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [moves, setMoves] = useState(INITIAL_MOVES)

  // Guided recommendation modal state
  const [showGuided, setShowGuided] = useState(false)
  const [guidedStep, setGuidedStep] = useState(1)
  const [selectedGoals, setSelectedGoals] = useState([])
  const [primaryCohort, setPrimaryCohort] = useState(null)
  const [secondaryCohorts, setSecondaryCohorts] = useState([])
  const [timeframe, setTimeframe] = useState(14)
  const [intensity, setIntensity] = useState('Standard')
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)
  const [recommendations, setRecommendations] = useState([])

  // Manual creation modal
  const [showManual, setShowManual] = useState(false)
  const [manualStep, setManualStep] = useState(1)

  // hydrate intent from query params (e.g., coming from Cohorts/Matrix/Muse)
  useEffect(() => {
    const cohortId = searchParams.get('cohortId')
    const goalId = searchParams.get('goal')
    if (cohortId) setPrimaryCohort(cohortId)
    if (goalId && UNIVERSAL_GOALS.find((g) => g.id === goalId)) {
      setSelectedGoals([goalId])
    }
  }, [searchParams])

  const filteredMoves = useMemo(() => {
    return moves.filter((move) => {
      const matchesSearch = move.name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesFilter = filterStatus === 'all' || move.status === filterStatus
      return matchesSearch && matchesFilter
    })
  }, [moves, searchQuery, filterStatus])

  const toggleGoal = (goalId) => {
    setSelectedGoals((prev) =>
      prev.includes(goalId) ? prev.filter((g) => g !== goalId) : [...prev, goalId]
    )
  }

  const toggleSecondaryCohort = (id) => {
    if (primaryCohort === id) return
    setSecondaryCohorts((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    )
  }

  const resetGuided = () => {
    setGuidedStep(1)
    setSelectedGoals([])
    setPrimaryCohort(null)
    setSecondaryCohorts([])
    setTimeframe(14)
    setIntensity('Standard')
    setRecommendations([])
    setLoadingRecommendations(false)
  }

  const handleGenerateRecommendations = () => {
    setLoadingRecommendations(true)
    setTimeout(() => {
      const cards = [
        {
          id: `rec-${Date.now()}-1`,
          name: 'Conversion Sprint',
          goals: selectedGoals.length ? selectedGoals : ['conversion'],
          timeframe,
          intensity,
          cohorts: [primaryCohort, ...secondaryCohorts].filter(Boolean),
          promise: 'Turn existing awareness into booked calls by combining proof-heavy posts with direct invites.',
          actions: [
            '4 posts focused on one main proof asset.',
            '1 email recycling the proof with a stronger CTA.',
            '2 outbound blocks of 20 DMs to your primary cohort.'
          ],
          impact: '+20–40% replies, 5–10 leads if executed at Standard intensity.',
          tradeoffs: 'Requires consistent DM blocks; needs at least one strong proof asset.'
        },
        {
          id: `rec-${Date.now()}-2`,
          name: 'Authority Loop',
          goals: ['authority', 'attention'],
          timeframe,
          intensity,
          cohorts: [primaryCohort].filter(Boolean),
          promise: 'Build default-choice positioning with proof + commentary.',
          actions: [
            '2 authority posts (case + POV).',
            'Weekly roundup email.',
            '1 partnership/collab outreach.'
          ],
          impact: 'Higher saves/shares; brand lift for subsequent conversion moves.',
          tradeoffs: 'Impact compounds over time; needs consistent voice.'
        },
        {
          id: `rec-${Date.now()}-3`,
          name: 'Insight Pulse',
          goals: ['insight', 'conversion'],
          timeframe: 7,
          intensity: 'Light',
          cohorts: [primaryCohort].filter(Boolean),
          promise: 'Run lightweight tests to learn fast.',
          actions: [
            '3 message/offer tests across channels.',
            'Daily micro-metrics capture.',
            '1 retrospective to pick winner.'
          ],
          impact: 'Validated hooks for the next sprint; de-risks larger pushes.',
          tradeoffs: 'Short horizon; needs follow-up sprint to exploit winners.'
        }
      ]
      setRecommendations(cards)
      setLoadingRecommendations(false)
      setGuidedStep(4)
    }, 800)
  }

  const persistMove = (card) => {
    const primaryGoal = card.goals[0] || 'conversion'
    const secondaryGoals = card.goals.slice(1)
    const newMove = {
      id: `m-${Date.now()}`,
      name: card.name,
      status: 'planning',
      primaryGoal,
      secondaryGoals,
      primaryCohort: primaryCohort || 'c1',
      secondaryCohorts,
      timeframe: card.timeframe || timeframe,
      intensity: card.intensity || intensity,
      progress: 0,
      daysElapsed: 0
    }
    setMoves((prev) => [newMove, ...prev])
    setShowGuided(false)
    resetGuided()
  }

  const createManualMove = () => {
    if (!selectedGoals.length || !primaryCohort) return
    const newMove = {
      id: `m-${Date.now()}`,
      name: 'Custom Move',
      status: 'planning',
      primaryGoal: selectedGoals[0],
      secondaryGoals: selectedGoals.slice(1),
      primaryCohort,
      secondaryCohorts,
      timeframe,
      intensity,
      progress: 0,
      daysElapsed: 0
    }
    setMoves((prev) => [newMove, ...prev])
    setShowManual(false)
    setManualStep(1)
    resetGuided()
  }

  const GoalChip = ({ goal, isSelected, isPrimary, onClick }) => (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left border p-4 rounded-lg transition-all hover:border-neutral-900 hover:bg-neutral-50',
        isSelected ? 'border-neutral-900 bg-neutral-100 shadow-sm' : 'border-neutral-200'
      )}
    >
      <div className="flex justify-between items-center mb-2">
        <span className="font-serif text-lg text-neutral-900">{goal.label}</span>
        {isSelected && (
          <span className={cn(
            'text-[10px] font-mono uppercase tracking-[0.2em] px-2 py-1 border',
            isPrimary ? 'bg-neutral-900 text-white border-neutral-900' : 'bg-neutral-200 text-neutral-700 border-neutral-300'
          )}>
            {isPrimary ? 'Primary' : 'Secondary'}
          </span>
        )}
      </div>
      <p className="text-sm text-neutral-600">{goal.desc}</p>
    </button>
  )

  const CohortCard = ({ cohort, selected, secondary, onClick }) => (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left border rounded-lg p-4 transition-all hover:border-neutral-900 hover:bg-neutral-50 flex items-center gap-3',
        selected ? 'border-neutral-900 bg-neutral-100 shadow-sm' : 'border-neutral-200',
        secondary ? 'opacity-90' : ''
      )}
    >
      <div className="text-2xl">{cohort.avatar}</div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-serif text-lg text-neutral-900">{cohort.name}</span>
          {selected && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
        </div>
        <div className="flex gap-2 mt-1 flex-wrap">
          {cohort.tags.map((t) => (
            <span key={t} className="text-[11px] px-2 py-1 bg-neutral-100 text-neutral-700 border border-neutral-200 rounded">{t}</span>
          ))}
        </div>
      </div>
    </button>
  )

  const MoveCard = ({ move, index }) => {
    const goalLabel = UNIVERSAL_GOALS.find((g) => g.id === move.primaryGoal)?.label || 'Goal'
    const primaryCohort = MOCK_COHORTS.find((c) => c.id === move.primaryCohort)
    const status = STATUS_META[move.status] || STATUS_META.planning
    const daysLeft = Math.max(move.timeframe - move.daysElapsed, 0)

    return (
      <motion.div
        key={move.id}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }}
      >
        <Link
          to={`/moves/${move.id}`}
          className="block runway-card p-6 hover:shadow-xl transition-all group"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-xl font-bold text-neutral-900 mb-2 group-hover:text-neutral-700 transition-colors">
                {move.name}
              </h3>
              <div className="flex flex-wrap items-center gap-2">
                <span className={cn(
                  'px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border',
                  status.className
                )}>
                  {status.label}
                </span>
                <span className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border bg-neutral-50 text-neutral-900 border-neutral-200">
                  {goalLabel}
                </span>
                {move.secondaryGoals?.length > 0 && (
                  <span className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border bg-neutral-100 text-neutral-700 border-neutral-200">
                    +{move.secondaryGoals.length} focus
                  </span>
                )}
              </div>
            </div>
            <Target className="w-8 h-8 text-neutral-700" />
          </div>

          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Progress</span>
              <span className="text-lg font-bold text-neutral-900">{move.progress}%</span>
            </div>
            <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${move.progress}%` }}
                transition={{ duration: 1, delay: index * 0.1 }}
                className="h-full bg-gradient-to-r from-neutral-700 to-neutral-900 rounded-full"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-neutral-200">
            <div className="flex items-center gap-2 text-sm text-neutral-600">
              <Clock className="w-4 h-4" />
              {daysLeft > 0 ? `Day ${move.daysElapsed} of ${move.timeframe}` : 'Completed'}
            </div>
            <div className="flex items-center gap-2 text-sm text-neutral-600">
              <Users className="w-4 h-4" />
              {primaryCohort?.name || 'Cohort'}
            </div>
            <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-neutral-900 group-hover:translate-x-1 transition-all" />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              onClick={(e) => { e.preventDefault(); navigate(`/matrix?moveId=${move.id}`) }}
              className="text-xs font-semibold text-neutral-700 hover:text-neutral-900 underline"
            >
              Open in Matrix
            </button>
            <button
              onClick={(e) => { e.preventDefault(); navigate(`/muse?moveId=${move.id}&cohortId=${move.primaryCohort}`) }}
              className="text-xs font-semibold text-neutral-700 hover:text-neutral-900 underline"
            >
              Draft in Muse
            </button>
          </div>
        </Link>
      </motion.div>
    )
  }

  const GuidedModal = () => (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-neutral-200">
          <div>
            <p className="micro-label mb-1">Guided Recommendations</p>
            <h2 className="text-2xl font-serif text-neutral-900">Design a universal Move</h2>
          </div>
          <button
            onClick={() => { setShowGuided(false); resetGuided() }}
            className="p-2 rounded-full hover:bg-neutral-100 text-neutral-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {/* Step tracker */}
          <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.2em] text-neutral-500">
            <span className={cn(guidedStep >= 1 ? 'text-neutral-900' : '')}>1 Goal</span>
            <span>·</span>
            <span className={cn(guidedStep >= 2 ? 'text-neutral-900' : '')}>2 Cohorts</span>
            <span>·</span>
            <span className={cn(guidedStep >= 3 ? 'text-neutral-900' : '')}>3 Tempo</span>
            <span>·</span>
            <span className={cn(guidedStep >= 4 ? 'text-neutral-900' : '')}>4 Recommendations</span>
          </div>

          {guidedStep === 1 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {UNIVERSAL_GOALS.map((goal) => (
                <GoalChip
                  key={goal.id}
                  goal={goal}
                  isSelected={selectedGoals.includes(goal.id)}
                  isPrimary={selectedGoals[0] === goal.id}
                  onClick={() => toggleGoal(goal.id)}
                />
              ))}
            </div>
          )}

          {guidedStep === 2 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <p className="micro-label">Primary Cohort (required)</p>
                {MOCK_COHORTS.map((cohort) => (
                  <CohortCard
                    key={`p-${cohort.id}`}
                    cohort={cohort}
                    selected={primaryCohort === cohort.id}
                    onClick={() => setPrimaryCohort(cohort.id)}
                  />
                ))}
              </div>
              <div className="space-y-3">
                <p className="micro-label">Also interesting for (optional)</p>
                {MOCK_COHORTS.map((cohort) => (
                  <CohortCard
                    key={`s-${cohort.id}`}
                    cohort={cohort}
                    selected={secondaryCohorts.includes(cohort.id)}
                    secondary
                    onClick={() => toggleSecondaryCohort(cohort.id)}
                  />
                ))}
                {compatibilityNote(primaryCohort, secondaryCohorts) && (
                  <div className={cn(
                    'p-3 border rounded-lg text-sm',
                    compatibilityNote(primaryCohort, secondaryCohorts)?.tone === 'warning'
                      ? 'border-amber-200 bg-amber-50 text-amber-800'
                      : 'border-green-200 bg-green-50 text-green-800'
                  )}>
                    {compatibilityNote(primaryCohort, secondaryCohorts)?.tone === 'warning' ? <AlertTriangle className="w-4 h-4 inline mr-2" /> : <CheckCircle2 className="w-4 h-4 inline mr-2" />}
                    {compatibilityNote(primaryCohort, secondaryCohorts)?.text}
                  </div>
                )}
              </div>
            </div>
          )}

          {guidedStep === 3 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <p className="micro-label">Timeframe</p>
                <div className="grid grid-cols-1 gap-3">
                  {TIMEFRAMES.map((tf) => (
                    <button
                      key={tf.value}
                      onClick={() => setTimeframe(tf.value)}
                      className={cn(
                        'text-left border rounded-lg p-4 hover:border-neutral-900 hover:bg-neutral-50 transition-all',
                        timeframe === tf.value ? 'border-neutral-900 bg-neutral-100' : 'border-neutral-200'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-lg text-neutral-900">{tf.label}</span>
                        {timeframe === tf.value && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                      </div>
                      <p className="text-sm text-neutral-600">{tf.helper}</p>
                    </button>
                  ))}
                </div>
              </div>
              <div className="space-y-3">
                <p className="micro-label">Intensity</p>
                <div className="grid grid-cols-1 gap-3">
                  {INTENSITIES.map((int) => (
                    <button
                      key={int.value}
                      onClick={() => setIntensity(int.value)}
                      className={cn(
                        'text-left border rounded-lg p-4 hover:border-neutral-900 hover:bg-neutral-50 transition-all',
                        intensity === int.value ? 'border-neutral-900 bg-neutral-100' : 'border-neutral-200'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-lg text-neutral-900">{int.label}</span>
                        {intensity === int.value && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                      </div>
                      <p className="text-sm text-neutral-600">{int.helper}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {guidedStep === 4 && (
            <div className="space-y-4">
              {loadingRecommendations && (
                <div className="flex items-center gap-3 text-neutral-700">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating universal recommendations...
                </div>
              )}
              {!loadingRecommendations && recommendations.length === 0 && (
                <div className="text-neutral-600">No recommendations yet.</div>
              )}
              {!loadingRecommendations && recommendations.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {recommendations.map((rec) => (
                    <div key={rec.id} className="border rounded-lg p-5 bg-neutral-50 hover:bg-white transition-shadow hover:shadow-md">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="micro-label mb-1">Recommended Move</p>
                          <h3 className="text-xl font-serif text-neutral-900">{rec.name}</h3>
                        </div>
                        <span className="px-3 py-1 text-[10px] font-mono uppercase tracking-[0.2em] border bg-neutral-900 text-white border-neutral-900">
                          {UNIVERSAL_GOALS.find((g) => g.id === rec.goals[0])?.label || 'Goal'}
                        </span>
                      </div>
                      <p className="text-sm text-neutral-700 mb-3">{rec.promise}</p>
                      <div className="mb-3">
                        <p className="micro-label mb-1">Concrete actions</p>
                        <ul className="space-y-2 text-sm text-neutral-700">
                          {rec.actions.map((a) => <li key={a} className="flex gap-2"><Flame className="w-4 h-4 text-neutral-500 mt-0.5" />{a}</li>)}
                        </ul>
                      </div>
                      <div className="mb-3 text-sm text-neutral-700">
                        <span className="font-semibold">Impact:</span> {rec.impact}
                      </div>
                      <div className="mb-4 text-sm text-neutral-700">
                        <span className="font-semibold">Tradeoffs:</span> {rec.tradeoffs}
                      </div>
                      <div className="flex items-center justify-between text-[12px] text-neutral-600 mb-4">
                        <span>{rec.timeframe} days • {rec.intensity}</span>
                        <span className="flex items-center gap-1"><Users className="w-4 h-4" /> {rec.cohorts.length || 1} cohort(s)</span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => persistMove(rec)}
                          className="flex-1 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 text-sm font-semibold"
                        >
                          Use this Move
                        </button>
                        <button
                          onClick={() => setRecommendations((prev) => prev.filter((r) => r.id !== rec.id))}
                          className="px-4 py-2 border border-neutral-300 rounded-lg text-sm text-neutral-700 hover:border-neutral-900"
                        >
                          Not my priority
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="p-6 border-t border-neutral-200 flex justify-between items-center bg-neutral-50">
          <div className="text-sm text-neutral-600">
            {guidedStep < 4 && 'Universal language only: keep goals/cohorts/timeframe consistent across industries.'}
          </div>
          <div className="flex gap-2">
            {guidedStep > 1 && guidedStep < 4 && (
              <button
                onClick={() => setGuidedStep((s) => Math.max(1, s - 1))}
                className="px-4 py-2 text-neutral-700 border border-neutral-300 rounded-lg hover:border-neutral-900 text-sm"
              >
                Back
              </button>
            )}
            {guidedStep < 3 && (
              <button
                disabled={guidedStep === 1 && selectedGoals.length === 0}
                onClick={() => setGuidedStep((s) => s + 1)}
                className="px-5 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 disabled:opacity-50 text-sm"
              >
                Continue
              </button>
            )}
            {guidedStep === 3 && (
              <button
                onClick={handleGenerateRecommendations}
                className="px-5 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 text-sm"
              >
                Generate Recommendations
              </button>
            )}
            {guidedStep === 4 && (
              <button
                onClick={() => { setShowGuided(false); resetGuided() }}
                className="px-5 py-2 border border-neutral-300 rounded-lg text-sm text-neutral-700 hover:border-neutral-900"
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  const ManualModal = () => (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-neutral-200">
          <div>
            <p className="micro-label mb-1">New Move</p>
            <h2 className="text-2xl font-serif text-neutral-900">Build a Move manually</h2>
          </div>
          <button
            onClick={() => { setShowManual(false); setManualStep(1); resetGuided() }}
            className="p-2 rounded-full hover:bg-neutral-100 text-neutral-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.2em] text-neutral-500">
            <span className={cn(manualStep >= 1 ? 'text-neutral-900' : '')}>1 Goal</span>
            <span>·</span>
            <span className={cn(manualStep >= 2 ? 'text-neutral-900' : '')}>2 Cohorts</span>
            <span>·</span>
            <span className={cn(manualStep >= 3 ? 'text-neutral-900' : '')}>3 Tempo</span>
          </div>

          {manualStep === 1 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {UNIVERSAL_GOALS.map((goal) => (
                <GoalChip
                  key={`m-${goal.id}`}
                  goal={goal}
                  isSelected={selectedGoals.includes(goal.id)}
                  isPrimary={selectedGoals[0] === goal.id}
                  onClick={() => toggleGoal(goal.id)}
                />
              ))}
            </div>
          )}

          {manualStep === 2 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <p className="micro-label">Primary Cohort</p>
                {MOCK_COHORTS.map((cohort) => (
                  <CohortCard
                    key={`mp-${cohort.id}`}
                    cohort={cohort}
                    selected={primaryCohort === cohort.id}
                    onClick={() => setPrimaryCohort(cohort.id)}
                  />
                ))}
              </div>
              <div className="space-y-3">
                <p className="micro-label">Secondary Cohorts (optional)</p>
                {MOCK_COHORTS.map((cohort) => (
                  <CohortCard
                    key={`ms-${cohort.id}`}
                    cohort={cohort}
                    selected={secondaryCohorts.includes(cohort.id)}
                    secondary
                    onClick={() => toggleSecondaryCohort(cohort.id)}
                  />
                ))}
              </div>
            </div>
          )}

          {manualStep === 3 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <p className="micro-label">Timeframe</p>
                <div className="grid grid-cols-1 gap-3">
                  {TIMEFRAMES.map((tf) => (
                    <button
                      key={`mtf-${tf.value}`}
                      onClick={() => setTimeframe(tf.value)}
                      className={cn(
                        'text-left border rounded-lg p-4 hover:border-neutral-900 hover:bg-neutral-50 transition-all',
                        timeframe === tf.value ? 'border-neutral-900 bg-neutral-100' : 'border-neutral-200'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-lg text-neutral-900">{tf.label}</span>
                        {timeframe === tf.value && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                      </div>
                      <p className="text-sm text-neutral-600">{tf.helper}</p>
                    </button>
                  ))}
                </div>
              </div>
              <div className="space-y-3">
                <p className="micro-label">Intensity</p>
                <div className="grid grid-cols-1 gap-3">
                  {INTENSITIES.map((int) => (
                    <button
                      key={`mint-${int.value}`}
                      onClick={() => setIntensity(int.value)}
                      className={cn(
                        'text-left border rounded-lg p-4 hover:border-neutral-900 hover:bg-neutral-50 transition-all',
                        intensity === int.value ? 'border-neutral-900 bg-neutral-100' : 'border-neutral-200'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-lg text-neutral-900">{int.label}</span>
                        {intensity === int.value && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                      </div>
                      <p className="text-sm text-neutral-600">{int.helper}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-neutral-200 flex justify-between items-center bg-neutral-50">
          <div className="text-sm text-neutral-600">Universal, not industry-specific. Primary goal + cohort are required.</div>
          <div className="flex gap-2">
            {manualStep > 1 && (
              <button
                onClick={() => setManualStep((s) => Math.max(1, s - 1))}
                className="px-4 py-2 text-neutral-700 border border-neutral-300 rounded-lg hover:border-neutral-900 text-sm"
              >
                Back
              </button>
            )}
            {manualStep < 3 && (
              <button
                disabled={manualStep === 1 && selectedGoals.length === 0}
                onClick={() => setManualStep((s) => s + 1)}
                className="px-5 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 disabled:opacity-50 text-sm"
              >
                Continue
              </button>
            )}
            {manualStep === 3 && (
              <button
                onClick={createManualMove}
                disabled={!selectedGoals.length || !primaryCohort}
                className="px-5 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 disabled:opacity-50 text-sm"
              >
                Save Move
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card flex flex-col gap-6 p-8 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <p className="micro-label mb-2">Universal Plays</p>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased mb-2">
            Moves in Motion
          </h1>
          <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
            Same structure for every industry
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => { setShowGuided(true); resetGuided() }}
            className="inline-flex items-center gap-2 border border-neutral-900 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            Guided Recommendations
          </button>
          <button
            onClick={() => { setShowManual(true); resetGuided() }}
            className="inline-flex items-center gap-2 border border-neutral-200 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-600 hover:border-neutral-900 hover:text-neutral-900 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Move
          </button>
          <Link
            to="/moves/war-room"
            className="inline-flex items-center gap-2 border border-neutral-200 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-600 hover:border-neutral-900 hover:text-neutral-900 transition-colors"
          >
            <Compass className="w-4 h-4" />
            War Room
          </Link>
          <Link
            to="/moves/library"
            className="inline-flex items-center gap-2 border border-neutral-200 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-600 hover:border-neutral-900 hover:text-neutral-900 transition-colors"
          >
            <Target className="w-4 h-4" />
            Library
          </Link>
        </div>
      </motion.div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <input
            type="text"
            placeholder="Search moves..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full border-b-2 border-neutral-200 bg-transparent py-4 pl-12 pr-4 focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="appearance-none border-b-2 border-neutral-200 bg-transparent py-4 pl-12 pr-8 focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg"
          >
            <option value="all">All Status</option>
            <option value="planning">Planning</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="completed">Completed</option>
            <option value="killed">Killed</option>
          </select>
        </div>
      </div>

      {/* Moves Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredMoves.map((move, index) => (
          <MoveCard key={move.id} move={move} index={index} />
        ))}
        {filteredMoves.length === 0 && (
          <div className="col-span-full border border-dashed border-neutral-200 p-10 rounded-xl text-center text-neutral-500">
            No moves yet. Start with Guided Recommendations or create one manually.
          </div>
        )}
      </div>

      {showGuided && <GuidedModal />}
      {showManual && <ManualModal />}
    </div>
  )
}
