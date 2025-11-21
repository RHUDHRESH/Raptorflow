import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, CheckCircle2, Info, AlertTriangle, TrendingUp, Lock } from 'lucide-react'
import { cn } from '../../utils/cn'
import { AnomalyType } from '../../utils/moveSystemTypes'

export default function SentinelFeed({ anomalies = [], insights = [], onDismiss }) {
  const getAnomalyIcon = (type) => {
    const icons = {
      [AnomalyType.TONE_CLASH]: AlertCircle,
      [AnomalyType.FATIGUE]: AlertTriangle,
      [AnomalyType.DRIFT]: TrendingUp,
      [AnomalyType.RULE_VIOLATION]: Lock,
      [AnomalyType.CAPACITY_OVERLOAD]: AlertCircle
    }
    return icons[type] || Info
  }

  const getAnomalyColor = (severity) => {
    if (severity >= 4) return 'border-red-200 bg-red-50'
    if (severity >= 3) return 'border-yellow-200 bg-yellow-50'
    return 'border-blue-200 bg-blue-50'
  }

  const allItems = [
    ...anomalies.map(a => ({ ...a, type: 'anomaly' })),
    ...insights.map(i => ({ ...i, type: 'insight' }))
  ].sort((a, b) => {
    if (a.type === 'anomaly' && b.type === 'insight') return -1
    if (a.type === 'insight' && b.type === 'anomaly') return 1
    return (b.severity || 0) - (a.severity || 0)
  })

  return (
    <div className="runway-card p-4 space-y-3 max-h-[600px] overflow-y-auto">
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-neutral-200">
        <AlertCircle className="w-5 h-5 text-neutral-900" />
        <h3 className="font-bold text-neutral-900">Chief of Staff Feed</h3>
      </div>

      <AnimatePresence>
        {allItems.length === 0 ? (
          <div className="text-center py-8 text-neutral-500">
            <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-green-500" />
            <p className="text-sm">All systems operational</p>
          </div>
        ) : (
          allItems.map((item, index) => {
            const Icon = item.type === 'anomaly' 
              ? getAnomalyIcon(item.anomaly_type || item.type)
              : Info

            return (
              <motion.div
                key={item.id || index}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className={cn(
                  "p-3 rounded-lg border",
                  item.type === 'anomaly' 
                    ? getAnomalyColor(item.severity || 3)
                    : "border-green-200 bg-green-50"
                )}
              >
                <div className="flex items-start gap-2">
                  <Icon className={cn(
                    "w-4 h-4 flex-shrink-0 mt-0.5",
                    item.type === 'anomaly' && item.severity >= 4
                      ? "text-red-600"
                      : item.type === 'anomaly' && item.severity >= 3
                      ? "text-yellow-600"
                      : "text-blue-600"
                  )} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-neutral-900 mb-1">
                      {item.message || item.title}
                    </p>
                    {item.move_name && (
                      <p className="text-[10px] text-neutral-600">
                        Move: {item.move_name}
                      </p>
                    )}
                    {item.resolution && (
                      <p className="text-[10px] text-neutral-600 mt-1">
                        {item.resolution}
                      </p>
                    )}
                  </div>
                  {onDismiss && (
                    <button
                      onClick={() => onDismiss(item.id)}
                      className="text-neutral-400 hover:text-neutral-900 text-xs"
                    >
                      ×
                    </button>
                  )}
                </div>
              </motion.div>
            )
          })
        )}
      </AnimatePresence>
    </div>
  )
}


