import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Users, 
  Target, 
  TrendingUp,
  Plus,
  Calendar,
  CheckCircle2
} from 'lucide-react'
import { cn } from '../utils/cn'
import MoveCard from '../components/moves/MoveCard'
import { 
  createMove, 
  generateMockManeuverTypes,
  MoveStatus,
  Posture
} from '../utils/moveSystemTypes'

// Mock cohort data
const mockCohort = {
  id: 1,
  name: 'Enterprise CTO – Safety Seeker',
  description: 'Chief Technology Officers at enterprise companies prioritizing security and reliability'
}

// Mock moves for this cohort
const mockMoves = [
  createMove({
    id: 'move-1',
    maneuver_type_id: 'authority-sprint',
    primary_icp_id: 1,
    status: MoveStatus.OODA_ACT,
    name: 'Q3 Authority Sprint – Enterprise CTOs',
    start_date: '2025-01-15',
    end_date: '2025-01-29',
    duration_days: 14,
    health_status: 'green',
    metrics: { impressions: 1250, replies: 45, sqls: 3 }
  }),
  createMove({
    id: 'move-2',
    maneuver_type_id: 'garrison',
    primary_icp_id: 1,
    status: MoveStatus.COMPLETE,
    name: 'Churn Defense – Enterprise Accounts',
    start_date: '2024-12-01',
    end_date: '2024-12-15',
    duration_days: 14,
    health_status: 'green',
    metrics: { churn_reduced: 12 }
  }),
  createMove({
    id: 'move-3',
    maneuver_type_id: 'asset-forge',
    primary_icp_id: 1,
    status: MoveStatus.OODA_DECIDE,
    name: 'Security Proof Pack',
    start_date: '2025-01-20',
    end_date: '2025-01-27',
    duration_days: 7,
    health_status: 'amber',
    metrics: {}
  })
]

const maneuverTypes = generateMockManeuverTypes()

export default function CohortsMoves() {
  const { id } = useParams()
  const [cohort] = useState(mockCohort) // In production, fetch by id
  const [moves] = useState(mockMoves)
  const [filterStatus, setFilterStatus] = useState('all')

  const filteredMoves = moves.filter(move => {
    if (filterStatus === 'all') return true
    if (filterStatus === 'active') return move.status.includes('OODA')
    if (filterStatus === 'complete') return move.status === MoveStatus.COMPLETE
    return true
  })

  const activeMoves = moves.filter(m => m.status.includes('OODA')).length
  const completeMoves = moves.filter(m => m.status === MoveStatus.COMPLETE).length
  const totalMoves = moves.length

  // Calculate posture distribution
  const postureDistribution = {
    [Posture.OFFENSIVE]: moves.filter(m => {
      const mt = maneuverTypes.find(mt => mt.id === m.maneuver_type_id)
      return mt?.category === Posture.OFFENSIVE
    }).length,
    [Posture.DEFENSIVE]: moves.filter(m => {
      const mt = maneuverTypes.find(mt => mt.id === m.maneuver_type_id)
      return mt?.category === Posture.DEFENSIVE
    }).length,
    [Posture.LOGISTICAL]: moves.filter(m => {
      const mt = maneuverTypes.find(mt => mt.id === m.maneuver_type_id)
      return mt?.category === Posture.LOGISTICAL
    }).length,
    [Posture.RECON]: moves.filter(m => {
      const mt = maneuverTypes.find(mt => mt.id === m.maneuver_type_id)
      return mt?.category === Posture.RECON
    }).length
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="runway-card p-6">
        <div className="flex items-start gap-4 mb-6">
          <Link
            to="/cohorts"
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-neutral-200 text-neutral-700 hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Users className="w-6 h-6 text-neutral-700" />
              <span className="micro-label tracking-[0.5em]">Cohort Moves</span>
            </div>
            <h1 className="font-serif text-3xl md:text-4xl text-black leading-tight mb-2">
              {cohort.name}
            </h1>
            <p className="text-sm text-neutral-600">{cohort.description}</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-neutral-200">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-1">Total Moves</p>
            <p className="text-2xl font-bold text-neutral-900">{totalMoves}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-1">Active</p>
            <p className="text-2xl font-bold text-blue-600">{activeMoves}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-1">Complete</p>
            <p className="text-2xl font-bold text-green-600">{completeMoves}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-1">Success Rate</p>
            <p className="text-2xl font-bold text-neutral-900">
              {totalMoves > 0 ? Math.round((completeMoves / totalMoves) * 100) : 0}%
            </p>
          </div>
        </div>
      </div>

      {/* Posture Distribution */}
      <div className="runway-card p-6">
        <h2 className="text-lg font-bold text-neutral-900 mb-4">Posture Distribution</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(postureDistribution).map(([posture, count]) => (
            <div key={posture} className="p-4 bg-neutral-50 rounded-lg border border-neutral-200">
              <p className="text-xs text-neutral-600 mb-1">{posture}</p>
              <p className="text-2xl font-bold text-neutral-900">{count}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
        >
          <option value="all">All Moves</option>
          <option value="active">Active</option>
          <option value="complete">Complete</option>
        </select>
        <Link
          to="/moves/library"
          className="inline-flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Move for this cohort
        </Link>
      </div>

      {/* Moves Timeline */}
      <div>
        <h2 className="text-xl font-bold text-neutral-900 mb-4">Timeline</h2>
        <div className="space-y-6">
          {/* Past Moves */}
          {filteredMoves.filter(m => m.status === MoveStatus.COMPLETE).length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-neutral-600 mb-3 uppercase tracking-[0.2em]">
                Past Moves
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredMoves
                  .filter(m => m.status === MoveStatus.COMPLETE)
                  .map((move) => {
                    const maneuverType = maneuverTypes.find(mt => mt.id === move.maneuver_type_id)
                    return (
                      <MoveCard
                        key={move.id}
                        move={move}
                        maneuverType={maneuverType}
                        cohort={cohort}
                      />
                    )
                  })}
              </div>
            </div>
          )}

          {/* Current Moves */}
          {filteredMoves.filter(m => m.status.includes('OODA')).length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-neutral-600 mb-3 uppercase tracking-[0.2em]">
                Current Moves
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredMoves
                  .filter(m => m.status.includes('OODA'))
                  .map((move) => {
                    const maneuverType = maneuverTypes.find(mt => mt.id === move.maneuver_type_id)
                    return (
                      <MoveCard
                        key={move.id}
                        move={move}
                        maneuverType={maneuverType}
                        cohort={cohort}
                      />
                    )
                  })}
              </div>
            </div>
          )}

          {/* Planned Moves */}
          {filteredMoves.filter(m => m.status === MoveStatus.PLANNING).length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-neutral-600 mb-3 uppercase tracking-[0.2em]">
                Planned Moves
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredMoves
                  .filter(m => m.status === MoveStatus.PLANNING)
                  .map((move) => {
                    const maneuverType = maneuverTypes.find(mt => mt.id === move.maneuver_type_id)
                    return (
                      <MoveCard
                        key={move.id}
                        move={move}
                        maneuverType={maneuverType}
                        cohort={cohort}
                      />
                    )
                  })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Empty State */}
      {filteredMoves.length === 0 && (
        <div className="runway-card p-12 text-center">
          <Target className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-neutral-900 mb-2">No moves for this cohort</h3>
          <p className="text-sm text-neutral-600 mb-6">
            Create your first move targeting this cohort
          </p>
          <Link
            to="/moves/library"
            className="inline-flex items-center gap-2 px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Move
          </Link>
        </div>
      )}
    </div>
  )
}


