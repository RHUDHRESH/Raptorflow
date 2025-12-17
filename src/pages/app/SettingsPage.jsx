import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Settings,
  FileText,
  CreditCard,
  Users,
  BarChart3,
  Lock,
  Plus,
  Save,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Trash2
} from 'lucide-react'
import useRaptorflowStore, { PLAN_LIMITS } from '../../store/raptorflowStore'
import { useAuth } from '../../contexts/AuthContext'
import { supabase, supabaseConfigured } from '../../lib/supabase'
import { EnhancedBillingTab } from '../../components/billing/BillingComponents'
import { EnhancedTeamTab } from '../../components/team/TeamComponents'

// Settings tabs
const SETTINGS_TABS = [
  { id: 'strategy', name: 'Strategy', icon: FileText, description: 'Brand rules, offers, proofs' },
  { id: 'billing', name: 'Billing', icon: CreditCard, description: 'Plan and payments' },
  { id: 'team', name: 'Team', icon: Users, description: 'Members and roles' },
  { id: 'usage', name: 'Usage', icon: BarChart3, description: 'Limits and meters' }
]

// Tab navigation
const TabNav = ({ activeTab, onTabChange }) => (
  <div className="flex flex-col gap-1 w-56 flex-shrink-0">
    {SETTINGS_TABS.map(tab => (
      <button
        key={tab.id}
        onClick={() => onTabChange(tab.id)}
        className={`flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-editorial ${activeTab === tab.id
          ? 'bg-signal-muted text-primary'
          : 'text-ink-400 hover:text-ink hover:bg-paper-200'
          }`}
      >
        <tab.icon className="w-5 h-5" strokeWidth={1.5} />
        <div>
          <div className="text-body-sm font-medium">{tab.name}</div>
          <div className="text-body-xs text-ink-400">{tab.description}</div>
        </div>
      </button>
    ))}
  </div>
)

// Strategy Tab
const StrategyTab = () => {
  const { profile } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [kitsByType, setKitsByType] = useState({})
  const [activeKitType, setActiveKitType] = useState('brand')
  const [editorText, setEditorText] = useState('')
  const [editorError, setEditorError] = useState(null)
  const [bundleStatus, setBundleStatus] = useState(null)

  const organizationId = profile?.current_org_id || profile?.organization_id || null

  const KIT_META = useMemo(() => ([
    { id: 'brand', name: 'BrandKit', description: 'Voice, style, taboo/required language' },
    { id: 'offer', name: 'OfferKit', description: 'Pricing, eligibility, urgency, guarantees' },
    { id: 'proof', name: 'ProofKit', description: 'Claims + proof bindings + permissions' },
    { id: 'audience', name: 'AudienceKit', description: 'Cohorts, triggers, objections, journey' },
    { id: 'channel', name: 'ChannelKit', description: 'Channel constraints, specs, measurement' },
    { id: 'ops', name: 'OpsKit', description: 'Capacity, approvals, risk, tool stack' },
  ]), [])

  const getKitTemplate = (kitType) => {
    if (kitType === 'brand') {
      return {
        brand_name: '',
        voice_profile: { voice_description: '', tone_sliders: {} },
        lexicon: { taboo_words: [] },
        examples: { good_examples: [], bad_examples: [] },
        claims_policy: { claims_must_be_cited: true },
        evidence_refs: [],
        assumptions: [],
      }
    }

    if (kitType === 'offer') {
      return {
        offer_name: '',
        pricing_tiers: [],
        guarantee: { type: 'none', duration_days: null, conditions: [] },
        urgency: { capacity_limit: null, cohort_start_dates: [], offer_end_date: null, reasons: [] },
        eligibility_rules: [],
        evidence_refs: [],
        assumptions: [],
      }
    }

    if (kitType === 'proof') {
      return {
        claims: [],
        proof_assets: [],
        known_gaps: [],
      }
    }

    if (kitType === 'audience') {
      return {
        cohorts: [],
        buying_triggers: [],
        objections: [],
        journey_stages: [],
        pii_handling: { contains_pii: false, pii_fields_present: [], allowed_storage: 'plain_prohibited' },
      }
    }

    if (kitType === 'channel') {
      return {
        channels: [],
        global_rules: [],
        measurement: { utm_convention: { source_map: {}, required_params: [] }, pixel_status: [] },
      }
    }

    if (kitType === 'ops') {
      return {
        team: [],
        approval_workflow: { steps: [], auto_approve_after_hours: null, requires_legal_review: false },
        risk_profile: { brand_risk_tolerance: 'medium', compliance_constraints: [], restricted_topics: [] },
        tooling: { tools: [] },
        execution_cadence: {},
        rules: [],
      }
    }

    return {}
  }

  const safeStringify = (value) => {
    try {
      return JSON.stringify(value ?? {}, null, 2)
    } catch {
      return '{}'
    }
  }

  const getCompleteness = (kitType, data) => {
    const checks = []
    const d = data || {}

    const isArray = (v) => Array.isArray(v)
    const isObject = (v) => !!v && typeof v === 'object' && !Array.isArray(v)

    if (kitType === 'brand') {
      checks.push({ label: 'voice_profile', ok: isObject(d.voice_profile) })
      checks.push({ label: 'lexicon.taboo_words', ok: isArray(d.lexicon?.taboo_words) })
      checks.push({ label: 'examples.good_examples', ok: isArray(d.examples?.good_examples) && d.examples.good_examples.length >= 1 })
      checks.push({ label: 'claims_policy.claims_must_be_cited', ok: d.claims_policy?.claims_must_be_cited === true })
    }

    if (kitType === 'offer') {
      checks.push({ label: 'offer_name', ok: typeof d.offer_name === 'string' && d.offer_name.trim().length > 0 })
      checks.push({ label: 'pricing_tiers', ok: isArray(d.pricing_tiers) && d.pricing_tiers.length >= 1 })
      checks.push({ label: 'guarantee', ok: isObject(d.guarantee) })
    }

    if (kitType === 'proof') {
      checks.push({ label: 'claims', ok: isArray(d.claims) })
      checks.push({ label: 'proof_assets', ok: isArray(d.proof_assets) })
    }

    if (kitType === 'audience') {
      checks.push({ label: 'cohorts', ok: isArray(d.cohorts) && d.cohorts.length >= 1 })
      checks.push({ label: 'objections', ok: isArray(d.objections) })
      checks.push({ label: 'pii_handling', ok: isObject(d.pii_handling) })
    }

    if (kitType === 'channel') {
      checks.push({ label: 'channels', ok: isArray(d.channels) && d.channels.length >= 1 })
      checks.push({ label: 'measurement', ok: isObject(d.measurement) })
    }

    if (kitType === 'ops') {
      checks.push({ label: 'team', ok: isArray(d.team) && d.team.length >= 1 })
      checks.push({ label: 'approval_workflow.steps', ok: isArray(d.approval_workflow?.steps) && d.approval_workflow.steps.length >= 1 })
      checks.push({ label: 'risk_profile', ok: isObject(d.risk_profile) })
    }

    const total = checks.length || 1
    const done = checks.filter(c => c.ok).length
    const blockers = checks.filter(c => !c.ok).map(c => c.label)
    const percent = Math.round((done / total) * 100)

    return { percent, blockers }
  }

  const loadKits = async () => {
    if (!organizationId) return
    if (!supabaseConfigured) return

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const [{ data: draftsRows, error: draftsErr }, { data: lockedRows, error: lockedErr }] = await Promise.all([
        supabase
          .from('kits')
          .select('id, organization_id, kit_type, schema_version, version, status, locked_at, locked_by, updated_at, data')
          .eq('organization_id', organizationId)
          .in('status', ['draft', 'review'])
          .order('version', { ascending: false }),
        supabase
          .from('current_locked_kits')
          .select('organization_id, kit_type, kit_id, schema_version, version, locked_at, locked_by, updated_at, data')
          .eq('organization_id', organizationId),
      ])

      if (draftsErr) throw draftsErr
      if (lockedErr) throw lockedErr

      const next = {}
      for (const meta of KIT_META) {
        const draft = (draftsRows || []).find(r => r.kit_type === meta.id)
        const locked = (lockedRows || []).find(r => r.kit_type === meta.id)
        next[meta.id] = { draft: draft || null, locked: locked || null }
      }

      setKitsByType(next)

      const current = next[activeKitType]
      const activeRow = current?.draft || current?.locked
      setEditorText(safeStringify(activeRow?.data || getKitTemplate(activeKitType)))
    } catch (e) {
      setError(e?.message || 'Failed to load kits')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadKits()
  }, [organizationId])

  useEffect(() => {
    const current = kitsByType?.[activeKitType]
    const activeRow = current?.draft || current?.locked
    setEditorError(null)
    setEditorText(safeStringify(activeRow?.data || getKitTemplate(activeKitType)))
  }, [activeKitType, kitsByType])

  const handleCreateDraft = async (kitType) => {
    if (!organizationId) {
      setError('Missing organization')
      return
    }
    if (!supabaseConfigured) {
      setError('Supabase is not configured in this environment')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const { data, error: rpcErr } = await supabase.rpc('create_kit_draft', {
        p_organization_id: organizationId,
        p_kit_type: kitType,
        p_schema_version: '1.0.0',
        p_data: getKitTemplate(kitType),
      })

      if (rpcErr) throw rpcErr

      setSuccess(`Created ${kitType} draft v${data?.version}`)
      setActiveKitType(kitType)
      await loadKits()
    } catch (e) {
      setError(e?.message || 'Failed to create draft')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveDraft = async () => {
    if (!supabaseConfigured) {
      setError('Supabase is not configured in this environment')
      return
    }

    const row = kitsByType?.[activeKitType]?.draft
    if (!row) {
      setError('No editable draft/review kit selected')
      return
    }

    let parsed
    try {
      parsed = JSON.parse(editorText || '{}')
    } catch (e) {
      setEditorError('Invalid JSON')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)
    setEditorError(null)
    try {
      const { error: updErr } = await supabase
        .from('kits')
        .update({ data: parsed })
        .eq('id', row.id)

      if (updErr) throw updErr

      setSuccess('Saved')
      await loadKits()
    } catch (e) {
      setError(e?.message || 'Failed to save')
    } finally {
      setLoading(false)
    }
  }

  const handleTransition = async (kitId, newStatus) => {
    if (!supabaseConfigured) {
      setError('Supabase is not configured in this environment')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const { error: rpcErr } = await supabase.rpc('transition_kit_status', {
        p_kit_id: kitId,
        p_new_status: newStatus,
      })

      if (rpcErr) throw rpcErr

      setSuccess(`Moved to ${newStatus}`)
      await loadKits()
    } catch (e) {
      setError(e?.message || 'Failed to update status')
    } finally {
      setLoading(false)
    }
  }

  const handleCheckLockedBundle = async () => {
    if (!organizationId) return
    if (!supabaseConfigured) {
      setBundleStatus({ ok: false, message: 'Supabase is not configured in this environment' })
      return
    }

    setBundleStatus(null)
    try {
      const { data, error: rpcErr } = await supabase.rpc('get_locked_kit_bundle', {
        p_organization_id: organizationId,
      })

      if (rpcErr) throw rpcErr

      setBundleStatus({ ok: true, message: 'All 6 kits locked', data })
    } catch (e) {
      setBundleStatus({ ok: false, message: e?.message || 'KIT_MISSING_LOCKED' })
    }
  }

  const active = kitsByType?.[activeKitType] || { draft: null, locked: null }
  const activeEditable = active.draft
  const activeLocked = active.locked
  const completeness = getCompleteness(activeKitType, (() => {
    try {
      return JSON.parse(editorText || '{}')
    } catch {
      return null
    }
  })())

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-xl text-ink">Strategy</h2>
          <p className="text-body-sm text-ink-400">Your brand truth - versioned and locked</p>
        </div>
        <button
          onClick={handleCheckLockedBundle}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
          disabled={loading || !organizationId}
        >
          <CheckCircle2 className="w-4 h-4" strokeWidth={1.5} />
          Verify Locked Kits
        </button>
      </div>

      {!organizationId && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-body-sm text-amber-800">
          No organization selected. Set a workspace/organization for this user.
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-xl text-body-sm text-red-700">
          <AlertTriangle className="w-4 h-4" strokeWidth={1.5} />
          {error}
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-body-sm text-emerald-700">
          <CheckCircle2 className="w-4 h-4" strokeWidth={1.5} />
          {success}
        </div>
      )}

      {bundleStatus && (
        <div className={`p-4 rounded-xl border text-body-sm ${bundleStatus.ok
          ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
          : 'bg-amber-50 border-amber-200 text-amber-800'
          }`}>
          {bundleStatus.message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {KIT_META.map(k => {
          const row = kitsByType?.[k.id] || { draft: null, locked: null }
          const locked = row.locked
          const draft = row.draft
          const status = locked ? 'locked' : draft ? draft.status : 'missing'
          const displayVersion = locked?.version || draft?.version || null
          const displaySchema = locked?.schema_version || draft?.schema_version || null
          const { percent, blockers } = getCompleteness(k.id, draft?.data || locked?.data || null)
          const isActive = activeKitType === k.id

          return (
            <button
              key={k.id}
              onClick={() => setActiveKitType(k.id)}
              className={`p-4 rounded-xl border text-left transition-editorial ${isActive ? 'border-primary bg-signal-muted' : 'border-border bg-card hover:bg-paper-200'
                }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-body-sm text-ink font-medium">{k.name}</div>
                  <div className="text-body-xs text-ink-400 mt-1">{k.description}</div>
                </div>
                <div className="text-right">
                  <div className={`inline-flex items-center px-2 py-0.5 rounded text-body-xs capitalize ${status === 'locked'
                    ? 'bg-emerald-50 text-emerald-700'
                    : status === 'review'
                      ? 'bg-amber-50 text-amber-700'
                      : status === 'draft'
                        ? 'bg-amber-50 text-amber-700'
                        : 'bg-red-50 text-red-700'
                    }`}>
                    {status}
                  </div>
                  {displayVersion && (
                    <div className="text-body-xs text-ink-400 mt-1">v{displayVersion}{displaySchema ? ` • ${displaySchema}` : ''}</div>
                  )}
                </div>
              </div>

              <div className="mt-3">
                <div className="flex items-center justify-between text-body-xs text-ink-400 mb-1">
                  <span>Completeness</span>
                  <span className="font-mono text-ink">{percent}%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${Math.min(percent, 100)}%` }} />
                </div>
                {blockers.length > 0 && (
                  <div className="mt-2 text-body-xs text-ink-400">
                    Blockers: {blockers.slice(0, 3).join(', ')}{blockers.length > 3 ? '…' : ''}
                  </div>
                )}
              </div>
            </button>
          )
        })}
      </div>

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="p-4 border-b border-border-light flex items-center justify-between gap-4">
          <div>
            <div className="text-body-sm text-ink font-medium">{KIT_META.find(k => k.id === activeKitType)?.name}</div>
            <div className="text-body-xs text-ink-400">
              {activeLocked ? `Locked v${activeLocked.version}` : activeEditable ? `Editing ${activeEditable.status} v${activeEditable.version}` : 'No kit exists yet'}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {!activeEditable && (
              <button
                onClick={() => handleCreateDraft(activeKitType)}
                className="flex items-center gap-1 px-3 py-1.5 text-body-xs text-primary bg-signal-muted rounded-lg hover:bg-primary/20 transition-editorial"
                disabled={loading || !organizationId}
              >
                <Plus className="w-3.5 h-3.5" strokeWidth={1.5} />
                Create Draft
              </button>
            )}

            {activeEditable && (
              <>
                <button
                  onClick={handleSaveDraft}
                  className="flex items-center gap-1 px-3 py-1.5 text-body-xs text-primary bg-signal-muted rounded-lg hover:bg-primary/20 transition-editorial"
                  disabled={loading}
                >
                  <Save className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Save
                </button>

                {activeEditable.status === 'draft' && (
                  <button
                    onClick={() => handleTransition(activeEditable.id, 'review')}
                    className="flex items-center gap-1 px-3 py-1.5 text-body-xs text-ink hover:bg-paper-200 rounded-lg transition-editorial"
                    disabled={loading}
                  >
                    <ChevronRight className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Send to Review
                  </button>
                )}

                {activeEditable.status === 'review' && (
                  <button
                    onClick={() => handleTransition(activeEditable.id, 'locked')}
                    className="flex items-center gap-1 px-3 py-1.5 text-body-xs text-primary bg-signal-muted rounded-lg hover:bg-primary/20 transition-editorial"
                    disabled={loading || completeness.blockers.length > 0}
                    title={completeness.blockers.length > 0 ? `Missing: ${completeness.blockers.join(', ')}` : undefined}
                  >
                    <Lock className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Lock
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="text-body-xs text-ink-400">JSON payload</div>
            <div className="text-body-xs text-ink-400">Completeness: <span className="font-mono text-ink">{completeness.percent}%</span></div>
          </div>

          <textarea
            value={editorText}
            onChange={(e) => {
              setEditorText(e.target.value)
              setEditorError(null)
            }}
            disabled={!activeEditable}
            className="w-full min-h-[360px] font-mono text-xs px-3 py-3 bg-paper border border-border rounded-lg text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary disabled:opacity-60"
          />

          {editorError && (
            <div className="mt-3 flex items-center gap-2 text-body-xs text-red-600">
              <AlertTriangle className="w-3.5 h-3.5" strokeWidth={1.5} />
              {editorError}
            </div>
          )}

          {!activeEditable && (
            <div className="mt-3 text-body-xs text-ink-400">
              Create a draft to edit. Agents only consume locked kits.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Billing Tab
const BillingTab = () => {
  const { currentPlan, getPlanLimits } = useRaptorflowStore()
  const { profile } = useAuth()
  const planLimits = getPlanLimits()

  const plans = [
    { id: 'starter', name: 'Starter', price: 5000 },
    { id: 'glide', name: 'Glide', price: 7000 },
    { id: 'soar', name: 'Soar', price: 12000 },
    { id: 'orbit', name: 'Orbit', price: 25000 }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-serif text-xl text-ink">Billing</h2>
        <p className="text-body-sm text-ink-400">Manage your subscription</p>
      </div>

      {/* Current plan */}
      <div className="bg-card border border-primary rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-signal-muted rounded-xl flex items-center justify-center">
              <CreditCard className="w-5 h-5 text-primary" strokeWidth={1.5} />
            </div>
            <div>
              <div className="text-body-sm text-ink font-medium">Current Plan</div>
              <div className="text-lg font-serif text-ink">{planLimits.name}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-mono text-ink">₹{planLimits.price.toLocaleString()}</div>
            <div className="text-body-xs text-ink-400">per month</div>
          </div>
        </div>

        <div className="pt-4 border-t border-border-light">
          <div className="grid grid-cols-3 gap-4 text-body-sm">
            <div>
              <div className="text-ink-400">Radar Scans</div>
              <div className="text-ink font-mono">{planLimits.radarScansPerDay}/day</div>
            </div>
            <div>
              <div className="text-ink-400">Black Box Duels</div>
              <div className="text-ink font-mono">{planLimits.blackBoxDuelsPerMonth}/mo</div>
            </div>
            <div>
              <div className="text-ink-400">Muse Generations</div>
              <div className="text-ink font-mono">{planLimits.museGenerationsPerMonth}/mo</div>
            </div>
          </div>
        </div>
      </div>

      {/* All plans */}
      <div>
        <h3 className="text-body-sm text-ink font-medium mb-3">All Plans</h3>
        <div className="grid grid-cols-2 gap-4">
          {plans.map(plan => {
            const limits = PLAN_LIMITS[plan.id]
            const isCurrent = currentPlan === plan.id

            return (
              <div
                key={plan.id}
                className={`p-4 rounded-xl border ${isCurrent ? 'border-primary bg-signal-muted' : 'border-border bg-card'
                  }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-body-sm text-ink font-medium">{plan.name}</span>
                  {isCurrent && (
                    <span className="px-2 py-0.5 bg-primary text-white rounded text-body-xs">
                      Current
                    </span>
                  )}
                </div>
                <div className="text-lg font-mono text-ink mb-3">
                  ₹{plan.price.toLocaleString()}/mo
                </div>
                <div className="space-y-1 text-body-xs text-ink-400">
                  <div>{limits.radarScansPerDay} scans/day</div>
                  <div>{limits.blackBoxDuelsPerMonth} duels/mo</div>
                  <div>{limits.museGenerationsPerMonth} generations/mo</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// Team Tab
const TeamTab = () => {
  const { profile } = useAuth()
  const { getPlanLimits } = useRaptorflowStore()
  const planLimits = getPlanLimits()

  // Mock team members
  const teamMembers = [
    { id: '1', name: profile?.full_name || 'You', email: profile?.email || 'you@example.com', role: 'Owner' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-xl text-ink">Team</h2>
          <p className="text-body-sm text-ink-400">
            {teamMembers.length} of {planLimits.seats} seats used
          </p>
        </div>
        <button
          disabled={teamMembers.length >= planLimits.seats}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial disabled:opacity-50"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          Invite Member
        </button>
      </div>

      {/* Team list */}
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-paper-200">
              <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400">Member</th>
              <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400">Role</th>
              <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400 w-12"></th>
            </tr>
          </thead>
          <tbody>
            {teamMembers.map(member => (
              <tr key={member.id} className="border-b border-border-light last:border-0">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-paper-200 rounded-full flex items-center justify-center">
                      <span className="text-body-xs text-ink font-medium">
                        {member.name[0].toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <div className="text-body-sm text-ink">{member.name}</div>
                      <div className="text-body-xs text-ink-400">{member.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-primary/10 text-primary rounded text-body-xs">
                    {member.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {member.role !== 'Owner' && (
                    <button className="p-1 text-ink-400 hover:text-red-500 transition-editorial">
                      <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Usage Tab
const UsageTab = () => {
  const { usage, getPlanLimits } = useRaptorflowStore()
  const planLimits = getPlanLimits()

  const usageMetrics = [
    {
      name: 'Radar Scans',
      used: usage.radarScansToday,
      limit: planLimits.radarScansPerDay,
      period: 'today',
      resetText: 'Resets daily at midnight'
    },
    {
      name: 'Black Box Duels',
      used: usage.blackBoxDuelsThisMonth,
      limit: planLimits.blackBoxDuelsPerMonth,
      period: 'this month',
      resetText: 'Resets on the 1st'
    },
    {
      name: 'Muse Generations',
      used: usage.museGenerationsThisMonth,
      limit: planLimits.museGenerationsPerMonth,
      period: 'this month',
      resetText: 'Resets on the 1st'
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-serif text-xl text-ink">Usage</h2>
        <p className="text-body-sm text-ink-400">Track your feature usage and limits</p>
      </div>

      {/* Usage meters */}
      <div className="space-y-4">
        {usageMetrics.map(metric => {
          const percentage = Math.round((metric.used / metric.limit) * 100)
          const isNearLimit = percentage >= 80
          const isAtLimit = percentage >= 100

          return (
            <div key={metric.name} className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="text-body-sm text-ink font-medium">{metric.name}</h3>
                  <p className="text-body-xs text-ink-400">{metric.resetText}</p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-mono text-ink">
                    {metric.used} <span className="text-ink-400">/ {metric.limit}</span>
                  </div>
                  <div className="text-body-xs text-ink-400">{metric.period}</div>
                </div>
              </div>

              <div className="h-3 bg-muted rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(percentage, 100)}%` }}
                  className={`h-full rounded-full ${isAtLimit ? 'bg-red-500' : isNearLimit ? 'bg-amber-500' : 'bg-primary'
                    }`}
                />
              </div>

              {isNearLimit && !isAtLimit && (
                <div className="flex items-center gap-2 mt-3 text-body-xs text-amber-600">
                  <AlertTriangle className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Approaching limit
                </div>
              )}
              {isAtLimit && (
                <div className="flex items-center gap-2 mt-3 text-body-xs text-red-500">
                  <AlertTriangle className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Limit reached
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Plan limits overview */}
      <div className="bg-paper-200 border border-border-light rounded-xl p-5">
        <h3 className="text-body-sm text-ink font-medium mb-4">Your Plan Limits ({planLimits.name})</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-body-sm">
          <div>
            <div className="text-ink-400">ICPs</div>
            <div className="text-ink font-mono">{planLimits.icps}</div>
          </div>
          <div>
            <div className="text-ink-400">Active Campaigns</div>
            <div className="text-ink font-mono">{planLimits.activeCampaigns}</div>
          </div>
          <div>
            <div className="text-ink-400">Moves/Month</div>
            <div className="text-ink font-mono">{planLimits.movesPerMonth}</div>
          </div>
          <div>
            <div className="text-ink-400">Seats</div>
            <div className="text-ink font-mono">{planLimits.seats}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Main Settings Page
const SettingsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get('tab') || 'strategy'

  const handleTabChange = (tab) => {
    setSearchParams({ tab })
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-serif text-headline-md text-ink">Settings</h1>
        <p className="text-body-sm text-ink-400 mt-1">Configure your RaptorFlow workspace</p>
      </motion.div>

      {/* Content */}
      <div className="flex gap-8">
        <TabNav activeTab={activeTab} onTabChange={handleTabChange} />

        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex-1 min-w-0"
        >
          {activeTab === 'strategy' && <StrategyTab />}
          {activeTab === 'billing' && <EnhancedBillingTab />}
          {activeTab === 'team' && <EnhancedTeamTab />}
          {activeTab === 'usage' && <UsageTab />}
        </motion.div>
      </div>
    </div>
  )
}

export default SettingsPage
