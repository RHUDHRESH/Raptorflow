import { motion } from 'framer-motion'
import { Calendar, TrendingUp, AlertCircle } from 'lucide-react'
import { cn } from '../../utils/cn'
import MoveCard from './MoveCard'

export default function SprintLane({ sprint, moves = [], maneuverTypes = [], cohorts = [], onMoveClick }) {
  const capacityPercent = sprint.capacity_budget > 0 
    ? Math.min((sprint.current_load / sprint.capacity_budget) * 100, 100)
    : 0

  const getCapacityColor = () => {
    if (capacityPercent >= 90) return 'bg-red-500'
    if (capacityPercent >= 70) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const formatDateRange = () => {
    if (!sprint.start_date || !sprint.end_date) return 'No dates set'
    const start = new Date(sprint.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    const end = new Date(sprint.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    return `${start} - ${end}`
  }

  return (
    <div className="runway-card p-6 mb-6">
      {/* Sprint Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-neutral-200">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="w-5 h-5 text-neutral-700" />
            <h3 className="font-bold text-lg text-neutral-900">{sprint.theme || 'Current Sprint'}</h3>
            {sprint.season_type && (
              <span className={cn(
                "px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] rounded",
                sprint.season_type === 'High_Season' 
                  ? "bg-red-100 text-red-900"
                  : sprint.season_type === 'Low_Season'
                  ? "bg-green-100 text-green-900"
                  : "bg-neutral-100 text-neutral-900"
              )}>
                {sprint.season_type === 'High_Season' ? 'Harvest' : sprint.season_type === 'Low_Season' ? 'Planting' : 'Shoulder'}
              </span>
            )}
          </div>
          <p className="text-sm text-neutral-600">{formatDateRange()}</p>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-neutral-700">Capacity</span>
            <span className={cn(
              "text-sm font-bold",
              capacityPercent >= 90 ? "text-red-600" : capacityPercent >= 70 ? "text-yellow-600" : "text-green-600"
            )}>
              {sprint.current_load} / {sprint.capacity_budget}
            </span>
          </div>
          <div className="w-32 h-2 bg-neutral-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${capacityPercent}%` }}
              transition={{ duration: 0.5 }}
              className={cn("h-full", getCapacityColor())}
            />
          </div>
        </div>
      </div>

      {/* Moves Grid */}
      {moves.length === 0 ? (
        <div className="text-center py-12 text-neutral-400">
          <p className="text-sm">No moves scheduled for this sprint</p>
          <p className="text-xs mt-1">Drag moves from the library to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {moves.map((move) => {
            const maneuverType = maneuverTypes.find(mt => mt.id === move.maneuver_type_id)
            const cohort = cohorts.find(c => c.id === move.primary_cohort_id)
            
            return (
              <MoveCard
                key={move.id}
                move={move}
                maneuverType={maneuverType}
                cohort={cohort}
                onClick={onMoveClick}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}


