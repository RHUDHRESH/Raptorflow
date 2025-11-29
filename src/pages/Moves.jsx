import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Target,
  Plus,
  Search,
  Filter,
  ArrowRight,
  Clock,
  Users,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Briefcase,
  Layers
} from 'lucide-react'
import { cn } from '../utils/cn'
import { LuxeHeading, LuxeButton, LuxeCard, LuxeModal, LuxeBadge, LuxeInput, LuxeEmptyState } from '../components/ui/PremiumUI'
import { pageTransition, staggerContainer, fadeInUp } from '../utils/animations'
import { moveService } from '../services/moveService'
import { campaignService } from '../services/campaignService'
import { useWorkspace } from '../context/WorkspaceContext'
import { toast } from '../components/Toast'

// --- Universal goal catalogue ---
const UNIVERSAL_GOALS = [
  { id: 'reach', label: 'Reach', desc: 'Get in front of more of the right people.' },
  { id: 'attention', label: 'Attention & Engagement', desc: 'Make them notice and interact.' },
  { id: 'conversion', label: 'Conversion & Pipeline', desc: 'Turn attention into sign-ups/requests.' },
  { id: 'revenue', label: 'Revenue & Upsell', desc: 'Turn existing interest/users into cash.' },
  { id: 'retention', label: 'Retention & Reactivation', desc: 'Keep people from drifting away.' },
  { id: 'authority', label: 'Authority & Brand Positioning', desc: 'Become the default choice in their head.' },
  { id: 'insight', label: 'Insight & Learning', desc: 'Learn what actually works so everything else gets smarter.' }
]

// --- Mock cohorts ---
const MOCK_COHORTS = [
  { id: 'c1', name: 'Enterprise CTOs', tags: ['ROI-first', 'Time-scarce'], avatar: '🎯' },
  { id: 'c2', name: 'Startup Founders', tags: ['Speed', 'Novelty'], avatar: '🚀' },
  { id: 'c3', name: 'Marketing Directors', tags: ['Habit', 'Trust'], avatar: '📊' },
  { id: 'c4', name: 'Creators', tags: ['Authenticity', 'Engagement'], avatar: '🎨' }
]

// --- Mock Campaigns ---
const MOCK_CAMPAIGNS = [
  { id: 'camp1', name: 'Q4 Enterprise Sprint' },
  { id: 'camp2', name: 'Founder Community Launch' }
]

const JOURNEY_STAGES = [
  { id: 'unaware', label: 'Unaware', color: 'bg-neutral-200' },
  { id: 'problem_aware', label: 'Problem Aware', color: 'bg-amber-100' },
  { id: 'solution_aware', label: 'Solution Aware', color: 'bg-blue-100' },
  { id: 'product_aware', label: 'Product Aware', color: 'bg-purple-100' },
  { id: 'most_aware', label: 'Most Aware', color: 'bg-green-100' },
];

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

const GoalChip = ({ goal, isSelected, isPrimary, onClick }) => (
  <button
    onClick={onClick}
    className={cn(
      'w-full text-left border p-4 rounded-none transition-all hover:border-neutral-900 hover:bg-neutral-50',
      isSelected ? 'border-neutral-900 bg-neutral-50 shadow-sm ring-1 ring-neutral-900' : 'border-neutral-200'
    )}
  >
    <div className="flex justify-between items-center mb-2">
      <span className="font-medium text-lg text-neutral-900">{goal.label}</span>
      {isSelected && (
        <LuxeBadge variant={isPrimary ? 'dark' : 'neutral'}>
          {isPrimary ? 'Primary' : 'Secondary'}
        </LuxeBadge>
      )}
    </div>
    <p className="text-sm text-neutral-600">{goal.desc}</p>
  </button>
)

const CohortCard = ({ cohort, selected, secondary, onClick }) => (
  <button
    onClick={onClick}
    className={cn(
      'w-full text-left border rounded-none p-4 transition-all hover:border-neutral-900 hover:bg-neutral-50 flex items-center gap-3',
      selected ? 'border-neutral-900 bg-neutral-50 shadow-sm ring-1 ring-neutral-900' : 'border-neutral-200',
      secondary ? 'opacity-90' : ''
    )}
  >
    <div className="text-2xl">{cohort.avatar}</div>
    <div className="flex-1">
      <div className="flex items-center gap-2">
        <span className="font-medium text-lg text-neutral-900">{cohort.name}</span>
        {selected && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
      </div>
      <div className="flex gap-2 mt-1 flex-wrap">
        {cohort.tags.map((t) => (
          <span key={t} className="text-[11px] px-2 py-1 bg-white text-neutral-600 border border-neutral-200 rounded-none uppercase tracking-wider">{t}</span>
        ))}
      </div>
    </div>
  </button>
)

const MoveCard = ({ move, index }) => {
  const goalLabel = UNIVERSAL_GOALS.find((g) => g.id === move.primaryGoal)?.label || 'Goal'
  const primaryCohort = MOCK_COHORTS.find((c) => c.id === move.primaryCohort)
  const daysLeft = Math.max(move.timeframe - move.daysElapsed, 0)
  const campaign = MOCK_CAMPAIGNS.find(c => c.id === move.campaignId)
  const fromStage = JOURNEY_STAGES.find(s => s.id === move.journeyStageFrom)
  const toStage = JOURNEY_STAGES.find(s => s.id === move.journeyStageTo)

  return (
    <LuxeCard delay={index * 0.05} className="h-full flex flex-col hover:border-neutral-400 group">
      <Link to={`/moves/${move.id}`} className="flex-1 flex flex-col">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            {campaign && (
              <div className="flex items-center gap-1.5 mb-2 text-xs text-neutral-500">
                <Briefcase className="w-3 h-3" />
                <span>{campaign.name}</span>
              </div>
            )}
            <h3 className="text-xl font-bold font-serif text-neutral-900 mb-2 group-hover:text-neutral-600 transition-colors">
              {move.name}
            </h3>
            <div className="flex flex-wrap items-center gap-2">
              <LuxeBadge variant={move.status === 'active' ? 'success' : 'neutral'}>
                {move.status}
              </LuxeBadge>
              <LuxeBadge variant="neutral">
                {goalLabel}
              </LuxeBadge>
            </div>
          </div>
          <Target className="w-8 h-8 text-neutral-200 group-hover:text-neutral-900 transition-colors" />
        </div>

        <div className="mb-4 flex-1">
          {fromStage && toStage && (
            <div className="flex items-center gap-2 mb-4 text-xs">
              <div className={cn("px-2 py-1 rounded", fromStage.color, "text-neutral-900")}>
                {fromStage.label}
              </div>
              <ArrowRight className="w-3 h-3 text-neutral-400" />
              <div className={cn("px-2 py-1 rounded", toStage.color, "text-neutral-900")}>
                {toStage.label}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-neutral-600">Progress</span>
            <span className="text-lg font-bold text-neutral-900">{move.progress}%</span>
          </div>
          <div className="w-full h-2 bg-neutral-100 rounded-none overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${move.progress}%` }}
              transition={{ duration: 1, delay: index * 0.1 }}
              className="h-full bg-neutral-900 rounded-none"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-neutral-100 mt-auto">
          <div className="flex items-center gap-2 text-sm text-neutral-600">
            <Clock className="w-4 h-4" />
            {daysLeft > 0 ? `Day ${move.daysElapsed} of ${move.timeframe}` : 'Completed'}
          </div>
          <div className="flex items-center gap-2 text-sm text-neutral-600">
            <Users className="w-4 h-4" />
            {primaryCohort?.name || 'Cohort'}
          </div>
          <ArrowRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-900 group-hover:translate-x-1 transition-all" />
        </div>
      </Link>
    </LuxeCard>
  )
}

export default function Moves() {
  const { activeWorkspace } = useWorkspace();
  const [moves, setMoves] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showGuided, setShowGuided] = useState(false)
  
  const [guidedStep, setGuidedStep] = useState(1)
  const [selectedGoals, setSelectedGoals] = useState([])
  const [primaryCohort, setPrimaryCohort] = useState(null)
  const [secondaryCohorts, setSecondaryCohorts] = useState([])
  const [journeyStageFrom, setJourneyStageFrom] = useState(null)
  const [journeyStageTo, setJourneyStageTo] = useState(null)
  const [timeframe, setTimeframe] = useState(14)
  const [intensity, setIntensity] = useState('Standard')
  
  const [recommendations, setRecommendations] = useState([])
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)

  useEffect(() => {
    const fetchMoves = async () => {
      if (!activeWorkspace?.id) return;
      setIsLoading(true);
      try {
        // Try fetching from API via moveService (assuming it handles API calls or supabase directly)
        const data = await moveService.getMoves(activeWorkspace.id);
        if (data) {
            // Map backend data to frontend expectations if needed
            const mappedMoves = data.map(m => ({
                ...m,
                primaryGoal: m.move_type, // Map move_type to primaryGoal
                timeframe: m.end_date && m.start_date ? Math.ceil((new Date(m.end_date) - new Date(m.start_date)) / (1000 * 60 * 60 * 24)) : 14,
                progress: 0, // Mock
                daysElapsed: 0 // Mock
            }));
            setMoves(mappedMoves);
        }
      } catch (err) {
        console.error("Error fetching moves", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMoves();
  }, [activeWorkspace]);

  const filteredMoves = useMemo(() => {
    return moves.filter(move => {
      const matchesSearch = move.name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || move.status === filterStatus
      return matchesSearch && matchesStatus
    })
  }, [moves, searchQuery, filterStatus])

  const resetGuided = () => {
    setGuidedStep(1)
    setSelectedGoals([])
    setPrimaryCohort(null)
    setSecondaryCohorts([])
    setJourneyStageFrom(null)
    setJourneyStageTo(null)
    setTimeframe(14)
    setIntensity('Standard')
    setRecommendations([])
  }

  const toggleGoal = (goalId) => {
    if (selectedGoals.includes(goalId)) {
      setSelectedGoals(selectedGoals.filter(id => id !== goalId))
    } else {
      setSelectedGoals([...selectedGoals, goalId])
    }
  }

  const toggleSecondaryCohort = (cohortId) => {
    if (secondaryCohorts.includes(cohortId)) {
      setSecondaryCohorts(secondaryCohorts.filter(id => id !== cohortId))
    } else {
      setSecondaryCohorts([...secondaryCohorts, cohortId])
    }
  }

  const handleGenerateRecommendations = () => {
    setLoadingRecommendations(true)
    setTimeout(() => {
      setRecommendations([{
        id: 'rec1',
        name: 'AI-Generated Sprint',
        goals: selectedGoals,
        cohorts: [primaryCohort, ...secondaryCohorts].filter(Boolean),
        timeframe,
        intensity,
        promise: 'Boost metrics by 20%',
        actions: ['Email blast', 'Social posts'],
        impact: 'High',
        tradeoffs: 'Requires creative assets'
      }])
      setLoadingRecommendations(false)
      setGuidedStep(5)
    }, 1500)
  }

  const persistMove = (move) => {
    toast.success('Move created!')
    setShowGuided(false)
    resetGuided()
  }

  return (
  <motion.div
    className="max-w-7xl mx-auto px-6 py-8 space-y-8"
    initial="initial"
    animate="animate"
    exit="exit"
    variants={staggerContainer}
  >
    <motion.div variants={fadeInUp} className="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <LuxeHeading level={1}>Moves</LuxeHeading>
        <p className="text-neutral-500 mt-2">Tactical actions to achieve your strategic goals.</p>
      </div>
      <LuxeButton onClick={() => setShowGuided(true)} icon={Plus}>
        New Move
      </LuxeButton>
    </motion.div>

    <motion.div variants={fadeInUp} className="flex flex-col md:flex-row gap-4 items-center bg-white p-4 rounded-none border border-neutral-200">
      <div className="relative flex-1 w-full">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
        <input
          type="text"
          placeholder="Search moves..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 rounded-none border-b-2 border-neutral-200 focus:border-neutral-900 outline-none transition-colors bg-transparent"
        />
      </div>
      <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
        <Filter className="h-4 w-4 text-neutral-400 shrink-0" />
        {['all', 'active', 'planning', 'completed'].map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={cn(
              'px-3 py-1.5 rounded-none text-sm font-bold uppercase tracking-wider whitespace-nowrap transition-colors',
              filterStatus === status
                ? 'bg-neutral-900 text-white'
                : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            )}
          >
            {status}
          </button>
        ))}
      </div>
    </motion.div>

    {isLoading ? (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div>
      </div>
    ) : (
      <>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence mode='popLayout'>
            {filteredMoves.map((move, index) => (
              <MoveCard key={move.id} move={move} index={index} />
            ))}
          </AnimatePresence>
        </div>

        {filteredMoves.length === 0 && (
          <LuxeEmptyState
            icon={Target}
            title="No moves found"
            description="Try adjusting your filters or create a new move."
            action={
              <LuxeButton onClick={() => setShowGuided(true)} variant="secondary" icon={Plus}>
                Create Move
              </LuxeButton>
            }
          />
        )}
      </>
    )}

    {/* Guided Modal */}
    <LuxeModal
      isOpen={showGuided}
      onClose={() => { setShowGuided(false); resetGuided() }}
      title="Design a Move"
      size="xl"
    >
      <div className="space-y-8">
        {/* Step tracker */}
        <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.2em] text-neutral-500 overflow-x-auto pb-2">
          <span className={cn(guidedStep >= 1 ? 'text-neutral-900 font-bold' : '')}>1 Goal</span>
          <ChevronRight className="w-3 h-3" />
          <span className={cn(guidedStep >= 2 ? 'text-neutral-900 font-bold' : '')}>2 Cohorts</span>
          <ChevronRight className="w-3 h-3" />
          <span className={cn(guidedStep >= 3 ? 'text-neutral-900 font-bold' : '')}>3 Journey</span>
          <ChevronRight className="w-3 h-3" />
          <span className={cn(guidedStep >= 4 ? 'text-neutral-900 font-bold' : '')}>4 Tempo</span>
          <ChevronRight className="w-3 h-3" />
          <span className={cn(guidedStep >= 5 ? 'text-neutral-900 font-bold' : '')}>5 Recs</span>
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">Primary Cohort</p>
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
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">Secondary (Optional)</p>
              {MOCK_COHORTS.map((cohort) => (
                <CohortCard
                  key={`s-${cohort.id}`}
                  cohort={cohort}
                  selected={secondaryCohorts.includes(cohort.id)}
                  secondary
                  onClick={() => toggleSecondaryCohort(cohort.id)}
                />
              ))}
            </div>
          </div>
        )}

        {guidedStep === 3 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">From Stage</p>
              <div className="space-y-2">
                {JOURNEY_STAGES.map(stage => (
                  <button
                    key={`from-${stage.id}`}
                    onClick={() => setJourneyStageFrom(stage.id)}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-none border transition-all flex items-center justify-between",
                      journeyStageFrom === stage.id ? "border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900" : "border-neutral-200 hover:border-neutral-400"
                    )}
                  >
                    <span className="text-sm font-medium text-neutral-900">{stage.label}</span>
                    {journeyStageFrom === stage.id && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-3">
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">To Stage</p>
              <div className="space-y-2">
                {JOURNEY_STAGES.map(stage => (
                  <button
                    key={`to-${stage.id}`}
                    onClick={() => setJourneyStageTo(stage.id)}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-none border transition-all flex items-center justify-between",
                      journeyStageTo === stage.id ? "border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900" : "border-neutral-200 hover:border-neutral-400"
                    )}
                  >
                    <span className="text-sm font-medium text-neutral-900">{stage.label}</span>
                    {journeyStageTo === stage.id && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {guidedStep === 4 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">Timeframe</p>
              <div className="grid grid-cols-1 gap-3">
                {TIMEFRAMES.map((tf) => (
                  <button
                    key={tf.value}
                    onClick={() => setTimeframe(tf.value)}
                    className={cn(
                      'text-left border rounded-none p-4 hover:border-neutral-900 hover:bg-neutral-50 transition-all',
                      timeframe === tf.value ? 'border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900' : 'border-neutral-200'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-lg text-neutral-900">{tf.label}</span>
                      {timeframe === tf.value && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                    </div>
                    <p className="text-sm text-neutral-600">{tf.helper}</p>
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-3">
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">Intensity</p>
              <div className="grid grid-cols-1 gap-3">
                {INTENSITIES.map((int) => (
                  <button
                    key={int.value}
                    onClick={() => setIntensity(int.value)}
                    className={cn(
                      'text-left border rounded-none p-4 hover:border-neutral-900 hover:bg-neutral-50 transition-all',
                      intensity === int.value ? 'border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900' : 'border-neutral-200'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-lg text-neutral-900">{int.label}</span>
                      {intensity === int.value && <CheckCircle2 className="w-4 h-4 text-neutral-900" />}
                    </div>
                    <p className="text-sm text-neutral-600">{int.helper}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {guidedStep === 5 && (
          <div className="space-y-4">
            {!loadingRecommendations && recommendations.length > 0 && (
              <div className="grid grid-cols-1 gap-4">
                {recommendations.map((rec) => (
                  <LuxeCard key={rec.id} className="bg-neutral-50 border-neutral-200">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-neutral-500 mb-1">Recommended Move</p>
                        <h3 className="text-xl font-serif text-neutral-900">{rec.name}</h3>
                      </div>
                      <LuxeBadge variant="dark">
                        {UNIVERSAL_GOALS.find((g) => g.id === rec.goals[0])?.label || 'Goal'}
                      </LuxeBadge>
                    </div>
                    <p className="text-sm text-neutral-700 mb-4">{rec.promise}</p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Concrete actions</p>
                        <ul className="space-y-2 text-sm text-neutral-700">
                          {rec.actions.map((a) => <li key={a} className="flex gap-2"><Flame className="w-4 h-4 text-neutral-400 mt-0.5" />{a}</li>)}
                        </ul>
                      </div>
                      <div className="space-y-2">
                        <div className="text-sm text-neutral-700">
                          <span className="font-semibold">Impact:</span> {rec.impact}
                        </div>
                        <div className="text-sm text-neutral-700">
                          <span className="font-semibold">Tradeoffs:</span> {rec.tradeoffs}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-neutral-500 mb-4 pt-4 border-t border-neutral-200">
                      <span>{rec.timeframe} days • {rec.intensity}</span>
                      <span className="flex items-center gap-1"><Users className="w-4 h-4" /> {rec.cohorts.length || 1} cohort(s)</span>
                    </div>
                    <div className="flex gap-3">
                      <LuxeButton
                        onClick={() => persistMove(rec)}
                        className="flex-1"
                      >
                        Use this Move
                      </LuxeButton>
                      <LuxeButton
                        variant="secondary"
                        onClick={() => setRecommendations((prev) => prev.filter((r) => r.id !== rec.id))}
                      >
                        Not my priority
                      </LuxeButton>
                    </div>
                  </LuxeCard>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="flex justify-between items-center pt-6 border-t border-neutral-100">
          <div className="text-xs text-neutral-500 hidden md:block">
            {guidedStep < 5 && 'Universal language only: keep goals/cohorts/timeframe consistent.'}
          </div>
          <div className="flex gap-3 ml-auto">
            {guidedStep > 1 && guidedStep < 5 && (
              <LuxeButton
                variant="secondary"
                onClick={() => setGuidedStep((s) => Math.max(1, s - 1))}
              >
                Back
              </LuxeButton>
            )}
            {guidedStep < 4 && (
              <LuxeButton
                disabled={guidedStep === 1 && selectedGoals.length === 0}
                onClick={() => setGuidedStep((s) => s + 1)}
              >
                Continue
              </LuxeButton>
            )}
            {guidedStep === 4 && (
              <LuxeButton
                onClick={handleGenerateRecommendations}
                isLoading={loadingRecommendations}
              >
                Generate Recommendations
              </LuxeButton>
            )}
            {guidedStep === 5 && (
              <LuxeButton
                variant="secondary"
                onClick={() => { setShowGuided(false); resetGuided() }}
              >
                Close
              </LuxeButton>
            )}
          </div>
        </div>
      </div>
    </LuxeModal>
  </motion.div>
)
}
