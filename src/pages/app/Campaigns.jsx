import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Plus, 
  Target, 
  Users, 
  Zap, 
  TrendingUp, 
  Calendar,
  ChevronRight,
  Play,
  Pause,
  CheckCircle2,
  AlertCircle,
  BarChart3,
  Settings,
  X,
  ArrowRight,
  Shield,
  Clock,
  DollarSign,
  Layers
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

import { Modal } from '@/components/system/Modal'
import { HairlineTable } from '@/components/system/HairlineTable'

// Protocol badges with colors
const PROTOCOL_BADGES = {
  A_AUTHORITY_BLITZ: { label: 'Authority Blitz' },
  B_TRUST_ANCHOR: { label: 'Trust Anchor' },
  C_COST_OF_INACTION: { label: 'Cost of Inaction' },
  D_HABIT_HARDCODE: { label: 'Habit Hardcode' },
  E_ENTERPRISE_WEDGE: { label: 'Enterprise Wedge' },
  F_CHURN_INTERCEPT: { label: 'Churn Intercept' }
}

// Goal options
const GOAL_OPTIONS = [
  { value: 'velocity', label: 'Velocity', description: 'Maximize growth speed, accept higher CAC', icon: Zap },
  { value: 'efficiency', label: 'Efficiency', description: 'Optimize unit economics, slower but profitable', icon: Target },
  { value: 'penetration', label: 'Penetration', description: 'Maximize market share, heavy brand investment', icon: Users }
]

// Demand source options
const DEMAND_SOURCES = [
  { value: 'capture', label: 'Demand Capture', description: 'Convert existing demand' },
  { value: 'creation', label: 'Demand Creation', description: 'Create new demand' },
  { value: 'expansion', label: 'Expansion', description: 'Grow existing accounts' }
]

// Persuasion axis options
const PERSUASION_AXES = [
  { value: 'money', label: 'Money', description: 'ROI, savings, revenue' },
  { value: 'time', label: 'Time', description: 'Speed, efficiency, automation' },
  { value: 'risk_image', label: 'Risk/Image', description: 'Security, reputation, compliance' }
]

// RAG status badge
const RAGBadge = ({ status }) => {
  const colors = {
    green: 'pill-neutral',
    amber: 'pill-accent',
    red: 'pill-accent',
    unknown: 'pill-neutral'
  }
  
  return (
    <span className={`pill-editorial ${colors[status] || colors.unknown}`}>
      {status || 'unknown'}
    </span>
  )
}

const StatusPill = ({ status }) => {
  const tone = status === 'active' ? 'pill-accent' : 'pill-neutral'
  return <span className={`pill-editorial ${tone}`}>{status || 'draft'}</span>
}

// Campaign wizard step
const WizardStep = ({ step, current, title, description }) => {
  const isActive = step === current
  const isComplete = step < current
  
  return (
    <div className={`flex items-center gap-3 ${isActive ? 'text-ink' : 'text-ink-400'}`}>
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
        ${isComplete ? 'bg-primary text-primary-foreground' : isActive ? 'bg-signal-muted text-primary' : 'bg-muted text-ink-400'}
      `}>
        {isComplete ? <CheckCircle2 className="w-4 h-4" strokeWidth={1.5} /> : step}
      </div>
      <div>
        <div className="font-medium">{title}</div>
        <div className="text-xs text-ink-400">{description}</div>
      </div>
    </div>
  )
}

// New campaign wizard modal
const NewCampaignWizard = ({ isOpen, onClose, icps = [], onSubmit }) => {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    goal: '',
    demand_source: '',
    persuasion_axis: '',
    icp_ids: [],
    primary_barriers: [],
    protocols: [],
    start_date: '',
    end_date: '',
    budget_plan: { total: 0, currency: 'INR', allocation: {} }
  })

  const handleNext = () => setStep(s => Math.min(s + 1, 4))
  const handleBack = () => setStep(s => Math.max(s - 1, 1))

  const handleSubmit = () => {
    onSubmit(formData)
    onClose()
    setStep(1)
    setFormData({
      name: '',
      description: '',
      goal: '',
      demand_source: '',
      persuasion_axis: '',
      icp_ids: [],
      primary_barriers: [],
      protocols: [],
      start_date: '',
      end_date: '',
      budget_plan: { total: 0, currency: 'INR', allocation: {} }
    })
  }

  if (!isOpen) return null

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose()
      }}
      title="Create campaign"
      description="Define your strategic marketing plan."
      contentClassName="max-w-3xl"
    >
      {/* Progress */}
      <div className="flex flex-wrap items-center gap-3 rounded-card border border-border bg-muted px-4 py-3">
        <WizardStep step={1} current={step} title="Strategy" description="Goal & approach" />
        <ChevronRight className="w-4 h-4 text-border" strokeWidth={1.5} />
        <WizardStep step={2} current={step} title="Targeting" description="ICPs & barriers" />
        <ChevronRight className="w-4 h-4 text-border" strokeWidth={1.5} />
        <WizardStep step={3} current={step} title="Timing" description="Schedule & budget" />
        <ChevronRight className="w-4 h-4 text-border" strokeWidth={1.5} />
        <WizardStep step={4} current={step} title="Review" description="Confirm & launch" />
      </div>

      {/* Content */}
      <div className="mt-5 max-h-[55vh] overflow-y-auto pr-1">
        {/* Step 1: Strategy */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm text-muted-foreground mb-2">Campaign name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Q1 Pipeline Acceleration"
                className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>

            <div>
              <label className="block text-sm text-muted-foreground mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of campaign objectives..."
                rows={3}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
              />
            </div>

            <div>
              <label className="block text-sm text-muted-foreground mb-3">Primary goal</label>
              <div className="grid grid-cols-3 gap-3">
                {GOAL_OPTIONS.map((option) => {
                  const Icon = option.icon
                  return (
                    <button
                      key={option.value}
                      onClick={() => setFormData({ ...formData, goal: option.value })}
                      className={`p-4 rounded-xl border text-left transition-all ${
                        formData.goal === option.value
                          ? 'bg-signal-muted border-primary/20'
                          : 'bg-background border-border hover:border-border-dark'
                      }`}
                    >
                      <Icon className={`w-5 h-5 mb-2 ${formData.goal === option.value ? 'text-primary' : 'text-ink-400'}`} strokeWidth={1.5} />
                      <div className="font-medium text-ink">{option.label}</div>
                      <div className="text-xs text-ink-400 mt-1">{option.description}</div>
                    </button>
                  )
                })}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-muted-foreground mb-3">Demand source</label>
                <div className="space-y-2">
                  {DEMAND_SOURCES.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setFormData({ ...formData, demand_source: option.value })}
                      className={`w-full p-3 rounded-lg border text-left transition-all ${
                        formData.demand_source === option.value
                          ? 'bg-signal-muted border-primary/20'
                          : 'bg-background border-border hover:border-border-dark'
                      }`}
                    >
                      <div className="font-medium text-ink text-sm">{option.label}</div>
                      <div className="text-xs text-ink-400">{option.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm text-muted-foreground mb-3">Persuasion axis</label>
                <div className="space-y-2">
                  {PERSUASION_AXES.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setFormData({ ...formData, persuasion_axis: option.value })}
                      className={`w-full p-3 rounded-lg border text-left transition-all ${
                        formData.persuasion_axis === option.value
                          ? 'bg-signal-muted border-primary/20'
                          : 'bg-background border-border hover:border-border-dark'
                      }`}
                    >
                      <div className="font-medium text-ink text-sm">{option.label}</div>
                      <div className="text-xs text-ink-400">{option.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Targeting */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm text-muted-foreground mb-3">Select Target ICPs</label>
              <div className="space-y-2">
                {icps.length > 0 ? icps.map((icp) => (
                  <button
                    key={icp.id}
                    onClick={() => {
                      const newIds = formData.icp_ids.includes(icp.id)
                        ? formData.icp_ids.filter(id => id !== icp.id)
                        : [...formData.icp_ids, icp.id]
                      setFormData({ ...formData, icp_ids: newIds })
                    }}
                    className={`w-full p-4 rounded-lg border text-left transition-all ${
                      formData.icp_ids.includes(icp.id)
                        ? 'bg-signal-muted border-primary/20'
                        : 'bg-background border-border hover:border-border-dark'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-ink">{icp.label}</div>
                        <div className="text-xs text-ink-400 mt-1">{icp.summary}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-ink-400">Fit: {icp.fit_score}%</span>
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          formData.icp_ids.includes(icp.id)
                            ? 'bg-emerald-500 border-emerald-500'
                            : 'border-border'
                        }`}>
                          {formData.icp_ids.includes(icp.id) && (
                            <CheckCircle2 className="w-3 h-3 text-white" />
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                )) : (
                  <div className="p-8 text-center text-ink-400 border border-dashed border-border rounded-lg">
                    No ICPs generated yet. Complete onboarding first.
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm text-muted-foreground mb-3">Primary barriers</label>
              <div className="grid grid-cols-2 gap-2">
                {['OBSCURITY', 'RISK', 'INERTIA', 'FRICTION', 'CAPACITY', 'ATROPHY'].map((barrier) => (
                  <button
                    key={barrier}
                    onClick={() => {
                      const newBarriers = formData.primary_barriers.includes(barrier)
                        ? formData.primary_barriers.filter(b => b !== barrier)
                        : [...formData.primary_barriers, barrier]
                      setFormData({ ...formData, primary_barriers: newBarriers })
                    }}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      formData.primary_barriers.includes(barrier)
                        ? 'bg-signal-muted border-primary/20'
                        : 'bg-background border-border hover:border-border-dark'
                    }`}
                  >
                    <div className="font-medium text-ink text-sm">{barrier}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Timing & Budget */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-muted-foreground mb-2">Start date</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
              <div>
                <label className="block text-sm text-muted-foreground mb-2">End date</label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-muted-foreground mb-2">Total budget (INR)</label>
              <input
                type="number"
                value={formData.budget_plan.total}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  budget_plan: { ...formData.budget_plan, total: parseInt(e.target.value) || 0 }
                })}
                placeholder="500000"
                className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>

            <div className="p-4 bg-muted rounded-lg border border-border">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-primary" strokeWidth={1.5} />
                <span className="text-sm text-ink-400">Budget allocation</span>
              </div>
              <p className="text-xs text-ink-400">
                Detailed budget allocation can be configured after campaign creation.
              </p>
            </div>
          </div>
        )}

        {/* Step 4: Review */}
        {step === 4 && (
          <div className="space-y-6">
            <div className="p-4 bg-card rounded-lg border border-border">
              <h3 className="font-medium text-ink mb-4">Campaign summary</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-ink-400">Name</span>
                  <span className="text-ink">{formData.name || 'Untitled'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-400">Goal</span>
                  <span className="text-ink capitalize">{formData.goal || 'Not set'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-400">Demand source</span>
                  <span className="text-ink capitalize">{formData.demand_source?.replace('_', ' ') || 'Not set'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-400">Persuasion</span>
                  <span className="text-ink capitalize">{formData.persuasion_axis?.replace('_', ' ') || 'Not set'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-400">Target ICPs</span>
                  <span className="text-ink">{formData.icp_ids.length} selected</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-400">Barriers</span>
                  <span className="text-ink">{formData.primary_barriers.join(', ') || 'None'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-400">Duration</span>
                  <span className="text-ink">
                    {formData.start_date && formData.end_date 
                      ? `${formData.start_date} → ${formData.end_date}`
                      : 'Not scheduled'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-400">Budget</span>
                  <span className="text-ink">₹{formData.budget_plan.total.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-signal-muted border border-primary/20 rounded-lg">
              <div className="flex items-center gap-2 text-primary">
                <CheckCircle2 className="w-4 h-4" strokeWidth={1.5} />
                <span className="text-sm">Ready to create campaign</span>
              </div>
              <p className="text-xs text-ink-400 mt-1">
                You can add moves and generate assets after creation.
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <button
          type="button"
          onClick={step === 1 ? onClose : handleBack}
          className="btn-editorial btn-ghost"
        >
          {step === 1 ? 'Cancel' : 'Back'}
        </button>

        {step < 4 ? (
          <button
            type="button"
            onClick={handleNext}
            disabled={step === 1 && (!formData.name || !formData.goal)}
            className="btn-editorial btn-primary"
          >
            Continue
            <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            className="btn-editorial btn-primary"
          >
            Create campaign
            <CheckCircle2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </Modal>
  )
}

// Main Campaigns page
const Campaigns = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [campaigns, setCampaigns] = useState([])
  const [icps, setIcps] = useState([])
  const [loading, setLoading] = useState(true)
  const [showWizard, setShowWizard] = useState(false)
  const [filter, setFilter] = useState('all')

  // Fetch campaigns and ICPs
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Start empty - user creates their own campaigns
        setCampaigns([])
        setIcps([])
      } catch (error) {
        console.error('Error fetching campaigns:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleCreateCampaign = async (data) => {
    console.log('Creating campaign:', data)
    // API call to create campaign
    const newCampaign = {
      id: `campaign-${Date.now()}`,
      ...data,
      status: 'draft',
      rag_status: 'unknown',
      move_count: 0
    }
    setCampaigns([newCampaign, ...campaigns])
  }

  const filteredCampaigns = filter === 'all' 
    ? campaigns 
    : campaigns.filter(c => c.status === filter)

  // Stats
  const stats = {
    total: campaigns.length,
    active: campaigns.filter(c => c.status === 'active').length,
    green: campaigns.filter(c => c.rag_status === 'green').length,
    atRisk: campaigns.filter(c => c.rag_status === 'red' || c.rag_status === 'amber').length
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-serif text-headline-md text-ink">Campaigns</h1>
          <p className="text-body-sm text-ink-400 mt-1">Strategic marketing plans across your ICPs</p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={() => setShowWizard(true)}
          className="btn-editorial btn-primary"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          New campaign
        </motion.button>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          {['all', 'active', 'planned', 'draft', 'completed'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-2 rounded-editorial text-body-sm transition-editorial ${
                filter === status
                  ? 'bg-muted text-ink'
                  : 'text-ink-400 hover:text-ink hover:bg-muted'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        <div className="text-body-xs text-ink-400">
          {stats.active} active · {stats.total} total
        </div>
      </div>

      <HairlineTable
        loading={loading}
        data={filteredCampaigns}
        onRowClick={(row) => navigate(`/app/campaigns/${row.id}`)}
        emptyTitle="No campaigns yet"
        emptyDescription="Create your first campaign to start executing your strategy."
        emptyAction="Create campaign"
        onEmptyAction={() => setShowWizard(true)}
        columns={[
          {
            key: 'name',
            header: 'Campaign',
            render: (row) => (
              <div>
                <div className="text-ink">{row.name}</div>
                <div className="text-xs text-ink-400 line-clamp-1">{row.description}</div>
              </div>
            )
          },
          {
            key: 'status',
            header: 'Status',
            render: (row) => <StatusPill status={row.status} />
          },
          {
            key: 'rag_status',
            header: 'Signal',
            render: (row) => <RAGBadge status={row.rag_status} />
          },
          {
            key: 'icps',
            header: 'ICPs',
            align: 'right',
            render: (row) => <span className="font-mono text-ink">{row.icp_ids?.length || 0}</span>
          },
          {
            key: 'moves',
            header: 'Moves',
            align: 'right',
            render: (row) => <span className="font-mono text-ink">{row.move_count || 0}</span>
          },
          {
            key: 'start_date',
            header: 'Dates',
            render: (row) => (
              <span className="text-ink-400 text-body-sm">
                {row.start_date ? `${row.start_date} → ${row.end_date || 'Ongoing'}` : '—'}
              </span>
            )
          }
        ]}
      />

      {/* New Campaign Wizard */}
      <AnimatePresence>
        {showWizard && (
          <NewCampaignWizard
            isOpen={showWizard}
            onClose={() => setShowWizard(false)}
            icps={icps}
            onSubmit={handleCreateCampaign}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default Campaigns
