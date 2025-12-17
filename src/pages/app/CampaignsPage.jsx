import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Plus,
  Layers,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  X,
  Trash2,
  Target,
  Calendar,
  Sparkles,
  PenLine,
  AlertTriangle,
  CheckCircle2,
  Circle,
  AlertCircle,
  Loader2,
  TrendingUp
} from 'lucide-react'
import useRaptorflowStore from '../../store/raptorflowStore'
import { Modal } from '@/components/system/Modal'

// Channel icons and names
const CHANNELS = [
  { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
  { id: 'twitter', name: 'X / Twitter', icon: '𝕏' },
  { id: 'instagram', name: 'Instagram', icon: '📸' },
  { id: 'email', name: 'Email', icon: '✉️' },
  { id: 'whatsapp', name: 'WhatsApp', icon: '💬' },
  { id: 'youtube', name: 'YouTube', icon: '▶️' }
]

const makeLocalId = () => `${Date.now()}_${Math.random().toString(36).slice(2, 9)}`

// Channel fit badge
const ChannelFitBadge = ({ fit }) => {
  const styles = {
    recommended: { bg: 'bg-emerald-50', text: 'text-emerald-600', icon: CheckCircle2, label: 'Recommended' },
    risky: { bg: 'bg-amber-50', text: 'text-amber-600', icon: AlertCircle, label: 'Risky' },
    notfit: { bg: 'bg-red-50', text: 'text-red-500', icon: AlertTriangle, label: "Don't use" }
  }
  const style = styles[fit] || styles.risky
  const Icon = style.icon

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-body-xs ${style.bg} ${style.text}`}>
      <Icon className="w-3 h-3" strokeWidth={1.5} />
      {style.label}
    </span>
  )
}

// Campaign card
const CampaignCard = ({ campaign, onClick }) => {
  const { getCampaignHealth, getCampaignPhase } = useRaptorflowStore()
  const health = getCampaignHealth?.(campaign.id)
  const phase = health?.phase || getCampaignPhase?.(campaign.id) || 'Awareness'
  const execution = typeof health?.execution === 'number' ? health.execution : null
  const performance = typeof health?.performance === 'number' ? health.performance : null

  const progress = campaign.kpis?.primary?.target > 0
    ? Math.round((campaign.kpis.primary.current / campaign.kpis.primary.target) * 100)
    : 0

  const objectiveId = `campaign_card_objective_${campaign.id}`

  return (
    <motion.button
      type="button"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      onClick={onClick}
      aria-label={`Open campaign ${campaign.name}`}
      aria-describedby={objectiveId}
      className="w-full text-left p-5 bg-card border border-border rounded-xl hover:border-border-dark transition-editorial group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-paper-200 rounded-xl flex items-center justify-center">
            <Layers className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
          </div>
          <div>
            <h3 className="font-serif text-lg text-ink group-hover:text-primary transition-editorial">
              {campaign.name}
            </h3>
            <p id={objectiveId} className="text-body-xs text-ink-400">{campaign.objective}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded text-body-xs capitalize ${campaign.status === 'active' ? 'bg-emerald-50 text-emerald-600' :
            campaign.status === 'draft' ? 'bg-amber-50 text-amber-600' :
              'bg-muted text-ink-400'
          }`}>
          {campaign.status}
        </span>
      </div>

      <div className="flex items-center justify-between text-body-xs text-ink-400 mb-4">
        <span className="inline-flex items-center gap-2">
          <span className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400">Phase: {phase}</span>
        </span>
        {execution !== null && performance !== null && (
          <span className="font-mono text-ink-400">
            Exec {execution}% · Perf {performance}%
          </span>
        )}
      </div>

      {/* Channels */}
      <div className="flex items-center gap-2 mb-4">
        {campaign.channels?.map(ch => {
          const channel = CHANNELS.find(c => c.id === ch)
          return (
            <span key={ch} className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400">
              {channel?.icon} {channel?.name}
            </span>
          )
        })}
      </div>

      {/* KPI Progress */}
      {campaign.kpis?.primary && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-body-xs text-ink-400">{campaign.kpis.primary.name}</span>
            <span className="text-body-xs text-ink font-mono">
              {campaign.kpis.primary.current} / {campaign.kpis.primary.target}
            </span>
          </div>
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between text-body-xs text-ink-400">
        <span>{new Date(campaign.createdAt).toLocaleDateString()}</span>
        <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-editorial" strokeWidth={1.5} />
      </div>
    </motion.button>
  )
}

// Create Campaign Modal
const CreateCampaignModal = ({ isOpen, onClose }) => {
  const navigate = useNavigate()
  const { cohorts, createCampaign, updateCampaign, getChannelFit } = useRaptorflowStore()

  const [view, setView] = useState('chooser')
  const [wizardStep, setWizardStep] = useState(1)
  const [source, setSource] = useState('blank')

  const [aiPrompt, setAiPrompt] = useState('')
  const [aiHints, setAiHints] = useState({ audience: false, offer: false, channel: false })
  const [aiTimeframe, setAiTimeframe] = useState('30')
  const [isGenerating, setIsGenerating] = useState(false)

  const [selectedTemplateId, setSelectedTemplateId] = useState(null)

  const [formData, setFormData] = useState(() => {
    const start = new Date().toISOString().slice(0, 10)
    const end = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
    return {
      name: '',
      objective: '',
      owner: 'me',
      startDate: start,
      endDate: end,
      kpiPrimary: '',
      kpiBaseline: 0,
      kpiTarget: 0,
      kpiDeadline: end,
      measurementMethod: 'manual',
      attribution: 'manual',
      primaryCohortId: '',
      secondaryCohortIds: [],
      stage: '',
      channels: [],
      deliverables: {
        landingPage: 0,
        ads: 0,
        emails: 0,
        linkedinPosts: 0,
        dmScripts: 0,
        caseStudies: 0,
        videoScripts: 0,
      },
      budget: '',
      timeBudget: '',
      approvalMode: 'solo',
      messageBackbone: 'none',
      storybrand: {
        character: '',
        problem: '',
        guide: '',
        plan: '',
        cta: '',
        success: '',
        failure: '',
      },
      aida: {
        attention: '',
        interest: '',
        desire: '',
        action: '',
      },
      pas: {
        problem: '',
        agitate: '',
        solve: '',
      },
    }
  })

  useEffect(() => {
    if (!isOpen) {
      setView('chooser')
      setWizardStep(1)
      setSource('blank')
      setAiPrompt('')
      setAiHints({ audience: false, offer: false, channel: false })
      setAiTimeframe('30')
      setSelectedTemplateId(null)
      const start = new Date().toISOString().slice(0, 10)
      const end = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
      setFormData(prev => ({
        ...prev,
        name: '',
        objective: '',
        startDate: start,
        endDate: end,
        kpiPrimary: '',
        kpiBaseline: 0,
        kpiTarget: 0,
        kpiDeadline: end,
        measurementMethod: 'manual',
        attribution: 'manual',
        primaryCohortId: '',
        secondaryCohortIds: [],
        stage: '',
        channels: [],
        deliverables: {
          landingPage: 0,
          ads: 0,
          emails: 0,
          linkedinPosts: 0,
          dmScripts: 0,
          caseStudies: 0,
          videoScripts: 0,
        },
        budget: '',
        timeBudget: '',
        approvalMode: 'solo',
        messageBackbone: 'none',
        storybrand: {
          character: '',
          problem: '',
          guide: '',
          plan: '',
          cta: '',
          success: '',
          failure: '',
        },
        aida: { attention: '', interest: '', desire: '', action: '' },
        pas: { problem: '', agitate: '', solve: '' },
      }))
    }
  }, [isOpen])

  const templates = useMemo(() => ([
    {
      id: 'tmpl_lead_gen_sprint',
      name: 'Lead Gen Sprint',
      subtitle: '30 days · pipeline focus',
      defaults: {
        kpiPrimary: 'qualified_leads',
        kpiBaseline: 0,
        kpiTarget: 30,
        channels: ['linkedin', 'email'],
        messageBackbone: 'aida',
        deliverables: {
          landingPage: 1,
          ads: 0,
          emails: 6,
          linkedinPosts: 12,
          dmScripts: 2,
          caseStudies: 1,
          videoScripts: 0,
        },
      },
    },
    {
      id: 'tmpl_webinar_to_sales',
      name: 'Webinar → Sales',
      subtitle: '21 days · event conversion',
      defaults: {
        kpiPrimary: 'booked_calls',
        kpiBaseline: 0,
        kpiTarget: 10,
        channels: ['linkedin', 'email'],
        messageBackbone: 'storybrand',
        deliverables: {
          landingPage: 1,
          ads: 0,
          emails: 5,
          linkedinPosts: 8,
          dmScripts: 1,
          caseStudies: 0,
          videoScripts: 1,
        },
      },
    },
    {
      id: 'tmpl_product_launch',
      name: 'Product Launch',
      subtitle: '14 days · announcement + follow-up',
      defaults: {
        kpiPrimary: 'signups',
        kpiBaseline: 0,
        kpiTarget: 100,
        channels: ['linkedin', 'email'],
        messageBackbone: 'pas',
        deliverables: {
          landingPage: 1,
          ads: 0,
          emails: 4,
          linkedinPosts: 6,
          dmScripts: 1,
          caseStudies: 0,
          videoScripts: 1,
        },
      },
    },
    {
      id: 'tmpl_winback',
      name: 'Retention Winback',
      subtitle: '30 days · reactivation',
      defaults: {
        kpiPrimary: 'paid_conversions',
        kpiBaseline: 0,
        kpiTarget: 10,
        channels: ['email', 'whatsapp'],
        messageBackbone: 'aida',
        deliverables: {
          landingPage: 0,
          ads: 0,
          emails: 6,
          linkedinPosts: 0,
          dmScripts: 0,
          caseStudies: 0,
          videoScripts: 0,
        },
      },
    },
  ]), [])

  const applyTemplate = (template) => {
    if (!template) return
    setSelectedTemplateId(template.id)
    setSource('template')
    const start = new Date().toISOString().slice(0, 10)
    const durationDays = template.id === 'tmpl_product_launch' ? 14 : template.id === 'tmpl_webinar_to_sales' ? 21 : 30
    const end = new Date(Date.now() + durationDays * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
    setFormData(prev => ({
      ...prev,
      name: template.name,
      objective: prev.objective || '',
      startDate: start,
      endDate: end,
      kpiDeadline: end,
      ...(template.defaults || {}),
      primaryCohortId: prev.primaryCohortId || cohorts?.[0]?.id || '',
    }))
    setView('wizard')
    setWizardStep(1)
  }

  const getChannelFitForSelected = (channelId) => {
    if (!formData.primaryCohortId) return 'risky'
    return getChannelFit(formData.primaryCohortId, channelId)
  }

  const warnings = useMemo(() => {
    const list = []
    if (formData.channels.length >= 6) list.push('You’re spreading thin. Pick 1–3 channels to start.')
    if (formData.secondaryCohortIds.length >= 2) list.push('Targeting is diluted. Keep 1 primary cohort.')
    if ((formData.objective || '').trim() && !/\d/.test(formData.objective)) list.push('Objective doesn’t look measurable. Add a number + timeframe.')
    return list
  }, [formData.channels.length, formData.objective, formData.secondaryCohortIds.length])

  const activationRequirements = useMemo(() => {
    const reasons = []
    if (!formData.name.trim()) reasons.push('Campaign name is required.')
    if (!formData.objective.trim()) reasons.push('One-line objective is required.')
    if (!formData.startDate || !formData.endDate) reasons.push('Start + end dates are required.')
    if (!formData.kpiPrimary) reasons.push('Primary KPI is required.')
    if (!Number.isFinite(Number(formData.kpiBaseline))) reasons.push('Baseline must be a number.')
    if (!Number.isFinite(Number(formData.kpiTarget)) || Number(formData.kpiTarget) <= Number(formData.kpiBaseline)) reasons.push('Target must be > baseline.')
    if (!formData.kpiDeadline) reasons.push('KPI deadline is required.')
    if (!formData.primaryCohortId) reasons.push('Primary cohort is required.')
    if (formData.channels.length === 0) reasons.push('Pick at least one channel.')
    reasons.push('No ready Move linked yet (create a Move in Moves, then attach it in the campaign).')
    return reasons
  }, [formData])

  const canActivate = activationRequirements.length === 0

  const handleGenerateBrief = async () => {
    if (!aiPrompt.trim()) return
    setIsGenerating(true)
    await new Promise(resolve => setTimeout(resolve, 1200))
    const timeframeDays = Number(aiTimeframe || 30)
    const start = new Date().toISOString().slice(0, 10)
    const end = new Date(Date.now() + timeframeDays * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)

    const objective = aiPrompt.trim().length > 140 ? `${aiPrompt.trim().slice(0, 137)}…` : aiPrompt.trim()
    const name = objective.length > 56 ? `${objective.slice(0, 53)}…` : objective

    setFormData(prev => ({
      ...prev,
      name: prev.name || name,
      objective: prev.objective || objective,
      startDate: start,
      endDate: end,
      kpiDeadline: end,
      kpiPrimary: prev.kpiPrimary || 'qualified_leads',
      kpiBaseline: Number.isFinite(Number(prev.kpiBaseline)) ? prev.kpiBaseline : 0,
      kpiTarget: Number(prev.kpiTarget || 30) || 30,
      primaryCohortId: prev.primaryCohortId || cohorts?.[0]?.id || '',
      channels: prev.channels.length ? prev.channels : ['linkedin', 'email'],
      deliverables: {
        ...prev.deliverables,
        emails: prev.deliverables?.emails || 6,
        linkedinPosts: prev.deliverables?.linkedinPosts || 12,
        dmScripts: prev.deliverables?.dmScripts || 2,
        landingPage: prev.deliverables?.landingPage || 1,
      },
      messageBackbone: prev.messageBackbone !== 'none' ? prev.messageBackbone : 'storybrand',
    }))

    setIsGenerating(false)
    setSource('ai')
    setView('wizard')
    setWizardStep(1)
  }

  const setDeliverable = (key, value) => {
    const next = Number(value)
    setFormData(prev => ({
      ...prev,
      deliverables: {
        ...(prev.deliverables || {}),
        [key]: Number.isFinite(next) && next >= 0 ? next : 0,
      }
    }))
  }

  const toggleSecondaryCohort = (cohortId) => {
    setFormData(prev => ({
      ...prev,
      secondaryCohortIds: prev.secondaryCohortIds.includes(cohortId)
        ? prev.secondaryCohortIds.filter(c => c !== cohortId)
        : [...prev.secondaryCohortIds, cohortId]
    }))
  }

  const toggleChannel = (channelId) => {
    setFormData(prev => ({
      ...prev,
      channels: prev.channels.includes(channelId)
        ? prev.channels.filter(c => c !== channelId)
        : [...prev.channels, channelId]
    }))
  }

  const canProceed = () => {
    if (wizardStep === 1) return Boolean(formData.name.trim()) && Boolean(formData.objective.trim()) && Boolean(formData.startDate) && Boolean(formData.endDate)
    if (wizardStep === 2) return Boolean(formData.kpiPrimary) && Number(formData.kpiTarget) > Number(formData.kpiBaseline) && Boolean(formData.kpiDeadline)
    if (wizardStep === 3) return Boolean(formData.primaryCohortId)
    if (wizardStep === 4) return formData.channels.length > 0
    return true
  }

  const buildCampaignPayload = () => {
    const baseline = Number(formData.kpiBaseline || 0)
    const target = Number(formData.kpiTarget || 0)
    const kpiName = formData.kpiPrimary || 'Primary KPI'
    return {
      name: formData.name.trim(),
      objective: formData.objective.trim(),
      cohorts: [formData.primaryCohortId, ...(formData.secondaryCohortIds || [])].filter(Boolean),
      channels: formData.channels,
      kpis: {
        primary: { name: kpiName, baseline: Number.isFinite(baseline) ? baseline : 0, target: Number.isFinite(target) ? target : 0, current: 0 },
        reach: { name: 'Reach', baseline: 0, target: 0, current: 0 },
        click: { name: 'Clicks', baseline: 0, target: 0, current: 0 },
        convert: { name: 'Conversions', baseline: 0, target: 0, current: 0 },
      },
      timeline: {
        startDate: formData.startDate,
        endDate: formData.endDate,
        milestones: [],
        weeks: [],
      },
      blueprint: {
        objective: {
          text: formData.objective.trim(),
          primaryKpi: { name: kpiName, baseline: baseline, target: target, current: 0 },
        },
      },
      brief: {
        attribution: formData.attribution,
        measurementMethod: formData.measurementMethod,
        stage: formData.stage || null,
        deliverables: formData.deliverables,
        budget: formData.budget || null,
        timeBudget: formData.timeBudget || null,
        approvalMode: formData.approvalMode,
        messageBackbone: formData.messageBackbone,
        storybrand: formData.storybrand,
        aida: formData.aida,
        pas: formData.pas,
      },
    }
  }

  const handleCreate = (activate) => {
    const payload = buildCampaignPayload()
    const newCampaign = createCampaign(payload)
    if (activate && newCampaign?.id) {
      updateCampaign?.(newCampaign.id, { status: 'active' })
    }
    onClose()
    navigate(`/app/campaigns/${newCampaign.id}`)
  }

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => !open && onClose()}
      title="Create Campaign"
      description="A campaign brief + KPI contract. Moves get linked later in Moves."
      contentClassName="max-w-3xl"
    >
      {view === 'chooser' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
              type="button"
              onClick={() => {
                setSource('ai')
                setView('ai_prompt')
              }}
              className="p-4 rounded-2xl border border-primary/20 bg-signal-muted text-left hover:bg-primary/10 transition-editorial"
            >
              <div className="flex items-center gap-2 text-body-sm text-ink font-medium">
                <Sparkles className="w-4 h-4 text-primary" strokeWidth={1.5} />
                AI Brief
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">Recommended</span>
              </div>
              <div className="mt-2 text-body-xs text-ink-400">Describe it vaguely. We’ll turn it into a measurable campaign brief.</div>
            </button>
            <button
              type="button"
              onClick={() => {
                setSource('template')
                setView('template_gallery')
              }}
              className="p-4 rounded-2xl border border-border bg-card text-left hover:bg-paper-200 transition-editorial"
            >
              <div className="flex items-center gap-2 text-body-sm text-ink font-medium">
                <Layers className="w-4 h-4" strokeWidth={1.5} />
                Start from Template
              </div>
              <div className="mt-2 text-body-xs text-ink-400">Pre-filled KPI + channels + deliverables + timing.</div>
            </button>
            <button
              type="button"
              onClick={() => {
                setSource('blank')
                setView('wizard')
                setWizardStep(1)
              }}
              className="p-4 rounded-2xl border border-border bg-card text-left hover:bg-paper-200 transition-editorial"
            >
              <div className="flex items-center gap-2 text-body-sm text-ink font-medium">
                <PenLine className="w-4 h-4" strokeWidth={1.5} />
                Blank Campaign
              </div>
              <div className="mt-2 text-body-xs text-ink-400">I’ll set everything myself.</div>
            </button>
          </div>
          <div className="text-body-xs text-ink-400">What you’ll get: a campaign brief + KPI tracker + a place to link Moves later (Moves are created in Moves).</div>
        </div>
      )}

      {view === 'ai_prompt' && (
        <div className="space-y-4">
          <div>
            <label className="block text-body-sm text-ink mb-2">What are you trying to achieve?</label>
            <textarea
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="E.g., Generate 50 qualified leads in 30 days from B2B founders using LinkedIn + email"
              rows={4}
              className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {['Audience', 'Offer', 'Channel'].map((label) => {
              const key = label.toLowerCase()
              const active = Boolean(aiHints[key])
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => setAiHints(prev => ({ ...prev, [key]: !prev[key] }))}
                  className={`px-3 py-1.5 rounded-full border text-body-xs transition-editorial ${
                    active ? 'border-primary bg-primary/10 text-primary' : 'border-border bg-paper text-ink-400 hover:text-ink'
                  }`}
                >
                  {label}
                </button>
              )
            })}

            <div className="flex items-center gap-2 ml-auto">
              <span className="text-body-xs text-ink-400">Timeframe</span>
              <select
                value={aiTimeframe}
                onChange={(e) => setAiTimeframe(e.target.value)}
                className="px-3 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink"
              >
                <option value="7">7 days</option>
                <option value="14">14 days</option>
                <option value="30">30 days</option>
                <option value="90">90 days</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setView('chooser')}
              className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
            >
              Back
            </button>
            <button
              type="button"
              onClick={handleGenerateBrief}
              disabled={!aiPrompt.trim() || isGenerating}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial disabled:opacity-50"
            >
              {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} /> : <Sparkles className="w-4 h-4" strokeWidth={1.5} />}
              Generate Brief
            </button>
          </div>
        </div>
      )}

      {view === 'template_gallery' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-serif text-lg text-ink">Choose a template</div>
              <div className="text-body-xs text-ink-400">Pre-fills KPI contract, channels, deliverables, and a message backbone.</div>
            </div>
            <button
              type="button"
              onClick={() => setView('chooser')}
              className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
            >
              Back
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {templates.map(t => (
              <button
                key={t.id}
                type="button"
                onClick={() => applyTemplate(t)}
                className={`p-4 rounded-2xl border text-left transition-editorial ${
                  selectedTemplateId === t.id ? 'border-primary bg-signal-muted' : 'border-border bg-card hover:bg-paper-200'
                }`}
              >
                <div className="font-serif text-lg text-ink">{t.name}</div>
                <div className="mt-1 text-body-xs text-ink-400">{t.subtitle}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {view === 'wizard' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-body-xs text-ink-400">
              {source === 'ai' ? 'AI Brief' : source === 'template' ? 'Template' : 'Blank'} · Step {wizardStep} of 8
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  if (wizardStep === 1) {
                    setView('chooser')
                    return
                  }
                  setWizardStep(s => Math.max(1, s - 1))
                }}
                className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
              >
                Back
              </button>
              {wizardStep < 8 ? (
                <button
                  type="button"
                  onClick={() => setWizardStep(s => Math.min(8, s + 1))}
                  disabled={!canProceed()}
                  className="px-3 py-2 text-body-xs bg-primary text-primary-foreground rounded-lg hover:opacity-95 transition-editorial disabled:opacity-50"
                >
                  Next
                </button>
              ) : null}
            </div>
          </div>

          {warnings.length > 0 && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-body-sm text-amber-700">
              {warnings.map((w, idx) => (
                <div key={`warn_${idx}`}>- {w}</div>
              ))}
            </div>
          )}

          {wizardStep === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-body-sm text-ink mb-2">Campaign name</label>
                <input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Campaign name"
                  className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                />
              </div>
              <div>
                <label className="block text-body-sm text-ink mb-2">One-line objective</label>
                <input
                  value={formData.objective}
                  onChange={(e) => setFormData(prev => ({ ...prev, objective: e.target.value.slice(0, 140) }))}
                  placeholder="Generate 50 qualified leads in 30 days"
                  className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                />
                <div className="mt-1 text-body-xs text-ink-400">{String(formData.objective || '').length}/140</div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-body-sm text-ink mb-2">Start date</label>
                  <input
                    type="date"
                    value={formData.startDate}
                    onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                    className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                  />
                </div>
                <div>
                  <label className="block text-body-sm text-ink mb-2">End date</label>
                  <input
                    type="date"
                    value={formData.endDate}
                    onChange={(e) => {
                      const next = e.target.value
                      setFormData(prev => ({ ...prev, endDate: next, kpiDeadline: prev.kpiDeadline || next }))
                    }}
                    className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                  />
                </div>
              </div>
            </div>
          )}

          {wizardStep === 2 && (
            <div className="space-y-4">
              <div className="text-body-sm text-ink">Success Metrics Contract</div>
              <div>
                <label className="block text-body-xs text-ink-400 mb-1">Primary KPI</label>
                <select
                  value={formData.kpiPrimary}
                  onChange={(e) => setFormData(prev => ({ ...prev, kpiPrimary: e.target.value }))}
                  className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                >
                  <option value="">Select KPI...</option>
                  <option value="leads">Leads captured</option>
                  <option value="booked_calls">Booked calls</option>
                  <option value="trials">Trials started</option>
                  <option value="paid_conversions">Paid conversions</option>
                  <option value="revenue">Revenue</option>
                  <option value="cac">CAC / CPA</option>
                  <option value="qualified_leads">Qualified leads</option>
                  <option value="signups">Signups</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Baseline</label>
                  <input
                    type="number"
                    value={formData.kpiBaseline}
                    onChange={(e) => setFormData(prev => ({ ...prev, kpiBaseline: Number(e.target.value || 0) }))}
                    className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                  />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Target</label>
                  <input
                    type="number"
                    value={formData.kpiTarget}
                    onChange={(e) => setFormData(prev => ({ ...prev, kpiTarget: Number(e.target.value || 0) }))}
                    className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Deadline</label>
                  <input
                    type="date"
                    value={formData.kpiDeadline}
                    onChange={(e) => setFormData(prev => ({ ...prev, kpiDeadline: e.target.value }))}
                    className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                  />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Attribution</label>
                  <select
                    value={formData.attribution}
                    onChange={(e) => setFormData(prev => ({ ...prev, attribution: e.target.value }))}
                    className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                  >
                    <option value="manual">Manual</option>
                    <option value="utm">UTM (later)</option>
                    <option value="crm">CRM (later)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-body-xs text-ink-400 mb-1">How it’s measured</label>
                <select
                  value={formData.measurementMethod}
                  onChange={(e) => setFormData(prev => ({ ...prev, measurementMethod: e.target.value }))}
                  className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                >
                  <option value="manual">Manual entry</option>
                  <option value="utm">UTM link tracking (later)</option>
                  <option value="crm">CRM integration (later)</option>
                </select>
              </div>
            </div>
          )}

          {wizardStep === 3 && (
            <div className="space-y-4">
              <div>
                <label className="block text-body-sm text-ink mb-2">Primary cohort / ICP</label>
                <select
                  value={formData.primaryCohortId}
                  onChange={(e) => setFormData(prev => ({ ...prev, primaryCohortId: e.target.value }))}
                  className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                >
                  <option value="">Select cohort...</option>
                  {(cohorts || []).map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <div className="text-body-sm text-ink mb-2">Secondary cohorts (optional)</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {(cohorts || []).filter(c => c.id !== formData.primaryCohortId).map(cohort => (
                    <button
                      key={cohort.id}
                      type="button"
                      onClick={() => toggleSecondaryCohort(cohort.id)}
                      className={`p-3 rounded-xl border text-left transition-editorial ${
                        formData.secondaryCohortIds.includes(cohort.id)
                          ? 'border-primary bg-signal-muted'
                          : 'border-border hover:border-border-dark'
                      }`}
                    >
                      <div className="text-body-sm text-ink font-medium">{cohort.name}</div>
                      <div className="text-body-xs text-ink-400 line-clamp-1">{cohort.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-body-sm text-ink mb-2">Funnel stage (optional)</label>
                <select
                  value={formData.stage}
                  onChange={(e) => setFormData(prev => ({ ...prev, stage: e.target.value }))}
                  className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                >
                  <option value="">None</option>
                  <option value="awareness">Awareness</option>
                  <option value="consideration">Consideration</option>
                  <option value="conversion">Conversion</option>
                  <option value="retention">Retention</option>
                </select>
              </div>
            </div>
          )}

          {wizardStep === 4 && (
            <div className="space-y-4">
              <div className="text-body-sm text-ink">Channels</div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {CHANNELS.map(channel => {
                  const isSelected = formData.channels.includes(channel.id)
                  const fit = getChannelFitForSelected(channel.id)
                  return (
                    <button
                      key={channel.id}
                      type="button"
                      onClick={() => toggleChannel(channel.id)}
                      className={`p-3 rounded-xl border text-center transition-editorial ${
                        isSelected
                          ? fit === 'notfit'
                            ? 'border-red-300 bg-red-50'
                            : 'border-primary bg-signal-muted'
                          : 'border-border hover:border-border-dark'
                      }`}
                    >
                      <div className="text-lg mb-1">{channel.icon}</div>
                      <div className="text-body-xs text-ink">{channel.name}</div>
                      {formData.primaryCohortId && (
                        <div className="mt-1">
                          <ChannelFitBadge fit={fit} />
                        </div>
                      )}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {wizardStep === 5 && (
            <div className="space-y-4">
              <div className="text-body-sm text-ink">Deliverables (Bill of Materials)</div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Landing page</label>
                  <input type="number" value={formData.deliverables.landingPage} onChange={(e) => setDeliverable('landingPage', e.target.value)} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Ads (variants)</label>
                  <input type="number" value={formData.deliverables.ads} onChange={(e) => setDeliverable('ads', e.target.value)} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Emails</label>
                  <input type="number" value={formData.deliverables.emails} onChange={(e) => setDeliverable('emails', e.target.value)} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">LinkedIn posts</label>
                  <input type="number" value={formData.deliverables.linkedinPosts} onChange={(e) => setDeliverable('linkedinPosts', e.target.value)} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">DM scripts</label>
                  <input type="number" value={formData.deliverables.dmScripts} onChange={(e) => setDeliverable('dmScripts', e.target.value)} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Case studies / proof</label>
                  <input type="number" value={formData.deliverables.caseStudies} onChange={(e) => setDeliverable('caseStudies', e.target.value)} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
                <div className="col-span-2">
                  <label className="block text-body-xs text-ink-400 mb-1">Video scripts</label>
                  <input type="number" value={formData.deliverables.videoScripts} onChange={(e) => setDeliverable('videoScripts', e.target.value)} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
              </div>
            </div>
          )}

          {wizardStep === 6 && (
            <div className="space-y-4">
              <div className="text-body-sm text-ink">Budget + Constraints</div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Budget (optional)</label>
                  <input value={formData.budget} onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value }))} placeholder="₹ / $" className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
                <div>
                  <label className="block text-body-xs text-ink-400 mb-1">Time budget (optional)</label>
                  <input value={formData.timeBudget} onChange={(e) => setFormData(prev => ({ ...prev, timeBudget: e.target.value }))} placeholder="hours/week" className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink" />
                </div>
              </div>
              <div>
                <label className="block text-body-xs text-ink-400 mb-1">Approval mode</label>
                <select value={formData.approvalMode} onChange={(e) => setFormData(prev => ({ ...prev, approvalMode: e.target.value }))} className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink">
                  <option value="solo">Solo (no approvals)</option>
                  <option value="team">Team approval required</option>
                  <option value="strict">Strict approvals</option>
                </select>
              </div>
            </div>
          )}

          {wizardStep === 7 && (
            <div className="space-y-4">
              <div className="text-body-sm text-ink">Pick a message backbone (optional)</div>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'storybrand', label: 'StoryBrand (7)' },
                  { id: 'aida', label: 'AIDA' },
                  { id: 'pas', label: 'PAS' },
                  { id: 'none', label: 'None' },
                ].map(opt => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, messageBackbone: opt.id }))}
                    className={`px-3 py-2 rounded-xl border text-body-sm transition-editorial ${
                      formData.messageBackbone === opt.id ? 'border-primary bg-signal-muted text-primary' : 'border-border bg-paper text-ink-400 hover:text-ink'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>

              {formData.messageBackbone === 'storybrand' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    ['character', 'Character'],
                    ['problem', 'Problem'],
                    ['guide', 'Guide'],
                    ['plan', 'Plan'],
                    ['cta', 'CTA'],
                    ['success', 'Success'],
                    ['failure', 'Failure'],
                  ].map(([key, label]) => (
                    <div key={key} className={key === 'failure' ? 'md:col-span-2' : ''}>
                      <label className="block text-body-xs text-ink-400 mb-1">{label}</label>
                      <input
                        value={formData.storybrand[key]}
                        onChange={(e) => setFormData(prev => ({ ...prev, storybrand: { ...prev.storybrand, [key]: e.target.value } }))}
                        className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                      />
                    </div>
                  ))}
                </div>
              )}

              {formData.messageBackbone === 'aida' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    ['attention', 'Attention'],
                    ['interest', 'Interest'],
                    ['desire', 'Desire'],
                    ['action', 'Action'],
                  ].map(([key, label]) => (
                    <div key={key}>
                      <label className="block text-body-xs text-ink-400 mb-1">{label}</label>
                      <input
                        value={formData.aida[key]}
                        onChange={(e) => setFormData(prev => ({ ...prev, aida: { ...prev.aida, [key]: e.target.value } }))}
                        className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                      />
                    </div>
                  ))}
                </div>
              )}

              {formData.messageBackbone === 'pas' && (
                <div className="space-y-3">
                  {[
                    ['problem', 'Problem'],
                    ['agitate', 'Agitate'],
                    ['solve', 'Solve'],
                  ].map(([key, label]) => (
                    <div key={key}>
                      <label className="block text-body-xs text-ink-400 mb-1">{label}</label>
                      <input
                        value={formData.pas[key]}
                        onChange={(e) => setFormData(prev => ({ ...prev, pas: { ...prev.pas, [key]: e.target.value } }))}
                        className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {wizardStep === 8 && (
            <div className="space-y-4">
              <div className="font-serif text-lg text-ink">Review</div>
              <div className="p-5 bg-card border border-border rounded-xl">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-serif text-xl text-ink">{formData.name || 'Campaign name'}</div>
                    <div className="text-body-sm text-ink-400 mt-1">{formData.objective || 'Objective line'}</div>
                  </div>
                  <span className="px-2 py-1 rounded text-body-xs bg-amber-50 text-amber-700">Draft</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-body-xs text-ink-400">
                  <div>
                    <div className="text-ink-400">Date range</div>
                    <div className="text-ink font-mono">{formData.startDate} → {formData.endDate}</div>
                  </div>
                  <div>
                    <div className="text-ink-400">Primary KPI</div>
                    <div className="text-ink font-mono">{formData.kpiBaseline} → {formData.kpiTarget} by {formData.kpiDeadline}</div>
                  </div>
                  <div>
                    <div className="text-ink-400">Cohort</div>
                    <div className="text-ink">{(cohorts || []).find(c => c.id === formData.primaryCohortId)?.name || '—'}</div>
                  </div>
                  <div>
                    <div className="text-ink-400">Channels</div>
                    <div className="text-ink">{formData.channels.length ? formData.channels.join(', ') : '—'}</div>
                  </div>
                </div>
                <div className="mt-4 text-body-xs text-ink-400">
                  Deliverables: {Object.entries(formData.deliverables || {}).filter(([, v]) => Number(v) > 0).map(([k, v]) => `${k}:${v}`).join(' · ') || '—'}
                </div>
              </div>

              {activationRequirements.length > 0 && (
                <div className="p-3 bg-paper border border-border rounded-xl text-body-xs text-ink-400">
                  <div className="text-body-sm text-ink mb-2">Activation gate</div>
                  {activationRequirements.map((r, idx) => (
                    <div key={`req_${idx}`}>- {r}</div>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => handleCreate(false)}
                  className="px-4 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
                >
                  Create Draft
                </button>
                <button
                  type="button"
                  onClick={() => handleCreate(true)}
                  disabled={!canActivate}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial disabled:opacity-50"
                >
                  Create & Activate
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </Modal>
  )
}

// Campaign Detail View
const CampaignDetail = ({ campaign }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    getMovesByCampaign,
    getMove,
    cohorts,
    moves: allMoves,
    updateCampaign,
    toggleTaskDone,
    getMoveDayNumber,
    getMoveTasksForDay,
    getCampaignHealth,
    getCampaignPhase,
    setPrimaryCampaignId,
    attachMoveToCampaign,
    getCampaignKpiRollup,
    applyCampaignKpiRollup,
  } = useRaptorflowStore()
  const moves = getMovesByCampaign(campaign.id)
  const campaignCohorts = cohorts.filter(c => campaign.cohorts?.includes(c.id))
  const [activeTab, setActiveTab] = useState('overview')

  const [attachMoveId, setAttachMoveId] = useState('')

  const [kpiEditorOpen, setKpiEditorOpen] = useState(false)
  const [kpiDraft, setKpiDraft] = useState(null)

  const [kpiCurrentEditOpen, setKpiCurrentEditOpen] = useState(false)
  const [kpiCurrentDraft, setKpiCurrentDraft] = useState(null)

  const [phaseEditorOpen, setPhaseEditorOpen] = useState(false)
  const [phaseDraft, setPhaseDraft] = useState(null)

  useEffect(() => {
    if (!kpiEditorOpen) setKpiDraft(null)
  }, [kpiEditorOpen])

  useEffect(() => {
    if (!kpiCurrentEditOpen) setKpiCurrentDraft(null)
  }, [kpiCurrentEditOpen])

  useEffect(() => {
    if (!phaseEditorOpen) setPhaseDraft(null)
  }, [phaseEditorOpen])

  const campaignTodayTasks = moves.flatMap(m => {
    const day = getMoveDayNumber?.(m.id) || 1
    const tasks = getMoveTasksForDay?.(m.id, day) || []
    return tasks
      .filter(t => t.status !== 'done')
      .map(t => ({
        id: t.id,
        text: t.text,
        moveId: m.id,
        moveName: m.name,
        day,
      }))
  })

  const campaignOpenTasks = moves.flatMap(m => {
    const tasks = Array.isArray(m.tasks) ? m.tasks : []
    return tasks
      .filter(t => t.status !== 'done')
      .map(t => ({
        id: t.id,
        text: t.text,
        moveId: m.id,
        moveName: m.name,
        day: t.day || 1,
      }))
  })

  const standaloneMoves = Array.isArray(allMoves)
    ? allMoves.filter(m => !m.campaignId)
    : []

  const health = getCampaignHealth?.(campaign.id)
  const phase = health?.phase || getCampaignPhase?.(campaign.id) || 'Awareness'

  const rollup = getCampaignKpiRollup?.(campaign.id)

  const tabs = ['overview', 'timeline', 'moves', 'schedule', 'performance', 'postmortem']
  const tabId = (key) => `campaign_tab_${key}`
  const panelId = (key) => `campaign_panel_${key}`

  const handleTabKeyDown = (e, current) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return
    e.preventDefault()
    const idx = tabs.indexOf(current)
    if (idx === -1) return
    const nextIdx = e.key === 'ArrowLeft'
      ? (idx - 1 + tabs.length) % tabs.length
      : e.key === 'ArrowRight'
        ? (idx + 1) % tabs.length
        : e.key === 'Home'
          ? 0
          : tabs.length - 1
    setActiveTab(tabs[nextIdx])
    requestAnimationFrame(() => {
      const el = document.getElementById(tabId(tabs[nextIdx]))
      el?.focus?.()
    })
  }

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const tab = params.get('tab')
    if (!tab) return
    if (['overview', 'timeline', 'moves', 'schedule', 'performance', 'postmortem'].includes(tab)) {
      setActiveTab(tab)
    }
  }, [location.search])

  const activationBlockers = (() => {
    const blockers = []
    const primary = campaign?.kpis?.primary
    const baselineOk = Number.isFinite(Number(primary?.baseline))
    const targetOk = Number(primary?.target || 0) > 0
    const nameOk = Boolean((primary?.name || '').toString().trim())

    if (!nameOk || !baselineOk || !targetOk) {
      blockers.push('KPI contract incomplete (primary KPI name + baseline + target).')
    }

    const readyMove = moves.some(m => {
      const tasks = Array.isArray(m?.checklistItems) ? m.checklistItems : []
      const metric = (m?.tracking?.metric || m?.metric || '').toString().trim()
      const hasTasks = tasks.length > 0
      const hasMetric = Boolean(metric)
      const hasChannel = Boolean(m?.channel)
      const hasCta = Boolean((m?.cta || '').toString().trim())
      return hasTasks && hasMetric && hasChannel && hasCta
    })
    if (!readyMove) blockers.push('No ready Move yet (needs tasks + measurement + channel + CTA).')
    return blockers
  })()

  const handleActivate = () => {
    if (activationBlockers.length) return
    updateCampaign(campaign.id, { status: 'active' })
  }

  const handleMovePhase = (fromIndex, toIndex) => {
    const phases = campaign?.blueprint?.phases || []
    if (!Array.isArray(phases) || phases.length < 2) return
    if (fromIndex < 0 || fromIndex >= phases.length) return
    if (toIndex < 0 || toIndex >= phases.length) return
    if (fromIndex === toIndex) return

    const next = [...phases]
    const [moved] = next.splice(fromIndex, 1)
    next.splice(toIndex, 0, moved)

    updateCampaign(campaign.id, {
      blueprint: {
        ...(campaign.blueprint || {}),
        phases: next,
      }
    })
  }

  const openPhaseEditor = () => {
    const phases = Array.isArray(campaign?.blueprint?.phases) ? campaign.blueprint.phases : []
    setPhaseDraft(phases.map(p => ({
      ...p,
      phase: p?.phase || 'Awareness',
      phaseObjective: p?.phaseObjective || '',
      messageFocus: p?.messageFocus || '',
      targetCohorts: Array.isArray(p?.targetCohorts) ? p.targetCohorts : [],
      channelMix: Array.isArray(p?.channelMix) ? p.channelMix : [],
    })))
    setPhaseEditorOpen(true)
  }

  const savePhases = () => {
    if (!Array.isArray(phaseDraft)) return
    updateCampaign(campaign.id, {
      blueprint: {
        ...(campaign.blueprint || {}),
        phases: phaseDraft,
      }
    })
    setPhaseEditorOpen(false)
  }

  const getTreeSnapshot = () => {
    const tree = campaign?.blueprint?.kpiTree || {}
    const primary = tree?.primary || { name: '', baseline: 0, target: 0, current: 0 }
    const stages = tree?.stages || {}
    return {
      primary,
      stages: {
        reach: stages?.reach || { name: 'Reach', baseline: 0, target: 0, current: 0 },
        click: stages?.click || { name: 'Clicks', baseline: 0, target: 0, current: 0 },
        convert: stages?.convert || { name: 'Conversions', baseline: 0, target: 0, current: 0 },
      },
      leadingIndicators: Array.isArray(tree?.leadingIndicators) ? tree.leadingIndicators : [],
      healthRules: Array.isArray(tree?.healthRules) ? tree.healthRules : [],
    }
  }

  const openKpiEditor = () => {
    const snap = getTreeSnapshot()
    setKpiDraft({
      primary: { ...snap.primary },
      stages: {
        reach: { ...snap.stages.reach },
        click: { ...snap.stages.click },
        convert: { ...snap.stages.convert },
      },
      leadingIndicators: snap.leadingIndicators.map(i => ({
        id: i?.id || makeLocalId(),
        name: i?.name || '',
        target: Number.isFinite(Number(i?.target)) ? Number(i.target) : 0,
      })),
      healthRules: snap.healthRules.map(r => ({
        id: r?.id || makeLocalId(),
        metric: r?.metric || 'primary',
        operator: r?.operator || '>=',
        threshold: Number.isFinite(Number(r?.threshold)) ? Number(r.threshold) : 0,
        severity: r?.severity || 'warn',
      })),
    })
    setKpiEditorOpen(true)
  }

  const saveKpiTree = () => {
    if (!kpiDraft) return

    const nextTree = {
      ...(campaign?.blueprint?.kpiTree || {}),
      primary: {
        ...(campaign?.blueprint?.kpiTree?.primary || {}),
        ...kpiDraft.primary,
        target: Number.isFinite(Number(kpiDraft.primary?.target)) ? Number(kpiDraft.primary.target) : 0,
      },
      stages: {
        ...(campaign?.blueprint?.kpiTree?.stages || {}),
        reach: {
          ...(campaign?.blueprint?.kpiTree?.stages?.reach || {}),
          ...kpiDraft.stages.reach,
          target: Number.isFinite(Number(kpiDraft.stages?.reach?.target)) ? Number(kpiDraft.stages.reach.target) : 0,
        },
        click: {
          ...(campaign?.blueprint?.kpiTree?.stages?.click || {}),
          ...kpiDraft.stages.click,
          target: Number.isFinite(Number(kpiDraft.stages?.click?.target)) ? Number(kpiDraft.stages.click.target) : 0,
        },
        convert: {
          ...(campaign?.blueprint?.kpiTree?.stages?.convert || {}),
          ...kpiDraft.stages.convert,
          target: Number.isFinite(Number(kpiDraft.stages?.convert?.target)) ? Number(kpiDraft.stages.convert.target) : 0,
        },
      },
      leadingIndicators: (kpiDraft.leadingIndicators || []).map(i => ({
        id: i?.id || makeLocalId(),
        name: i?.name || '',
        target: Number.isFinite(Number(i?.target)) ? Number(i.target) : 0,
      })),
      healthRules: (kpiDraft.healthRules || []).map(r => ({
        id: r?.id || makeLocalId(),
        metric: r?.metric || 'primary',
        operator: r?.operator || '>=',
        threshold: Number.isFinite(Number(r?.threshold)) ? Number(r.threshold) : 0,
        severity: r?.severity || 'warn',
      })),
    }

    const nextBlueprint = {
      ...(campaign?.blueprint || {}),
      objective: {
        ...(campaign?.blueprint?.objective || {}),
        primaryKpi: nextTree.primary,
      },
      kpiTree: nextTree,
    }

    const nextKpis = {
      ...(campaign?.kpis || {}),
      primary: {
        ...(campaign?.kpis?.primary || {}),
        name: nextTree.primary?.name || campaign?.kpis?.primary?.name || '',
        target: Number.isFinite(Number(nextTree.primary?.target)) ? Number(nextTree.primary.target) : 0,
      },
      reach: {
        ...(campaign?.kpis?.reach || {}),
        name: nextTree.stages?.reach?.name || campaign?.kpis?.reach?.name || 'Reach',
        target: Number.isFinite(Number(nextTree.stages?.reach?.target)) ? Number(nextTree.stages.reach.target) : 0,
      },
      click: {
        ...(campaign?.kpis?.click || {}),
        name: nextTree.stages?.click?.name || campaign?.kpis?.click?.name || 'Clicks',
        target: Number.isFinite(Number(nextTree.stages?.click?.target)) ? Number(nextTree.stages.click.target) : 0,
      },
      convert: {
        ...(campaign?.kpis?.convert || {}),
        name: nextTree.stages?.convert?.name || campaign?.kpis?.convert?.name || 'Conversions',
        target: Number.isFinite(Number(nextTree.stages?.convert?.target)) ? Number(nextTree.stages.convert.target) : 0,
      },
    }

    updateCampaign(campaign.id, {
      blueprint: nextBlueprint,
      kpis: nextKpis,
    })

    setKpiEditorOpen(false)
  }

  const getTimelineWeeks = () => {
    const weeks = campaign?.timeline?.weeks
    if (!Array.isArray(weeks)) return []
    return [...weeks].sort((a, b) => (a?.week || 0) - (b?.week || 0))
  }

  const getPhaseOptions = () => {
    const phases = campaign?.blueprint?.phases
    if (Array.isArray(phases) && phases.length) return phases.map(p => p.phase).filter(Boolean)
    return ['Awareness', 'Engagement', 'Conversion', 'Retention']
  }

  const setTimelineWeeks = (weeks) => {
    const normalized = (Array.isArray(weeks) ? weeks : [])
      .map(w => ({
        week: Number(w?.week || 0),
        phase: w?.phase || 'Awareness',
        moveIds: Array.isArray(w?.moveIds)
          ? w.moveIds
          : Array.isArray(w?.moves)
            ? w.moves
            : [],
      }))
      .filter(w => Number.isFinite(w.week) && w.week > 0)
      .sort((a, b) => a.week - b.week)

    updateCampaign(campaign.id, {
      timeline: {
        ...(campaign.timeline || {}),
        weeks: normalized,
      }
    })
  }

  const handleAddWeek = () => {
    const weeks = getTimelineWeeks()
    const nextWeekNumber = weeks.length ? Math.max(...weeks.map(w => Number(w.week || 0))) + 1 : 1
    const phaseOptions = getPhaseOptions()
    const defaultPhase = phaseOptions[0] || 'Awareness'
    setTimelineWeeks([
      ...weeks,
      { week: nextWeekNumber, phase: defaultPhase, moveIds: [] },
    ])
  }

  const handleRemoveWeek = (weekNumber) => {
    const weeks = getTimelineWeeks().filter(w => w.week !== weekNumber)
    setTimelineWeeks(weeks)
  }

  const handleSetWeekPhase = (weekNumber, nextPhase) => {
    const weeks = getTimelineWeeks().map(w =>
      w.week === weekNumber ? { ...w, phase: nextPhase } : w
    )
    setTimelineWeeks(weeks)
  }

  const handleAssignMoveToWeek = (weekNumber, moveId) => {
    if (!moveId) return
    const weeks = getTimelineWeeks().map(w => {
      if (w.week !== weekNumber) return w
      const ids = Array.isArray(w.moveIds) ? w.moveIds : []
      if (ids.includes(moveId)) return w
      return { ...w, moveIds: [...ids, moveId] }
    })
    setTimelineWeeks(weeks)
  }

  const handleUnassignMoveFromWeek = (weekNumber, moveId) => {
    const weeks = getTimelineWeeks().map(w => {
      if (w.week !== weekNumber) return w
      const ids = Array.isArray(w.moveIds) ? w.moveIds : []
      return { ...w, moveIds: ids.filter(id => id !== moveId) }
    })
    setTimelineWeeks(weeks)
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <button
            type="button"
            onClick={() => {
              if (window.history.length > 1) {
                navigate(-1)
              } else {
                navigate('/app/campaigns')
              }
            }}
            className="text-body-xs text-ink-400 hover:text-ink mb-2 flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper rounded"
          >
            ← Back to campaigns
          </button>
          <h1 className="font-serif text-headline-md text-ink">{campaign.name}</h1>
          <p className="text-body-sm text-ink-400 mt-1">{campaign.objective}</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setPrimaryCampaignId?.(campaign.id)}
            className="px-3 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
          >
            Set as primary
          </button>
          {campaign.status === 'draft' && (
            <button
              onClick={handleActivate}
              disabled={activationBlockers.length > 0}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
            >
              Activate Campaign
            </button>
          )}
          <span className={`px-3 py-1.5 rounded-lg text-body-sm capitalize ${campaign.status === 'active' ? 'bg-emerald-50 text-emerald-600' :
              campaign.status === 'draft' ? 'bg-amber-50 text-amber-600' :
                'bg-muted text-ink-400'
            }`}>
            {campaign.status}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 bg-paper-200 rounded text-body-xs text-ink-400">Phase: {phase}</span>
          {typeof health?.execution === 'number' && typeof health?.performance === 'number' && (
            <span className="text-body-xs text-ink-400 font-mono">
              Exec {health.execution}% · Perf {health.performance}%
            </span>
          )}
          {health?.rag && (
            <span className={`px-2 py-1 rounded text-body-xs capitalize border ${health.rag === 'green'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : health.rag === 'red'
                  ? 'bg-red-50 text-red-700 border-red-200'
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}>
              {health.rag}{Array.isArray(health.issues) && health.issues.length ? ` · ${health.issues.length}` : ''}
            </span>
          )}
        </div>
        <div className="inline-flex items-center gap-1 p-1 bg-paper-200 rounded-xl" role="tablist" aria-label="Campaign sections">
          <button
            id={tabId('overview')}
            role="tab"
            type="button"
            aria-selected={activeTab === 'overview'}
            aria-controls={panelId('overview')}
            tabIndex={activeTab === 'overview' ? 0 : -1}
            onKeyDown={(e) => handleTabKeyDown(e, 'overview')}
            onClick={() => setActiveTab('overview')}
            className={`px-3 py-1.5 rounded-lg text-body-xs transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper ${activeTab === 'overview' ? 'bg-card text-ink border border-border' : 'text-ink-400 hover:text-ink'
              }`}
          >
            Overview
          </button>
          <button
            id={tabId('timeline')}
            role="tab"
            type="button"
            aria-selected={activeTab === 'timeline'}
            aria-controls={panelId('timeline')}
            tabIndex={activeTab === 'timeline' ? 0 : -1}
            onKeyDown={(e) => handleTabKeyDown(e, 'timeline')}
            onClick={() => setActiveTab('timeline')}
            className={`px-3 py-1.5 rounded-lg text-body-xs transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper ${activeTab === 'timeline' ? 'bg-card text-ink border border-border' : 'text-ink-400 hover:text-ink'
              }`}
          >
            Timeline
          </button>
          <button
            id={tabId('moves')}
            role="tab"
            type="button"
            aria-selected={activeTab === 'moves'}
            aria-controls={panelId('moves')}
            tabIndex={activeTab === 'moves' ? 0 : -1}
            onKeyDown={(e) => handleTabKeyDown(e, 'moves')}
            onClick={() => setActiveTab('moves')}
            className={`px-3 py-1.5 rounded-lg text-body-xs transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper ${activeTab === 'moves' ? 'bg-card text-ink border border-border' : 'text-ink-400 hover:text-ink'
              }`}
          >
            Moves
          </button>
          <button
            id={tabId('schedule')}
            role="tab"
            type="button"
            aria-selected={activeTab === 'schedule'}
            aria-controls={panelId('schedule')}
            tabIndex={activeTab === 'schedule' ? 0 : -1}
            onKeyDown={(e) => handleTabKeyDown(e, 'schedule')}
            onClick={() => setActiveTab('schedule')}
            className={`px-3 py-1.5 rounded-lg text-body-xs transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper ${activeTab === 'schedule' ? 'bg-card text-ink border border-border' : 'text-ink-400 hover:text-ink'
              }`}
          >
            Schedule
          </button>
          <button
            id={tabId('performance')}
            role="tab"
            type="button"
            aria-selected={activeTab === 'performance'}
            aria-controls={panelId('performance')}
            tabIndex={activeTab === 'performance' ? 0 : -1}
            onKeyDown={(e) => handleTabKeyDown(e, 'performance')}
            onClick={() => setActiveTab('performance')}
            className={`px-3 py-1.5 rounded-lg text-body-xs transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper ${activeTab === 'performance' ? 'bg-card text-ink border border-border' : 'text-ink-400 hover:text-ink'
              }`}
          >
            Performance
          </button>
          <button
            id={tabId('postmortem')}
            role="tab"
            type="button"
            aria-selected={activeTab === 'postmortem'}
            aria-controls={panelId('postmortem')}
            tabIndex={activeTab === 'postmortem' ? 0 : -1}
            onKeyDown={(e) => handleTabKeyDown(e, 'postmortem')}
            onClick={() => setActiveTab('postmortem')}
            className={`px-3 py-1.5 rounded-lg text-body-xs transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper ${activeTab === 'postmortem' ? 'bg-card text-ink border border-border' : 'text-ink-400 hover:text-ink'
              }`}
          >
            Post-mortem
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'overview' && (
            <div role="tabpanel" id={panelId('overview')} aria-labelledby={tabId('overview')} tabIndex={0}>
              {campaign.status === 'draft' && activationBlockers.length > 0 && (
                <div className="bg-card border border-border rounded-xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h2 className="font-serif text-lg text-ink">Activation blockers</h2>
                      <div className="text-body-xs text-ink-400">Fix these before you go Active.</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openKpiEditor()}
                        className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
                      >
                        Fix KPIs
                      </button>
                      <button
                        onClick={() => setActiveTab('moves')}
                        className="px-3 py-2 text-body-xs bg-primary text-primary-foreground rounded-lg hover:opacity-95 transition-editorial"
                      >
                        Add / Ready a move
                      </button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {activationBlockers.map((b, idx) => (
                      <div key={`activation_blocker_${idx}`} className="text-body-sm text-ink-400">- {b}</div>
                    ))}
                  </div>
                </div>
              )}

              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="font-serif text-lg text-ink">Today</h2>
                    <div className="text-body-xs text-ink-400">Campaign to-dos across moves</div>
                  </div>
                  <div className="text-body-xs text-ink-400 font-mono">{campaignTodayTasks.length} today · {campaignOpenTasks.length} open</div>
                </div>

                {campaignTodayTasks.length > 0 ? (
                  <div className="space-y-2">
                    {campaignTodayTasks.slice(0, 10).map(task => (
                      <div
                        key={`${task.moveId}_${task.id}`}
                        className="flex items-start justify-between gap-3 p-3 bg-paper rounded-xl border border-border-light"
                      >
                        <div className="flex items-start gap-3">
                          <button
                            type="button"
                            onClick={() => toggleTaskDone?.(task.moveId, task.id)}
                            className="mt-0.5 flex-shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper rounded"
                            aria-label="Mark task done"
                          >
                            <Circle className="w-5 h-5 text-ink-300" strokeWidth={1.5} />
                          </button>
                          <div className="min-w-0">
                            <div className="text-body-sm text-ink">{task.text}</div>
                            <button
                              onClick={() => navigate(`/app/moves/${task.moveId}`)}
                              className="text-body-xs text-ink-400 hover:text-primary transition-editorial"
                            >
                              {task.moveName} · Day {task.day}
                            </button>
                          </div>
                        </div>

                        <button
                          onClick={() => navigate(`/app/moves/${task.moveId}`)}
                          className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
                        >
                          Open
                        </button>
                      </div>
                    ))}

                    {campaignTodayTasks.length > 10 && (
                      <div className="text-body-xs text-ink-400">Showing 10 of {campaignTodayTasks.length}. Use Matrix for the full list.</div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-10">
                    <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" strokeWidth={1.5} />
                    <div className="font-serif text-lg text-ink mb-1">No tasks due today</div>
                    <div className="text-body-sm text-ink-400">Here are open tasks across this campaign:</div>
                    <div className="mt-4 max-w-xl mx-auto text-left space-y-2">
                      {(campaignOpenTasks.slice(0, 6) || []).map(t => (
                        <div key={`${t.moveId}_${t.id}`} className="flex items-start justify-between gap-3 p-3 bg-paper rounded-xl border border-border-light">
                          <div className="min-w-0">
                            <div className="text-body-sm text-ink">{t.text}</div>
                            <button
                              onClick={() => navigate(`/app/moves/${t.moveId}`)}
                              className="text-body-xs text-ink-400 hover:text-primary transition-editorial"
                            >
                              {t.moveName} · Day {t.day}
                            </button>
                          </div>
                          <button
                            onClick={() => navigate(`/app/moves/${t.moveId}`)}
                            className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
                          >
                            Open
                          </button>
                        </div>
                      ))}
                      {campaignOpenTasks.length === 0 && (
                        <div className="text-body-sm text-ink-400">No open tasks yet. Add a move to generate tasks.</div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="font-serif text-lg text-ink">Moves</h2>
                    <div className="text-body-xs text-ink-400">What’s inside this campaign</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {standaloneMoves.length > 0 && (
                      <div className="flex items-center gap-2">
                        <select
                          value={attachMoveId}
                          onChange={(e) => setAttachMoveId(e.target.value)}
                          className="px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink"
                        >
                          <option value="">Attach existing move…</option>
                          {standaloneMoves.map(m => (
                            <option key={`standalone_${m.id}`} value={m.id}>{m.name}</option>
                          ))}
                        </select>
                        <button
                          onClick={() => {
                            if (!attachMoveId) return
                            attachMoveToCampaign?.(attachMoveId, campaign.id)
                            setAttachMoveId('')
                          }}
                          disabled={!attachMoveId}
                          className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-300 transition-editorial disabled:opacity-50"
                        >
                          Attach
                        </button>
                      </div>
                    )}
                    <button
                      onClick={() => setActiveTab('moves')}
                      className="px-3 py-2 text-body-xs bg-primary text-primary-foreground rounded-lg hover:opacity-95 transition-editorial"
                    >
                      Add / Manage
                    </button>
                  </div>
                </div>

                {moves.length ? (
                  <div className="space-y-2">
                    {moves.slice(0, 5).map(m => {
                      const openCount = (m.tasks || []).filter(t => t.status !== 'done').length
                      return (
                        <div key={m.id} className="flex items-start justify-between gap-3 p-3 bg-paper rounded-xl border border-border-light">
                          <div className="min-w-0">
                            <div className="text-body-sm text-ink font-medium">{m.name}</div>
                            <div className="text-body-xs text-ink-400">{openCount} open tasks · {m.status}</div>
                          </div>
                          <button
                            onClick={() => navigate(`/app/moves/${m.id}`)}
                            className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
                          >
                            Open
                          </button>
                        </div>
                      )
                    })}
                    {moves.length > 5 && (
                      <div className="text-body-xs text-ink-400">Showing 5 of {moves.length}. See the Moves tab for the full list.</div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Target className="w-12 h-12 text-ink-300 mx-auto mb-3" strokeWidth={1.5} />
                    <div className="font-serif text-lg text-ink mb-1">No moves yet</div>
                    <div className="text-body-sm text-ink-400">A campaign is a war plan. Moves are the execution units.</div>
                    <div className="mt-4 flex items-center justify-center gap-2">
                      <button
                        onClick={() => setActiveTab('moves')}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
                      >
                        Create your first move
                      </button>
                      {standaloneMoves.length > 0 && (
                        <button
                          onClick={() => setActiveTab('moves')}
                          className="px-4 py-2 border border-border rounded-lg text-body-sm text-ink hover:bg-paper-200 transition-editorial"
                        >
                          Attach an existing move
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {health?.rag && Array.isArray(health.issues) && (
                <div className="bg-card border border-border rounded-xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h2 className="font-serif text-lg text-ink">Health</h2>
                      <div className="text-body-xs text-ink-400">Green = rules OK · Amber = warnings · Red = failures</div>
                    </div>
                    <div className="text-body-xs text-ink-400 font-mono">{health.rag}</div>
                  </div>

                  {health.issues.length ? (
                    <div className="space-y-2">
                      {health.issues.map(i => (
                        <div key={i.id} className="p-3 bg-paper rounded-xl border border-border-light">
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                              <div className="text-body-sm text-ink font-medium">
                                {i.metric} {i.operator} {i.threshold}%
                              </div>
                              <div className="text-body-xs text-ink-400 font-mono">Current: {i.value}%</div>
                            </div>
                            <span className={`px-2 py-1 rounded text-body-xs capitalize border ${i.severity === 'fail'
                                ? 'bg-red-50 text-red-700 border-red-200'
                                : 'bg-amber-50 text-amber-700 border-amber-200'
                              }`}>
                              {i.severity}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-body-sm text-ink-400">All health rules are currently passing.</div>
                  )}
                </div>
              )}

              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="font-serif text-lg text-ink">Campaign KPIs</h2>
                    <div className="text-body-xs text-ink-400">Progress + rollup from move tracking</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => applyCampaignKpiRollup?.(campaign.id)}
                      className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
                    >
                      Apply rollup
                    </button>
                    {!kpiCurrentEditOpen ? (
                      <button
                        onClick={() => {
                          const base = campaign.kpis || {}
                          setKpiCurrentDraft({
                            primary: Number(base?.primary?.current || 0),
                            reach: Number(base?.reach?.current || 0),
                            click: Number(base?.click?.current || 0),
                            convert: Number(base?.convert?.current || 0),
                          })
                          setKpiCurrentEditOpen(true)
                        }}
                        className="inline-flex items-center gap-1 px-3 py-2 text-body-xs text-primary hover:bg-signal-muted rounded-lg transition-editorial"
                      >
                        <PenLine className="w-3.5 h-3.5" strokeWidth={1.5} />
                        Edit current
                      </button>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setKpiCurrentEditOpen(false)}
                          className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => {
                            if (!kpiCurrentDraft) return
                            const nextKpis = {
                              ...(campaign.kpis || {}),
                              primary: { ...(campaign.kpis?.primary || {}), current: Number(kpiCurrentDraft.primary || 0) },
                              reach: { ...(campaign.kpis?.reach || {}), current: Number(kpiCurrentDraft.reach || 0) },
                              click: { ...(campaign.kpis?.click || {}), current: Number(kpiCurrentDraft.click || 0) },
                              convert: { ...(campaign.kpis?.convert || {}), current: Number(kpiCurrentDraft.convert || 0) },
                            }

                            const tree = campaign?.blueprint?.kpiTree || {}
                            const nextTree = {
                              ...tree,
                              primary: { ...(tree.primary || {}), current: Number(kpiCurrentDraft.primary || 0) },
                              stages: {
                                ...(tree.stages || {}),
                                reach: { ...(tree.stages?.reach || {}), current: Number(kpiCurrentDraft.reach || 0) },
                                click: { ...(tree.stages?.click || {}), current: Number(kpiCurrentDraft.click || 0) },
                                convert: { ...(tree.stages?.convert || {}), current: Number(kpiCurrentDraft.convert || 0) },
                              }
                            }

                            updateCampaign(campaign.id, {
                              kpis: nextKpis,
                              blueprint: {
                                ...(campaign.blueprint || {}),
                                kpiTree: nextTree,
                                objective: {
                                  ...(campaign.blueprint?.objective || {}),
                                  primaryKpi: nextTree.primary,
                                }
                              }
                            })
                            setKpiCurrentEditOpen(false)
                          }}
                          className="px-3 py-2 text-body-xs bg-primary text-primary-foreground rounded-lg hover:opacity-95 transition-editorial"
                        >
                          Save
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {rollup && (
                  <div className="mb-4 p-3 bg-paper-200 rounded-xl border border-border-light">
                    <div className="text-body-xs text-ink-400 mb-2">Rollup preview (sum of tracking updates)</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {(['primary', 'reach', 'click', 'convert']).map(key => (
                        <div key={`rollup_${key}`} className="px-3 py-2 bg-card border border-border rounded-lg">
                          <div className="text-body-xs text-ink-400 capitalize">{key}</div>
                          <div className="text-body-sm text-ink font-mono">{Number(rollup?.totals?.[key] || 0).toLocaleString()}</div>
                          {(rollup?.sources?.[key] || []).slice(0, 2).map(s => (
                            <div key={`${key}_${s.moveId}`} className="text-body-xs text-ink-400 truncate">{s.name}: +{Number(s.sum || 0).toLocaleString()}</div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(campaign.kpis || {}).map(([key, kpi]) => {
                    const progress = kpi.target > 0 ? Math.round((kpi.current / kpi.target) * 100) : 0
                    const isCore = ['primary', 'reach', 'click', 'convert'].includes(key)
                    return (
                      <div key={key} className="p-4 bg-paper-200 rounded-xl">
                        <div className="text-body-xs text-ink-400 mb-1">{kpi.name || key}</div>
                        <div className="text-xl font-mono text-ink mb-2">
                          {kpiCurrentEditOpen && isCore && kpiCurrentDraft ? (
                            <input
                              type="number"
                              value={Number(kpiCurrentDraft[key] || 0)}
                              onChange={(e) => setKpiCurrentDraft(prev => ({ ...(prev || {}), [key]: Number(e.target.value || 0) }))}
                              className="w-full px-2 py-1 bg-card border border-border rounded-lg text-body-sm text-ink font-mono"
                            />
                          ) : (
                            kpi.current?.toLocaleString()
                          )}
                        </div>
                        <div className="h-1 bg-paper-300 rounded-full overflow-hidden mb-1">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: `${Math.min(progress, 100)}%` }}
                          />
                        </div>
                        <div className="text-body-xs text-ink-400">
                          Target: {kpi.target?.toLocaleString()}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              <div className="bg-card border border-border rounded-xl p-5">
                <h2 className="font-serif text-lg text-ink mb-2">War plan</h2>
                <div className="text-body-sm text-ink-400">
                  {campaign.blueprint?.objective?.text || campaign.objective}
                </div>
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-paper-200 rounded-xl">
                    <div className="text-body-xs text-ink-400 mb-1">Pinned Strategy</div>
                    <div className="text-body-sm text-ink font-mono">v{campaign.strategyVersionId}</div>
                  </div>
                  <div className="p-4 bg-paper-200 rounded-xl">
                    <div className="text-body-xs text-ink-400 mb-1">Phases</div>
                    <div className="text-body-sm text-ink">{(campaign.blueprint?.phases || []).length || 4}</div>
                  </div>
                </div>

                <div className="mt-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-serif text-ink">Phase sequence</div>
                    <div className="flex items-center gap-2">
                      <div className="text-body-xs text-ink-400">Reorder to match your plan</div>
                      {!phaseEditorOpen ? (
                        <button
                          onClick={openPhaseEditor}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs text-primary hover:bg-signal-muted rounded-lg transition-editorial"
                        >
                          <PenLine className="w-3.5 h-3.5" strokeWidth={1.5} />
                          Edit
                        </button>
                      ) : (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setPhaseEditorOpen(false)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-300 transition-editorial"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={savePhases}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs bg-primary text-primary-foreground rounded-lg hover:opacity-95 transition-editorial"
                          >
                            Save
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    {(() => {
                      const phases = phaseEditorOpen && Array.isArray(phaseDraft)
                        ? phaseDraft
                        : (campaign.blueprint?.phases || [])

                      const patchPhase = (idx, patch) => {
                        setPhaseDraft(prev => {
                          if (!Array.isArray(prev)) return prev
                          const next = [...prev]
                          next[idx] = { ...(next[idx] || {}), ...patch }
                          return next
                        })
                      }

                      const toggleCohort = (idx, cohortId) => {
                        patchPhase(idx, {
                          targetCohorts: (phases[idx]?.targetCohorts || []).includes(cohortId)
                            ? (phases[idx]?.targetCohorts || []).filter(id => id !== cohortId)
                            : [...(phases[idx]?.targetCohorts || []), cohortId]
                        })
                      }

                      const toggleChannel = (idx, channelId) => {
                        patchPhase(idx, {
                          channelMix: (phases[idx]?.channelMix || []).includes(channelId)
                            ? (phases[idx]?.channelMix || []).filter(id => id !== channelId)
                            : [...(phases[idx]?.channelMix || []), channelId]
                        })
                      }

                      return phases.map((p, idx) => (
                        <div key={`${p.phase}_${idx}`} className="p-3 bg-paper-200 rounded-xl border border-border-light">
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0 flex-1">
                              <div className="text-body-sm text-ink font-medium">{idx + 1}. {p.phase}</div>

                              {phaseEditorOpen ? (
                                <div className="mt-2 space-y-2">
                                  <input
                                    value={p.phaseObjective || ''}
                                    onChange={(e) => patchPhase(idx, { phaseObjective: e.target.value })}
                                    placeholder="Phase objective"
                                    className="w-full px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink"
                                  />
                                  <input
                                    value={p.messageFocus || ''}
                                    onChange={(e) => patchPhase(idx, { messageFocus: e.target.value })}
                                    placeholder="Message focus (one line)"
                                    className="w-full px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink"
                                  />

                                  <div className="pt-1">
                                    <div className="text-body-xs text-ink-400 mb-1">Target cohorts</div>
                                    <div className="flex flex-wrap gap-2">
                                      {(cohorts || []).map(c => {
                                        const on = (p.targetCohorts || []).includes(c.id)
                                        return (
                                          <button
                                            key={`${p.phase}_${c.id}`}
                                            onClick={() => toggleCohort(idx, c.id)}
                                            className={`px-2.5 py-1 rounded-lg text-body-xs border transition-editorial ${on ? 'bg-primary/10 text-primary border-primary/20' : 'bg-card text-ink-400 border-border'
                                              }`}
                                            type="button"
                                          >
                                            {c.name}
                                          </button>
                                        )
                                      })}
                                    </div>
                                  </div>

                                  <div className="pt-1">
                                    <div className="text-body-xs text-ink-400 mb-1">Channel mix</div>
                                    <div className="flex flex-wrap gap-2">
                                      {CHANNELS.map(ch => {
                                        const on = (p.channelMix || []).includes(ch.id)
                                        return (
                                          <button
                                            key={`${p.phase}_${ch.id}`}
                                            onClick={() => toggleChannel(idx, ch.id)}
                                            className={`px-2.5 py-1 rounded-lg text-body-xs border transition-editorial ${on ? 'bg-primary/10 text-primary border-primary/20' : 'bg-card text-ink-400 border-border'
                                              }`}
                                            type="button"
                                          >
                                            {ch.name}
                                          </button>
                                        )
                                      })}
                                    </div>
                                  </div>
                                </div>
                              ) : (
                                <>
                                  <div className="text-body-xs text-ink-400">{p.phaseObjective || ''}</div>
                                  <div className="mt-2 text-body-xs text-ink-400">
                                    Cohorts: {(p.targetCohorts || []).length} · Channels: {(p.channelMix || []).length}
                                  </div>
                                </>
                              )}
                            </div>

                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleMovePhase(idx, idx - 1)}
                                disabled={idx === 0}
                                className="p-2 rounded-lg border border-border text-ink-400 hover:text-ink hover:bg-paper-300 transition-editorial disabled:opacity-40 disabled:hover:bg-transparent"
                                aria-label="Move phase up"
                                type="button"
                              >
                                <ChevronUp className="w-4 h-4" strokeWidth={1.5} />
                              </button>
                              <button
                                onClick={() => handleMovePhase(idx, idx + 1)}
                                disabled={idx === (campaign.blueprint?.phases || []).length - 1}
                                className="p-2 rounded-lg border border-border text-ink-400 hover:text-ink hover:bg-paper-300 transition-editorial disabled:opacity-40 disabled:hover:bg-transparent"
                                aria-label="Move phase down"
                                type="button"
                              >
                                <ChevronDown className="w-4 h-4" strokeWidth={1.5} />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))
                    })()}
                  </div>
                </div>

                <div className="mt-6">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-serif text-ink">KPI tree</div>
                    <div className="flex items-center gap-2">
                      <div className="text-body-xs text-ink-400">Primary + funnel stages</div>
                      {!kpiEditorOpen ? (
                        <button
                          onClick={openKpiEditor}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs text-primary hover:bg-signal-muted rounded-lg transition-editorial"
                        >
                          <PenLine className="w-3.5 h-3.5" strokeWidth={1.5} />
                          Edit
                        </button>
                      ) : (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setKpiEditorOpen(false)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-300 transition-editorial"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={saveKpiTree}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs bg-primary text-primary-foreground rounded-lg hover:opacity-95 transition-editorial"
                          >
                            Save
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {(() => {
                      const tree = campaign?.blueprint?.kpiTree
                      const primary = tree?.primary
                      const stages = tree?.stages || {}
                      const draft = kpiDraft
                      const cards = [
                        { key: 'primary', label: 'Primary', kpi: primary, draftKey: 'primary' },
                        { key: 'reach', label: 'Reach', kpi: stages.reach, draftKey: 'reach' },
                        { key: 'click', label: 'Clicks', kpi: stages.click, draftKey: 'click' },
                        { key: 'convert', label: 'Conversions', kpi: stages.convert, draftKey: 'convert' },
                      ]

                      const getDraftKpi = (key) => {
                        if (!draft) return null
                        if (key === 'primary') return draft.primary
                        return draft.stages?.[key]
                      }

                      const setDraftKpi = (key, patch) => {
                        setKpiDraft(prev => {
                          if (!prev) return prev
                          if (key === 'primary') return { ...prev, primary: { ...prev.primary, ...patch } }
                          return {
                            ...prev,
                            stages: {
                              ...(prev.stages || {}),
                              [key]: { ...(prev.stages?.[key] || {}), ...patch },
                            },
                          }
                        })
                      }

                      return cards.map(c => {
                        const editing = Boolean(kpiEditorOpen && draft)
                        const value = editing ? getDraftKpi(c.draftKey) : c.kpi
                        return (
                          <div key={c.key} className="p-4 bg-paper-200 rounded-xl border border-border-light">
                            <div className="text-body-xs text-ink-400 mb-1">{c.label}</div>

                            {editing ? (
                              <div className="space-y-2">
                                <input
                                  value={value?.name || ''}
                                  onChange={(e) => setDraftKpi(c.draftKey, { name: e.target.value })}
                                  placeholder="KPI name"
                                  className="w-full px-3 py-2 bg-card border border-border rounded-lg text-body-sm text-ink"
                                />
                                <div className="flex items-center gap-2">
                                  <div className="text-body-xs text-ink-400">Target</div>
                                  <input
                                    type="number"
                                    value={Number.isFinite(Number(value?.target)) ? Number(value.target) : 0}
                                    onChange={(e) => setDraftKpi(c.draftKey, { target: Number(e.target.value || 0) })}
                                    className="w-28 px-2 py-1.5 bg-card border border-border rounded-lg text-body-xs text-ink font-mono"
                                  />
                                </div>
                              </div>
                            ) : (
                              <>
                                <div className="text-body-sm text-ink font-medium">{c.kpi?.name || '—'}</div>
                                <div className="mt-2 text-body-xs text-ink-400 font-mono">
                                  {Number(c.kpi?.current || 0).toLocaleString()} / {Number(c.kpi?.target || 0).toLocaleString()}
                                </div>
                              </>
                            )}
                          </div>
                        )
                      })
                    })()}
                  </div>

                  {kpiEditorOpen && kpiDraft && (
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="p-4 bg-paper-200 rounded-xl border border-border-light">
                        <div className="flex items-center justify-between mb-3">
                          <div className="font-serif text-ink">Leading indicators</div>
                          <button
                            onClick={() => setKpiDraft(prev => ({
                              ...prev,
                              leadingIndicators: [...(prev?.leadingIndicators || []), { id: makeLocalId(), name: '', target: 0 }],
                            }))}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs text-primary hover:bg-signal-muted rounded-lg transition-editorial"
                          >
                            <Plus className="w-3.5 h-3.5" strokeWidth={1.5} />
                            Add
                          </button>
                        </div>

                        {(kpiDraft.leadingIndicators || []).length ? (
                          <div className="space-y-2">
                            {(kpiDraft.leadingIndicators || []).map((li, idx) => (
                              <div key={li.id} className="flex items-center gap-2">
                                <input
                                  value={li?.name || ''}
                                  onChange={(e) => setKpiDraft(prev => {
                                    const next = [...(prev?.leadingIndicators || [])]
                                    next[idx] = { ...next[idx], name: e.target.value }
                                    return { ...prev, leadingIndicators: next }
                                  })}
                                  placeholder="Indicator name"
                                  className="flex-1 px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink"
                                />
                                <input
                                  type="number"
                                  value={Number.isFinite(Number(li?.target)) ? Number(li.target) : 0}
                                  onChange={(e) => setKpiDraft(prev => {
                                    const next = [...(prev?.leadingIndicators || [])]
                                    next[idx] = { ...next[idx], target: Number(e.target.value || 0) }
                                    return { ...prev, leadingIndicators: next }
                                  })}
                                  className="w-24 px-2 py-2 bg-card border border-border rounded-lg text-body-xs text-ink font-mono"
                                />
                                <button
                                  onClick={() => setKpiDraft(prev => ({
                                    ...prev,
                                    leadingIndicators: (prev?.leadingIndicators || []).filter(x => x.id !== li.id),
                                  }))}
                                  className="p-2 rounded-lg border border-border text-ink-400 hover:text-ink hover:bg-paper-300 transition-editorial"
                                  aria-label="Remove leading indicator"
                                >
                                  <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                                </button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-body-xs text-ink-400">No leading indicators yet.</div>
                        )}
                      </div>

                      <div className="p-4 bg-paper-200 rounded-xl border border-border-light">
                        <div className="flex items-center justify-between mb-3">
                          <div className="font-serif text-ink">Health rules</div>
                          <button
                            onClick={() => setKpiDraft(prev => ({
                              ...prev,
                              healthRules: [...(prev?.healthRules || []), { id: makeLocalId(), metric: 'primary', operator: '>=', threshold: 0, severity: 'warn' }],
                            }))}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-body-xs text-primary hover:bg-signal-muted rounded-lg transition-editorial"
                          >
                            <Plus className="w-3.5 h-3.5" strokeWidth={1.5} />
                            Add
                          </button>
                        </div>

                        {(kpiDraft.healthRules || []).length ? (
                          <div className="space-y-2">
                            {(kpiDraft.healthRules || []).map((r, idx) => (
                              <div key={r.id} className="flex items-center gap-2">
                                <select
                                  value={r?.metric || 'primary'}
                                  onChange={(e) => setKpiDraft(prev => {
                                    const next = [...(prev?.healthRules || [])]
                                    next[idx] = { ...next[idx], metric: e.target.value }
                                    return { ...prev, healthRules: next }
                                  })}
                                  className="px-2 py-2 bg-card border border-border rounded-lg text-body-xs text-ink"
                                >
                                  <option value="primary">Primary</option>
                                  <option value="reach">Reach</option>
                                  <option value="click">Clicks</option>
                                  <option value="convert">Conversions</option>
                                </select>
                                <select
                                  value={r?.operator || '>='}
                                  onChange={(e) => setKpiDraft(prev => {
                                    const next = [...(prev?.healthRules || [])]
                                    next[idx] = { ...next[idx], operator: e.target.value }
                                    return { ...prev, healthRules: next }
                                  })}
                                  className="px-2 py-2 bg-card border border-border rounded-lg text-body-xs text-ink font-mono"
                                >
                                  <option value=">=">&gt;=</option>
                                  <option value="<=">&lt;=</option>
                                </select>
                                <input
                                  type="number"
                                  value={Number.isFinite(Number(r?.threshold)) ? Number(r.threshold) : 0}
                                  onChange={(e) => setKpiDraft(prev => {
                                    const next = [...(prev?.healthRules || [])]
                                    next[idx] = { ...next[idx], threshold: Number(e.target.value || 0) }
                                    return { ...prev, healthRules: next }
                                  })}
                                  className="w-24 px-2 py-2 bg-card border border-border rounded-lg text-body-xs text-ink font-mono"
                                />
                                <select
                                  value={r?.severity || 'warn'}
                                  onChange={(e) => setKpiDraft(prev => {
                                    const next = [...(prev?.healthRules || [])]
                                    next[idx] = { ...next[idx], severity: e.target.value }
                                    return { ...prev, healthRules: next }
                                  })}
                                  className="px-2 py-2 bg-card border border-border rounded-lg text-body-xs text-ink"
                                >
                                  <option value="warn">Warn</option>
                                  <option value="fail">Fail</option>
                                </select>
                                <button
                                  onClick={() => setKpiDraft(prev => ({
                                    ...prev,
                                    healthRules: (prev?.healthRules || []).filter(x => x.id !== r.id),
                                  }))}
                                  className="p-2 rounded-lg border border-border text-ink-400 hover:text-ink hover:bg-paper-300 transition-editorial"
                                  aria-label="Remove health rule"
                                >
                                  <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                                </button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-body-xs text-ink-400">No health rules yet.</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'timeline' && (
            <div role="tabpanel" id={panelId('timeline')} aria-labelledby={tabId('timeline')} tabIndex={0}>
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-serif text-lg text-ink">Timeline</h2>
                  <button
                    type="button"
                    onClick={handleAddWeek}
                    className="flex items-center gap-1 px-3 py-1.5 text-body-sm text-primary hover:bg-signal-muted rounded-lg transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
                  >
                    <Plus className="w-4 h-4" strokeWidth={1.5} />
                    Add week
                  </button>
                </div>

                {getTimelineWeeks().length ? (
                  <div className="space-y-3">
                    {getTimelineWeeks().map((week) => {
                      const phaseOptions = getPhaseOptions()
                      const moveIds = week.moveIds || week.moves || []
                      const weekMoves = moveIds
                        .map(id => moves.find(m => m.id === id) || getMove?.(id))
                        .filter(Boolean)
                      const availableMoves = moves.filter(m => !moveIds.includes(m.id))

                      return (
                        <div key={`${campaign.id}_week_${week.week}`} className="p-4 bg-paper-200 rounded-xl">
                          <div className="flex items-start justify-between gap-3 mb-3">
                            <div className="min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="text-body-sm text-ink font-medium">Week {week.week}</span>
                                <select
                                  value={week.phase || 'Awareness'}
                                  onChange={(e) => handleSetWeekPhase(week.week, e.target.value)}
                                  className="px-2 py-1 bg-card border border-border rounded-lg text-body-xs text-ink"
                                >
                                  {phaseOptions.map(p => (
                                    <option key={`${week.week}_${p}`} value={p}>{p}</option>
                                  ))}
                                </select>
                              </div>
                              <div className="text-body-xs text-ink-400 mt-1">{moveIds.length} moves assigned</div>
                            </div>

                            <button
                              type="button"
                              onClick={() => handleRemoveWeek(week.week)}
                              className="p-2 rounded-lg border border-border text-ink-400 hover:text-ink hover:bg-paper-300 transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
                              aria-label="Remove week"
                            >
                              <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                            </button>
                          </div>

                          <div className="space-y-2">
                            {moveIds.length > 0 ? (
                              <div className="flex flex-wrap gap-2">
                                {(weekMoves.length ? weekMoves : moveIds.map(id => ({ id, name: id }))).map((m) => (
                                  <div
                                    key={`${week.week}_${m.id}`}
                                    className="inline-flex items-center gap-1 px-2 py-1 bg-card border border-border rounded-lg"
                                  >
                                    <button
                                      type="button"
                                      onClick={() => navigate(`/app/moves/${m.id}`)}
                                      className="text-body-xs text-ink hover:text-primary transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper rounded"
                                    >
                                      {m.name}
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => handleUnassignMoveFromWeek(week.week, m.id)}
                                      className="p-1 text-ink-400 hover:text-ink transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper rounded"
                                      aria-label="Unassign move"
                                    >
                                      <X className="w-3.5 h-3.5" strokeWidth={1.5} />
                                    </button>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="text-body-xs text-ink-400">No moves scheduled.</div>
                            )}

                            <div className="flex items-center gap-2">
                              <select
                                defaultValue=""
                                onChange={(e) => {
                                  const value = e.target.value
                                  if (!value) return
                                  handleAssignMoveToWeek(week.week, value)
                                  e.target.value = ''
                                }}
                                className="flex-1 px-3 py-2 bg-card border border-border rounded-lg text-body-xs text-ink"
                              >
                                <option value="">Assign a move…</option>
                                {availableMoves.map(m => (
                                  <option key={`${week.week}_assign_${m.id}`} value={m.id}>{m.name}</option>
                                ))}
                              </select>
                              <button
                                type="button"
                                onClick={() => navigate(`/app/campaigns/${campaign.id}`)}
                                className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-300 transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
                                title="Manage moves in this campaign"
                              >
                                Moves
                              </button>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-10">
                    <Calendar className="w-12 h-12 text-ink-300 mx-auto mb-3" strokeWidth={1.5} />
                    <div className="font-serif text-lg text-ink mb-1">No timeline yet</div>
                    <div className="text-body-sm text-ink-400">Add weeks and assign moves.</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'moves' && (
            <div role="tabpanel" id={panelId('moves')} aria-labelledby={tabId('moves')} tabIndex={0}>
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-serif text-lg text-ink">Moves</h2>
                </div>

                {moves.length > 0 ? (
                  <div className="space-y-3">
                    {moves.map(move => {
                      const completedTasks = move.checklistItems.filter(t => t.done).length
                      const totalTasks = move.checklistItems.length
                      const day = getMoveDayNumber?.(move.id) || 1
                      const todayTodo = (getMoveTasksForDay?.(move.id, day) || []).filter(t => t.status !== 'done').length

                      return (
                        <button
                          key={move.id}
                          type="button"
                          onClick={() => navigate(`/app/moves/${move.id}`)}
                          aria-label={`Open move ${move.name}`}
                          className="w-full text-left p-4 bg-paper-200 rounded-xl hover:bg-paper-300 transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-body-sm text-ink font-medium">{move.name}</span>
                            <span className={`px-2 py-0.5 rounded text-body-xs capitalize ${move.status === 'active' ? 'bg-emerald-50 text-emerald-600' :
                                move.status === 'generating' ? 'bg-paper text-ink-400' :
                                  move.status === 'pending' ? 'bg-amber-50 text-amber-600' :
                                    move.status === 'paused' ? 'bg-ink-100 text-ink-400' :
                                      move.status === 'completed' ? 'bg-primary/10 text-primary' :
                                        'bg-muted text-ink-400'
                              }`}>
                              {move.status}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-body-xs text-ink-400">
                            <span>{completedTasks}/{totalTasks} tasks complete</span>
                            <span className="font-mono">Today: {todayTodo}</span>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Target className="w-12 h-12 text-ink-300 mx-auto mb-3" strokeWidth={1.5} />
                    <p className="text-body-sm text-ink-400">No moves linked yet. Create a Move in Moves, then attach it here.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'schedule' && (
            <div role="tabpanel" id={panelId('schedule')} aria-labelledby={tabId('schedule')} tabIndex={0}>
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-serif text-lg text-ink">Schedule</h2>
                  <button
                    type="button"
                    disabled
                    className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg opacity-60"
                  >
                    Execution (soon)
                  </button>
                </div>
                <div className="text-body-sm text-ink-400">Campaign-level calendar. Link and schedule moves via Timeline.</div>
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div role="tabpanel" id={panelId('performance')} aria-labelledby={tabId('performance')} tabIndex={0}>
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h2 className="font-serif text-lg text-ink">Performance</h2>
                    <div className="text-body-xs text-ink-400">KPI progress + rollup from moves</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => applyCampaignKpiRollup?.(campaign.id)}
                    className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
                  >
                    Apply rollup
                  </button>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {(['primary', 'reach', 'click', 'convert']).map(key => (
                    <div key={`perf_${key}`} className="p-4 bg-paper-200 rounded-xl">
                      <div className="text-body-xs text-ink-400 capitalize">{key}</div>
                      <div className="mt-2 text-body-sm text-ink font-mono">
                        {Number(campaign?.kpis?.[key]?.current || 0).toLocaleString()} / {Number(campaign?.kpis?.[key]?.target || 0).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>

                {rollup && (
                  <div className="mt-4 text-body-xs text-ink-400">Rollup sources are visible in Overview → Campaign KPIs.</div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'postmortem' && (
            <div role="tabpanel" id={panelId('postmortem')} aria-labelledby={tabId('postmortem')} tabIndex={0}>
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-serif text-lg text-ink">Post-mortem</h2>
                  <button
                    type="button"
                    onClick={() => setActiveTab('moves')}
                    className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
                  >
                    Review moves
                  </button>
                </div>
                <div className="text-body-sm text-ink-400">Capture learnings + what to change next cycle.</div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Channels */}
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="font-serif text-lg text-ink mb-3">Channels</h3>
            <div className="space-y-2">
              {campaign.channels?.map(ch => {
                const channel = CHANNELS.find(c => c.id === ch)
                return (
                  <div key={ch} className="flex items-center gap-2 px-3 py-2 bg-paper-200 rounded-lg">
                    <span>{channel?.icon}</span>
                    <span className="text-body-sm text-ink">{channel?.name}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Cohorts */}
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="font-serif text-lg text-ink mb-3">Target Cohorts</h3>
            <div className="space-y-2">
              {campaignCohorts.map(cohort => (
                <div key={cohort.id} className="px-3 py-2 bg-paper-200 rounded-lg">
                  <div className="text-body-sm text-ink font-medium">{cohort.name}</div>
                  <div className="text-body-xs text-ink-400 line-clamp-1">{cohort.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="font-serif text-lg text-ink mb-3">Timeline</h3>
            <div className="space-y-2 text-body-sm">
              <div className="flex items-center justify-between">
                <span className="text-ink-400">Created</span>
                <span className="text-ink">{new Date(campaign.createdAt).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-400">Last updated</span>
                <span className="text-ink">{new Date(campaign.updatedAt).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}

// Main Campaigns Page
const CampaignsPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { campaigns, getCampaign } = useRaptorflowStore()
  const [blankOpen, setBlankOpen] = useState(false)

  useEffect(() => {
    if (id === 'new') setBlankOpen(true)
  }, [id])

  // If viewing a specific campaign
  if (id && id !== 'new') {
    const campaign = getCampaign(id)
    if (campaign) {
      return <CampaignDetail campaign={campaign} />
    }
  }

  return (
    <>
      <CampaignsListView
        campaigns={campaigns}
        onNavigate={navigate}
        onOpenCreate={() => setBlankOpen(true)}
      />

      <CreateCampaignModal
        isOpen={blankOpen}
        onClose={() => {
          setBlankOpen(false)
          if (id === 'new') navigate('/app/campaigns')
        }}
      />
    </>
  )
}

// List view
const CampaignsListView = ({ campaigns, onNavigate, onOpenCreate }) => {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-serif text-headline-md text-ink">Campaigns</h1>
          <p className="text-body-sm text-ink-400 mt-1">Your war plans — each contains moves, tasks, and learning.</p>
        </motion.div>

        <motion.button
          type="button"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={onOpenCreate}
          aria-label="Create a new campaign"
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          New Campaign
        </motion.button>
      </div>

      {campaigns.length > 0 ? (
        <>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-serif text-xl text-ink">Your campaigns</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.map((campaign) => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                onClick={() => onNavigate(`/app/campaigns/${campaign.id}`)}
              />
            ))}
          </div>
        </>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-10"
        >
          <Layers className="w-12 h-12 text-ink-300 mx-auto mb-3" strokeWidth={1.5} />
          <h2 className="font-serif text-xl text-ink mb-2">No campaigns yet</h2>
          <p className="text-body-sm text-ink-400 mb-6">Create a campaign to organize your moves and track KPIs.</p>
          <button
            type="button"
            onClick={onOpenCreate}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-paper"
          >
            Create your first campaign
          </button>
        </motion.div>
      )}
    </div>
  )
}

export default CampaignsPage
