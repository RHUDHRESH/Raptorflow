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

// Protocol badges with colors
const PROTOCOL_BADGES = {
  A_AUTHORITY_BLITZ: { label: 'Authority Blitz', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  B_TRUST_ANCHOR: { label: 'Trust Anchor', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  C_COST_OF_INACTION: { label: 'Cost of Inaction', color: 'bg-amber-500/20 text-amber-400 border-amber-500/30' },
  D_HABIT_HARDCODE: { label: 'Habit Hardcode', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
  E_ENTERPRISE_WEDGE: { label: 'Enterprise Wedge', color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' },
  F_CHURN_INTERCEPT: { label: 'Churn Intercept', color: 'bg-red-500/20 text-red-400 border-red-500/30' }
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
    green: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    amber: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    red: 'bg-red-500/20 text-red-400 border-red-500/30',
    unknown: 'bg-white/10 text-white/40 border-white/20'
  }
  
  return (
    <span className={`px-2 py-0.5 rounded text-xs border ${colors[status] || colors.unknown}`}>
      {status?.toUpperCase() || 'N/A'}
    </span>
  )
}

// Campaign card component
const CampaignCard = ({ campaign, onSelect }) => {
  const statusColors = {
    draft: 'bg-white/10 text-white/60',
    planned: 'bg-blue-500/20 text-blue-400',
    active: 'bg-emerald-500/20 text-emerald-400',
    paused: 'bg-amber-500/20 text-amber-400',
    completed: 'bg-purple-500/20 text-purple-400',
    cancelled: 'bg-red-500/20 text-red-400'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      onClick={() => onSelect(campaign)}
      className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 cursor-pointer hover:border-white/20 transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium text-white">{campaign.name}</h3>
          <p className="text-white/40 text-sm mt-1 line-clamp-2">{campaign.description}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs ${statusColors[campaign.status]}`}>
          {campaign.status}
        </span>
      </div>

      {/* Strategy badges */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="px-2 py-1 bg-white/5 rounded text-xs text-white/60">
          {campaign.goal}
        </span>
        <span className="px-2 py-1 bg-white/5 rounded text-xs text-white/60">
          {campaign.demand_source}
        </span>
      </div>

      {/* Protocol badges */}
      <div className="flex flex-wrap gap-2 mb-4">
        {campaign.protocols?.slice(0, 2).map((protocol) => (
          <span 
            key={protocol}
            className={`px-2 py-1 rounded text-xs border ${PROTOCOL_BADGES[protocol]?.color || 'bg-white/10'}`}
          >
            {PROTOCOL_BADGES[protocol]?.label || protocol}
          </span>
        ))}
        {campaign.protocols?.length > 2 && (
          <span className="px-2 py-1 bg-white/5 rounded text-xs text-white/40">
            +{campaign.protocols.length - 2} more
          </span>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/10">
        <div>
          <div className="text-xs text-white/40">ICPs</div>
          <div className="text-lg font-medium text-white">{campaign.icp_ids?.length || 0}</div>
        </div>
        <div>
          <div className="text-xs text-white/40">Moves</div>
          <div className="text-lg font-medium text-white">{campaign.move_count || 0}</div>
        </div>
        <div>
          <div className="text-xs text-white/40">RAG</div>
          <RAGBadge status={campaign.rag_status} />
        </div>
      </div>

      {/* Date range */}
      {campaign.start_date && (
        <div className="flex items-center gap-2 mt-4 text-xs text-white/40">
          <Calendar className="w-3 h-3" />
          {campaign.start_date} → {campaign.end_date || 'Ongoing'}
        </div>
      )}
    </motion.div>
  )
}

// Campaign wizard step
const WizardStep = ({ step, current, title, description }) => {
  const isActive = step === current
  const isComplete = step < current
  
  return (
    <div className={`flex items-center gap-3 ${isActive ? 'text-white' : 'text-white/40'}`}>
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
        ${isComplete ? 'bg-emerald-500 text-white' : isActive ? 'bg-white/20 text-white' : 'bg-white/10'}
      `}>
        {isComplete ? <CheckCircle2 className="w-4 h-4" /> : step}
      </div>
      <div>
        <div className="font-medium">{title}</div>
        <div className="text-xs text-white/40">{description}</div>
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
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-[#0a0a0f] border border-white/10 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h2 className="text-xl font-medium text-white">Create Campaign</h2>
            <p className="text-sm text-white/40">Define your strategic marketing battle</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
            <X className="w-5 h-5 text-white/60" />
          </button>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-between px-6 py-4 bg-white/5 border-b border-white/10">
          <WizardStep step={1} current={step} title="Strategy" description="Goal & approach" />
          <ChevronRight className="w-4 h-4 text-white/20" />
          <WizardStep step={2} current={step} title="Targeting" description="ICPs & barriers" />
          <ChevronRight className="w-4 h-4 text-white/20" />
          <WizardStep step={3} current={step} title="Timing" description="Schedule & budget" />
          <ChevronRight className="w-4 h-4 text-white/20" />
          <WizardStep step={4} current={step} title="Review" description="Confirm & launch" />
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[50vh]">
          {/* Step 1: Strategy */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm text-white/60 mb-2">Campaign Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Q1 Pipeline Acceleration"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of campaign objectives..."
                  rows={3}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none resize-none"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-3">Primary Goal</label>
                <div className="grid grid-cols-3 gap-3">
                  {GOAL_OPTIONS.map((option) => {
                    const Icon = option.icon
                    return (
                      <button
                        key={option.value}
                        onClick={() => setFormData({ ...formData, goal: option.value })}
                        className={`p-4 rounded-xl border text-left transition-all ${
                          formData.goal === option.value
                            ? 'bg-white/10 border-white/30'
                            : 'bg-white/5 border-white/10 hover:border-white/20'
                        }`}
                      >
                        <Icon className={`w-5 h-5 mb-2 ${formData.goal === option.value ? 'text-white' : 'text-white/40'}`} />
                        <div className="font-medium text-white">{option.label}</div>
                        <div className="text-xs text-white/40 mt-1">{option.description}</div>
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-white/60 mb-3">Demand Source</label>
                  <div className="space-y-2">
                    {DEMAND_SOURCES.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setFormData({ ...formData, demand_source: option.value })}
                        className={`w-full p-3 rounded-lg border text-left transition-all ${
                          formData.demand_source === option.value
                            ? 'bg-white/10 border-white/30'
                            : 'bg-white/5 border-white/10 hover:border-white/20'
                        }`}
                      >
                        <div className="font-medium text-white text-sm">{option.label}</div>
                        <div className="text-xs text-white/40">{option.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-3">Persuasion Axis</label>
                  <div className="space-y-2">
                    {PERSUASION_AXES.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setFormData({ ...formData, persuasion_axis: option.value })}
                        className={`w-full p-3 rounded-lg border text-left transition-all ${
                          formData.persuasion_axis === option.value
                            ? 'bg-white/10 border-white/30'
                            : 'bg-white/5 border-white/10 hover:border-white/20'
                        }`}
                      >
                        <div className="font-medium text-white text-sm">{option.label}</div>
                        <div className="text-xs text-white/40">{option.description}</div>
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
                <label className="block text-sm text-white/60 mb-3">Select Target ICPs</label>
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
                          ? 'bg-white/10 border-white/30'
                          : 'bg-white/5 border-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-white">{icp.label}</div>
                          <div className="text-xs text-white/40 mt-1">{icp.summary}</div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-white/60">Fit: {icp.fit_score}%</span>
                          <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                            formData.icp_ids.includes(icp.id)
                              ? 'bg-emerald-500 border-emerald-500'
                              : 'border-white/30'
                          }`}>
                            {formData.icp_ids.includes(icp.id) && (
                              <CheckCircle2 className="w-3 h-3 text-white" />
                            )}
                          </div>
                        </div>
                      </div>
                    </button>
                  )) : (
                    <div className="p-8 text-center text-white/40 border border-dashed border-white/20 rounded-lg">
                      No ICPs generated yet. Complete onboarding first.
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-3">Primary Barriers</label>
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
                          ? 'bg-white/10 border-white/30'
                          : 'bg-white/5 border-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="font-medium text-white text-sm">{barrier}</div>
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
                  <label className="block text-sm text-white/60 mb-2">Start Date</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-2">End Date</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">Total Budget (INR)</label>
                <input
                  type="number"
                  value={formData.budget_plan.total}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    budget_plan: { ...formData.budget_plan, total: parseInt(e.target.value) || 0 }
                  })}
                  placeholder="500000"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none"
                />
              </div>

              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-amber-400" />
                  <span className="text-sm text-white/60">Budget allocation</span>
                </div>
                <p className="text-xs text-white/40">
                  Detailed budget allocation can be configured after campaign creation.
                </p>
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {step === 4 && (
            <div className="space-y-6">
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <h3 className="font-medium text-white mb-4">Campaign Summary</h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-white/40">Name</span>
                    <span className="text-white">{formData.name || 'Untitled'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Goal</span>
                    <span className="text-white capitalize">{formData.goal || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Demand Source</span>
                    <span className="text-white capitalize">{formData.demand_source?.replace('_', ' ') || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Persuasion</span>
                    <span className="text-white capitalize">{formData.persuasion_axis?.replace('_', ' ') || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Target ICPs</span>
                    <span className="text-white">{formData.icp_ids.length} selected</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Barriers</span>
                    <span className="text-white">{formData.primary_barriers.join(', ') || 'None'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Duration</span>
                    <span className="text-white">
                      {formData.start_date && formData.end_date 
                        ? `${formData.start_date} → ${formData.end_date}`
                        : 'Not scheduled'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Budget</span>
                    <span className="text-white">₹{formData.budget_plan.total.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                <div className="flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="text-sm">Ready to create campaign</span>
                </div>
                <p className="text-xs text-white/40 mt-1">
                  You can add moves and generate assets after creation.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-white/10 bg-white/5">
          <button
            onClick={step === 1 ? onClose : handleBack}
            className="px-4 py-2 text-white/60 hover:text-white transition-colors"
          >
            {step === 1 ? 'Cancel' : 'Back'}
          </button>
          
          {step < 4 ? (
            <button
              onClick={handleNext}
              disabled={step === 1 && (!formData.name || !formData.goal)}
              className="px-6 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              Continue
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="px-6 py-2 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-600 transition-colors flex items-center gap-2"
            >
              Create Campaign
              <CheckCircle2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </motion.div>
    </div>
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
        // Mock data for now - replace with API calls
        setCampaigns([
          {
            id: '1',
            name: 'Q1 Pipeline Acceleration',
            description: 'Build brand awareness and capture demand among tech founders scaling to Series A',
            goal: 'velocity',
            demand_source: 'creation',
            persuasion_axis: 'time',
            status: 'active',
            protocols: ['A_AUTHORITY_BLITZ', 'B_TRUST_ANCHOR'],
            icp_ids: ['icp-1', 'icp-2'],
            primary_barriers: ['OBSCURITY', 'RISK'],
            rag_status: 'green',
            move_count: 5,
            start_date: '2025-01-01',
            end_date: '2025-03-31'
          },
          {
            id: '2',
            name: 'Enterprise Expansion',
            description: 'Drive upsells and cross-sells within existing enterprise accounts',
            goal: 'penetration',
            demand_source: 'expansion',
            persuasion_axis: 'money',
            status: 'planned',
            protocols: ['E_ENTERPRISE_WEDGE'],
            icp_ids: ['icp-3'],
            primary_barriers: ['CAPACITY'],
            rag_status: 'unknown',
            move_count: 0,
            start_date: '2025-02-01',
            end_date: '2025-04-30'
          }
        ])

        setIcps([
          { id: 'icp-1', label: 'Desperate Scaler', summary: 'Fast-growing startups overwhelmed by scale', fit_score: 92 },
          { id: 'icp-2', label: 'Frustrated Optimizer', summary: 'Companies that tried alternatives and failed', fit_score: 78 },
          { id: 'icp-3', label: 'Risk Mitigator', summary: 'Conservative orgs needing proof', fit_score: 65 }
        ])
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
          <h1 className="text-3xl font-light text-white">Campaigns</h1>
          <p className="text-white/40 mt-1">
            Strategic marketing battles across your ICPs
          </p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={() => setShowWizard(true)}
          className="flex items-center gap-2 px-4 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Campaign
        </motion.button>
      </div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-4 gap-4 mb-8"
      >
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-white/60" />
            </div>
            <div>
              <div className="text-2xl font-medium text-white">{stats.total}</div>
              <div className="text-sm text-white/40">Total</div>
            </div>
          </div>
        </div>
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <Play className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <div className="text-2xl font-medium text-white">{stats.active}</div>
              <div className="text-sm text-white/40">Active</div>
            </div>
          </div>
        </div>
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <div className="text-2xl font-medium text-white">{stats.green}</div>
              <div className="text-sm text-white/40">On Track</div>
            </div>
          </div>
        </div>
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-500/20 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <div className="text-2xl font-medium text-white">{stats.atRisk}</div>
              <div className="text-sm text-white/40">At Risk</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="flex items-center gap-2 mb-6"
      >
        {['all', 'active', 'planned', 'draft', 'completed'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
              filter === status
                ? 'bg-white/10 text-white'
                : 'text-white/40 hover:text-white/60'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </motion.div>

      {/* Campaign grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-64 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : filteredCampaigns.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCampaigns.map((campaign, index) => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              onSelect={(c) => navigate(`/app/campaigns/${c.id}`)}
            />
          ))}
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Target className="w-8 h-8 text-white/20" />
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No campaigns yet</h3>
          <p className="text-white/40 mb-6">Create your first campaign to start executing your strategy</p>
          <button
            onClick={() => setShowWizard(true)}
            className="px-4 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors"
          >
            Create Campaign
          </button>
        </motion.div>
      )}

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
