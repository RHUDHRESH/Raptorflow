import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate, useParams } from 'react-router-dom'
import { 
  Zap, 
  Target, 
  Users, 
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  DollarSign,
  Calendar,
  ArrowRight,
  ArrowLeft,
  Shield,
  Rocket,
  Activity,
  BarChart3,
  Play,
  ChevronRight,
  Calculator
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

// Step indicator
const StepIndicator = ({ steps, currentStep }) => (
  <div className="flex items-center justify-center gap-2 mb-8">
    {steps.map((step, i) => (
      <div key={i} className="flex items-center">
        <div className={`
          w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all
          ${i + 1 < currentStep ? 'bg-emerald-500 text-white' : 
            i + 1 === currentStep ? 'bg-white/20 text-white' : 'bg-white/10 text-white/40'}
        `}>
          {i + 1 < currentStep ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
        </div>
        {i < steps.length - 1 && (
          <div className={`w-12 h-0.5 mx-2 ${i + 1 < currentStep ? 'bg-emerald-500' : 'bg-white/10'}`} />
        )}
      </div>
    ))}
  </div>
)

// Revenue simulator preview
const SimulatorPreview = ({ inputs, outputs }) => (
  <div className="bg-white/5 border border-white/10 rounded-xl p-6">
    <div className="flex items-center gap-2 mb-4">
      <Calculator className="w-5 h-5 text-amber-400" />
      <h3 className="font-medium text-white">Revenue Simulation</h3>
    </div>
    
    <div className="grid grid-cols-2 gap-6">
      <div>
        <div className="text-sm text-white/60 mb-3">Current State</div>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-white/40">Monthly Leads</span>
            <span className="text-white">{outputs.current?.monthly_leads || 0}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-white/40">Monthly Deals</span>
            <span className="text-white">{outputs.current?.monthly_deals || 0}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-white/40">Monthly ARR</span>
            <span className="text-white">₹{(outputs.current?.monthly_arr / 100000)?.toFixed(1) || 0}L</span>
          </div>
        </div>
      </div>
      
      <div>
        <div className="text-sm text-emerald-400 mb-3">Projected (30 days)</div>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-white/40">Monthly Leads</span>
            <span className="text-emerald-400">+{outputs.improvement?.additional_leads || 0}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-white/40">Monthly Deals</span>
            <span className="text-emerald-400">+{outputs.improvement?.additional_deals?.toFixed(1) || 0}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-white/40">ARR Increase</span>
            <span className="text-emerald-400">+₹{(outputs.improvement?.additional_arr / 100000)?.toFixed(1) || 0}L</span>
          </div>
        </div>
      </div>
    </div>
    
    {outputs.improvement?.percentage_lift > 0 && (
      <div className="mt-4 pt-4 border-t border-white/10">
        <div className="flex items-center justify-center gap-2 text-emerald-400">
          <TrendingUp className="w-5 h-5" />
          <span className="text-lg font-medium">
            {Math.round(outputs.improvement.percentage_lift)}% potential uplift
          </span>
        </div>
      </div>
    )}
  </div>
)

// Main Spike Setup page
const SpikeSetup = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    // Targets
    target_arr_increase: 500000,
    pipeline_target: 2500000,
    cac_ceiling: 5000,
    max_payback_months: 12,
    // Current metrics
    monthly_traffic: 10000,
    traffic_to_lead_rate: 3,
    lead_to_opp_rate: 15,
    opp_to_close_rate: 25,
    avg_deal_value: 50000,
    sales_cycle_days: 45,
    // Strategy
    campaign_id: '',
    icp_ids: [],
    protocols: []
  })

  // Simulation outputs
  const [simulation, setSimulation] = useState({
    current: { monthly_leads: 300, monthly_deals: 11, monthly_arr: 550000 },
    improvement: { additional_leads: 90, additional_deals: 3.3, additional_arr: 165000, percentage_lift: 30 }
  })

  // Mock data
  const [campaigns, setCampaigns] = useState([
    { id: '1', name: 'Q1 Pipeline', goal: 'velocity' },
    { id: '2', name: 'Enterprise Push', goal: 'penetration' }
  ])
  
  const [icps, setIcps] = useState([
    { id: '1', label: 'Desperate Scaler', fit_score: 92 },
    { id: '2', label: 'Frustrated Optimizer', fit_score: 78 },
    { id: '3', label: 'Risk Mitigator', fit_score: 65 }
  ])

  const protocols = [
    { id: 'A_AUTHORITY_BLITZ', label: 'Authority Blitz', description: 'Build thought leadership' },
    { id: 'B_TRUST_ANCHOR', label: 'Trust Anchor', description: 'Build credibility' },
    { id: 'C_COST_OF_INACTION', label: 'Cost of Inaction', description: 'Create urgency' }
  ]

  const steps = ['Goals', 'Funnel', 'Strategy', 'Guardrails', 'Review']

  const handleNext = () => setStep(s => Math.min(s + 1, 5))
  const handleBack = () => setStep(s => Math.max(s - 1, 1))

  const handleLaunch = async () => {
    setLoading(true)
    try {
      // API call to create spike
      console.log('Launching spike:', formData)
      await new Promise(resolve => setTimeout(resolve, 2000))
      navigate('/app/spikes')
    } catch (error) {
      console.error('Error launching spike:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="w-16 h-16 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Zap className="w-8 h-8 text-amber-400" />
        </div>
        <h1 className="text-3xl font-light text-white mb-2">Launch Your Spike</h1>
        <p className="text-white/40">30 days to clarity, control, and growth</p>
      </motion.div>

      {/* Step indicator */}
      <StepIndicator steps={steps} currentStep={step} />

      {/* Content */}
      <motion.div
        key={step}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8"
      >
        {/* Step 1: Goals */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-medium text-white mb-2">Define Your Goals</h2>
              <p className="text-white/40">What do you want to achieve in 30 days?</p>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-2">Spike Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Q1 Growth Spike"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">Target ARR Increase (₹)</label>
                <input
                  type="number"
                  value={formData.target_arr_increase}
                  onChange={(e) => setFormData({ ...formData, target_arr_increase: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">Pipeline Target (₹)</label>
                <input
                  type="number"
                  value={formData.pipeline_target}
                  onChange={(e) => setFormData({ ...formData, pipeline_target: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Funnel Metrics */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-medium text-white mb-2">Current Funnel Metrics</h2>
              <p className="text-white/40">Enter your current performance to model improvements</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">Monthly Traffic</label>
                <input
                  type="number"
                  value={formData.monthly_traffic}
                  onChange={(e) => setFormData({ ...formData, monthly_traffic: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">Traffic → Lead Rate (%)</label>
                <input
                  type="number"
                  value={formData.traffic_to_lead_rate}
                  onChange={(e) => setFormData({ ...formData, traffic_to_lead_rate: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">Lead → Opp Rate (%)</label>
                <input
                  type="number"
                  value={formData.lead_to_opp_rate}
                  onChange={(e) => setFormData({ ...formData, lead_to_opp_rate: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">Opp → Close Rate (%)</label>
                <input
                  type="number"
                  value={formData.opp_to_close_rate}
                  onChange={(e) => setFormData({ ...formData, opp_to_close_rate: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">Avg Deal Value (₹)</label>
                <input
                  type="number"
                  value={formData.avg_deal_value}
                  onChange={(e) => setFormData({ ...formData, avg_deal_value: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">Sales Cycle (days)</label>
                <input
                  type="number"
                  value={formData.sales_cycle_days}
                  onChange={(e) => setFormData({ ...formData, sales_cycle_days: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
              </div>
            </div>

            {/* Simulator Preview */}
            <SimulatorPreview inputs={formData} outputs={simulation} />
          </div>
        )}

        {/* Step 3: Strategy */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-medium text-white mb-2">Select Strategy</h2>
              <p className="text-white/40">Choose your campaign, ICPs, and protocols</p>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-3">Link to Campaign</label>
              <div className="space-y-2">
                {campaigns.map(campaign => (
                  <button
                    key={campaign.id}
                    onClick={() => setFormData({ ...formData, campaign_id: campaign.id })}
                    className={`w-full p-4 rounded-lg border text-left transition-all ${
                      formData.campaign_id === campaign.id
                        ? 'bg-white/10 border-white/30'
                        : 'bg-white/5 border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="font-medium text-white">{campaign.name}</div>
                    <div className="text-sm text-white/40">{campaign.goal}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-3">Target ICPs</label>
              <div className="space-y-2">
                {icps.map(icp => (
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
                      <div className="font-medium text-white">{icp.label}</div>
                      <span className="text-sm text-white/40">Fit: {icp.fit_score}%</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-3">Protocols to Execute</label>
              <div className="space-y-2">
                {protocols.map(protocol => (
                  <button
                    key={protocol.id}
                    onClick={() => {
                      const newProtocols = formData.protocols.includes(protocol.id)
                        ? formData.protocols.filter(p => p !== protocol.id)
                        : [...formData.protocols, protocol.id]
                      setFormData({ ...formData, protocols: newProtocols })
                    }}
                    className={`w-full p-4 rounded-lg border text-left transition-all ${
                      formData.protocols.includes(protocol.id)
                        ? 'bg-white/10 border-white/30'
                        : 'bg-white/5 border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="font-medium text-white">{protocol.label}</div>
                    <div className="text-sm text-white/40">{protocol.description}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Guardrails */}
        {step === 4 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-medium text-white mb-2">Set Guardrails</h2>
              <p className="text-white/40">Define your kill switch thresholds</p>
            </div>

            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
              <div className="flex items-center gap-2 text-amber-400 mb-2">
                <Shield className="w-5 h-5" />
                <span className="font-medium">Kill Switch Protection</span>
              </div>
              <p className="text-sm text-white/60">
                These guardrails will automatically pause campaigns if metrics breach thresholds.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">CAC Ceiling (₹)</label>
                <input
                  type="number"
                  value={formData.cac_ceiling}
                  onChange={(e) => setFormData({ ...formData, cac_ceiling: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
                <p className="text-xs text-white/40 mt-1">Pause if CAC exceeds this value</p>
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">Max Payback (months)</label>
                <input
                  type="number"
                  value={formData.max_payback_months}
                  onChange={(e) => setFormData({ ...formData, max_payback_months: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                />
                <p className="text-xs text-white/40 mt-1">Alert if payback period exceeds</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <div className="font-medium text-white">Weekly RAG Review</div>
                  <div className="text-sm text-white/40">Automated health check every week</div>
                </div>
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <div className="font-medium text-white">Conversion Floor Alert</div>
                  <div className="text-sm text-white/40">Alert if demo conversion drops below 10%</div>
                </div>
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Review */}
        {step === 5 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-medium text-white mb-2">Review & Launch</h2>
              <p className="text-white/40">Confirm your spike configuration</p>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="font-medium text-white">Goals</h3>
                <div className="p-4 bg-white/5 rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-white/40">Target ARR Increase</span>
                    <span className="text-white">₹{(formData.target_arr_increase / 100000).toFixed(1)}L</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/40">Pipeline Target</span>
                    <span className="text-white">₹{(formData.pipeline_target / 100000).toFixed(1)}L</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium text-white">Guardrails</h3>
                <div className="p-4 bg-white/5 rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-white/40">CAC Ceiling</span>
                    <span className="text-white">₹{formData.cac_ceiling.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/40">Max Payback</span>
                    <span className="text-white">{formData.max_payback_months} months</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium text-white">Strategy</h3>
              <div className="p-4 bg-white/5 rounded-lg space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-white/40">Campaign</span>
                  <span className="text-white">{campaigns.find(c => c.id === formData.campaign_id)?.name || 'None'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/40">ICPs</span>
                  <span className="text-white">{formData.icp_ids.length} selected</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/40">Protocols</span>
                  <span className="text-white">{formData.protocols.length} selected</span>
                </div>
              </div>
            </div>

            <SimulatorPreview inputs={formData} outputs={simulation} />

            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
              <div className="flex items-center gap-2 text-emerald-400">
                <Rocket className="w-5 h-5" />
                <span className="font-medium">Ready to launch</span>
              </div>
              <p className="text-sm text-white/60 mt-1">
                Your 30-day spike will begin immediately upon launch.
              </p>
            </div>
          </div>
        )}
      </motion.div>

      {/* Footer */}
      <div className="flex items-center justify-between mt-6">
        <button
          onClick={() => step === 1 ? navigate('/app/spikes') : handleBack()}
          className="flex items-center gap-2 px-4 py-2 text-white/60 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          {step === 1 ? 'Cancel' : 'Back'}
        </button>

        {step < 5 ? (
          <button
            onClick={handleNext}
            className="flex items-center gap-2 px-6 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors"
          >
            Continue
            <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleLaunch}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Launching...
              </>
            ) : (
              <>
                <Rocket className="w-4 h-4" />
                Launch Spike
              </>
            )}
          </button>
        )}
      </div>
    </div>
  )
}

export default SpikeSetup

