import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  FileText, 
  Download, 
  CreditCard, 
  Check, 
  Building, 
  Package, 
  Target, 
  Compass, 
  Users, 
  Map,
  Shield,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

// This would be fetched from the backend using the share token
const mockSharedData = {
  company: {
    name: 'Acme Analytics',
    website: 'acme.io',
    industry: 'Software / SaaS',
    employeeCount: '51-200',
    stage: 'series-a'
  },
  product: {
    name: 'Acme Insights',
    type: 'saas',
    mainJob: 'Automates monthly financial reporting for growing startups',
    priceRange: '300-800'
  },
  positioning: {
    danKennedy: 'We save finance teams 40+ hours per month on manual reporting by automating the entire process from data collection to board-ready presentations.',
    dunford: 'We\'re better than Looker or Tableau for Series A-B startups who need investor-ready metrics without hiring a data team.',
    derived: {
      valueProposition: 'For growing startups who struggle with manual reporting, Acme Insights automates financial reports so you can impress investors without hiring a data team.',
      clarityScore: 78
    }
  },
  strategy: {
    goalPrimary: 'velocity',
    demandSource: 'creation',
    persuasionAxis: 'time'
  },
  icps: [
    { id: '1', label: 'Desperate Scaler', fitScore: 92, summary: 'Series A-B startups with 50-200 people overwhelmed by manual processes.' },
    { id: '2', label: 'Frustrated Optimizer', fitScore: 78, summary: 'Companies that tried BI tools but found them too complex for their needs.' }
  ],
  warPlan: {
    phases: [
      { name: 'Discovery & Authority', days: '1-30' },
      { name: 'Launch & Validation', days: '31-60' },
      { name: 'Optimization & Scale', days: '61-90' }
    ]
  },
  salesRep: {
    name: 'Sarah Johnson',
    email: 'sarah@raptorflow.com'
  },
  createdAt: '2024-12-04T10:00:00Z'
}

const plans = [
  { id: 'ascent', name: 'Ascent', price: 5000, cohorts: 2 },
  { id: 'glide', name: 'Glide', price: 7000, cohorts: 5, recommended: true },
  { id: 'soar', name: 'Soar', price: 10000, cohorts: 'Unlimited' }
]

const Section = ({ icon: Icon, title, children, defaultOpen = true }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  
  return (
    <div className="border-b border-white/5 last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full py-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5 text-amber-400" />
          <span className="text-white font-medium">{title}</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-white/40" /> : <ChevronDown className="w-4 h-4 text-white/40" />}
      </button>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          className="pb-6"
        >
          {children}
        </motion.div>
      )}
    </div>
  )
}

const SharedView = () => {
  const { token } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPlan, setSelectedPlan] = useState('glide')
  const [paymentLoading, setPaymentLoading] = useState(false)

  useEffect(() => {
    // In reality, this would fetch from the backend using the token
    const fetchData = async () => {
      try {
        // Simulate API call
        await new Promise(r => setTimeout(r, 1000))
        
        if (!token || token === 'invalid') {
          setError('Invalid or expired link')
          setLoading(false)
          return
        }

        setData(mockSharedData)
        setLoading(false)
      } catch (err) {
        setError('Failed to load strategy data')
        setLoading(false)
      }
    }

    fetchData()
  }, [token])

  const handlePayment = async () => {
    setPaymentLoading(true)
    // In reality, this would initiate payment
    await new Promise(r => setTimeout(r, 1500))
    // Would redirect to PhonePe payment page
    alert('Redirecting to PhonePe payment...')
    setPaymentLoading(false)
  }

  const handleDownloadPDF = () => {
    // Would generate and download PDF
    alert('PDF download would start here')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-amber-400 animate-spin mx-auto mb-4" />
          <p className="text-white/40">Loading your strategy...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h1 className="text-2xl font-light text-white mb-2">Link Invalid</h1>
          <p className="text-white/40 mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors"
          >
            Go to Homepage
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[600px] bg-gradient-radial from-amber-900/10 via-transparent to-transparent opacity-50" />
      </div>

      {/* Header */}
      <header className="relative z-20 border-b border-white/5 bg-zinc-950/80 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-xl tracking-tight font-light text-white">
            Raptor<span className="italic font-normal text-amber-200">flow</span>
          </span>
          <button
            onClick={handleDownloadPDF}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            Download PDF
          </button>
        </div>
      </header>

      <main className="relative z-10 max-w-4xl mx-auto px-6 py-12">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500/10 text-amber-400 rounded-full text-sm mb-6">
            <FileText className="w-4 h-4" />
            Strategy Prepared by {data.salesRep.name}
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            {data.company.name} <span className="italic text-amber-200">Strategy Overview</span>
          </h1>
          <p className="text-white/40">
            Review your customized 90-day strategy and choose a plan to get started
          </p>
        </motion.div>

        {/* Content sections */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-zinc-900/50 border border-white/10 rounded-2xl mb-8"
        >
          {/* Company & Product */}
          <Section icon={Building} title="Company & Product">
            <div className="grid grid-cols-2 gap-6 px-4">
              <div>
                <h4 className="text-xs text-white/40 uppercase tracking-wider mb-2">Company</h4>
                <p className="text-white font-medium">{data.company.name}</p>
                <p className="text-white/60 text-sm">{data.company.industry}</p>
                <p className="text-white/40 text-sm">{data.company.employeeCount} employees</p>
              </div>
              <div>
                <h4 className="text-xs text-white/40 uppercase tracking-wider mb-2">Product</h4>
                <p className="text-white font-medium">{data.product.name}</p>
                <p className="text-white/60 text-sm">{data.product.mainJob}</p>
              </div>
            </div>
          </Section>

          {/* Positioning */}
          <Section icon={Target} title="Positioning">
            <div className="px-4 space-y-4">
              <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                <p className="text-amber-400 text-sm mb-2">Value Proposition</p>
                <p className="text-white italic">"{data.positioning.derived.valueProposition}"</p>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-white/40 text-sm">Positioning Clarity Score:</span>
                <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-amber-500 rounded-full"
                    style={{ width: `${data.positioning.derived.clarityScore}%` }}
                  />
                </div>
                <span className="text-amber-400 font-medium">{data.positioning.derived.clarityScore}%</span>
              </div>
            </div>
          </Section>

          {/* Strategy */}
          <Section icon={Compass} title="Strategic Direction">
            <div className="px-4 grid grid-cols-3 gap-4">
              <div className="p-4 bg-white/5 rounded-xl text-center">
                <p className="text-2xl font-light text-white capitalize">{data.strategy.goalPrimary}</p>
                <p className="text-xs text-white/40">Primary Goal</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl text-center">
                <p className="text-2xl font-light text-white capitalize">{data.strategy.demandSource}</p>
                <p className="text-xs text-white/40">Demand Source</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl text-center">
                <p className="text-2xl font-light text-white capitalize">{data.strategy.persuasionAxis}</p>
                <p className="text-xs text-white/40">Persuasion Axis</p>
              </div>
            </div>
          </Section>

          {/* ICPs */}
          <Section icon={Users} title="Target ICPs">
            <div className="px-4 space-y-3">
              {data.icps.map((icp) => (
                <div key={icp.id} className="p-4 bg-white/5 rounded-xl flex items-start gap-4">
                  <div className={`
                    px-2 py-1 rounded text-xs font-medium
                    ${icp.fitScore >= 80 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}
                  `}>
                    {icp.fitScore}%
                  </div>
                  <div>
                    <p className="text-white font-medium">{icp.label}</p>
                    <p className="text-white/50 text-sm">{icp.summary}</p>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          {/* War Plan */}
          <Section icon={Map} title="90-Day War Plan">
            <div className="px-4">
              <div className="flex gap-2">
                {data.warPlan.phases.map((phase, i) => (
                  <div key={i} className="flex-1 p-4 bg-white/5 rounded-xl text-center">
                    <p className="text-white font-medium">{phase.name}</p>
                    <p className="text-xs text-white/40">Days {phase.days}</p>
                  </div>
                ))}
              </div>
            </div>
          </Section>
        </motion.div>

        {/* Plan Selection & Payment */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/20 rounded-2xl p-8"
        >
          <h2 className="text-xl font-light text-white text-center mb-6">
            Choose Your Plan & Complete Payment
          </h2>

          {/* Plan options */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            {plans.map((plan) => (
              <button
                key={plan.id}
                onClick={() => setSelectedPlan(plan.id)}
                className={`
                  p-4 rounded-xl border text-center transition-all
                  ${selectedPlan === plan.id
                    ? 'bg-amber-500/20 border-amber-500/50 ring-2 ring-amber-500'
                    : 'bg-white/5 border-white/10 hover:border-white/20'
                  }
                  ${plan.recommended ? 'relative' : ''}
                `}
              >
                {plan.recommended && (
                  <span className="absolute -top-2 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-amber-500 text-black text-[10px] uppercase rounded-full">
                    Recommended
                  </span>
                )}
                <p className="text-white font-medium mb-1">{plan.name}</p>
                <p className="text-2xl font-light text-white mb-1">₹{plan.price.toLocaleString()}</p>
                <p className="text-xs text-white/40">{plan.cohorts} cohorts</p>
              </button>
            ))}
          </div>

          {/* Payment button */}
          <button
            onClick={handlePayment}
            disabled={paymentLoading}
            className="w-full py-4 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            {paymentLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <CreditCard className="w-5 h-5" />
                Pay ₹{plans.find(p => p.id === selectedPlan)?.price.toLocaleString()} with PhonePe
              </>
            )}
          </button>

          <div className="flex items-center justify-center gap-2 mt-4 text-white/30 text-xs">
            <Shield className="w-4 h-4" />
            <span>Secured by PhonePe Payment Gateway</span>
          </div>
        </motion.div>

        {/* Footer */}
        <div className="mt-12 text-center text-white/30 text-sm">
          <p>
            Questions? Contact {data.salesRep.name} at{' '}
            <a href={`mailto:${data.salesRep.email}`} className="text-amber-400 hover:underline">
              {data.salesRep.email}
            </a>
          </p>
        </div>
      </main>
    </div>
  )
}

export default SharedView

