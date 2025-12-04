import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Target,
  Users,
  DollarSign,
  Percent,
  Clock,
  Activity,
  ChevronDown,
  ChevronRight,
  Plus,
  RefreshCw,
  Filter,
  Download
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

// Metric categories
const METRIC_CATEGORIES = {
  acquisition: { label: 'Acquisition', icon: Users, color: 'blue' },
  pipeline: { label: 'Pipeline', icon: Target, color: 'purple' },
  activation: { label: 'Activation', icon: Activity, color: 'green' },
  retention: { label: 'Retention', icon: RefreshCw, color: 'amber' },
  economics: { label: 'Unit Economics', icon: DollarSign, color: 'emerald' }
}

// RAG status colors
const RAG_COLORS = {
  green: {
    bg: 'bg-emerald-500',
    light: 'bg-emerald-500/20',
    text: 'text-emerald-400',
    border: 'border-emerald-500/30'
  },
  amber: {
    bg: 'bg-amber-500',
    light: 'bg-amber-500/20',
    text: 'text-amber-400',
    border: 'border-amber-500/30'
  },
  red: {
    bg: 'bg-red-500',
    light: 'bg-red-500/20',
    text: 'text-red-400',
    border: 'border-red-500/30'
  },
  unknown: {
    bg: 'bg-white/30',
    light: 'bg-white/10',
    text: 'text-white/40',
    border: 'border-white/20'
  }
}

// Overall RAG indicator
const RAGIndicator = ({ status, size = 'md' }) => {
  const colors = RAG_COLORS[status] || RAG_COLORS.unknown
  const sizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  }
  
  return (
    <div className={`${sizes[size]} rounded-full ${colors.bg}`} />
  )
}

// Trend indicator
const TrendIndicator = ({ trend, value }) => {
  if (!trend || trend === 'flat') {
    return <Minus className="w-4 h-4 text-white/40" />
  }
  
  const isUp = trend === 'up'
  const TrendIcon = isUp ? TrendingUp : TrendingDown
  const color = isUp ? 'text-emerald-400' : 'text-red-400'
  
  return (
    <div className={`flex items-center gap-1 ${color}`}>
      <TrendIcon className="w-4 h-4" />
      {value && <span className="text-xs">{value}%</span>}
    </div>
  )
}

// Metric card
const MetricCard = ({ metric, onClick, expanded }) => {
  const colors = RAG_COLORS[metric.rag_status] || RAG_COLORS.unknown
  const percentOfTarget = metric.target ? Math.round((metric.value / metric.target) * 100) : 0
  
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white/5 backdrop-blur-sm border rounded-xl p-4 cursor-pointer hover:border-white/20 transition-all ${colors.border}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="text-sm text-white/60">{metric.name}</div>
          <div className="text-2xl font-medium text-white mt-1">
            {metric.value?.toLocaleString()}{metric.unit === 'percentage' ? '%' : ''}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <RAGIndicator status={metric.rag_status} />
          <TrendIndicator trend={metric.trend} value={metric.trend_value} />
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs">
          <span className="text-white/40">Target: {metric.target?.toLocaleString()}</span>
          <span className={colors.text}>{percentOfTarget}%</span>
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div 
            className={`h-full ${colors.bg} rounded-full transition-all`}
            style={{ width: `${Math.min(percentOfTarget, 100)}%` }}
          />
        </div>
      </div>
      
      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-4 pt-4 border-t border-white/10"
        >
          <div className="text-xs text-white/40 space-y-2">
            <div className="flex justify-between">
              <span>Period</span>
              <span className="text-white/60">{metric.period || 'This Month'}</span>
            </div>
            <div className="flex justify-between">
              <span>Source</span>
              <span className="text-white/60">{metric.source || 'Manual'}</span>
            </div>
            <div className="flex justify-between">
              <span>Last Updated</span>
              <span className="text-white/60">{new Date(metric.updated_at).toLocaleDateString()}</span>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

// Category section
const CategorySection = ({ category, metrics, onMetricClick }) => {
  const [isOpen, setIsOpen] = useState(true)
  const config = METRIC_CATEGORIES[category] || METRIC_CATEGORIES.acquisition
  const Icon = config.icon
  
  // Calculate category RAG
  const categoryRAG = metrics.every(m => m.rag_status === 'green') ? 'green'
    : metrics.some(m => m.rag_status === 'red') ? 'red'
    : 'amber'
  
  return (
    <div className="mb-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full mb-4 group"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg bg-${config.color}-500/20 flex items-center justify-center`}>
            <Icon className={`w-4 h-4 text-${config.color}-400`} />
          </div>
          <span className="font-medium text-white">{config.label}</span>
          <RAGIndicator status={categoryRAG} size="sm" />
          <span className="text-sm text-white/40">{metrics.length} metrics</span>
        </div>
        <ChevronDown className={`w-5 h-5 text-white/40 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {metrics.map(metric => (
              <MetricCard 
                key={metric.id} 
                metric={metric}
                onClick={() => onMetricClick(metric)}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// RAG summary panel
const RAGSummary = ({ metrics }) => {
  const summary = {
    green: metrics.filter(m => m.rag_status === 'green').length,
    amber: metrics.filter(m => m.rag_status === 'amber').length,
    red: metrics.filter(m => m.rag_status === 'red').length,
    unknown: metrics.filter(m => !m.rag_status || m.rag_status === 'unknown').length
  }
  
  const total = metrics.length
  const overallRAG = summary.red > 0 ? 'red' : summary.amber > 0 ? 'amber' : summary.green > 0 ? 'green' : 'unknown'
  const overallColors = RAG_COLORS[overallRAG]
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white/5 backdrop-blur-sm border ${overallColors.border} rounded-xl p-6 mb-8`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className={`w-16 h-16 ${overallColors.light} rounded-2xl flex items-center justify-center`}>
            {overallRAG === 'green' && <CheckCircle2 className={`w-8 h-8 ${overallColors.text}`} />}
            {overallRAG === 'amber' && <AlertCircle className={`w-8 h-8 ${overallColors.text}`} />}
            {overallRAG === 'red' && <AlertTriangle className={`w-8 h-8 ${overallColors.text}`} />}
            {overallRAG === 'unknown' && <Activity className={`w-8 h-8 ${overallColors.text}`} />}
          </div>
          <div>
            <div className="text-sm text-white/60">Overall Health</div>
            <div className={`text-2xl font-medium ${overallColors.text}`}>
              {overallRAG === 'green' && 'On Track'}
              {overallRAG === 'amber' && 'Needs Attention'}
              {overallRAG === 'red' && 'Critical Issues'}
              {overallRAG === 'unknown' && 'No Data'}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="text-center">
            <div className="flex items-center gap-2">
              <RAGIndicator status="green" />
              <span className="text-2xl font-medium text-white">{summary.green}</span>
            </div>
            <div className="text-xs text-white/40">On Track</div>
          </div>
          <div className="text-center">
            <div className="flex items-center gap-2">
              <RAGIndicator status="amber" />
              <span className="text-2xl font-medium text-white">{summary.amber}</span>
            </div>
            <div className="text-xs text-white/40">Warning</div>
          </div>
          <div className="text-center">
            <div className="flex items-center gap-2">
              <RAGIndicator status="red" />
              <span className="text-2xl font-medium text-white">{summary.red}</span>
            </div>
            <div className="text-xs text-white/40">Critical</div>
          </div>
        </div>
      </div>
      
      {/* Progress bar visualization */}
      <div className="mt-6 h-2 bg-white/10 rounded-full overflow-hidden flex">
        <div 
          className="h-full bg-emerald-500 transition-all"
          style={{ width: `${(summary.green / total) * 100}%` }}
        />
        <div 
          className="h-full bg-amber-500 transition-all"
          style={{ width: `${(summary.amber / total) * 100}%` }}
        />
        <div 
          className="h-full bg-red-500 transition-all"
          style={{ width: `${(summary.red / total) * 100}%` }}
        />
      </div>
    </motion.div>
  )
}

// Add metric modal
const AddMetricModal = ({ isOpen, onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    metric_name: '',
    value: '',
    target_value: '',
    scope_type: 'business',
    unit: 'count'
  })
  
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-[#0a0a0f] border border-white/10 rounded-2xl w-full max-w-md"
      >
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-medium text-white">Record Metric</h2>
          <p className="text-sm text-white/40">Add a new metric measurement</p>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-2">Metric Name</label>
            <select
              value={formData.metric_name}
              onChange={(e) => setFormData({ ...formData, metric_name: e.target.value })}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
            >
              <option value="">Select metric...</option>
              <option value="website_traffic">Website Traffic</option>
              <option value="demo_requests">Demo Requests</option>
              <option value="demo_conversion_rate">Demo Conversion Rate</option>
              <option value="pipeline_value">Pipeline Value</option>
              <option value="win_rate">Win Rate</option>
              <option value="activation_rate">Activation Rate</option>
              <option value="monthly_churn_rate">Monthly Churn Rate</option>
              <option value="nrr">Net Revenue Retention</option>
              <option value="cac">Customer Acquisition Cost</option>
            </select>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white/60 mb-2">Current Value</label>
              <input
                type="number"
                value={formData.value}
                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                placeholder="0"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-2">Target Value</label>
              <input
                type="number"
                value={formData.target_value}
                onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                placeholder="0"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none"
              />
            </div>
          </div>
        </div>
        
        <div className="p-6 border-t border-white/10 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-white/60 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              onAdd(formData)
              onClose()
              setFormData({ metric_name: '', value: '', target_value: '', scope_type: 'business', unit: 'count' })
            }}
            className="px-6 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors"
          >
            Add Metric
          </button>
        </div>
      </motion.div>
    </div>
  )
}

// Main Matrix page
const Matrix = () => {
  const { user } = useAuth()
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [expandedMetric, setExpandedMetric] = useState(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true)
      try {
        // Mock data
        setMetrics([
          { id: '1', name: 'Website Traffic', category: 'acquisition', value: 8500, target: 10000, unit: 'visits', rag_status: 'amber', trend: 'up', trend_value: 12, updated_at: new Date() },
          { id: '2', name: 'Demo Requests', category: 'acquisition', value: 45, target: 50, unit: 'count', rag_status: 'green', trend: 'up', trend_value: 8, updated_at: new Date() },
          { id: '3', name: 'Demo Conversion', category: 'acquisition', value: 18, target: 20, unit: 'percentage', rag_status: 'amber', trend: 'flat', updated_at: new Date() },
          { id: '4', name: 'Pipeline Value', category: 'pipeline', value: 420000, target: 500000, unit: 'currency', rag_status: 'amber', trend: 'up', trend_value: 15, updated_at: new Date() },
          { id: '5', name: 'Opportunities', category: 'pipeline', value: 28, target: 30, unit: 'count', rag_status: 'green', trend: 'up', trend_value: 5, updated_at: new Date() },
          { id: '6', name: 'Win Rate', category: 'pipeline', value: 22, target: 25, unit: 'percentage', rag_status: 'amber', trend: 'down', trend_value: -3, updated_at: new Date() },
          { id: '7', name: 'Activation Rate', category: 'activation', value: 55, target: 60, unit: 'percentage', rag_status: 'amber', trend: 'up', trend_value: 10, updated_at: new Date() },
          { id: '8', name: 'Time to Value', category: 'activation', value: 4, target: 3, unit: 'days', rag_status: 'red', trend: 'flat', updated_at: new Date() },
          { id: '9', name: 'Churn Rate', category: 'retention', value: 4.5, target: 3, unit: 'percentage', rag_status: 'red', trend: 'up', trend_value: 1.5, updated_at: new Date() },
          { id: '10', name: 'NRR', category: 'retention', value: 108, target: 110, unit: 'percentage', rag_status: 'amber', trend: 'down', trend_value: -2, updated_at: new Date() },
          { id: '11', name: 'CAC', category: 'economics', value: 4200, target: 5000, unit: 'currency', rag_status: 'green', trend: 'down', trend_value: -8, updated_at: new Date() },
          { id: '12', name: 'LTV:CAC', category: 'economics', value: 4.5, target: 5, unit: 'ratio', rag_status: 'green', trend: 'up', trend_value: 5, updated_at: new Date() }
        ])
      } catch (error) {
        console.error('Error fetching metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [])

  const handleAddMetric = (data) => {
    console.log('Adding metric:', data)
    // API call to add metric
  }

  // Group metrics by category
  const groupedMetrics = Object.keys(METRIC_CATEGORIES).reduce((acc, category) => {
    acc[category] = metrics.filter(m => m.category === category)
    return acc
  }, {})

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">Matrix</h1>
          <p className="text-white/40 mt-1">
            RAG dashboard and performance tracking
          </p>
        </motion.div>

        <div className="flex items-center gap-3">
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white/60 hover:text-white hover:border-white/20 transition-all"
          >
            <Download className="w-4 h-4" />
            Export
          </motion.button>
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Metric
          </motion.button>
        </div>
      </div>

      {/* RAG Summary */}
      {!loading && <RAGSummary metrics={metrics} />}

      {/* Metrics by category */}
      {loading ? (
        <div className="space-y-8">
          {[1, 2, 3].map(i => (
            <div key={i}>
              <div className="h-8 w-48 bg-white/5 rounded animate-pulse mb-4" />
              <div className="grid grid-cols-3 gap-4">
                {[1, 2, 3].map(j => (
                  <div key={j} className="h-32 bg-white/5 rounded-xl animate-pulse" />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div>
          {Object.entries(groupedMetrics).map(([category, categoryMetrics]) => (
            categoryMetrics.length > 0 && (
              <CategorySection
                key={category}
                category={category}
                metrics={categoryMetrics}
                onMetricClick={(metric) => setExpandedMetric(expandedMetric === metric.id ? null : metric.id)}
              />
            )
          ))}
        </div>
      )}

      {/* Add Metric Modal */}
      <AnimatePresence>
        {showAddModal && (
          <AddMetricModal
            isOpen={showAddModal}
            onClose={() => setShowAddModal(false)}
            onAdd={handleAddMetric}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default Matrix
