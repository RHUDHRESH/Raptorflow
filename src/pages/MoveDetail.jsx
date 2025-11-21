import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  Calendar, 
  Target, 
  Eye,
  Brain,
  Sliders,
  PlayCircle,
  PauseCircle,
  XCircle,
  Copy,
  Users,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  BarChart3,
  Mail,
  Linkedin,
  Globe
} from 'lucide-react'
import { cn } from '../utils/cn'
import { MoveStatus, Posture, FoggRole } from '../utils/moveSystemTypes'
import { generateMockManeuverTypes } from '../utils/moveSystemTypes'

// Mock data - in production this would come from API
const mockMove = {
  id: 1,
  name: 'Q3 Authority Sprint – Enterprise CTOs',
  maneuver_type_id: 'authority-sprint',
  status: MoveStatus.OODA_ORIENT,
  primary_icp_id: 1,
  line_of_operation_id: 'loo-1',
  line_of_operation_name: 'Upmarket Expansion',
  icp_name: 'Enterprise CTO – Safety Seeker',
  start_date: '2025-01-15',
  end_date: '2025-01-29',
  duration_days: 14,
  current_day: 5,
  ooda_config: {
    observe_sources: ['GA', 'CRM', 'LI'],
    orient_rules: 'Cohort is high-motivation but high-risk aversion. Center of Gravity = LinkedIn + security communities. Season = Planting → accept longer runway, lower intensity.',
    decide_logic: 'If CTR < 1%, switch creative. If engagement > 5%, double down.',
    act_tasks: [
      { day: 1, task: "Publish 'Big Risk' whitepaper", channel: 'LinkedIn', status: 'complete' },
      { day: 3, task: 'LI post #1 (template link)', channel: 'LinkedIn', status: 'pending' },
      { day: 5, task: 'Case-study email #1', channel: 'Email', status: 'pending' },
      { day: 7, task: 'Security webinar announcement', channel: 'Email', status: 'pending' },
      { day: 10, task: 'Follow-up DM sequence', channel: 'LinkedIn', status: 'pending' },
      { day: 14, task: 'Soft ask: Demo request', channel: 'Email', status: 'pending' }
    ]
  },
  fogg_dynamic_config: {
    target_motivation: 'High',
    target_ability: 'Medium',
    prompt_frequency: 'Daily'
  },
  metrics: {
    impressions: 1250,
    replies: 45,
    sqls: 3,
    ctr: 3.6,
    engagement_rate: 4.2
  },
  health_status: 'green',
  anomalies_detected: []
}

const maneuverTypes = generateMockManeuverTypes()

export default function MoveDetail() {
  const { id } = useParams()
  const [move] = useState(mockMove) // In production, fetch by id
  const [oodaPhase, setOodaPhase] = useState(move.status)
  const maneuverType = maneuverTypes.find(mt => mt.id === move.maneuver_type_id)

  const getStatusColor = (status) => {
    if (status === MoveStatus.COMPLETE) return 'bg-green-100 text-green-900 border-green-200'
    if (status === MoveStatus.KILLED) return 'bg-red-100 text-red-900 border-red-200'
    if (status.includes('Act')) return 'bg-blue-100 text-blue-900 border-blue-200'
    if (status.includes('Decide')) return 'bg-purple-100 text-purple-900 border-purple-200'
    if (status.includes('Orient')) return 'bg-yellow-100 text-yellow-900 border-yellow-200'
    return 'bg-neutral-100 text-neutral-900 border-neutral-200'
  }

  const getPostureColor = (posture) => {
    const colors = {
      [Posture.OFFENSIVE]: 'bg-red-100 text-red-900',
      [Posture.DEFENSIVE]: 'bg-blue-100 text-blue-900',
      [Posture.LOGISTICAL]: 'bg-purple-100 text-purple-900',
      [Posture.RECON]: 'bg-green-100 text-green-900'
    }
    return colors[posture] || 'bg-neutral-100 text-neutral-900'
  }

  const getChannelIcon = (channel) => {
    const icons = {
      'LinkedIn': Linkedin,
      'Email': Mail,
      'GA': BarChart3,
      'CRM': Users,
      'LI': Linkedin,
      'Website': Globe
    }
    return icons[channel] || Globe
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="runway-card p-6">
        <div className="flex items-start gap-4 mb-6">
          <Link
            to="/moves/war-room"
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-neutral-200 text-neutral-700 hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="micro-label tracking-[0.5em]">Move Detail</span>
              <span className={cn(
                "px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border rounded",
                getStatusColor(move.status)
              )}>
                {move.status}
              </span>
            </div>
            <h1 className="font-serif text-3xl md:text-4xl text-black leading-tight mb-3">
              {move.name}
            </h1>
            <div className="flex items-center gap-3 flex-wrap">
              {maneuverType && (
                <>
                  <span className={cn(
                    "px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] rounded",
                    getPostureColor(maneuverType.category)
                  )}>
                    {maneuverType.category}
                  </span>
                  {maneuverType.fogg_role && (
                    <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                      {maneuverType.fogg_role}
                    </span>
                  )}
                  <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                    {maneuverType.tier}
                  </span>
                </>
              )}
              <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                {move.duration_days} days · Day {move.current_day}/{move.duration_days}
              </span>
            </div>
          </div>
        </div>

        {/* Meta Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-neutral-200">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-1">Line of Operation</p>
            <p className="text-sm font-medium text-neutral-900">{move.line_of_operation_name}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-1">Primary Cohort</p>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-neutral-200 flex items-center justify-center">
                <Users className="w-3 h-3 text-neutral-700" />
              </div>
              <p className="text-sm font-medium text-neutral-900">{move.icp_name}</p>
            </div>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-1">Health Status</p>
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-3 h-3 rounded-full border-2",
                move.health_status === 'green' ? 'border-green-500 bg-green-100' :
                move.health_status === 'amber' ? 'border-yellow-500 bg-yellow-100' :
                'border-red-500 bg-red-100'
              )} />
              <p className="text-sm font-medium text-neutral-900 capitalize">{move.health_status}</p>
            </div>
          </div>
        </div>
      </div>

      {/* OODA Sections */}
      <div className="space-y-6">
        {/* OBSERVE */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="runway-card p-6"
        >
          <div className="flex items-center gap-3 mb-4 pb-4 border-b border-neutral-200">
            <Eye className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-neutral-900">Observe</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-neutral-700 mb-2">Data Sources</p>
              <div className="flex items-center gap-2 flex-wrap">
                {move.ooda_config.observe_sources.map((source, i) => {
                  const Icon = getChannelIcon(source)
                  return (
                    <div key={i} className="flex items-center gap-2 px-3 py-2 bg-neutral-50 rounded-lg border border-neutral-200">
                      <Icon className="w-4 h-4 text-neutral-700" />
                      <span className="text-sm font-medium text-neutral-900">{source}</span>
                    </div>
                  )
                })}
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-neutral-700 mb-2">Current Snapshots</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(move.metrics).slice(0, 4).map(([key, value]) => (
                  <div key={key} className="p-3 bg-neutral-50 rounded-lg border border-neutral-200">
                    <p className="text-xs text-neutral-600 mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                    <p className="text-lg font-bold text-neutral-900">{value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                <span className="font-medium">Last 30d:</span> 2% demo conversion, 0 enterprise logos.
              </p>
            </div>
          </div>
        </motion.div>

        {/* ORIENT */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="runway-card p-6"
        >
          <div className="flex items-center gap-3 mb-4 pb-4 border-b border-neutral-200">
            <Brain className="w-6 h-6 text-yellow-600" />
            <h2 className="text-xl font-bold text-neutral-900">Orient</h2>
          </div>
          
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-900 leading-relaxed">
              {move.ooda_config.orient_rules}
            </p>
          </div>

          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3 bg-neutral-50 rounded-lg">
              <p className="text-xs text-neutral-600 mb-1">Motivation</p>
              <p className="text-sm font-medium text-neutral-900">{move.fogg_dynamic_config.target_motivation}</p>
            </div>
            <div className="p-3 bg-neutral-50 rounded-lg">
              <p className="text-xs text-neutral-600 mb-1">Ability</p>
              <p className="text-sm font-medium text-neutral-900">{move.fogg_dynamic_config.target_ability}</p>
            </div>
            <div className="p-3 bg-neutral-50 rounded-lg">
              <p className="text-xs text-neutral-600 mb-1">Prompt Frequency</p>
              <p className="text-sm font-medium text-neutral-900">{move.fogg_dynamic_config.prompt_frequency}</p>
            </div>
          </div>
        </motion.div>

        {/* DECIDE */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="runway-card p-6"
        >
          <div className="flex items-center gap-3 mb-4 pb-4 border-b border-neutral-200">
            <Sliders className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-bold text-neutral-900">Decide</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-neutral-700 mb-3">Decision Logic</p>
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <p className="text-sm text-purple-900">{move.ooda_config.decide_logic}</p>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-neutral-700 mb-3">Channel Weights</p>
              <div className="space-y-3">
                {['LinkedIn', 'Email', 'Events'].map((channel) => {
                  const Icon = getChannelIcon(channel)
                  return (
                    <div key={channel} className="flex items-center gap-3">
                      <Icon className="w-5 h-5 text-neutral-700" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-neutral-900">{channel}</span>
                          <span className="text-xs text-neutral-600">33%</span>
                        </div>
                        <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                          <div className="h-full bg-neutral-900" style={{ width: '33%' }} />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="flex items-center gap-4 pt-4 border-t border-neutral-200">
              <div className="flex-1 p-3 bg-neutral-50 rounded-lg">
                <p className="text-xs text-neutral-600 mb-1">Impact on Intensity</p>
                <p className="text-sm font-medium text-neutral-900">+2 points</p>
              </div>
              <div className="flex-1 p-3 bg-neutral-50 rounded-lg">
                <p className="text-xs text-neutral-600 mb-1">Capacity Usage</p>
                <p className="text-sm font-medium text-neutral-900">28 / 40</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* ACT */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="runway-card p-6"
        >
          <div className="flex items-center justify-between mb-4 pb-4 border-b border-neutral-200">
            <div className="flex items-center gap-3">
              <PlayCircle className="w-6 h-6 text-green-600" />
              <h2 className="text-xl font-bold text-neutral-900">Act</h2>
            </div>
            {move.status === MoveStatus.OODA_DECIDE && (
              <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                <PlayCircle className="w-4 h-4" />
                Deploy Act Phase
              </button>
            )}
          </div>
          
          <div className="space-y-3">
            {move.ooda_config.act_tasks.map((task, index) => {
              const Icon = getChannelIcon(task.channel)
              const isComplete = task.status === 'complete'
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    "flex items-start gap-3 p-4 rounded-lg border transition-colors",
                    isComplete 
                      ? "bg-green-50 border-green-200" 
                      : "bg-neutral-50 border-neutral-200 hover:bg-neutral-100"
                  )}
                >
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                    isComplete ? "bg-green-200" : "bg-neutral-200"
                  )}>
                    {isComplete ? (
                      <CheckCircle2 className="w-4 h-4 text-green-700" />
                    ) : (
                      <Icon className="w-4 h-4 text-neutral-700" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-neutral-600">D{task.day}</span>
                      <span className="text-xs px-2 py-0.5 bg-neutral-200 text-neutral-700 rounded">
                        {task.channel}
                      </span>
                    </div>
                    <p className={cn(
                      "text-sm",
                      isComplete ? "text-green-900 line-through" : "text-neutral-900"
                    )}>
                      {task.task}
                    </p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </div>

      {/* Bottom Actions */}
      <div className="runway-card p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-neutral-600">
              <TrendingUp className="w-4 h-4" />
              <span>Impressions: {move.metrics.impressions}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-neutral-600">
              <Users className="w-4 h-4" />
              <span>Replies: {move.metrics.replies}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-neutral-600">
              <Target className="w-4 h-4" />
              <span>SQLs: {move.metrics.sqls}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-4 py-2 border border-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors">
              <PauseCircle className="w-4 h-4" />
              Pause Move
            </button>
            <button className="flex items-center gap-2 px-4 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 transition-colors">
              <XCircle className="w-4 h-4" />
              Kill Move
            </button>
            <button className="flex items-center gap-2 px-4 py-2 border border-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors">
              <Copy className="w-4 h-4" />
              Clone Move
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
