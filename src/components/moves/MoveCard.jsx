import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Target, 
  Clock, 
  Users, 
  TrendingUp, 
  AlertCircle,
  CheckCircle2,
  PlayCircle,
  PauseCircle
} from 'lucide-react'
import { cn } from '../../utils/cn'
import { MoveStatus, Posture } from '../../utils/moveSystemTypes'

export default function MoveCard({ move, maneuverType, icp, compact = false, onClick }) {
  const getStatusColor = (status) => {
    if (status === MoveStatus.COMPLETE) return 'bg-green-50 text-green-900 border-green-200'
    if (status === MoveStatus.KILLED) return 'bg-red-50 text-red-900 border-red-200'
    if (status.includes('OODA: Act')) return 'bg-blue-50 text-blue-900 border-blue-200'
    if (status.includes('OODA')) return 'bg-yellow-50 text-yellow-900 border-yellow-200'
    return 'bg-neutral-50 text-neutral-900 border-neutral-200'
  }

  const getHealthRingColor = (health) => {
    if (health === 'green') return 'border-green-500'
    if (health === 'amber') return 'border-yellow-500'
    if (health === 'red') return 'border-red-500'
    return 'border-neutral-300'
  }

  const getPostureColor = (posture) => {
    const colors = {
      [Posture.OFFENSIVE]: 'bg-red-100 text-red-900',
      [Posture.DEFENSIVE]: 'bg-blue-100 text-blue-900',
      [Posture.LOGISTICAL]: 'bg-purple-100 text-purple-900',
      [Posture.RECON]: 'bg-green-100 text-green-900'
    }
    return colors[posture] || 'bg-neutral-100 text-neutral-900'
  }

  const cardContent = (
    <div className={cn(
      "runway-card p-4 hover:shadow-xl transition-all cursor-pointer group",
      compact && "p-3"
    )}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <div className={cn(
              "w-2 h-2 rounded-full border-2",
              getHealthRingColor(move.health_status)
            )} />
            <h3 className={cn(
              "font-bold text-neutral-900 truncate",
              compact ? "text-sm" : "text-base"
            )}>
              {move.name || maneuverType?.name}
            </h3>
          </div>
          {maneuverType && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className={cn(
                "px-2 py-0.5 text-[10px] font-mono uppercase tracking-[0.1em] rounded",
                getPostureColor(maneuverType.category)
              )}>
                {maneuverType.category}
              </span>
              {maneuverType.fogg_role && (
                <span className="px-2 py-0.5 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                  {maneuverType.fogg_role}
                </span>
              )}
              <span className="px-2 py-0.5 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                T{maneuverType?.tier === 'Foundation' ? '1' : maneuverType?.tier === 'Traction' ? '2' : maneuverType?.tier === 'Scale' ? '3' : '4'}
              </span>
            </div>
          )}
        </div>
        <Target className={cn(
          "text-neutral-400 group-hover:text-neutral-900 transition-colors flex-shrink-0",
          compact ? "w-4 h-4" : "w-5 h-5"
        )} />
      </div>

      {/* ICP Chip */}
      {icp && (
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-full bg-neutral-200 flex items-center justify-center">
            <Users className="w-3 h-3 text-neutral-700" />
          </div>
          <span className="text-xs text-neutral-600 truncate">{icp.name}</span>
        </div>
      )}

      {/* Status & Duration */}
      <div className="flex items-center justify-between mb-3">
        <span className={cn(
          "px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] border rounded",
          getStatusColor(move.status)
        )}>
          {move.status}
        </span>
        {move.start_date && (
          <div className="flex items-center gap-1 text-xs text-neutral-500">
            <Clock className="w-3 h-3" />
            <span>{move.duration_days || maneuverType?.base_duration_days || 14}d</span>
          </div>
        )}
      </div>

      {/* Metrics Preview */}
      {move.metrics && Object.keys(move.metrics).length > 0 && !compact && (
        <div className="pt-3 border-t border-neutral-200">
          <div className="flex items-center gap-4 text-xs">
            {move.metrics.impressions && (
              <div className="flex items-center gap-1">
                <TrendingUp className="w-3 h-3 text-neutral-400" />
                <span className="text-neutral-600">{move.metrics.impressions}</span>
              </div>
            )}
            {move.metrics.replies && (
              <div className="flex items-center gap-1">
                <Users className="w-3 h-3 text-neutral-400" />
                <span className="text-neutral-600">{move.metrics.replies}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Anomalies */}
      {move.anomalies_detected && move.anomalies_detected.length > 0 && (
        <div className="mt-2 pt-2 border-t border-yellow-200">
          <div className="flex items-center gap-1 text-xs text-yellow-700">
            <AlertCircle className="w-3 h-3" />
            <span>{move.anomalies_detected.length} alert{move.anomalies_detected.length > 1 ? 's' : ''}</span>
          </div>
        </div>
      )}
    </div>
  )

  if (onClick) {
    return (
      <div onClick={() => onClick(move)}>
        {cardContent}
      </div>
    )
  }

  return (
    <Link to={`/moves/${move.id}`}>
      {cardContent}
    </Link>
  )
}


