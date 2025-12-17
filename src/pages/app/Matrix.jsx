import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
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

import useRaptorflowStore from '../../store/raptorflowStore'

import { Modal } from '@/components/system/Modal'
import { HairlineTable } from '@/components/system/HairlineTable'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ExecutionPanel from '@/pages/app/ExecutionPanel'

// Metric categories
const METRIC_CATEGORIES = {
  acquisition: { label: 'Acquisition', icon: Users, color: 'blue' },
  pipeline: { label: 'Pipeline', icon: Target, color: 'purple' },
  activation: { label: 'Activation', icon: Activity, color: 'green' },
  retention: { label: 'Retention', icon: RefreshCw, color: 'amber' },
  economics: { label: 'Unit Economics', icon: DollarSign, color: 'emerald' }
}

// RAG status colors - High contrast for readability
const RAG_COLORS = {
  green: {
    bg: 'bg-emerald-500',
    light: 'bg-emerald-50',
    text: 'text-emerald-600',
    border: 'border-emerald-200'
  },
  amber: {
    bg: 'bg-amber-500',
    light: 'bg-amber-50',
    text: 'text-amber-600',
    border: 'border-amber-200'
  },
  red: {
    bg: 'bg-red-500',
    light: 'bg-red-50',
    text: 'text-red-600',
    border: 'border-red-200'
  },
  unknown: {
    bg: 'bg-gray-400',
    light: 'bg-gray-50',
    text: 'text-gray-500',
    border: 'border-gray-200'
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
    return <Minus className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
  }

  const isUp = trend === 'up'
  const TrendIcon = isUp ? TrendingUp : TrendingDown
  const color = 'text-primary'

  return (
    <div className={`flex items-center gap-1 ${color}`}>
      <TrendIcon className="w-4 h-4" strokeWidth={1.5} />
      {value && <span className="text-xs">{value}%</span>}
    </div>
  )
}

// Metric card
const MetricCard = ({ metric, onClick, expanded }) => {
  const colors = RAG_COLORS[metric.rag_status] || RAG_COLORS.unknown
  const percentOfTarget = metric.target ? Math.round((metric.value / metric.target) * 100) : 0
  const progressBar = metric.rag_status === 'green' ? 'bg-ink-300' : 'bg-primary'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-card border rounded-xl p-4 cursor-pointer hover:border-border-dark transition-editorial ${colors.border}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="text-sm text-ink-400">{metric.name}</div>
          <div className="text-2xl font-medium text-ink mt-1">
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
          <span className="text-ink-400">Target: {metric.target?.toLocaleString()}</span>
          <span className={colors.text}>{percentOfTarget}%</span>
        </div>
        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full ${progressBar} rounded-full transition-all`}
            style={{ width: `${Math.min(percentOfTarget, 100)}%` }}
          />
        </div>
      </div>

      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-4 pt-4 border-t border-border"
        >
          <div className="text-xs text-ink-400 space-y-2">
            <div className="flex justify-between">
              <span>Period</span>
              <span className="text-ink">{metric.period || 'This Month'}</span>
            </div>
            <div className="flex justify-between">
              <span>Source</span>
              <span className="text-ink">{metric.source || 'Manual'}</span>
            </div>
            <div className="flex justify-between">
              <span>Last Updated</span>
              <span className="text-ink">{new Date(metric.updated_at).toLocaleDateString()}</span>
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
          <div className="w-8 h-8 rounded-lg bg-muted border border-border flex items-center justify-center">
            <Icon className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
          </div>
          <span className="font-medium text-ink">{config.label}</span>
          <RAGIndicator status={categoryRAG} size="sm" />
          <span className="text-sm text-ink-400">{metrics.length} metrics</span>
        </div>
        <ChevronDown className={`w-5 h-5 text-ink-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} strokeWidth={1.5} />
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

// RAG summary panel - Premium design
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

  const statusText = {
    green: 'On Track',
    amber: 'Needs Attention',
    red: 'Critical Issues',
    unknown: 'No Data'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="bg-card border border-border rounded-2xl p-6 shadow-sm"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        {/* Overall status */}
        <div className="flex items-center gap-4">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className={`w-14 h-14 ${overallColors.light} rounded-2xl flex items-center justify-center`}
          >
            {overallRAG === 'green' && <CheckCircle2 className={`w-7 h-7 ${overallColors.text}`} strokeWidth={1.5} />}
            {overallRAG === 'amber' && <AlertCircle className={`w-7 h-7 ${overallColors.text}`} strokeWidth={1.5} />}
            {overallRAG === 'red' && <AlertTriangle className={`w-7 h-7 ${overallColors.text}`} strokeWidth={1.5} />}
            {overallRAG === 'unknown' && <Activity className={`w-7 h-7 ${overallColors.text}`} strokeWidth={1.5} />}
          </motion.div>
          <div>
            <div className="text-sm text-muted-foreground">Overall Health</div>
            <div className={`text-xl font-semibold ${overallColors.text}`}>
              {statusText[overallRAG]}
            </div>
          </div>
        </div>

        {/* Stats cards */}
        <div className="flex items-center gap-4">
          {[
            { status: 'green', label: 'On track', count: summary.green },
            { status: 'amber', label: 'Warning', count: summary.amber },
            { status: 'red', label: 'Critical', count: summary.red }
          ].map(({ status, label, count }, i) => (
            <motion.div
              key={status}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
              className="flex items-center gap-2 px-4 py-2 bg-muted/50 rounded-xl"
            >
              <div className={`w-2.5 h-2.5 rounded-full ${RAG_COLORS[status].bg}`} />
              <span className="text-xl font-semibold text-foreground">{count}</span>
              <span className="text-xs text-muted-foreground hidden sm:inline">{label}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Animated progress bar */}
      <div className="mt-6">
        <div className="h-2 bg-muted rounded-full overflow-hidden flex">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(summary.green / total) * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="h-full bg-emerald-500"
          />
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(summary.amber / total) * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut', delay: 0.1 }}
            className="h-full bg-amber-500"
          />
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(summary.red / total) * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
            className="h-full bg-red-500"
          />
        </div>
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

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose()
      }}
      title="Record metric"
      description="Add a new metric measurement."
      contentClassName="max-w-md"
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-muted-foreground mb-2">Metric</label>
          <select
            value={formData.metric_name}
            onChange={(e) => setFormData({ ...formData, metric_name: e.target.value })}
            className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="">Select metric…</option>
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
            <label className="block text-sm text-muted-foreground mb-2">Current</label>
            <input
              type="number"
              value={formData.value}
              onChange={(e) => setFormData({ ...formData, value: e.target.value })}
              placeholder="0"
              className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Target</label>
            <input
              type="number"
              value={formData.target_value}
              onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
              placeholder="0"
              className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
        </div>

        <div className="pt-2 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-md border border-border bg-transparent text-foreground hover:bg-muted transition-editorial"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => {
              onAdd(formData)
              onClose()
              setFormData({
                metric_name: '',
                value: '',
                target_value: '',
                scope_type: 'business',
                unit: 'count'
              })
            }}
            className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:opacity-95 transition-editorial"
          >
            Add metric
          </button>
        </div>
      </div>
    </Modal>
  )
}

// Main Matrix page
const Matrix = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { createSignal } = useRaptorflowStore()
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [expandedMetric, setExpandedMetric] = useState(null)
  const [activeTab, setActiveTab] = useState('war_room')

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

  const flattenedMetrics = Object.entries(groupedMetrics).flatMap(([category, list]) =>
    list.map((m) => ({ ...m, category }))
  )

  const categoryLabel = (cat) => (METRIC_CATEGORIES[cat]?.label ? METRIC_CATEGORIES[cat].label : cat)

  // Get time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const userName = user?.user_metadata?.full_name?.split(' ')?.[0] || 'there'

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Premium Hero Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-card via-card to-muted border border-border p-8"
      >
        {/* Decorative background elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-primary/3 rounded-full blur-2xl translate-y-1/2 -translate-x-1/2" />

        <div className="relative flex items-start justify-between">
          <div className="space-y-2">
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-sm text-muted-foreground"
            >
              {getGreeting()}, <span className="text-foreground font-medium">{userName}</span>
            </motion.p>
            <motion.h1
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 }}
              className="font-serif text-3xl md:text-4xl text-foreground"
            >
              Command Matrix
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-muted-foreground max-w-md"
            >
              Your marketing performance at a glance. Track KPIs, spot trends, and take action.
            </motion.p>
          </div>

          <div className="flex items-center gap-3">
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-2 px-4 py-2.5 bg-background border border-border rounded-xl text-muted-foreground hover:text-foreground hover:border-border-dark transition-all duration-200"
            >
              <Download className="w-4 h-4" strokeWidth={1.5} />
              <span className="hidden sm:inline">Export</span>
            </motion.button>
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.05 }}
              whileHover={{ scale: 1.02, boxShadow: '0 4px 20px rgba(255, 177, 98, 0.25)' }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all duration-200"
            >
              <Plus className="w-4 h-4" strokeWidth={2} />
              Add metric
            </motion.button>
          </div>
        </div>
      </motion.div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="war_room">War Room</TabsTrigger>
          <TabsTrigger value="execution">Execution</TabsTrigger>
        </TabsList>

        <TabsContent value="war_room" className="mt-6 space-y-8">
          {/* RAG Summary */}
          {!loading && <RAGSummary metrics={metrics} />}

          {/* Metrics table */}
          <HairlineTable
            loading={loading}
            data={flattenedMetrics}
            onRowClick={(row) => setExpandedMetric(expandedMetric === row.id ? null : row.id)}
            emptyTitle="No metrics yet"
            emptyDescription="Add your first metric to start tracking performance."
            emptyAction="Add metric"
            onEmptyAction={() => setShowAddModal(true)}
            columns={[
              {
                key: 'name',
                header: 'Metric',
                render: (row) => (
                  <div>
                    <div className="text-ink">{row.name}</div>
                    <div className="text-xs text-ink-400">{categoryLabel(row.category)}</div>
                  </div>
                )
              },
              {
                key: 'value',
                header: 'Current',
                align: 'right',
                render: (row) => (
                  <span className="font-mono text-ink">
                    {row.value?.toLocaleString()}
                    {row.unit === 'percentage' ? '%' : ''}
                  </span>
                )
              },
              {
                key: 'target',
                header: 'Target',
                align: 'right',
                render: (row) => (
                  <span className="font-mono text-ink-400">{row.target?.toLocaleString() ?? '-'}</span>
                )
              },
              {
                key: 'rag_status',
                header: 'Signal',
                align: 'right',
                render: (row) => (
                  <div className="inline-flex items-center justify-end gap-2">
                    <RAGIndicator status={row.rag_status} />
                    <span className="text-xs text-ink-400">{row.rag_status || 'unknown'}</span>
                  </div>
                )
              },
              {
                key: 'trend',
                header: 'Trend',
                align: 'right',
                render: (row) => (
                  <div className="inline-flex items-center justify-end">
                    <TrendIndicator trend={row.trend} value={row.trend_value} />
                  </div>
                )
              }
            ]}
          />
        </TabsContent>

        <TabsContent value="execution" className="mt-6">
          <ExecutionPanel />
        </TabsContent>
      </Tabs>

      {expandedMetric ? (
        <div className="mt-4 rounded-card border border-border bg-card p-4">
          {(() => {
            const metric = metrics.find((m) => m.id === expandedMetric)
            if (!metric) return null
            return (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-xs text-ink-400">Period</div>
                  <div className="text-ink">{metric.period || 'This Month'}</div>
                </div>
                <div>
                  <div className="text-xs text-ink-400">Source</div>
                  <div className="text-ink">{metric.source || 'Manual'}</div>
                </div>
                <div>
                  <div className="text-xs text-ink-400">Last updated</div>
                  <div className="text-ink">{new Date(metric.updated_at).toLocaleDateString()}</div>
                </div>

                <div className="md:col-span-3 pt-2 flex items-center justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      const created = createSignal?.({
                        title: `${metric.name}: investigate leverage`,
                        statement: `This metric is off-track. Identify the bottleneck and mechanism before testing.`,
                        zone: metric.category || 'signal',
                        status: 'triage',
                        effort: 'medium',
                        primaryMetric: { id: metric.id, name: metric.name, unit: metric.unit },
                        baseline: {
                          value: metric.value,
                          target: metric.target,
                          unit: metric.unit,
                          period: metric.period || 'This Month',
                        },
                        evidenceRefs: [{ type: 'matrix_metric', id: metric.id, label: metric.name }],
                        ice: {
                          impact: metric.rag_status === 'red' ? 4 : 3,
                          confidence: 2,
                          ease: 2,
                        },
                      })
                      if (created?.id) navigate(`/app/signals/${created.id}`)
                    }}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
                  >
                    <Plus className="w-4 h-4" strokeWidth={1.5} />
                    Create Signal
                  </button>
                </div>
              </div>
            )
          })()}
        </div>
      ) : null}

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
