import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
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
  ArrowRight,
  AlertCircle
} from 'lucide-react'
import { cn } from '../utils/cn'
import CohortsBuilder from '../components/CohortsBuilder'
import CohortsTagSystem from '../components/cohorts/CohortsTagSystem'

// Mock cohorts data
const mockCohorts = [
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

// Plan limits
const PLAN_LIMITS = {
  ascent: 3,
  glide: 6,
  soar: 9
};

const getUserPlan = () => {
  return localStorage.getItem('userPlan') || 'ascent';
};

const getCohortsLimit = () => {
  const plan = getUserPlan().toLowerCase();
  return PLAN_LIMITS[plan] || PLAN_LIMITS.ascent;
};

export default function CohortsManager() {
  const [cohorts, setCohorts] = useState(() => {
    // Load from localStorage on mount
    const saved = localStorage.getItem('cohorts');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Ensure it's an array
        return Array.isArray(parsed) ? parsed : mockCohorts;
      } catch (e) {
        return mockCohorts;
      }
    }
    return mockCohorts;
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showCohortsBuilder, setShowCohortsBuilder] = useState(false)
  const [selectedCohort, setSelectedCohort] = useState(null)
  const [cohortTags, setCohortTags] = useState({}) // Map of cohort ID to tags
  const [showLimitModal, setShowLimitModal] = useState(false)

  const userPlan = getUserPlan();
  const cohortsLimit = getCohortsLimit();
  const currentCohortsCount = Array.isArray(cohorts) ? cohorts.length : 0;
  const canCreateCohort = currentCohortsCount < cohortsLimit;
  const planName = userPlan.charAt(0).toUpperCase() + userPlan.slice(1);

  // Reload cohorts when builder closes
  const handleCohortsBuilderClose = () => {
    setShowCohortsBuilder(false);
    const saved = localStorage.getItem('cohorts');
    if (saved) {
      try {
        setCohorts(JSON.parse(saved));
      } catch (e) {
        // Keep current state
      }
    }
  }

  const handleCreateClick = () => {
    if (!canCreateCohort) {
      setShowLimitModal(true);
      return;
    }
    setShowCohortsBuilder(true);
  }

  const filteredCohorts = (Array.isArray(cohorts) ? cohorts : []).filter(cohort => {
    if (!cohort || !cohort.name || !cohort.description) return false;
    const matchesSearch = cohort.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cohort.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || cohort.status === filterStatus
    return matchesSearch && matchesFilter
  })

  return (
    <>
      {showCohortsBuilder && (
        <CohortsBuilder 
          onClose={handleCohortsBuilderClose}
          onboardingData={{}}
        />
      )}
      {/* Limit Reached Modal */}
      <AnimatePresence>
        {showLimitModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowLimitModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-black rounded-lg shadow-xl max-w-md w-full p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 rounded-full bg-red-50 border-2 border-red-200 flex items-center justify-center flex-shrink-0">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h2 className="font-serif text-2xl text-black mb-1">Limit Reached</h2>
                  <p className="font-sans text-sm text-neutral-600">Cohort Creation Limit</p>
                </div>
              </div>
              <div className="space-y-4 mb-6">
                <p className="font-sans text-base text-neutral-900">
                  You've reached your <strong>{planName}</strong> plan limit of <strong>{cohortsLimit} cohorts</strong>.
                </p>
                <p className="font-sans text-sm text-neutral-600">
                  Upgrade to <strong>{userPlan === 'ascent' ? 'Glide' : 'Soar'}</strong> to create more cohorts and unlock additional features.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowLimitModal(false)}
                  className="flex-1 border-2 border-black text-black px-6 py-3 text-sm font-semibold uppercase tracking-[0.1em] hover:bg-black hover:text-white transition-colors"
                >
                  Close
                </button>
                <Link
                  to="/settings?tab=pricing"
                  onClick={() => setShowLimitModal(false)}
                  className="flex-1 bg-black text-white px-6 py-3 text-sm font-semibold uppercase tracking-[0.1em] hover:bg-neutral-800 transition-colors text-center"
                >
                  Upgrade Plan
                </Link>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      <div className="space-y-8 animate-fade-in">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full border border-neutral-200 bg-white flex items-center justify-center">
                <Users className="w-8 h-8 text-neutral-900" />
              </div>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="micro-label tracking-[0.5em]">Audience Archive</span>
                  <span className="h-px w-16 bg-neutral-200" />
                </div>
                <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
                  Curate the Lineup
                </h1>
                <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
                  Profiles, districts, and signature buyers in one gallery
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-neutral-700">
                <span className="font-bold">{planName}</span> Plan
              </p>
              <p className="text-xs text-neutral-500 mt-1">
                {currentCohortsCount} / {cohortsLimit} cohorts
              </p>
              <div className="w-24 h-2 bg-neutral-200 rounded-full mt-2 overflow-hidden">
                <div 
                  className="h-full bg-black transition-all duration-500"
                  style={{ width: `${Math.min((currentCohortsCount / cohortsLimit) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total cohorts', value: currentCohortsCount, icon: Users, color: 'primary' },
          { label: 'Active', value: (Array.isArray(cohorts) ? cohorts : []).filter(i => i && i.status === 'active').length, icon: CheckCircle2, color: 'accent' },
          { label: 'Recommended', value: (Array.isArray(cohorts) ? cohorts : []).filter(i => i && i.recommended).length, icon: Sparkles, color: 'primary' },
          { label: 'Avg Match Score', value: Array.isArray(cohorts) && cohorts.length > 0 ? Math.round(cohorts.reduce((acc, i) => acc + (i?.matchScore || 0), 0) / cohorts.length) : 0, icon: TrendingUp, color: 'accent' },
        ].map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="runway-card p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={cn(
                  "w-12 h-12 border-2 border-neutral-200 flex items-center justify-center",
                  stat.color === 'primary' ? "bg-neutral-100 text-neutral-900" : "bg-neutral-100 text-neutral-900"
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
              placeholder="Search cohorts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="pl-12 pr-8 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent appearance-none"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>
        <motion.button
          whileHover={canCreateCohort ? { scale: 1.02 } : {}}
          whileTap={canCreateCohort ? { scale: 0.98 } : {}}
          onClick={handleCreateClick}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-colors shadow-lg ${
            canCreateCohort
              ? 'bg-neutral-900 text-white hover:bg-neutral-800 shadow-neutral-900/20'
              : 'bg-neutral-300 text-neutral-500 cursor-not-allowed shadow-neutral-300/20'
          }`}
        >
          <Plus className="w-5 h-5" />
          Create cohort
        </motion.button>
      </div>

      {/* Cohorts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <AnimatePresence>
          {filteredCohorts.map((cohort, index) => (
            <motion.div
              key={cohort.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: index * 0.05 }}
              className="runway-card p-6 hover:shadow-xl transition-all cursor-pointer group"
              onClick={() => setSelectedCohort(cohort)}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-bold text-neutral-900">{cohort.name}</h3>
                    {cohort.recommended && (
                      <span className="px-2 py-1 text-xs font-medium bg-neutral-100 text-neutral-900 rounded-lg">
                        Recommended
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-neutral-600 mb-3">{cohort.description}</p>
                </div>
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  cohort.status === 'active' ? "bg-green-500" : "bg-yellow-500"
                )} />
              </div>

              {/* Match Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-neutral-700">Match Score</span>
                  <span className="text-lg font-bold text-neutral-900">{cohort.matchScore}%</span>
                </div>
                <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${cohort.matchScore}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className="h-full bg-gradient-to-r from-neutral-700 to-neutral-900 rounded-full"
                  />
                </div>
              </div>

              {/* Tags */}
              {cohortTags[cohort.id] && cohortTags[cohort.id].length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {cohortTags[cohort.id].slice(0, 5).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 text-[10px] font-medium bg-neutral-100 text-neutral-700 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                    {cohortTags[cohort.id].length > 5 && (
                      <span className="px-2 py-0.5 text-[10px] font-medium text-neutral-500">
                        +{cohortTags[cohort.id].length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Attributes */}
              <div className="space-y-2 mb-4">
                {Object.entries(cohort.attributes).slice(0, 3).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-2 text-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-neutral-700" />
                    <span className="text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}:</span>
                    <span className="text-neutral-900 font-medium">{value}</span>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-4 border-t border-neutral-200">
                <button 
                  onClick={() => setSelectedCohort(cohort)}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-all duration-180"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                <Link
                  to={`/cohorts/${cohort.id}/moves`}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-neutral-900 hover:bg-neutral-50 rounded-lg transition-all duration-180"
                >
                  View Moves
                  <ArrowRight className="w-4 h-4" />
                </Link>
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
              className="runway-card p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <h2 className="text-2xl font-display font-bold mb-6">
                {selectedCohort ? 'Edit cohort' : 'Create New cohort'}
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Cohort Name</label>
                  <input
                    type="text"
                    placeholder="e.g., Enterprise SaaS CTOs"
                    defaultValue={selectedCohort?.name}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 transition-all duration-180"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Description</label>
                  <textarea
                    rows={3}
                    placeholder="Describe your ideal customer profile..."
                    defaultValue={selectedCohort?.description}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none transition-all duration-180"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Tags</label>
                  <CohortsTagSystem
                    selectedTags={cohortTags[selectedCohort?.id] || []}
                    onChange={(tags) => setCohortTags(prev => ({ ...prev, [selectedCohort?.id || 'new']: tags }))}
                    maxTags={20}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">Company Size</label>
                    <input
                      type="text"
                      placeholder="e.g., 100-500"
                      className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">Industry</label>
                    <input
                      type="text"
                      placeholder="e.g., SaaS"
                      className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
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
                    className="flex-1 px-6 py-3 rounded-xl bg-neutral-900 text-white font-medium hover:bg-neutral-800 transition-colors"
                  >
                    Create cohort
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      </div>
    </>
  )
}

