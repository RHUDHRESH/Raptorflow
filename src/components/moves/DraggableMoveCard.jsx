import { useDraggable } from '@dnd-kit/core'
import { motion } from 'framer-motion'
import { Target, GripVertical } from 'lucide-react'
import { cn } from '../../utils/cn'
import MoveCard from './MoveCard'

export default function DraggableMoveCard({ move, maneuverType, icp, isOverlay = false }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging
  } = useDraggable({
    id: move.id,
    data: {
      move,
      maneuverType,
      icp
    }
  })

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
  } : undefined

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "relative",
        isDragging && "z-50",
        isOverlay && "opacity-50"
      )}
    >
      <div className="relative group">
        {/* Drag Handle */}
        <div
          {...listeners}
          {...attributes}
          className={cn(
            "absolute -left-2 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-neutral-900 text-white flex items-center justify-center cursor-grab active:cursor-grabbing opacity-0 group-hover:opacity-100 transition-opacity duration-180 z-10",
            isDragging && "opacity-100"
          )}
        >
          <GripVertical className="w-4 h-4" />
        </div>
        
        <motion.div
          animate={{
            scale: isDragging ? 1.05 : 1,
            opacity: isDragging ? 0.8 : 1
          }}
          transition={{ duration: 0.18 }}
        >
          <MoveCard
            move={move}
            maneuverType={maneuverType}
            icp={icp}
            compact={false}
          />
        </motion.div>
      </div>
    </div>
  )
}

