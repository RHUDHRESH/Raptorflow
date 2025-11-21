import { useDroppable } from '@dnd-kit/core'
import { motion } from 'framer-motion'
import { Calendar, Plus } from 'lucide-react'
import { cn } from '../../utils/cn'
import MoveCard from './MoveCard'

export default function DroppableSprintLane({ 
  sprint, 
  moves = [], 
  maneuverTypes = [], 
  icps = [],
  onMoveClick 
}) {
  const { setNodeRef, isOver } = useDroppable({
    id: sprint.id,
    data: {
      sprint
    }
  })

  const capacityPercent = sprint.capacity_budget > 0 
    ? Math.min((sprint.current_load / sprint.capacity_budget) * 100, 100)
    : 0

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "runway-card p-6 mb-6 transition-all duration-180",
        isOver && "ring-2 ring-green-500 ring-offset-2 bg-green-50"
      )}
    >
      {/* Sprint Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-neutral-200">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="w-5 h-5 text-neutral-700" />
            <h3 className="font-bold text-lg text-neutral-900">{sprint.theme || 'Current Sprint'}</h3>
          </div>
          <p className="text-sm text-neutral-600">
            {sprint.start_date && sprint.end_date 
              ? `${new Date(sprint.start_date).toLocaleDateString()} - ${new Date(sprint.end_date).toLocaleDateString()}`
              : 'No dates set'}
          </p>
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
              transition={{ duration: 0.3 }}
              className={cn(
                "h-full",
                capacityPercent >= 90 ? "bg-red-500" : capacityPercent >= 70 ? "bg-yellow-500" : "bg-green-500"
              )}
            />
          </div>
        </div>
      </div>

      {/* Drop Zone Indicator */}
      {isOver && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-4 border-2 border-dashed border-green-500 rounded-lg bg-green-50 text-center"
        >
          <p className="text-sm font-medium text-green-900">Drop move here to add to sprint</p>
        </motion.div>
      )}

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
            const icp = icps.find(i => i.id === move.primary_icp_id)
            
            return (
              <MoveCard
                key={move.id}
                move={move}
                maneuverType={maneuverType}
                icp={icp}
                onClick={onMoveClick}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}

