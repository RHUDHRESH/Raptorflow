import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowLeft, Map, Sparkles, Target, Zap, Shield, Users, Clock, ChevronRight, Check, TrendingUp, DollarSign, PieChart, BarChart3, Eye, Lightbulb } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'

const protocols = {
  A: { name: 'Authority Blitz', icon: Sparkles, desc: 'Build thought leadership fast', color: 'text-purple-400 bg-purple-500/10' },
  B: { name: 'Trust Anchor', icon: Shield, desc: 'Validation and social proof', color: 'text-blue-400 bg-blue-500/10' },
  C: { name: 'Cost of Inaction', icon: Target, desc: 'Create urgency to act', color: 'text-red-400 bg-red-500/10' },
  D: { name: 'Facilitator Nudge', icon: Zap, desc: 'Smooth onboarding & activation', color: 'text-green-400 bg-green-500/10' },
  E: { name: 'Champions Armory', icon: Users, desc: 'Arm your internal advocates', color: 'text-amber-400 bg-amber-500/10' },
  F: { name: 'Churn Intercept', icon: Clock, desc: 'Retention & expansion plays', color: 'text-pink-400 bg-pink-500/10' },
}

const generateMarketInsights = (company, icps) => {
  const selectedICPs = icps.filter(i => i.selected)
  const isMidMarket = selectedICPs.some(i => i.id === 'frustrated-optimizer')
  const isEnterprise = selectedICPs.some(i => i.id === 'risk-mitigator')
  const isStartup = selectedICPs.some(i => i.id === 'desperate-scaler')
  
  // Generate realistic TAM/SAM/SOM based on ICP mix
  let tam = 50000000
  let sam = 5000000
  let som = 250000
  
  if (isEnterprise) {
    tam = 100000000
    sam = 15000000
    som = 500000
  } else if (isMidMarket) {
    tam = 50000000
    sam = 8000000
    som = 300000
  } else if (isStartup) {
    tam = 30000000
    sam = 5000000
    som = 200000
  }
  
  return {
    tam,
    sam,
    som,
    marketGrowth: 28,
    marketCagr: 18,
    competitorCount: isEnterprise ? 5 : 12,
    marketLeader: isEnterprise ? 'Salesforce' : 'HubSpot',
    averageContractValue: isEnterprise ? 150000 : isStartup ? 15000 : 50000,
    salesCycle: isEnterprise ? '6-9 months' : '4-6 weeks',
  }
}

const generateFinancialProjections = (company, icps, strategy) => {
  const selectedICPs = icps.filter(i => i.selected)
  const budget = parseInt(company.budget || 5000) * 100 // Monthly spend
  const avgContractValue = selectedICPs.length > 0 ? 50000 : 30000
  
  const months = []
  let cumulativeRevenue = 0
  let cumulativeLeads = 0
  
  for (let i = 0; i < 12; i++) {
    // Ramp curve: slow start, accelerates
    const rampFactor = Math.pow(1.15, i) // 15% month-over-month growth
    const monthlyLeads = Math.floor(10 * rampFactor)
    const conversionRate = 0.15 + (i * 0.01) // Improves over time
    const closedDeals = Math.floor(monthlyLeads * conversionRate)
    const monthlyRevenue = closedDeals * avgContractValue
    
    cumulativeLeads += monthlyLeads
    cumulativeRevenue += monthlyRevenue
    
    months.push({
      month: `M${i + 1}`,
      leads: monthlyLeads,
      revenue: monthlyRevenue,
      deals: closedDeals,
      cumulativeRevenue,
      cumulativeLeads,
      efficiency: i > 0 ? (monthlyRevenue / budget).toFixed(1) : 0,
    })
  }
  
  return {
    months,
    totalProjectedRevenue: cumulativeRevenue,
    totalProjectedLeads: cumulativeLeads,
    avgCAC: budget / (cumulativeLeads || 1),
    roi: ((cumulativeRevenue - (budget * 12)) / (budget * 12) * 100).toFixed(0),
    paybackMonths: Math.ceil(((budget * 12) / (cumulativeRevenue / 12)) || 6),
  }
}

const generateWarPlan = (strategy, icps) => {
  const selectedICPs = icps.filter(i => i.selected)
  
  return {
    phases: [
      {
        id: 1,
        name: 'Discovery & Authority',
        days: '1-30',
        objectives: [
          'Establish thought leadership positioning',
          'Build initial content foundation',
          'Set up tracking & attribution'
        ],
        campaigns: ['Authority Blitz', 'Content Waterfall'],
        kpis: [
          { name: 'Content pieces published', target: '8-12' },
          { name: 'Website traffic', target: '+30%' },
          { name: 'LinkedIn impressions', target: '50k' }
        ]
      },
      {
        id: 2,
        name: 'Launch & Validation',
        days: '31-60',
        objectives: [
          'Launch demand capture campaigns',
          'Build trust & social proof',
          'Start outbound to ICP accounts'
        ],
        campaigns: ['Trust Anchor', 'Spear Attack'],
        kpis: [
          { name: 'Demo conversion rate', target: '15%+' },
          { name: 'Pipeline generated', target: '$100k+' },
          { name: 'Case studies collected', target: '3' }
        ]
      },
      {
        id: 3,
        name: 'Optimization & Scale',
        days: '61-90',
        objectives: [
          'Double down on winning channels',
          'Kill underperforming experiments',
          'Prepare for next quarter'
        ],
        campaigns: ['Expansion Plays', 'Churn Intercept'],
        kpis: [
          { name: 'CAC payback', target: '<12 months' },
          { name: 'Win rate', target: '25%+' },
          { name: 'NRR', target: '110%+' }
        ]
      }
    ],
    activeProtocols: strategy.recommendedProtocols || ['A', 'B']
  }
}

const StepWarPlan = () => {
  const navigate = useNavigate()
  const { company, strategy, icps, warPlan, setWarPlan, toggleProtocol, nextStep, prevStep } = useOnboardingStore()
  
  const [isGenerating, setIsGenerating] = useState(true)
  const [activePhase, setActivePhase] = useState(1)
  const [activeTab, setActiveTab] = useState('overview')
  const [marketInsights, setMarketInsights] = useState(null)
  const [financials, setFinancials] = useState(null)

  // Generate war plan on mount
  useEffect(() => {
    if (!warPlan.generated) {
      setTimeout(() => {
        const plan = generateWarPlan(strategy, icps)
        const insights = generateMarketInsights(company, icps)
        const projections = generateFinancialProjections(company, icps, strategy)
        
        setMarketInsights(insights)
        setFinancials(projections)
        
        setWarPlan({
          generated: true,
          phases: plan.phases,
          protocols: Object.keys(protocols).reduce((acc, key) => ({
            ...acc,
            [key]: {
              ...protocols[key],
              active: plan.activeProtocols.includes(key)
            }
          }), {}),
          skeleton: plan
        })
        setIsGenerating(false)
      }, 2000)
    } else {
      setIsGenerating(false)
      // Regenerate insights if not already set
      if (!marketInsights) {
        const insights = generateMarketInsights(company, icps)
        const projections = generateFinancialProjections(company, icps, strategy)
        setMarketInsights(insights)
        setFinancials(projections)
      }
    }
  }, [])

  const handleNext = () => {
    nextStep()
    navigate('/onboarding/plan')
  }

  const handleBack = () => {
    prevStep()
    navigate('/onboarding/icps')
  }

  if (isGenerating) {
    return (
      <div className="min-h-[calc(100vh-140px)] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="relative mb-8">
            <div className="w-20 h-20 border-4 border-amber-500/20 rounded-full animate-pulse" />
            <Map className="absolute inset-0 m-auto w-8 h-8 text-amber-400 animate-pulse" />
          </div>
          <h2 className="text-2xl font-light text-white mb-2">Building your 90-Day War Plan...</h2>
          <p className="text-white/40">Generating market insights, financial projections, and tactical roadmap</p>
        </motion.div>
      </div>
    )
  }

  const selectedICPs = icps.filter(i => i.selected)

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col">
      <div className="flex-1 max-w-7xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-amber-500/10 rounded-xl">
              <Map className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 7 of 8 · War Plan Preview
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            Your 90-Day <span className="italic text-amber-200">War Plan</span>
          </h1>
          <p className="text-white/40 max-w-xl">
            Strategic roadmap + financial projections + market positioning.
          </p>
        </motion.div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex gap-2 mb-8 border-b border-white/10 overflow-x-auto"
        >
          {[
            { id: 'overview', label: 'Timeline & Phases', icon: Clock },
            { id: 'market', label: 'Market Analysis', icon: PieChart },
            { id: 'financial', label: 'Financial Projections', icon: TrendingUp },
            { id: 'positioning', label: 'Positioning Strategy', icon: Lightbulb },
          ].map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 text-sm border-b-2 transition-colors whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'border-amber-500 text-amber-400'
                    : 'border-transparent text-white/40 hover:text-white/60'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </motion.div>

        {/* TAB: Overview */}
        {activeTab === 'overview' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
            {/* Summary cards */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-2 lg:grid-cols-4 gap-4"
            >
              <div className="p-4 bg-zinc-900/50 border border-white/10 rounded-xl text-center">
                <div className="text-3xl font-light text-white mb-1">{selectedICPs.length}</div>
                <div className="text-xs text-white/40">Target ICPs</div>
              </div>
              <div className="p-4 bg-zinc-900/50 border border-white/10 rounded-xl text-center">
                <div className="text-3xl font-light text-white mb-1">3</div>
                <div className="text-xs text-white/40">Phases</div>
              </div>
              <div className="p-4 bg-zinc-900/50 border border-white/10 rounded-xl text-center">
                <div className="text-3xl font-light text-white mb-1">
                  {Object.values(warPlan.protocols || {}).filter(p => p.active).length}
                </div>
                <div className="text-xs text-white/40">Active Protocols</div>
              </div>
              <div className="p-4 bg-gradient-to-br from-amber-500/20 to-amber-600/5 border border-amber-500/30 rounded-xl text-center">
                <div className="text-3xl font-light text-amber-400 mb-1">90</div>
                <div className="text-xs text-amber-400/60">Days Covered</div>
              </div>
            </motion.div>

            {/* Timeline */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">
                90-Day Timeline
              </h3>

              {/* Phase tabs */}
              <div className="flex gap-2 mb-6 overflow-x-auto">
                {warPlan.phases?.map((phase) => (
                  <button
                    key={phase.id}
                    onClick={() => setActivePhase(phase.id)}
                    className={`
                      flex-1 min-w-[150px] p-4 rounded-xl border text-left transition-all
                      ${activePhase === phase.id
                        ? 'bg-amber-500/20 border-amber-500/50'
                        : 'bg-white/5 border-white/10 hover:border-white/20'
                      }
                    `}
                  >
                    <div className="text-xs text-white/40 mb-1">Days {phase.days}</div>
                    <div className={`font-medium ${activePhase === phase.id ? 'text-white' : 'text-white/60'}`}>
                      {phase.name}
                    </div>
                  </button>
                ))}
              </div>

              {/* Active phase details */}
              {warPlan.phases?.filter(p => p.id === activePhase).map((phase) => (
                <div key={phase.id} className="space-y-6">
                  {/* Objectives */}
                  <div>
                    <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Objectives</h4>
                    <ul className="space-y-2">
                      {phase.objectives.map((obj, i) => (
                        <li key={i} className="flex items-center gap-3 text-sm text-white/80">
                          <Check className="w-4 h-4 text-amber-400" />
                          {obj}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Campaigns */}
                  <div>
                    <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Campaigns</h4>
                    <div className="flex flex-wrap gap-2">
                      {phase.campaigns.map((campaign, i) => (
                        <span key={i} className="px-3 py-1.5 bg-amber-500/10 text-amber-400 rounded-full text-sm">
                          {campaign}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* KPIs */}
                  <div>
                    <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Key Metrics</h4>
                    <div className="grid grid-cols-3 gap-3">
                      {phase.kpis.map((kpi, i) => (
                        <div key={i} className="p-3 bg-white/5 rounded-lg">
                          <div className="text-lg font-light text-white">{kpi.target}</div>
                          <div className="text-xs text-white/40">{kpi.name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </motion.div>
          </motion.div>
        )}

        {/* TAB: Market Analysis */}
        {activeTab === 'market' && marketInsights && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
            {/* TAM/SAM/SOM */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-6 bg-gradient-to-br from-blue-500/20 to-blue-600/5 border border-blue-500/20 rounded-2xl"
              >
                <div className="text-xs text-blue-400/60 uppercase tracking-wider mb-2">Total Addressable Market</div>
                <div className="text-4xl font-light text-blue-300 mb-2">₹{(marketInsights.tam / 10000000).toFixed(1)}Cr</div>
                <div className="text-xs text-blue-400/40">Entire market opportunity</div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="p-6 bg-gradient-to-br from-amber-500/20 to-amber-600/5 border border-amber-500/20 rounded-2xl"
              >
                <div className="text-xs text-amber-400/60 uppercase tracking-wider mb-2">Serviceable Addressable Market</div>
                <div className="text-4xl font-light text-amber-300 mb-2">₹{(marketInsights.sam / 1000000).toFixed(1)}Cr</div>
                <div className="text-xs text-amber-400/40">Reachable segment for you</div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="p-6 bg-gradient-to-br from-green-500/20 to-green-600/5 border border-green-500/20 rounded-2xl"
              >
                <div className="text-xs text-green-400/60 uppercase tracking-wider mb-2">Serviceable Obtainable Market</div>
                <div className="text-4xl font-light text-green-300 mb-2">₹{(marketInsights.som / 100000).toFixed(1)}Lac</div>
                <div className="text-xs text-green-400/40">Year 1 realistic target</div>
              </motion.div>
            </div>

            {/* Market Dynamics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
              >
                <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">Market Dynamics</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm text-white/60">Market Growth (YoY)</span>
                      <span className="text-sm font-light text-white">{marketInsights.marketGrowth}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${marketInsights.marketGrowth}%` }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm text-white/60">Market CAGR (5Y)</span>
                      <span className="text-sm font-light text-white">{marketInsights.marketCagr}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: `${Math.min(marketInsights.marketCagr, 100)}%` }} />
                    </div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
              >
                <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">Competitive Landscape</h3>
                <div className="space-y-4">
                  <div>
                    <span className="text-sm text-white/60">Direct Competitors: {marketInsights.competitorCount}</span>
                    <div className="mt-2 text-sm text-white/40">Moderate competitive intensity</div>
                  </div>
                  <div>
                    <span className="text-sm text-white/60">Market Leader: {marketInsights.marketLeader}</span>
                    <div className="mt-2 text-sm text-white/40">~{Math.floor(100 / (marketInsights.competitorCount + 1))}% of market</div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Sales Dynamics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6"
            >
              <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl text-center">
                <DollarSign className="w-8 h-8 text-amber-400 mx-auto mb-3" />
                <div className="text-2xl font-light text-white mb-1">₹{(marketInsights.averageContractValue / 100000).toFixed(1)}Lac</div>
                <div className="text-xs text-white/40">Avg Contract Value</div>
              </div>
              <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl text-center">
                <Clock className="w-8 h-8 text-blue-400 mx-auto mb-3" />
                <div className="text-2xl font-light text-white mb-1">{marketInsights.salesCycle}</div>
                <div className="text-xs text-white/40">Sales Cycle Length</div>
              </div>
              <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl text-center">
                <Target className="w-8 h-8 text-green-400 mx-auto mb-3" />
                <div className="text-2xl font-light text-white mb-1">15-25%</div>
                <div className="text-xs text-white/40">Typical Win Rate</div>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* TAB: Financial Projections */}
        {activeTab === 'financial' && financials && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
            {/* Key Financial Metrics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-4 gap-6"
            >
              <div className="p-6 bg-gradient-to-br from-green-500/20 to-green-600/5 border border-green-500/20 rounded-2xl">
                <div className="text-xs text-green-400/60 uppercase tracking-wider mb-2">Year 1 Revenue</div>
                <div className="text-3xl font-light text-green-300 mb-1">₹{(financials.totalProjectedRevenue / 100000).toFixed(1)}Lac</div>
                <div className="text-xs text-green-400/40">Projected annual ARR</div>
              </div>
              <div className="p-6 bg-gradient-to-br from-blue-500/20 to-blue-600/5 border border-blue-500/20 rounded-2xl">
                <div className="text-xs text-blue-400/60 uppercase tracking-wider mb-2">Total Leads</div>
                <div className="text-3xl font-light text-blue-300 mb-1">{financials.totalProjectedLeads}</div>
                <div className="text-xs text-blue-400/40">Expected leads generated</div>
              </div>
              <div className="p-6 bg-gradient-to-br from-yellow-500/20 to-yellow-600/5 border border-yellow-500/20 rounded-2xl">
                <div className="text-xs text-yellow-400/60 uppercase tracking-wider mb-2">Avg CAC</div>
                <div className="text-3xl font-light text-yellow-300 mb-1">₹{financials.avgCAC.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
                <div className="text-xs text-yellow-400/40">Per acquired customer</div>
              </div>
              <div className="p-6 bg-gradient-to-br from-red-500/20 to-red-600/5 border border-red-500/20 rounded-2xl">
                <div className="text-xs text-red-400/60 uppercase tracking-wider mb-2">ROI</div>
                <div className="text-3xl font-light text-red-300 mb-1">{financials.roi}%</div>
                <div className="text-xs text-red-400/40">Return on marketing</div>
              </div>
            </motion.div>

            {/* 12-Month Revenue Projection Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-6">12-Month Revenue Projection</h3>
              <div className="flex items-flex-end justify-between h-64 gap-2">
                {financials.months.map((month, i) => {
                  const maxRevenue = Math.max(...financials.months.map(m => m.cumulativeRevenue))
                  const heightPercent = (month.cumulativeRevenue / maxRevenue) * 100
                  return (
                    <div key={month.month} className="flex-1 flex flex-col items-center">
                      <div className="relative w-full h-full flex items-flex-end justify-center mb-2">
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${heightPercent}%` }}
                          transition={{ delay: i * 0.05, duration: 0.5 }}
                          className="w-full bg-gradient-to-t from-amber-500 to-amber-400 rounded-t-sm"
                          title={`₹${(month.cumulativeRevenue / 100000).toFixed(1)}Lac`}
                        />
                      </div>
                      <div className="text-xs text-white/40">{month.month}</div>
                    </div>
                  )
                })}
              </div>
            </motion.div>

            {/* Detailed monthly breakdown */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-4">Monthly Breakdown</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-4 text-white/40">Month</th>
                      <th className="text-right py-3 px-4 text-white/40">Leads</th>
                      <th className="text-right py-3 px-4 text-white/40">Closed Deals</th>
                      <th className="text-right py-3 px-4 text-white/40">Monthly Revenue</th>
                      <th className="text-right py-3 px-4 text-white/40">Cumulative</th>
                    </tr>
                  </thead>
                  <tbody>
                    {financials.months.map((month) => (
                      <tr key={month.month} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4 text-white">{month.month}</td>
                        <td className="text-right py-3 px-4 text-white/60">{month.leads}</td>
                        <td className="text-right py-3 px-4 text-white/60">{month.deals}</td>
                        <td className="text-right py-3 px-4 text-green-400">₹{(month.revenue / 100000).toFixed(1)}Lac</td>
                        <td className="text-right py-3 px-4 text-amber-400 font-medium">₹{(month.cumulativeRevenue / 100000).toFixed(1)}Lac</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* TAB: Positioning */}
        {activeTab === 'positioning' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
            {/* ICP-specific positioning */}
            <div className="space-y-6">
              {selectedICPs.map((icp, index) => (
                <motion.div
                  key={icp.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
                >
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-medium text-white">{icp.label}</h3>
                    <span className="text-sm text-amber-400 bg-amber-500/10 px-3 py-1 rounded-full">Fit: {icp.fitScore}%</span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
                    <div>
                      <div className="text-xs text-white/40 uppercase tracking-wider mb-2">Key Pain Point</div>
                      <ul className="space-y-2">
                        {icp.psychographics.painPoints.slice(0, 2).map((pain, i) => (
                          <li key={i} className="text-sm text-white/80 flex items-center gap-2">
                            <span className="text-red-400">▸</span>{pain}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="text-xs text-white/40 uppercase tracking-wider mb-2">Primary Motivation</div>
                      <ul className="space-y-2">
                        {icp.psychographics.motivations.slice(0, 2).map((mot, i) => (
                          <li key={i} className="text-sm text-white/80 flex items-center gap-2">
                            <span className="text-green-400">▸</span>{mot}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="text-xs text-white/40 uppercase tracking-wider mb-2">Decision Maker</div>
                      <div className="text-sm text-white/80 space-y-2">
                        {icp.buyingCommittee.slice(0, 2).map((member, i) => (
                          <div key={i}>
                            <div className="font-medium text-white">{member.title}</div>
                            <div className="text-xs text-white/40">{member.role}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                    <div className="text-xs text-amber-400 font-medium mb-2">💡 Positioning Angle</div>
                    <p className="text-sm text-amber-400/80">
                      Lead with: "We help {icp.label.toLowerCase()}s {icp.psychographics.motivations[0]?.toLowerCase()}"
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Execution Protocols Sidebar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8 p-6 bg-zinc-900/50 border border-white/10 rounded-2xl"
        >
          <h3 className="text-sm uppercase tracking-[0.15em] text-white/40 mb-4">
            Execution Protocols
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(warPlan.protocols || {}).map(([key, protocol]) => {
              const Icon = protocols[key].icon
              return (
                <button
                  key={key}
                  onClick={() => toggleProtocol(key, !protocol.active)}
                  className={`
                    p-3 rounded-xl border text-left transition-all flex items-center gap-2
                    ${protocol.active
                      ? 'bg-gradient-to-r from-amber-500/10 to-transparent border-amber-500/30'
                      : 'bg-white/5 border-white/10 opacity-50 hover:opacity-75'
                    }
                  `}
                >
                  <div className={`p-2 rounded-lg ${protocols[key].color}`}>
                    <Icon className="w-3 h-3" />
                  </div>
                  <div className="flex-1">
                    <div className={`text-xs font-medium ${protocol.active ? 'text-white' : 'text-white/60'}`}>
                      {protocol.name}
                    </div>
                    <div className="text-[10px] text-white/40">{protocols[key].desc}</div>
                  </div>
                </button>
              )
            })}
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-white/40 hover:text-white text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          <button
            onClick={handleNext}
            className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium bg-amber-500 hover:bg-amber-400 text-black transition-all"
          >
            Choose Your Plan
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default StepWarPlan
