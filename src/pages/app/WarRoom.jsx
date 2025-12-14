import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Target, 
  Zap, 
  Users, 
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Activity,
  Calendar,
  Play,
  Pause,
  ChevronRight,
  Shield,
  Clock,
  BarChart3,
  Layers,
  ArrowUpRight
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

// Protocol badges
const PROTOCOL_COLORS = {
  A_AUTHORITY_BLITZ: 'purple',
  B_TRUST_ANCHOR: 'blue',
  C_COST_OF_INACTION: 'amber',
  D_HABIT_HARDCODE: 'green',
  E_ENTERPRISE_WEDGE: 'cyan',
  F_CHURN_INTERCEPT: 'red'
}

// RAG Status badge
const RAGBadge = ({ status, size = 'sm' }) => {
  const config = {
    green: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', label: 'On Track' },
    amber: { bg: 'bg-amber-500/20', text: 'text-amber-400', label: 'Warning' },
    red: { bg: 'bg-red-500/20', text: 'text-red-400', label: 'Critical' },
    unknown: { bg: 'bg-white/10', text: 'text-white/40', label: 'Unknown' }
  }
  
  const { bg, text, label } = config[status] || config.unknown
  
  return (
    <span className={`px-2 py-0.5 rounded ${size === 'lg' ? 'text-sm' : 'text-xs'} ${bg} ${text}`}>
      {label}
    </span>
  )
}

// Strategy snapshot card
const StrategySnapshot = ({ campaigns, moves, icps }) => {
  const activeCampaigns = campaigns.filter(c => c.status === 'active').length
  const activeMoves = moves.filter(m => m.status === 'running').length
  const selectedICPs = icps.filter(i => i.is_selected).length
  
  // Goal distribution
  const goalDist = {
    velocity: campaigns.filter(c => c.goal === 'velocity').length,
    efficiency: campaigns.filter(c => c.goal === 'efficiency').length,
    penetration: campaigns.filter(c => c.goal === 'penetration').length
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6"
    >
      <h3 className="text-lg font-medium text-white mb-4">Strategy Snapshot</h3>
      
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <div className="text-3xl font-medium text-white">{activeCampaigns}</div>
          <div className="text-sm text-white/40">Active Campaigns</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-medium text-white">{activeMoves}</div>
          <div className="text-sm text-white/40">Running Moves</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-medium text-white">{selectedICPs}</div>
          <div className="text-sm text-white/40">Target ICPs</div>
        </div>
      </div>
      
      {/* Goal distribution */}
      <div>
        <div className="text-sm text-white/60 mb-2">Goal Distribution</div>
        <div className="flex gap-2">
          {goalDist.velocity > 0 && (
            <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
              Velocity: {goalDist.velocity}
            </span>
          )}
          {goalDist.efficiency > 0 && (
            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
              Efficiency: {goalDist.efficiency}
            </span>
          )}
          {goalDist.penetration > 0 && (
            <span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded text-xs">
              Penetration: {goalDist.penetration}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  )
}

// Campaign board item
const CampaignBoardItem = ({ campaign, onClick }) => {
  const statusColors = {
    draft: 'border-white/10',
    planned: 'border-blue-500/30',
    active: 'border-emerald-500/30',
    paused: 'border-amber-500/30',
    completed: 'border-purple-500/30'
  }
  
  return (
    <motion.div
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={`bg-white/5 border ${statusColors[campaign.status]} rounded-lg p-4 cursor-pointer hover:border-white/20 transition-all`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="font-medium text-white text-sm">{campaign.name}</div>
        <RAGBadge status={campaign.rag_status} />
      </div>
      <div className="flex items-center gap-2 text-xs text-white/40">
        <span>{campaign.goal}</span>
        <span>•</span>
        <span>{campaign.icp_ids?.length || 0} ICPs</span>
        <span>•</span>
        <span>{campaign.move_count || 0} moves</span>
      </div>
    </motion.div>
  )
}

// Kill switch panel
const KillSwitchPanel = ({ guardrails }) => {
  const triggeredCount = guardrails.filter(g => g.is_triggered).length
  const activeCount = guardrails.filter(g => g.is_active).length
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className={`bg-white/5 backdrop-blur-sm border rounded-xl p-6 ${
        triggeredCount > 0 ? 'border-red-500/30' : 'border-white/10'
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield className={`w-5 h-5 ${triggeredCount > 0 ? 'text-red-400' : 'text-white/60'}`} />
          <h3 className="text-lg font-medium text-white">Kill Switch</h3>
        </div>
        {triggeredCount > 0 && (
          <span className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded text-xs">
            {triggeredCount} Triggered
          </span>
        )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white/5 rounded-lg p-3">
          <div className="text-2xl font-medium text-white">{activeCount}</div>
          <div className="text-xs text-white/40">Active Rules</div>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className={`text-2xl font-medium ${triggeredCount > 0 ? 'text-red-400' : 'text-white'}`}>
            {triggeredCount}
          </div>
          <div className="text-xs text-white/40">Triggered</div>
        </div>
      </div>
      
      {/* Recent triggers */}
      {triggeredCount > 0 && (
        <div className="space-y-2">
          {guardrails.filter(g => g.is_triggered).slice(0, 3).map(g => (
            <div key={g.id} className="flex items-center justify-between p-2 bg-red-500/10 rounded-lg">
              <span className="text-sm text-red-400">{g.name}</span>
              <AlertTriangle className="w-4 h-4 text-red-400" />
            </div>
          ))}
        </div>
      )}
      
      {triggeredCount === 0 && (
        <div className="flex items-center gap-2 text-emerald-400 text-sm">
          <CheckCircle2 className="w-4 h-4" />
          All systems nominal
        </div>
      )}
    </motion.div>
  )
}

// Task queue
const TaskQueue = ({ tasks }) => {
  const pendingTasks = tasks.filter(t => t.status === 'pending')
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress')
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 }}
      className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-white">Task Queue</h3>
        <span className="text-sm text-white/40">
          {pendingTasks.length + inProgressTasks.length} pending
        </span>
      </div>
      
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {inProgressTasks.concat(pendingTasks).slice(0, 6).map((task, i) => (
          <div 
            key={task.id || i}
            className="flex items-center gap-3 p-3 bg-white/5 rounded-lg"
          >
            <div className={`w-2 h-2 rounded-full ${
              task.status === 'in_progress' ? 'bg-blue-400' : 'bg-white/30'
            }`} />
            <div className="flex-1">
              <div className="text-sm text-white">{task.task}</div>
              <div className="text-xs text-white/40">{task.move_name || 'Move task'}</div>
            </div>
            {task.due_date && (
              <div className="text-xs text-white/40">
                <Clock className="w-3 h-3 inline mr-1" />
                {task.due_date}
              </div>
            )}
          </div>
        ))}
        
        {pendingTasks.length + inProgressTasks.length === 0 && (
          <div className="text-center py-8 text-white/40 text-sm">
            No pending tasks
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Quick stats row
const QuickStats = ({ metrics }) => {
  const statCards = [
    { label: 'Pipeline', value: metrics.pipeline_value, format: 'currency', trend: 'up' },
    { label: 'Win Rate', value: metrics.win_rate, format: 'percent', trend: 'flat' },
    { label: 'CAC', value: metrics.cac, format: 'currency', trend: 'down' },
    { label: 'NRR', value: metrics.nrr, format: 'percent', trend: 'up' }
  ]
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 }}
      className="grid grid-cols-4 gap-4 mb-6"
    >
      {statCards.map((stat, i) => (
        <div key={stat.label} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="text-sm text-white/40 mb-1">{stat.label}</div>
          <div className="flex items-end justify-between">
            <div className="text-2xl font-medium text-white">
              {stat.format === 'currency' && '₹'}
              {stat.value?.toLocaleString() || '—'}
              {stat.format === 'percent' && '%'}
            </div>
            <div className={`flex items-center gap-1 text-xs ${
              stat.trend === 'up' ? 'text-emerald-400' : 
              stat.trend === 'down' ? 'text-red-400' : 'text-white/40'
            }`}>
              {stat.trend === 'up' && <TrendingUp className="w-3 h-3" />}
              {stat.trend === 'down' && <TrendingUp className="w-3 h-3 rotate-180" />}
              {stat.trend === 'flat' && '—'}
            </div>
          </div>
        </div>
      ))}
    </motion.div>
  )
}

// Main War Room page
const WarRoom = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [campaigns, setCampaigns] = useState([])
  const [moves, setMoves] = useState([])
  const [icps, setIcps] = useState([])
  const [guardrails, setGuardrails] = useState([])
  const [tasks, setTasks] = useState([])
  const [metrics, setMetrics] = useState({})

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Start empty - data comes from user's campaigns, moves, etc.
        setCampaigns([])
        setMoves([])
        setIcps([])
        setGuardrails([])
        setTasks([])
        setMetrics({
          pipeline_value: 0,
          win_rate: 0,
          cac: 0,
          nrr: 0
        })
      } catch (error) {
        console.error('Error fetching war room data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Campaign board columns
  const campaignColumns = {
    'Active': campaigns.filter(c => c.status === 'active'),
    'Planned': campaigns.filter(c => c.status === 'planned'),
    'Paused': campaigns.filter(c => c.status === 'paused'),
    'Completed': campaigns.filter(c => c.status === 'completed')
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-xl flex items-center justify-center">
            <Target className="w-5 h-5 text-red-400" />
          </div>
          <div>
            <h1 className="text-3xl font-light text-white">War Room</h1>
            <p className="text-white/40">Strategic command center</p>
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      {!loading && <QuickStats metrics={metrics} />}

      {/* Main Grid */}
      {loading ? (
        <div className="grid grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-64 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          {/* Left column */}
          <div className="col-span-2 space-y-6">
            {/* Strategy Snapshot */}
            <StrategySnapshot campaigns={campaigns} moves={moves} icps={icps} />
            
            {/* Campaign Board */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-white">Campaign Board</h3>
                <button 
                  onClick={() => navigate('/app/campaigns')}
                  className="flex items-center gap-1 text-sm text-white/40 hover:text-white transition-colors"
                >
                  View All
                  <ArrowUpRight className="w-4 h-4" />
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(campaignColumns).slice(0, 2).map(([status, statusCampaigns]) => (
                  <div key={status}>
                    <div className="text-sm text-white/40 mb-2">{status} ({statusCampaigns.length})</div>
                    <div className="space-y-2">
                      {statusCampaigns.slice(0, 3).map(campaign => (
                        <CampaignBoardItem
                          key={campaign.id}
                          campaign={campaign}
                          onClick={() => navigate(`/app/campaigns/${campaign.id}`)}
                        />
                      ))}
                      {statusCampaigns.length === 0 && (
                        <div className="p-4 border border-dashed border-white/10 rounded-lg text-center text-white/30 text-sm">
                          None
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Right column */}
          <div className="space-y-6">
            {/* Kill Switch Panel */}
            <KillSwitchPanel guardrails={guardrails} />
            
            {/* Task Queue */}
            <TaskQueue tasks={tasks} />
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-6 grid grid-cols-4 gap-4"
      >
        <button 
          onClick={() => navigate('/app/spikes/new')}
          className="p-4 bg-white/5 border border-white/10 rounded-xl hover:border-white/20 transition-all group"
        >
          <Zap className="w-5 h-5 text-amber-400 mb-2" />
          <div className="text-sm font-medium text-white">Launch Spike</div>
          <div className="text-xs text-white/40">30-day GTM sprint</div>
        </button>
        
        <button 
          onClick={() => navigate('/app/campaigns')}
          className="p-4 bg-white/5 border border-white/10 rounded-xl hover:border-white/20 transition-all group"
        >
          <Layers className="w-5 h-5 text-blue-400 mb-2" />
          <div className="text-sm font-medium text-white">New Campaign</div>
          <div className="text-xs text-white/40">Strategic initiative</div>
        </button>
        
        <button 
          onClick={() => navigate('/app/matrix')}
          className="p-4 bg-white/5 border border-white/10 rounded-xl hover:border-white/20 transition-all group"
        >
          <BarChart3 className="w-5 h-5 text-emerald-400 mb-2" />
          <div className="text-sm font-medium text-white">View Metrics</div>
          <div className="text-xs text-white/40">RAG dashboard</div>
        </button>
        
        <button 
          onClick={() => navigate('/app/muse')}
          className="p-4 bg-white/5 border border-white/10 rounded-xl hover:border-white/20 transition-all group"
        >
          <Activity className="w-5 h-5 text-purple-400 mb-2" />
          <div className="text-sm font-medium text-white">Generate Assets</div>
          <div className="text-xs text-white/40">Content factory</div>
        </button>
      </motion.div>
    </div>
  )
}

export default WarRoom

