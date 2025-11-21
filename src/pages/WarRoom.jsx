import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Target, 
  Calendar, 
  TrendingUp, 
  AlertCircle,
  Plus,
  Filter
} from 'lucide-react'
import { cn } from '../utils/cn'
import SprintLane from '../components/moves/SprintLane'
import SentinelFeed from '../components/moves/SentinelFeed'
import { 
  createSprint, 
  createMove, 
  generateMockManeuverTypes,
  MoveStatus,
  SeasonType
} from '../utils/moveSystemTypes'

// Mock data - in production this would come from API/state management
const mockSprints = [
  createSprint({
    id: 'sprint-1',
    start_date: '2025-01-15',
    end_date: '2025-01-29',
    theme: 'Authority Wave - Week 1',
    capacity_budget: 40,
    current_load: 28,
    season_type: SeasonType.LOW_SEASON,
    move_ids: ['move-1', 'move-2', 'move-3']
  })
]

const mockMoves = [
  createMove({
    id: 'move-1',
    maneuver_type_id: 'authority-sprint',
    sprint_id: 'sprint-1',
    line_of_operation_id: 'loo-1',
    primary_icp_id: 1,
    status: MoveStatus.OODA_ACT,
    start_date: '2025-01-15',
    end_date: '2025-01-29',
    duration_days: 14,
    health_status: 'green',
    metrics: { impressions: 1250, replies: 45, sqls: 3 }
  }),
  createMove({
    id: 'move-2',
    maneuver_type_id: 'asset-forge',
    sprint_id: 'sprint-1',
    line_of_operation_id: 'loo-1',
    primary_icp_id: 1,
    status: MoveStatus.OODA_DECIDE,
    start_date: '2025-01-15',
    end_date: '2025-01-22',
    duration_days: 7,
    health_status: 'amber',
    metrics: {}
  }),
  createMove({
    id: 'move-3',
    maneuver_type_id: 'garrison',
    sprint_id: 'sprint-1',
    line_of_operation_id: 'loo-1',
    primary_icp_id: 2,
    status: MoveStatus.OODA_OBSERVE,
    start_date: '2025-01-20',
    end_date: '2025-01-27',
    duration_days: 7,
    health_status: 'green',
    metrics: { accounts_reviewed: 12 }
  })
]

const mockCohorts = [
  { id: 1, name: 'Enterprise CTOs' },
  { id: 2, name: 'E-commerce Founders' }
]

const mockAnomalies = [
  {
    id: 'anomaly-1',
    move_id: 'move-2',
    move_name: 'Asset Forge – Corporate Proof Pack',
    anomaly_type: 'Tone_Clash',
    severity: 3,
    message: 'Tone Clash: Proposed meme post in Authority Sprint violates Safety Seeker profile – blocked.',
    resolution: 'Content adjusted to match cohort tone guidelines'
  },
  {
    id: 'anomaly-2',
    move_id: 'move-1',
    move_name: 'Authority Sprint – Enterprise CTOs',
    anomaly_type: 'Capacity_Overload',
    severity: 2,
    message: 'Capacity Overload: adding Scarcity Flank will exceed Sprint budget by 6 points.',
    resolution: 'Move scheduled for next sprint'
  }
]

const mockInsights = [
  {
    id: 'insight-1',
    title: "Quest 'Operation First Five' 67% complete – 1 Move remaining.",
    severity: 1
  }
]

export default function WarRoom() {
  const [sprints, setSprints] = useState(mockSprints)
  const [moves, setMoves] = useState(mockMoves)
  const [maneuverTypes] = useState(generateMockManeuverTypes())
  const [cohorts] = useState(mockCohorts)
  const [anomalies, setAnomalies] = useState(mockAnomalies)
  const [insights, setInsights] = useState(mockInsights)
  const [selectedLoo, setSelectedLoo] = useState('all')

  const currentSprint = sprints[0] // In production, get active sprint
  const sprintMoves = moves.filter(m => m.sprint_id === currentSprint?.id)

  const handleDismissAnomaly = (id) => {
    setAnomalies(prev => prev.filter(a => a.id !== id))
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <span className="micro-label tracking-[0.5em]">War Room</span>
            <span className="h-px w-16 bg-neutral-200" />
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-400">Command Center</span>
          </div>
          <div className="space-y-4">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Kinetic Operations
            </h1>
            <p className="font-sans text-base text-neutral-600 max-w-2xl leading-relaxed">
              Directed graph of maneuvers. See all active Moves, Lines of Operation, and Sprints in one view.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Operational Context Bar */}
      <div className="runway-card p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-[0.2em] text-neutral-500">Season:</span>
            <span className={cn(
              "px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] rounded",
              currentSprint?.season_type === SeasonType.LOW_SEASON
                ? "bg-green-100 text-green-900"
                : currentSprint?.season_type === SeasonType.HIGH_SEASON
                ? "bg-red-100 text-red-900"
                : "bg-neutral-100 text-neutral-900"
            )}>
              {currentSprint?.season_type === SeasonType.LOW_SEASON ? 'Planting · Low Season' : 
               currentSprint?.season_type === SeasonType.HIGH_SEASON ? 'Harvest · High Season' : 
               'Shoulder Season'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-[0.2em] text-neutral-500">Sprint:</span>
            <span className="text-sm font-medium text-neutral-900">
              {currentSprint ? `${currentSprint.current_load} / ${currentSprint.capacity_budget} intensity points` : 'No active sprint'}
            </span>
          </div>
          <div className="flex items-center gap-2 flex-1">
            <span className="text-xs uppercase tracking-[0.2em] text-neutral-500">Lines of Operation:</span>
            <div className="flex gap-2">
              {['Direct Bookings Uplift', 'Enterprise Pipeline', 'Operation First Five'].map((loo) => (
                <button
                  key={loo}
                  onClick={() => setSelectedLoo(loo === selectedLoo ? 'all' : loo)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors",
                    selectedLoo === loo
                      ? "border-neutral-900 bg-neutral-900 text-white"
                      : "border-neutral-200 bg-white text-neutral-700 hover:border-neutral-900"
                  )}
                >
                  {loo}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sprint Lanes - Main Area */}
        <div className="lg:col-span-3 space-y-6">
          {currentSprint ? (
            <SprintLane
              sprint={currentSprint}
              moves={sprintMoves}
              maneuverTypes={maneuverTypes}
              cohorts={cohorts}
              onMoveClick={(move) => {
                // Navigate to move detail
                window.location.href = `/moves/${move.id}`
              }}
            />
          ) : (
            <div className="runway-card p-12 text-center">
              <Calendar className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-neutral-900 mb-2">No Active Sprint</h3>
              <p className="text-sm text-neutral-600 mb-6">
                Create a new sprint to start scheduling moves
              </p>
              <button className="inline-flex items-center gap-2 border border-neutral-900 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-colors">
                <Plus className="w-4 h-4" />
                Create Sprint
              </button>
            </div>
          )}
        </div>

        {/* Right Sidebar - Sentinel Feed */}
        <div className="lg:col-span-1">
          <SentinelFeed
            anomalies={anomalies}
            insights={insights}
            onDismiss={handleDismissAnomaly}
          />
        </div>
      </div>
    </div>
  )
}


