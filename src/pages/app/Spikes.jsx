import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Plus, 
  Zap, 
  Target, 
  Users, 
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  DollarSign,
  Calendar,
  Play,
  Pause,
  ChevronRight,
  ArrowRight,
  Shield,
  Rocket,
  Activity,
  BarChart3
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

// Phase colors and labels
const PHASE_CONFIG = {
  setup: { label: 'Setup', color: 'amber', icon: Target },
  week_1: { label: 'Week 1', color: 'blue', icon: Rocket },
  week_2: { label: 'Week 2', color: 'blue', icon: Activity },
  week_3: { label: 'Week 3', color: 'blue', icon: TrendingUp },
  week_4: { label: 'Week 4', color: 'emerald', icon: CheckCircle2 },
  review: { label: 'Review', color: 'purple', icon: BarChart3 }
}

// Status configuration
const STATUS_CONFIG = {
  draft: { label: 'Draft', color: 'bg-white/10 text-white/60' },
  setup: { label: 'In Setup', color: 'bg-amber-500/20 text-amber-400' },
  active: { label: 'Active', color: 'bg-emerald-500/20 text-emerald-400' },
  paused: { label: 'Paused', color: 'bg-amber-500/20 text-amber-400' },
  completed: { label: 'Completed', color: 'bg-purple-500/20 text-purple-400' },
  cancelled: { label: 'Cancelled', color: 'bg-red-500/20 text-red-400' }
}

// RAG colors
const RAG_COLORS = {
  green: 'bg-emerald-500',
  amber: 'bg-amber-500',
  red: 'bg-red-500',
  unknown: 'bg-white/30'
}

// Spike card component
const SpikeCard = ({ spike, onClick }) => {
  const statusConfig = STATUS_CONFIG[spike.status] || STATUS_CONFIG.draft
  const currentWeek = Math.min(4, Math.floor((Date.now() - new Date(spike.start_date).getTime()) / (7 * 24 * 60 * 60 * 1000)) + 1)
  const progress = spike.status === 'completed' ? 100 : Math.min(100, (currentWeek / 4) * 100)
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      onClick={onClick}
      className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 cursor-pointer hover:border-white/20 transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-xl flex items-center justify-center">
            <Zap className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-white">{spike.name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={`px-2 py-0.5 rounded text-xs ${statusConfig.color}`}>
                {statusConfig.label}
              </span>
              {spike.current_phase && (
                <span className="text-xs text-white/40">
                  {PHASE_CONFIG[spike.current_phase]?.label || spike.current_phase}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className={`w-3 h-3 rounded-full ${RAG_COLORS[spike.rag_status] || RAG_COLORS.unknown}`} />
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-white/40 mb-1">
          <span>Week {currentWeek} of 4</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden flex">
          {[1, 2, 3, 4].map(week => (
            <div 
              key={week}
              className={`flex-1 ${week <= currentWeek ? 'bg-amber-500' : 'bg-white/5'} ${week < 4 ? 'border-r border-white/10' : ''}`}
            />
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/10">
        <div>
          <div className="text-xs text-white/40">Target ARR</div>
          <div className="text-lg font-medium text-white">
            ₹{(spike.targets?.target_arr_increase / 100000)?.toFixed(1)}L
          </div>
        </div>
        <div>
          <div className="text-xs text-white/40">Pipeline</div>
          <div className="text-lg font-medium text-white">
            ₹{(spike.pipeline_value / 100000)?.toFixed(1) || 0}L
          </div>
        </div>
        <div>
          <div className="text-xs text-white/40">Moves</div>
          <div className="text-lg font-medium text-white">{spike.move_ids?.length || 0}</div>
        </div>
      </div>

      {/* Date range */}
      {spike.start_date && (
        <div className="flex items-center gap-2 mt-4 text-xs text-white/40">
          <Calendar className="w-3 h-3" />
          {new Date(spike.start_date).toLocaleDateString()} → {new Date(spike.end_date).toLocaleDateString()}
        </div>
      )}
    </motion.div>
  )
}

// Stats card
const StatsCard = ({ icon: Icon, label, value, trend, color = 'white' }) => (
  <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
    <div className="flex items-center gap-3">
      <div className={`w-10 h-10 bg-${color}-500/20 rounded-lg flex items-center justify-center`}>
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
      <div>
        <div className="text-2xl font-medium text-white">{value}</div>
        <div className="text-sm text-white/40">{label}</div>
      </div>
    </div>
  </div>
)

// Main Spikes page
const Spikes = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [spikes, setSpikes] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    const fetchSpikes = async () => {
      setLoading(true)
      try {
        // Start empty - user creates their own spikes
        setSpikes([])
      } catch (error) {
        console.error('Error fetching spikes:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSpikes()
  }, [])

  const filteredSpikes = filter === 'all' 
    ? spikes 
    : spikes.filter(s => s.status === filter)

  // Stats
  const stats = {
    total: spikes.length,
    active: spikes.filter(s => s.status === 'active').length,
    totalPipeline: spikes.reduce((sum, s) => sum + (s.pipeline_value || 0), 0),
    totalTargetARR: spikes.reduce((sum, s) => sum + (s.targets?.target_arr_increase || 0), 0)
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-xl flex items-center justify-center">
              <Zap className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h1 className="text-3xl font-light text-white">Spikes</h1>
              <p className="text-white/40">30-day GTM command implants</p>
            </div>
          </div>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={() => navigate('/app/spikes/new')}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          Launch Spike
        </motion.button>
      </div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-4 gap-4 mb-8"
      >
        <StatsCard icon={Zap} label="Total Spikes" value={stats.total} color="amber" />
        <StatsCard icon={Play} label="Active" value={stats.active} color="emerald" />
        <StatsCard icon={TrendingUp} label="Total Pipeline" value={`₹${(stats.totalPipeline / 100000).toFixed(1)}L`} color="blue" />
        <StatsCard icon={Target} label="Target ARR" value={`₹${(stats.totalTargetARR / 100000).toFixed(1)}L`} color="purple" />
      </motion.div>

      {/* Info banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-xl p-6 mb-8"
      >
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <Rocket className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-white mb-1">The RaptorFlow Command Spike</h3>
            <p className="text-white/60 text-sm mb-3">
              A 30-day focused GTM implant that gives you clarity, control, and protection. 
              No wasteful spending. No guessing. Just execution with guardrails.
            </p>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2 text-amber-400">
                <Target className="w-4 h-4" />
                Focused strategy
              </div>
              <div className="flex items-center gap-2 text-amber-400">
                <Shield className="w-4 h-4" />
                Kill switch protection
              </div>
              <div className="flex items-center gap-2 text-amber-400">
                <BarChart3 className="w-4 h-4" />
                Weekly RAG reviews
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex items-center gap-2 mb-6"
      >
        {['all', 'active', 'setup', 'completed'].map((status) => (
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

      {/* Spikes grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-64 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : filteredSpikes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredSpikes.map((spike) => (
            <SpikeCard
              key={spike.id}
              spike={spike}
              onClick={() => navigate(`/app/spikes/${spike.id}`)}
            />
          ))}
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <div className="w-16 h-16 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Zap className="w-8 h-8 text-amber-400" />
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No spikes yet</h3>
          <p className="text-white/40 mb-6">Launch your first 30-day GTM spike</p>
          <button
            onClick={() => navigate('/app/spikes/new')}
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            Launch Spike
          </button>
        </motion.div>
      )}
    </div>
  )
}

export default Spikes

