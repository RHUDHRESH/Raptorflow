import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, AlertTriangle, Wrench, Loader2, Play } from 'lucide-react'
import useRaptorflowStore from '@/store/raptorflowStore'
import { Modal } from '@/components/system/Modal'

const GateRow = ({ gate, onFix }) => {
  const Icon = gate.ok ? CheckCircle2 : AlertTriangle

  return (
    <div className="flex items-start justify-between gap-3 p-3 bg-paper rounded-xl border border-border-light">
      <div className="flex items-start gap-3">
        <Icon
          className={gate.ok ? 'w-5 h-5 text-emerald-600 mt-0.5' : 'w-5 h-5 text-amber-600 mt-0.5'}
          strokeWidth={1.5}
        />
        <div>
          <div className="text-body-sm text-ink font-medium">{gate.label}</div>
          <div className="text-body-xs text-ink-400 mt-0.5">{gate.detail}</div>
        </div>
      </div>

      {!gate.ok && (
        <button
          type="button"
          onClick={onFix}
          className="flex items-center gap-2 px-3 py-2 bg-paper-200 rounded-lg text-body-xs text-ink hover:bg-paper-200/70 transition-editorial"
        >
          <Wrench className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
          Fix
        </button>
      )}
    </div>
  )
}

const PreFlightChecklistModal = ({ open, onOpenChange, moveId, onStarted }) => {
  const { getMove, getMoveReadiness, fixMoveReadiness, startMoveGeneration } = useRaptorflowStore()
  const [starting, setStarting] = useState(false)
  const [tick, setTick] = useState(0)

  const move = getMove?.(moveId)

  const readiness = useMemo(() => {
    return getMoveReadiness?.(moveId)
  }, [getMoveReadiness, moveId, tick])

  const ready = Boolean(readiness?.ready)
  const gates = readiness?.gates || []

  useEffect(() => {
    if (!open) {
      setStarting(false)
      setTick(t => t + 1)
    }
  }, [open])

  const handleFix = (gateId) => {
    fixMoveReadiness?.(moveId, gateId)
    setTick(t => t + 1)
  }

  const handleStart = () => {
    if (!moveId || !ready || starting) return
    setStarting(true)
    const res = startMoveGeneration?.(moveId)
    if (res?.ok) {
      if (typeof onStarted === 'function') onStarted(moveId)
      onOpenChange(false)
      return
    }
    setStarting(false)
    setTick(t => t + 1)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="Pre-flight checklist"
      description={move?.name ? `Ready-gates for: ${move.name}` : 'Ready-gates to start this move.'}
      contentClassName="max-w-2xl"
    >
      <div className="px-5 pb-5">
        <div className="p-4 bg-paper-200 border border-border-light rounded-xl mb-4">
          <div className="text-body-sm text-ink font-medium">What this does</div>
          <div className="text-body-xs text-ink-400 mt-1">
            We pin your strategy, make sure the move has a target + channel + metric, and ensure you have at least one proof item.
          </div>
        </div>

        <div className="space-y-2 mb-5">
          {gates.map(g => (
            <GateRow key={g.id} gate={g} onFix={() => handleFix(g.id)} />
          ))}
        </div>

        <div className="flex items-center justify-between">
          <div className="text-body-xs text-ink-400">
            {ready ? 'All gates passed.' : 'Fix the remaining gates to proceed.'}
          </div>

          <button
            type="button"
            onClick={handleStart}
            disabled={!ready || starting}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial disabled:opacity-50"
          >
            {starting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} />
                Starting…
              </>
            ) : (
              <>
                <Play className="w-4 h-4" strokeWidth={1.5} />
                Start move
              </>
            )}
          </button>
        </div>
      </div>
    </Modal>
  )
}

export default PreFlightChecklistModal
