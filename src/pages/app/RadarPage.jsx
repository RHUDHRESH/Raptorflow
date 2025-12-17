import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Radio,
  FileText,
  Target,
  Loader2,
  Plus,
  ChevronRight,
  Clock,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Copy,
  Info,
  X,
  Zap
} from 'lucide-react'
import useRaptorflowStore from '../../store/raptorflowStore'
import { BRAND_ICONS } from '@/components/brand/BrandSystem'

const copyToClipboard = async (text) => {
  const value = String(text || '')
  if (!value) return false

  try {
    await navigator.clipboard.writeText(value)
    return true
  } catch {
    try {
      const el = document.createElement('textarea')
      el.value = value
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
      return true
    } catch {
      return false
    }
  }
}

const Modal = ({ open, title, onClose, children }) => (
  <AnimatePresence>
    {open && (
      <>
        <motion.button
          type="button"
          aria-label="Close dialog"
          className="fixed inset-0 z-50 bg-ink-900/80 backdrop-blur-3xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        />
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-6">
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label={title}
            className="relative w-full max-w-[760px] bg-card border border-border rounded-2xl overflow-hidden shadow-[0_30px_120px_rgba(0,0,0,0.55)] ring-1 ring-primary/10"
            initial={{ opacity: 0, y: 18, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 18, scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
          >
            <div className="absolute -top-24 left-1/2 h-56 w-56 -translate-x-1/2 rounded-full bg-primary/20 blur-3xl opacity-60 pointer-events-none" />
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-60 pointer-events-none" />

            <div className="relative flex items-center justify-between px-5 py-4 border-b border-border-light bg-paper/60 backdrop-blur-sm">
              <h2 className="font-serif text-xl md:text-2xl text-ink tracking-tight">{title}</h2>
              <button
                type="button"
                aria-label="Close"
                onClick={onClose}
                className="p-2 rounded-lg text-ink-400 hover:text-ink hover:bg-paper-200 transition-editorial"
              >
                <X className="w-4 h-4" strokeWidth={1.5} />
              </button>
            </div>
            <div className="relative p-5 max-h-[72vh] overflow-auto">
              {children}
            </div>
          </motion.div>
        </div>
      </>
    )}
  </AnimatePresence>
)

// Scan type selector
const ScanTypeSelector = ({ value, onChange }) => (
  <div className="flex gap-2 p-1.5 bg-paper-200 rounded-2xl border border-border-light">
    <button
      type="button"
      onClick={() => onChange('small')}
      className="relative flex-1 rounded-lg"
    >
      {value === 'small' && (
        <motion.div
          layoutId="scanTypeHighlight"
          className="absolute inset-0 bg-card shadow-sm rounded-lg"
          transition={{ type: 'spring', stiffness: 420, damping: 34 }}
        />
      )}
      <motion.div
        className="relative flex items-center justify-center gap-2 px-4 py-3 rounded-lg"
        animate={{ opacity: value === 'small' ? 1 : 0.7 }}
        transition={{ duration: 0.18 }}
        whileTap={{ scale: 0.98 }}
      >
        <FileText
          className={`w-4 h-4 ${value === 'small' ? 'text-ink' : 'text-ink-400'}`}
          strokeWidth={1.5}
        />
        <div className="text-left">
          <div className={`text-body-sm font-medium ${value === 'small' ? 'text-ink' : 'text-ink-400'}`}>Recon</div>
          <div className="text-body-xs text-ink-400">Signals + post angles</div>
        </div>
      </motion.div>
    </button>

    <button
      type="button"
      onClick={() => onChange('big')}
      className="relative flex-1 rounded-lg"
    >
      {value === 'big' && (
        <motion.div
          layoutId="scanTypeHighlight"
          className="absolute inset-0 bg-card shadow-sm rounded-lg"
          transition={{ type: 'spring', stiffness: 420, damping: 34 }}
        />
      )}
      <motion.div
        className="relative flex items-center justify-center gap-2 px-4 py-3 rounded-lg"
        animate={{ opacity: value === 'big' ? 1 : 0.7 }}
        transition={{ duration: 0.18 }}
        whileTap={{ scale: 0.98 }}
      >
        <Target
          className={`w-4 h-4 ${value === 'big' ? 'text-ink' : 'text-ink-400'}`}
          strokeWidth={1.5}
        />
        <div className="text-left">
          <div className={`text-body-sm font-medium ${value === 'big' ? 'text-ink' : 'text-ink-400'}`}>Dossier</div>
          <div className="text-body-xs text-ink-400">Moves + execution</div>
        </div>
      </motion.div>
    </button>
  </div>
)

const ScanFocusSelector = ({ value, onChange, items }) => (
  <div className="bg-paper-200 p-1.5 rounded-2xl border border-border-light">
    <div className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <button
          key={item.value}
          type="button"
          onClick={() => onChange(item.value)}
          className="relative rounded-xl"
        >
          {value === item.value && (
            <motion.div
              layoutId="scanFocusHighlight"
              className="absolute inset-0 bg-card shadow-sm rounded-xl"
              transition={{ type: 'spring', stiffness: 420, damping: 34 }}
            />
          )}
          <motion.div
            className="relative px-3 py-2 rounded-xl"
            animate={{ opacity: value === item.value ? 1 : 0.7 }}
            transition={{ duration: 0.18 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center gap-2">
              {item.icon && (
                <item.icon
                  className={`w-3.5 h-3.5 ${value === item.value ? 'text-primary' : 'text-ink-400'}`}
                  strokeWidth={1.5}
                />
              )}
              <div className={`text-body-xs font-medium ${value === item.value ? 'text-ink' : 'text-ink-400'}`}>{item.label}</div>
            </div>
            <div className="text-[11px] leading-snug text-ink-400">{item.description}</div>
          </motion.div>
        </button>
      ))}
    </div>
  </div>
)

const CohortSelector = ({ cohorts, value, onChange }) => {
  const safeValue = Array.isArray(value) ? value : []

  const setPrimary = (id) => {
    if (!id) return
    if (!safeValue.includes(id)) return
    onChange([id, ...safeValue.filter((cId) => cId !== id)])
  }

  const removeCohort = (id) => {
    if (!id) return
    const next = safeValue.filter((cId) => cId !== id)
    onChange(next)
  }

  const addCohort = (id) => {
    if (!id) return
    if (safeValue.includes(id)) return
    if (!safeValue.length) {
      onChange([id])
      return
    }
    onChange([...safeValue, id])
  }

  const selected = safeValue
    .map((id) => cohorts.find((c) => c.id === id))
    .filter(Boolean)
  const unselected = cohorts.filter((c) => !safeValue.includes(c.id))

  return (
    <div className="bg-paper-200 p-2 rounded-2xl border border-border-light">
      <div className="flex items-center justify-between gap-3 px-2 pt-1">
        <div className="text-body-xs text-ink-400">Selected</div>
        <div className="text-body-xs text-ink-400">{safeValue.length} total</div>
      </div>

      <div className="mt-2 flex flex-wrap gap-1.5 px-1">
        {selected.length === 0 && (
          <div className="w-full p-3 rounded-xl border border-border-light bg-paper">
            <div className="text-body-sm text-ink font-medium">Select at least one cohort</div>
            <div className="text-body-xs text-ink-400 mt-1">Recon/Dossier needs a cohort signal to scan.</div>
          </div>
        )}
        {selected.map((cohort) => {
          const isPrimary = safeValue[0] === cohort.id

          return (
            <div key={cohort.id} className="relative">
              {isPrimary && (
                <motion.div
                  layoutId="cohortPrimaryHighlight"
                  className="absolute inset-0 bg-card shadow-sm rounded-xl"
                  transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                />
              )}
              <motion.div
                className={`relative flex items-center gap-2 px-3 py-2 rounded-xl border transition-editorial ${isPrimary ? 'border-transparent' : 'border-primary/20 bg-signal-muted'
                  }`}
                whileTap={{ scale: 0.98 }}
              >
                <button
                  type="button"
                  onClick={() => setPrimary(cohort.id)}
                  className="text-left"
                >
                  <div className="text-body-xs font-medium text-ink">{cohort.name}</div>
                  <div className="text-[11px] leading-snug text-ink-400">{isPrimary ? 'Primary (click to change)' : 'Included (click to make primary)'}</div>
                </button>

                <button
                  type="button"
                  aria-label={`Remove ${cohort.name}`}
                  onClick={() => removeCohort(cohort.id)}
                  className="ml-1 p-1 rounded-lg text-ink-400 hover:text-ink hover:bg-paper-200 transition-editorial"
                >
                  <X className="w-3.5 h-3.5" strokeWidth={1.5} />
                </button>
              </motion.div>
            </div>
          )
        })}
      </div>

      {unselected.length > 0 && (
        <div className="mt-3 pt-3 border-t border-border-light">
          <div className="flex items-center justify-between gap-3 px-2">
            <div className="text-body-xs text-ink-400">Add cohorts</div>
            <div className="text-[11px] leading-none text-ink-400 px-2 py-1 rounded-full bg-paper border border-border-light">
              {unselected.length} available
            </div>
          </div>

          <div className="mt-2 flex flex-wrap gap-1.5 px-1">
            {unselected.map((cohort) => (
              <button
                key={cohort.id}
                type="button"
                onClick={() => addCohort(cohort.id)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border-light bg-paper hover:bg-paper-300 transition-editorial"
              >
                <Plus className="w-3.5 h-3.5 text-ink-400" strokeWidth={1.5} />
                <div className="text-left">
                  <div className="text-body-xs font-medium text-ink">{cohort.name}</div>
                  <div className="text-[11px] leading-snug text-ink-400">Add</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

const RadarSweep = ({ label, variant = 'small' }) => {
  const isBig = variant === 'big'
  const blips = isBig
    ? [
      { x: '22%', y: '28%', s: 'h-2.5 w-2.5', d: 0.0, dur: 1.1 },
      { x: '66%', y: '36%', s: 'h-2 w-2', d: 0.15, dur: 1.25 },
      { x: '56%', y: '64%', s: 'h-2 w-2', d: 0.3, dur: 1.35 },
      { x: '38%', y: '54%', s: 'h-1.5 w-1.5', d: 0.45, dur: 1.5 },
      { x: '72%', y: '58%', s: 'h-1.5 w-1.5', d: 0.6, dur: 1.6 }
    ]
    : [
      { x: '28%', y: '35%', s: 'h-2 w-2', d: 0.0, dur: 1.2 },
      { x: '60%', y: '52%', s: 'h-1.5 w-1.5', d: 0.2, dur: 1.35 },
      { x: '52%', y: '25%', s: 'h-1.5 w-1.5', d: 0.5, dur: 1.5 }
    ]

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${isBig ? 'w-44 h-44 md:w-56 md:h-56' : 'w-32 h-32'}`}>
        {isBig && (
          <motion.div
            className="absolute -inset-10 rounded-full bg-primary/20 blur-3xl opacity-70"
            animate={{ opacity: [0.45, 0.85, 0.45], scale: [0.98, 1.06, 0.98] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
          />
        )}

        <div className="absolute inset-0 rounded-full bg-paper-200 border border-border-light" />
        <div className="absolute inset-0 rounded-full bg-gradient-to-b from-transparent via-primary/10 to-transparent" />
        <div className={`absolute ${isBig ? 'inset-6' : 'inset-4'} rounded-full border border-border-light`} />
        <div className={`absolute ${isBig ? 'inset-12' : 'inset-8'} rounded-full border border-border-light`} />
        {isBig && <div className="absolute inset-[22%] rounded-full border border-border-light opacity-80" />}

        <div className="absolute left-1/2 top-2 bottom-2 w-px bg-border-light" />
        <div className="absolute top-1/2 left-2 right-2 h-px bg-border-light" />
        {isBig && (
          <>
            <div className="absolute left-1/2 top-[10%] bottom-[10%] w-px bg-border-light/60 rotate-45 origin-center" />
            <div className="absolute left-1/2 top-[10%] bottom-[10%] w-px bg-border-light/60 -rotate-45 origin-center" />
          </>
        )}

        {isBig && (
          <motion.div
            className="absolute inset-0 rounded-full border border-primary/30"
            animate={{ scale: [0.92, 1.26], opacity: [0.3, 0] }}
            transition={{ duration: 1.25, repeat: Infinity, ease: 'easeOut' }}
          />
        )}

        <motion.div
          className="absolute inset-0 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: isBig ? 1.1 : 1.6, repeat: Infinity, ease: 'linear' }}
          style={{ willChange: 'transform' }}
        >
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: isBig
                ? 'conic-gradient(from 90deg, rgba(0,0,0,0) 0deg, rgba(180,140,70,0.00) 18deg, rgba(180,140,70,0.24) 34deg, rgba(180,140,70,0.10) 52deg, rgba(0,0,0,0) 76deg)'
                : 'conic-gradient(from 90deg, rgba(0,0,0,0) 0deg, rgba(180,140,70,0.00) 20deg, rgba(180,140,70,0.18) 36deg, rgba(180,140,70,0.08) 54deg, rgba(0,0,0,0) 78deg)'
            }}
          />
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: isBig
                ? 'radial-gradient(circle at center, rgba(180,140,70,0.14) 0%, rgba(180,140,70,0.05) 36%, rgba(0,0,0,0) 70%)'
                : 'radial-gradient(circle at center, rgba(180,140,70,0.10) 0%, rgba(180,140,70,0.04) 38%, rgba(0,0,0,0) 72%)'
            }}
          />
        </motion.div>

        {isBig && (
          <motion.div
            className="absolute inset-0"
            animate={{ rotate: -360 }}
            transition={{ duration: 2.4, repeat: Infinity, ease: 'linear' }}
          >
            <div
              className="absolute inset-0 rounded-full"
              style={{
                background:
                  'conic-gradient(from 90deg, rgba(0,0,0,0) 0deg, rgba(180,140,70,0.00) 12deg, rgba(180,140,70,0.12) 26deg, rgba(180,140,70,0.05) 44deg, rgba(0,0,0,0) 74deg)'
              }}
            />
          </motion.div>
        )}

        <motion.div
          className={`absolute left-1/2 top-1/2 ${isBig ? 'h-2.5 w-2.5' : 'h-2 w-2'} -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary`}
          animate={{ opacity: [0.35, 1, 0.35], scale: isBig ? [0.9, 1.8, 0.9] : [0.9, 1.5, 0.9] }}
          transition={{ duration: isBig ? 1.0 : 1.2, repeat: Infinity, ease: 'easeInOut' }}
        />

        {blips.map((b, idx) => (
          <motion.div
            key={`${b.x}-${b.y}-${idx}`}
            className={`absolute ${b.s} rounded-full ${isBig ? 'bg-primary shadow-[0_0_24px_rgba(180,140,70,0.25)]' : 'bg-primary'}`}
            style={{ left: b.x, top: b.y }}
            animate={{ opacity: isBig ? [0.05, 1, 0.1] : [0.12, 1, 0.12], scale: isBig ? [0.65, 1.7, 0.85] : [0.8, 1.4, 0.8] }}
            transition={{ duration: b.dur, repeat: Infinity, ease: 'easeInOut', delay: b.d }}
          />
        ))}
      </div>

      <div className="mt-5 text-center">
        <motion.div
          className="font-serif text-lg text-ink"
          animate={{ opacity: [0.85, 1, 0.85] }}
          transition={{ duration: isBig ? 1.05 : 1.35, repeat: Infinity, ease: 'easeInOut' }}
        >
          {isBig ? 'Dossier…' : 'Recon…'}
        </motion.div>
        <div className="text-body-sm text-ink-400">{label}</div>
        {isBig && <div className="mt-1 text-[11px] text-ink-400">Multi-pass sweep • signal amplification • synthesis</div>}
      </div>
    </div>
  )
}

// Post suggestion card
const PostSuggestion = ({ suggestion, onOpenMuse }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="p-4 bg-card border border-border rounded-xl"
  >
    <div className="flex items-start justify-between mb-3">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-paper-200 rounded-lg flex items-center justify-center">
          <FileText className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
        </div>
        <span className="text-body-xs text-ink-400 capitalize">{suggestion.channel}</span>
      </div>
      <span className="px-2.5 py-1 rounded-full bg-signal-muted text-primary border border-primary/20 text-[11px] leading-none font-medium">
        Post idea
      </span>
    </div>
    <p className="text-body-sm text-ink mb-4">{suggestion.content}</p>
    <PostSuggestionActions suggestion={suggestion} onOpenMuse={onOpenMuse} />
  </motion.div>
)

const PostSuggestionActions = ({ suggestion, onOpenMuse }) => {
  const [copied, setCopied] = useState(false)

  const copyText = async () => {
    const text = String(suggestion?.content || '')
    if (!text) return

    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 900)
    } catch {
      try {
        const el = document.createElement('textarea')
        el.value = text
        document.body.appendChild(el)
        el.select()
        document.execCommand('copy')
        document.body.removeChild(el)
        setCopied(true)
        window.setTimeout(() => setCopied(false), 900)
      } catch {
        setCopied(false)
      }
    }
  }

  return (
    <div className="flex items-center justify-between gap-3">
      <button
        type="button"
        onClick={copyText}
        className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-body-xs transition-editorial ${copied
          ? 'border-primary/20 bg-signal-muted text-primary'
          : 'border-border bg-paper hover:bg-paper-200 text-ink'
          }`}
      >
        <Copy className="w-3.5 h-3.5" strokeWidth={1.5} />
        {copied ? 'Copied' : 'Copy'}
      </button>

      <button
        type="button"
        onClick={onOpenMuse}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-body-xs font-medium hover:opacity-95 transition-editorial"
      >
        <Sparkles className="w-3.5 h-3.5" strokeWidth={1.5} />
        Generate full post
      </button>
    </div>
  )
}

// Move suggestion card
const MoveSuggestion = ({ suggestion, onConvert, campaigns, focus }) => {
  const [selectedCampaign, setSelectedCampaign] = useState(campaigns[0]?.id || '')
  const [copied, setCopied] = useState(false)

  const copyMove = async () => {
    const summary = [
      suggestion?.name ? `Move: ${suggestion.name}` : null,
      focus ? `Focus: ${focus}` : null,
      suggestion?.channel ? `Channel: ${suggestion.channel}` : null,
      suggestion?.cta ? `CTA: ${suggestion.cta}` : null,
      suggestion?.metric ? `Metric: ${suggestion.metric}` : null,
      suggestion?.durationDays ? `Duration: ${suggestion.durationDays} days` : null,
      suggestion?.reason ? `Why now: ${suggestion.reason}` : null
    ]
      .filter(Boolean)
      .join('\n')

    const ok = await copyToClipboard(summary)
    if (!ok) return
    setCopied(true)
    window.setTimeout(() => setCopied(false), 900)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-5 bg-card border border-primary/20 rounded-xl"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-signal-muted rounded-lg flex items-center justify-center">
            <Target className="w-4 h-4 text-primary" strokeWidth={1.5} />
          </div>
          <div>
            <div className="text-body-sm text-ink font-medium">Suggested Move</div>
            <div className="text-body-xs text-ink-400">Based on {focus || 'trends'}</div>
          </div>
        </div>
        <span className="px-2 py-1 bg-signal-muted text-primary rounded text-body-xs">
          Recommended
        </span>
      </div>

      <div className="p-4 bg-paper-200 rounded-lg mb-4">
        <h4 className="text-body-sm text-ink font-medium mb-2">{suggestion.name}</h4>
        <div className="grid grid-cols-2 gap-3 text-body-xs">
          <div>
            <span className="text-ink-400">Channel</span>
            <div className="text-ink capitalize">{suggestion.channel}</div>
          </div>
          <div>
            <span className="text-ink-400">Duration</span>
            <div className="text-ink">{suggestion.durationDays} days</div>
          </div>
          <div>
            <span className="text-ink-400">CTA</span>
            <div className="text-ink">{suggestion.cta}</div>
          </div>
          <div>
            <span className="text-ink-400">Metric</span>
            <div className="text-ink capitalize">{suggestion.metric}</div>
          </div>
        </div>
        {suggestion.reason && (
          <div className="mt-3 pt-3 border-t border-border-light">
            <span className="text-body-xs text-ink-400">Why now:</span>
            <p className="text-body-xs text-ink mt-1">{suggestion.reason}</p>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        <select
          value={selectedCampaign}
          onChange={(e) => setSelectedCampaign(e.target.value)}
          className="flex-1 px-3 py-2 bg-paper border border-border rounded-lg text-body-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
        >
          <option value="">Select campaign...</option>
          {campaigns.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <button
          type="button"
          onClick={copyMove}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-body-sm transition-editorial border ${copied
            ? 'border-primary/20 bg-signal-muted text-primary'
            : 'border-border bg-paper hover:bg-paper-200 text-ink'
            }`}
        >
          <Copy className="w-4 h-4" strokeWidth={1.5} />
          {copied ? 'Copied' : 'Copy'}
        </button>
        <button
          onClick={() => onConvert(selectedCampaign)}
          disabled={!selectedCampaign}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial disabled:opacity-50"
        >
          Convert to Move
          <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
        </button>
      </div>
    </motion.div>
  )
}

// Scan history item
const ScanHistoryItem = ({ scan, cohorts, onClick }) => {
  const cohortIds = scan.cohorts?.length ? scan.cohorts : [scan.cohort]
  const cohort = cohorts.find(c => c.id === cohortIds[0])
  const outputCount = scan.outputs?.length || 0
  const scanLabel = scan.type === 'big' ? 'Dossier' : 'Recon'

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      onClick={onClick}
      className="flex items-center justify-between p-3 bg-paper hover:bg-paper-200 rounded-xl border border-border-light cursor-pointer transition-editorial group"
    >
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${scan.type === 'big' ? 'bg-signal-muted' : 'bg-paper-200'
          }`}>
          {scan.type === 'big' ? (
            <Target className="w-4 h-4 text-primary" strokeWidth={1.5} />
          ) : (
            <FileText className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
          )}
        </div>
        <div>
          <div className="text-body-sm text-ink">{scanLabel}</div>
          <div className="text-body-xs text-ink-400">
            {cohortIds.length > 1 ? `${cohortIds.length} cohorts` : (cohort?.name || 'All cohorts')} • {outputCount} results • {scan.focus || 'trends'}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-body-xs text-ink-400">
          {new Date(scan.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
        <ChevronRight className="w-4 h-4 text-ink-400 opacity-0 group-hover:opacity-100 transition-editorial" strokeWidth={1.5} />
      </div>
    </motion.div>
  )
}

// Main Radar Page
const RadarPage = () => {
  const navigate = useNavigate()
  const {
    cohorts,
    campaigns,
    radarScans,
    runRadarScan,
    convertRadarToMove,
    createSignal,
    canUseRadar,
    usage,
    getPlanLimits,
    openMuseDrawer
  } = useRaptorflowStore()

  const planLimits = getPlanLimits()
  const [scanType, setScanType] = useState('small')
  const [selectedCohorts, setSelectedCohorts] = useState(cohorts[0]?.id ? [cohorts[0].id] : [])
  const scanFocusOptions = useMemo(() => (
    [
      { value: 'trends', label: 'Trends', description: 'what people are talking about', icon: BRAND_ICONS.speed },
      { value: 'competitors', label: 'Competitors', description: 'positioning + claims', icon: Target },
      { value: 'objections', label: 'Objections', description: 'friction + doubts', icon: FileText },
      { value: 'launch', label: 'Launch', description: 'what changed + why now', icon: ArrowRight },
      { value: 'hiring', label: 'Hiring', description: 'headcount + priorities', icon: Sparkles }
    ]
  ), [])
  const [scanFocus, setScanFocus] = useState('trends')
  const [isScanning, setIsScanning] = useState(false)
  const [currentScan, setCurrentScan] = useState(null)
  const [scanContextLabel, setScanContextLabel] = useState('')
  const [scanContextVariant, setScanContextVariant] = useState('small')
  const [copiedBrief, setCopiedBrief] = useState(false)
  const [isInfoOpen, setIsInfoOpen] = useState(false)
  const [isTodayScansOpen, setIsTodayScansOpen] = useState(false)
  const [scanDetails, setScanDetails] = useState(null)
  const [isScanDetailsOpen, setIsScanDetailsOpen] = useState(false)
  const [isResultsOpen, setIsResultsOpen] = useState(false)

  const scansRemaining = planLimits.radarScansPerDay - usage.radarScansToday
  const cohortLabel = useMemo(() => {
    if (!selectedCohorts?.length) return 'your audience'
    if (selectedCohorts.length > 1) return `${selectedCohorts.length} cohorts`
    return cohorts.find(c => c.id === selectedCohorts[0])?.name || 'your audience'
  }, [cohorts, selectedCohorts])

  const currentScanCohortLabel = useMemo(() => {
    if (!currentScan) return ''
    const ids = currentScan.cohorts?.length ? currentScan.cohorts : [currentScan.cohort]
    if (ids.length > 1) return `${ids.length} cohorts`
    return cohorts.find(c => c.id === ids[0])?.name || 'your audience'
  }, [cohorts, currentScan])

  const currentScanOutputs = useMemo(() => {
    const outputs = currentScan?.outputs || []
    return {
      posts: outputs.filter(o => o.type === 'post'),
      moves: outputs.filter(o => o.type === 'move')
    }
  }, [currentScan])

  const handleScan = async () => {
    if (!canUseRadar() || !selectedCohorts?.length) return

    setIsScanning(true)
    setCurrentScan(null)
    setScanContextVariant(scanType)
    setScanContextLabel(scanType === 'big' ? `Dossier: ${scanFocus} • ${cohortLabel}` : `Recon: ${scanFocus} • ${cohortLabel}`)
    setIsResultsOpen(true)

    // Simulate scan delay
    await new Promise(resolve => setTimeout(resolve, scanType === 'big' ? 3200 : 1200))

    const scan = runRadarScan(scanType, selectedCohorts, scanFocus)
    setCurrentScan(scan)
    setIsScanning(false)
  }

  const handleConvertToMove = (campaignId) => {
    if (!currentScan || !campaignId) return

    const newMove = convertRadarToMove(currentScan.id, campaignId)
    if (newMove) {
      navigate(`/app/moves/${newMove.id}`)
    }
  }

  const handleOpenMuse = () => {
    openMuseDrawer({ assetType: 'post' })
  }

  const todayScans = radarScans.filter(s => {
    const scanDate = new Date(s.createdAt).toDateString()
    const today = new Date().toDateString()
    return scanDate === today
  })

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key !== 'Escape') return

      if (isScanDetailsOpen) {
        setIsScanDetailsOpen(false)
        return
      }
      if (isTodayScansOpen) {
        setIsTodayScansOpen(false)
        return
      }
      if (isResultsOpen) {
        setIsResultsOpen(false)
        return
      }
      if (isInfoOpen) {
        setIsInfoOpen(false)
      }
    }

    if (!isInfoOpen && !isTodayScansOpen && !isScanDetailsOpen && !isResultsOpen) return

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [isInfoOpen, isTodayScansOpen, isScanDetailsOpen, isResultsOpen])

  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-serif text-headline-md text-ink">Radar</h1>
          <p className="text-body-sm text-ink-400 mt-1">Scan for trending content and move opportunities</p>
        </motion.div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            aria-label="Radar info"
            onClick={() => setIsInfoOpen(true)}
            className="p-2 rounded-lg text-ink-400 hover:text-ink hover:bg-paper-200 transition-editorial"
          >
            <Info className="w-4 h-4" strokeWidth={1.5} />
          </button>

          <motion.button
            type="button"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 px-3 py-1.5 bg-paper-200 rounded-full border border-border-light"
          >
            <Radio className="w-3.5 h-3.5 text-ink-400" strokeWidth={1.5} />
            <span className="text-body-xs text-ink">
              <span className="font-medium">{scansRemaining}</span> left today
            </span>
          </motion.button>

          <motion.button
            type="button"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => setIsTodayScansOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-card border border-border rounded-xl hover:border-border-dark transition-editorial"
          >
            <Clock className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
            <span className="text-body-sm text-ink">Today's scans</span>
            <span className="text-[11px] leading-none text-ink-400 px-2 py-1 rounded-full bg-paper border border-border-light">
              {todayScans.length}
            </span>
          </motion.button>
        </div>
      </div>

      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="relative overflow-hidden bg-card border border-border rounded-2xl p-5"
        >
          <div className="absolute -right-24 -top-24 h-56 w-56 rounded-full bg-primary/10 blur-3xl opacity-70 pointer-events-none" />
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

          <div className="flex items-center justify-between gap-4 mb-4">
            <div>
              <h2 className="font-serif text-xl text-ink tracking-tight">Run a Scan</h2>
              <div className="text-body-xs text-ink-400 mt-1">Pick a focus, choose cohorts, and ship what pops.</div>
            </div>
            <button
              type="button"
              onClick={() => setIsResultsOpen(true)}
              disabled={!currentScan}
              className="text-body-xs text-ink-400 hover:text-ink transition-editorial disabled:opacity-50"
            >
              View last results
            </button>
          </div>

          <div className="mb-4">
            <label className="block text-body-xs text-ink-400 mb-2">Scan type</label>
            <ScanTypeSelector value={scanType} onChange={setScanType} />
            <div className="mt-2 flex items-center justify-between gap-3">
              <div className="text-body-xs text-ink-400">
                {scanType === 'big' ? 'Dossier: longer + higher confidence.' : 'Recon: fast signals for today.'}
              </div>
              <span className={`px-2.5 py-1 rounded-full text-[11px] leading-none border ${scanType === 'big'
                ? 'bg-primary/10 text-primary border-primary/20'
                : 'bg-paper text-ink-400 border-border-light'
                }`}>
                {scanType === 'big' ? 'Dossier' : 'Recon'}
              </span>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-body-xs text-ink-400 mb-2">Target cohorts</label>
            <CohortSelector cohorts={cohorts} value={selectedCohorts} onChange={setSelectedCohorts} />
          </div>

          <div className="mb-6">
            <label className="block text-body-xs text-ink-400 mb-2">Scan focus</label>
            <ScanFocusSelector value={scanFocus} onChange={setScanFocus} items={scanFocusOptions} />
          </div>

          <button
            onClick={handleScan}
            disabled={!canUseRadar() || isScanning || !selectedCohorts?.length}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial disabled:opacity-50"
          >
            {isScanning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} />
                {scanType === 'big' ? 'Compiling dossier…' : 'Running recon…'}
              </>
            ) : (
              <>
                <Radio className="w-4 h-4" strokeWidth={1.5} />
                Run {scanType === 'small' ? 'Recon' : 'Dossier'}
              </>
            )}
          </button>

          {!canUseRadar() && (
            <p className="text-body-xs text-ink-400 text-center mt-3">
              You've used all your scans for today. Resets at midnight.
            </p>
          )}
        </motion.div>
      </div>

      <Modal
        open={isInfoOpen}
        title="Radar: how it works"
        onClose={() => setIsInfoOpen(false)}
      >
        <ul className="space-y-3 text-body-sm text-ink-400">
          <li className="flex items-start gap-3">
            <span className="mt-2 w-1.5 h-1.5 rounded-full bg-primary/60 flex-shrink-0" />
            <span><strong className="text-ink">Recon</strong> gives quick signals and post angles for immediate content.</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="mt-2 w-1.5 h-1.5 rounded-full bg-primary/60 flex-shrink-0" />
            <span><strong className="text-ink">Dossier</strong> synthesizes the moment into a move + execution plan.</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="mt-2 w-1.5 h-1.5 rounded-full bg-primary/60 flex-shrink-0" />
            <span>Scans analyze your cohort's interests and current trends.</span>
          </li>
        </ul>
      </Modal>

      <Modal
        open={isTodayScansOpen}
        title="Today's scans"
        onClose={() => setIsTodayScansOpen(false)}
      >
        {todayScans.length > 0 ? (
          <div className="space-y-2">
            {todayScans.map(scan => (
              <ScanHistoryItem
                key={scan.id}
                scan={scan}
                cohorts={cohorts}
                onClick={() => {
                  setScanDetails(scan)
                  setIsScanDetailsOpen(true)
                }}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-ink-300 mx-auto mb-3" strokeWidth={1.5} />
            <p className="text-body-sm text-ink-400">No scans yet today</p>
          </div>
        )}
      </Modal>

      <Modal
        open={isScanDetailsOpen}
        title="Scan details"
        onClose={() => setIsScanDetailsOpen(false)}
      >
        {scanDetails ? (
          <div className="space-y-4">
            <div className="p-4 bg-paper-200 rounded-xl border border-border-light">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-body-xs text-ink-400">Type</div>
                  <div className="text-body-sm text-ink">{scanDetails.type === 'big' ? 'Dossier' : 'Recon'}</div>
                </div>
                <div className="text-right">
                  <div className="text-body-xs text-ink-400">Time</div>
                  <div className="text-body-sm text-ink">
                    {new Date(scanDetails.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>

              <div className="mt-3 text-body-xs text-ink-400">
                Cohort: <span className="text-ink">{scanDetails.cohorts?.length > 1 ? `${scanDetails.cohorts.length} cohorts` : (cohorts.find(c => c.id === scanDetails.cohort)?.name || 'All cohorts')}</span>
              </div>
              <div className="mt-1 text-body-xs text-ink-400">
                Focus: <span className="text-ink capitalize">{scanDetails.focus || 'trends'}</span>
              </div>
              <div className="mt-1 text-body-xs text-ink-400">
                Results: <span className="text-ink">{scanDetails.outputs?.length || 0}</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsScanDetailsOpen(false)}
                className="px-4 py-2 border border-border bg-background rounded-xl text-body-sm hover:bg-muted transition-editorial"
              >
                Close
              </button>
              <button
                type="button"
                onClick={() => {
                  setCurrentScan(scanDetails)
                  setIsResultsOpen(true)
                  setIsScanDetailsOpen(false)
                }}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-xl text-body-sm hover:opacity-95 transition-editorial"
              >
                Open results
              </button>
            </div>
          </div>
        ) : null}
      </Modal>

      <Modal
        open={isResultsOpen}
        title={isScanning ? (scanContextVariant === 'big' ? 'Dossier…' : 'Recon…') : currentScan ? 'Scan results' : 'Scan results'}
        onClose={() => setIsResultsOpen(false)}
      >
        {isScanning && (
          <div className="py-4">
            <RadarSweep
              variant={scanContextVariant}
              label={scanContextLabel || `${scanContextVariant === 'big' ? 'Dossier' : 'Recon'}: ${scanFocus} • ${cohortLabel}`}
            />
          </div>
        )}

        {!isScanning && currentScan && (
          <div>
            <div className="relative p-4 bg-paper-200 rounded-2xl border border-border-light mb-5 overflow-hidden">
              <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-primary/15 blur-3xl opacity-70 pointer-events-none" />
              <div className="relative flex items-start justify-between gap-4">
                <div>
                  <div className="text-body-xs text-ink-400">Scan brief</div>
                  <div className="mt-1 font-serif text-lg text-ink tracking-tight capitalize">
                    {currentScan.type === 'big' ? 'Dossier' : 'Recon'} • {currentScan.focus || 'trends'}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="px-2.5 py-1 rounded-full text-[11px] leading-none bg-paper border border-border-light text-ink-400">
                      {currentScanCohortLabel}
                    </span>
                    <span className="px-2.5 py-1 rounded-full text-[11px] leading-none bg-paper border border-border-light text-ink-400 capitalize">
                      {currentScan.focus || 'trends'}
                    </span>
                    <span className={`px-2.5 py-1 rounded-full text-[11px] leading-none border ${currentScan.type === 'big'
                      ? 'bg-primary/10 text-primary border-primary/20'
                      : 'bg-paper text-ink-400 border-border-light'
                      }`}>
                      {currentScan.type === 'big' ? 'Dossier' : 'Recon'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      if (!currentScan?.id) return
                      const cohortIds = Array.isArray(currentScan.cohorts) && currentScan.cohorts.length
                        ? currentScan.cohorts
                        : currentScan.cohort
                          ? [currentScan.cohort]
                          : []

                      const suggestedMove = (currentScan.outputs || []).find(o => o.type === 'move')?.suggestedMove
                      const postAngle = (currentScan.outputs || []).find(o => o.type === 'post')?.content
                      const statement =
                        currentScan.type === 'big'
                          ? (suggestedMove?.reason ? `Signal from Radar: ${suggestedMove.reason}` : 'Signal from Radar: investigate this leverage.')
                          : (postAngle ? `Signal from Radar: ${postAngle}` : 'Signal from Radar: investigate this leverage.')

                      const title =
                        currentScan.type === 'big'
                          ? (suggestedMove?.name ? `Radar Dossier: ${suggestedMove.name}` : 'Radar Dossier Signal')
                          : 'Radar Recon Signal'

                      const created = createSignal?.({
                        title,
                        statement,
                        zone: currentScan.focus || 'signal',
                        status: 'triage',
                        effort: 'medium',
                        cohortIds,
                        channelIds: suggestedMove?.channel ? [suggestedMove.channel] : [],
                        evidenceRefs: [{ type: 'radar_scan', id: currentScan.id, label: `${currentScan.type === 'big' ? 'Dossier' : 'Recon'} • ${currentScan.focus || 'trends'}` }],
                        ice: { impact: 3, confidence: 2, ease: 2 },
                      })
                      if (created?.id) {
                        setIsResultsOpen(false)
                        navigate(`/app/signals/${created.id}`)
                      }
                    }}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-body-xs font-medium hover:opacity-95 transition-editorial"
                  >
                    <Zap className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Promote to Signal
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      const posts = (currentScan.outputs || [])
                        .filter(o => o.type === 'post')
                        .map(o => o.content)
                        .filter(Boolean)
                      const text = posts.join('\n\n')
                      if (!text) return
                      navigator.clipboard.writeText(text).catch(() => { })
                    }}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border bg-paper hover:bg-paper-200 text-body-xs text-ink transition-editorial"
                  >
                    <Copy className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Copy all
                  </button>
                  <button
                    onClick={handleScan}
                    disabled={!canUseRadar()}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-body-xs font-medium hover:opacity-95 transition-editorial disabled:opacity-50"
                  >
                    <RefreshCw className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Rescan
                  </button>
                </div>
              </div>
            </div>

            <motion.div
              initial="hidden"
              animate="show"
              variants={{
                hidden: { opacity: 1 },
                show: { opacity: 1, transition: { staggerChildren: 0.06 } }
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="font-serif text-lg text-ink">Recon angles</div>
                <span className="text-[11px] leading-none text-ink-400 px-2 py-1 rounded-full bg-paper border border-border-light">
                  {currentScanOutputs.posts.length}
                </span>
              </div>
              <div className="space-y-4">
                {currentScanOutputs.posts.map((output, index) => (
                  <motion.div
                    key={`post-${index}`}
                    variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }}
                    transition={{ duration: 0.28, ease: 'easeOut' }}
                  >
                    <PostSuggestion suggestion={output} onOpenMuse={handleOpenMuse} />
                  </motion.div>
                ))}
                {currentScanOutputs.posts.length === 0 && (
                  <div className="p-4 bg-paper border border-border-light rounded-xl text-body-sm text-ink-400">
                    No recon angles returned.
                  </div>
                )}
              </div>

              <div className="mt-7 flex items-center justify-between mb-2">
                <div className="font-serif text-lg text-ink">Dossier move</div>
                <span className="text-[11px] leading-none text-ink-400 px-2 py-1 rounded-full bg-paper border border-border-light">
                  {currentScanOutputs.moves.length}
                </span>
              </div>
              <div className="space-y-4">
                {currentScanOutputs.moves.map((output, index) => (
                  <motion.div
                    key={`move-${index}`}
                    variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }}
                    transition={{ duration: 0.28, ease: 'easeOut' }}
                  >
                    <MoveSuggestion
                      suggestion={output.suggestedMove}
                      campaigns={campaigns}
                      onConvert={handleConvertToMove}
                      focus={currentScan.focus}
                    />
                  </motion.div>
                ))}
                {currentScanOutputs.moves.length === 0 && (
                  <div className="p-4 bg-paper border border-border-light rounded-xl text-body-sm text-ink-400">
                    No dossier move returned.
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}

        {!isScanning && !currentScan && (
          <div className="text-center py-8">
            <Radio className="w-12 h-12 text-ink-300 mx-auto mb-3" strokeWidth={1.5} />
            <p className="text-body-sm text-ink-400">Run a scan to see a focused brief and ready-to-ship outputs.</p>
            <button
              type="button"
              onClick={() => setIsResultsOpen(false)}
              className="mt-4 inline-flex items-center justify-center px-4 py-2 rounded-lg border border-border bg-paper hover:bg-paper-200 text-body-sm text-ink transition-editorial"
            >
              Close
            </button>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default RadarPage
