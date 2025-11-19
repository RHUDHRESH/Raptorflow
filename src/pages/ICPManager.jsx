import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Users, 
  Plus, 
  Search, 
  Filter, 
  Sparkles, 
  TrendingUp, 
  Target,
  CheckCircle2,
  XCircle,
  Edit2,
  Trash2,
  ArrowRight
} from 'lucide-react'
import { cn } from '../utils/cn'

// Mock ICP data
const mockICPs = [
  {
    id: 1,
    name: 'Enterprise SaaS CTOs',
    description: 'Chief Technology Officers at SaaS companies with 100-500 employees',
    matchScore: 94,
    status: 'active',
    attributes: {
      companySize: '100-500',
      industry: 'SaaS',
      role: 'CTO',
      budget: '$50k-$200k',
      painPoints: ['Scalability', 'Security', 'Integration'],
    },
    recommended: true,
  },
  {
    id: 2,
    name: 'E-commerce Founders',
    description: 'Founders of e-commerce businesses generating $1M-$10M annually',
    matchScore: 87,
    status: 'active',
    attributes: {
      companySize: '10-50',
      industry: 'E-commerce',
      role: 'Founder',
      budget: '$20k-$100k',
      painPoints: ['Conversion', 'Retention', 'Logistics'],
    },
    recommended: true,
  },
  {
    id: 3,
    name: 'Healthcare Administrators',
    description: 'Administrators at healthcare facilities managing patient data',
    matchScore: 72,
    status: 'draft',
    attributes: {
      companySize: '50-200',
      industry: 'Healthcare',
      role: 'Administrator',
      budget: '$30k-$150k',
      painPoints: ['Compliance', 'Efficiency', 'Data Management'],
    },
    recommended: false,
  },
]

export default function ICPManager() {
  const [icps, setICPs] = useState(mockICPs)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedICP, setSelectedICP] = useState(null)

  const filteredICPs = icps.filter(icp => {
    const matchesSearch = icp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      icp.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || icp.status === filterStatus
    return matchesSearch && matchesFilter
  })

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 p-12 text-white"
      >
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
              <Users className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-4xl font-display font-bold mb-2">ICP Manager</h1>
              <p className="text-primary-100 text-lg">
                Define and manage your Ideal Customer Profiles with AI-powered recommendations
              </p>
            </div>
          </div>
        </div>
        
        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-accent-500/20 rounded-full blur-3xl" />
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total ICPs', value: icps.length, icon: Users, color: 'primary' },
          { label: 'Active', value: icps.filter(i => i.status === 'active').length, icon: CheckCircle2, color: 'accent' },
          { label: 'Recommended', value: icps.filter(i => i.recommended).length, icon: Sparkles, color: 'primary' },
          { label: 'Avg Match Score', value: Math.round(icps.reduce((acc, i) => acc + i.matchScore, 0) / icps.length), icon: TrendingUp, color: 'accent' },
        ].map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center",
                  stat.color === 'primary' ? "bg-primary-100 text-primary-600" : "bg-accent-100 text-accent-600"
                )}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
              <div className="text-3xl font-bold text-neutral-900 mb-1">{stat.value}</div>
              <div className="text-sm text-neutral-600">{stat.label}</div>
            </motion.div>
          )
        })}
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex-1 flex gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              placeholder="Search ICPs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="pl-12 pr-8 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/20"
        >
          <Plus className="w-5 h-5" />
          Create ICP
        </motion.button>
      </div>

      {/* ICP Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <AnimatePresence>
          {filteredICPs.map((icp, index) => (
            <motion.div
              key={icp.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: index * 0.05 }}
              className="glass rounded-2xl p-6 hover:shadow-xl transition-all cursor-pointer group"
              onClick={() => setSelectedICP(icp)}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-bold text-neutral-900">{icp.name}</h3>
                    {icp.recommended && (
                      <span className="px-2 py-1 text-xs font-medium bg-accent-100 text-accent-700 rounded-lg">
                        Recommended
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-neutral-600 mb-3">{icp.description}</p>
                </div>
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  icp.status === 'active' ? "bg-green-500" : "bg-yellow-500"
                )} />
              </div>

              {/* Match Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-neutral-700">Match Score</span>
                  <span className="text-lg font-bold text-primary-600">{icp.matchScore}%</span>
                </div>
                <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${icp.matchScore}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
                  />
                </div>
              </div>

              {/* Attributes */}
              <div className="space-y-2 mb-4">
                {Object.entries(icp.attributes).slice(0, 3).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-2 text-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                    <span className="text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}:</span>
                    <span className="text-neutral-900 font-medium">{value}</span>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-4 border-t border-neutral-200">
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors">
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                  View
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Create Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <h2 className="text-2xl font-display font-bold mb-6">Create New ICP</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">ICP Name</label>
                  <input
                    type="text"
                    placeholder="e.g., Enterprise SaaS CTOs"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Description</label>
                  <textarea
                    rows={3}
                    placeholder="Describe your ideal customer profile..."
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">Company Size</label>
                    <input
                      type="text"
                      placeholder="e.g., 100-500"
                      className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">Industry</label>
                    <input
                      type="text"
                      placeholder="e.g., SaaS"
                      className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
                <div className="flex gap-4 pt-4">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-6 py-3 rounded-xl border border-neutral-200 text-neutral-700 font-medium hover:bg-neutral-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-6 py-3 rounded-xl bg-primary-600 text-white font-medium hover:bg-primary-700 transition-colors"
                  >
                    Create ICP
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

