import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  CheckCircle2, 
  Circle, 
  Radio, 
  Box, 
  Sparkles,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Minus,
  Play,
  Plus,
  Target,
  AlertCircle,
  ArrowRight,
  MoreHorizontal,
  BarChart3,
  Calendar,
  Clock,
  ExternalLink,
  Search,
  Filter
} from 'lucide-react'
import { BrandIcon } from '@/components/brand/BrandSystem';
import useRaptorflowStore from '../../store/raptorflowStore'

// RAG status colors
const RAG_COLORS = {
  green: { bg: 'bg-emerald-500', light: 'bg-emerald-50', text: 'text-emerald-600' },
  amber: { bg: 'bg-amber-500', light: 'bg-amber-50', text: 'text-amber-600' },
  red: { bg: 'bg-red-500', light: 'bg-red-50', text: 'text-red-600' },
}

// KPI Card
const KPICard = ({ name, current, target, baseline, trend }) => {
  const progress = target > 0 ? Math.round((current / target) * 100) : 0
  const ragStatus = progress >= 80 ? 'green' : progress >= 50 ? 'amber' : 'red'
  const colors = RAG_COLORS[ragStatus]
  const hasBaseline = typeof baseline === 'number'
  
  return (
    <div className="p-4 bg-card border border-border rounded-xl">
      <div className="flex items-start justify-between mb-2">
        <span className="text-body-xs text-ink-400">{name}</span>
        <div className={`w-2 h-2 rounded-full ${colors.bg}`} />
      </div>
      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-2xl font-medium text-ink font-mono">{Number(current || 0).toLocaleString()}</span>
        <span className="text-body-xs text-ink-400">/ {Number(target || 0).toLocaleString()}</span>
      </div>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden mb-2">
        <div
          className={`h-full ${colors.bg} rounded-full transition-all`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-body-xs text-ink-400">{progress}% of target{hasBaseline ? ` · baseline ${baseline}` : ''}</span>
        {trend !== undefined && <TrendIndicator value={trend} />}
      </div>
    </div>
  )
}

// Trend indicator
const TrendIndicator = ({ value, inverse = false }) => {
  if (!value || value === 0) {
    return <Minus className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
  }
  
  const isPositive = inverse ? value < 0 : value > 0
  const TrendIcon = value > 0 ? TrendingUp : TrendingDown
  
  return (
    <div className={`flex items-center gap-1 ${isPositive ? 'text-emerald-600' : 'text-red-500'}`}>
      <TrendIcon className="w-4 h-4" strokeWidth={1.5} />
      <span className="text-xs font-mono">{Math.abs(value)}%</span>
    </div>
  )
}

// Task item component
const TaskItem = ({ task, onToggle, onNavigate }) => (
  <motion.div
    initial={{ opacity: 0, x: -10 }}
    animate={{ opacity: 1, x: 0 }}
    className="flex items-start gap-3 p-3 bg-paper hover:bg-paper-200 rounded-xl border border-border-light transition-editorial group"
  >
    <button
      onClick={() => onToggle(task.moveId, task.id)}
      className="mt-0.5 flex-shrink-0"
    >
      {task.done ? (
        <CheckCircle2 className="w-5 h-5 text-primary" strokeWidth={1.5} />
      ) : (
        <Circle className="w-5 h-5 text-ink-300 group-hover:text-ink-400" strokeWidth={1.5} />
      )}
    </button>
    <div className="flex-1 min-w-0">
      <p className={`text-body-sm ${task.done ? 'text-ink-400 line-through' : 'text-ink'}`}>
        {task.text}
      </p>
      <button 
        onClick={() => onNavigate(`/app/moves/${task.moveId}`)}
        className="text-body-xs text-ink-400 hover:text-primary transition-editorial"
      >
        {task.moveName}
      </button>
    </div>
    <button
      onClick={() => onNavigate(`/app/moves/${task.moveId}`)}
      className="opacity-0 group-hover:opacity-100 p-1 text-ink-400 hover:text-ink transition-editorial"
    >
      <ChevronRight className="w-4 h-4" strokeWidth={1.5} />
    </button>
  </motion.div>
)

// Active move card
const MoveCard = ({ move, campaign, onNavigate, onOpenMuse, week }) => {
  const completedTasks = move.checklistItems.filter(t => t.done).length
  const totalTasks = move.checklistItems.length
  const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 bg-card border border-border rounded-xl hover:border-border-dark transition-editorial group"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="text-body-sm font-medium text-ink">{move.name}</h4>
          <p className="text-body-xs text-ink-400">{campaign?.name}</p>
        </div>
        <span className={`px-2 py-0.5 rounded text-body-xs capitalize ${
          move.status === 'active' ? 'bg-paper-200 text-ink' :
          move.status === 'pending' ? 'bg-paper-200 text-ink-400' :
          'bg-muted text-ink-400'
        }`}>
          {move.status}
        </span>
      </div>
      
      <div className="flex items-center gap-2 mb-3">
        <span className="px-2 py-0.5 bg-paper-200 rounded text-body-xs text-ink-400 capitalize">
          {move.channel}
        </span>
        <span className="px-2 py-0.5 bg-paper-200 rounded text-body-xs text-ink-400">
          {move.durationDays}d
        </span>
      </div>
      
      {/* Progress */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-body-xs text-ink-400">{completedTasks}/{totalTasks} tasks</span>
          <span className="text-body-xs text-ink font-mono">{progress}%</span>
        </div>
        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-ink-300 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
      
      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => onNavigate(`/app/moves/${move.id}`)}
          className="flex-1 px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
        >
          View
        </button>
        <button
          onClick={() => onOpenMuse(move.id)}
          className="flex items-center gap-1 px-3 py-2 text-body-xs text-primary bg-signal-muted rounded-lg hover:bg-primary/20 transition-editorial"
        >
          <Sparkles className="w-3.5 h-3.5" strokeWidth={1.5} />
          Generate
        </button>
      </div>

      {week?.days?.length ? (
        <div className="mt-3 pt-3 border-t border-border-light">
          <div className="flex items-center justify-between mb-2">
            <div className="text-body-xs text-ink-400">This week</div>
            <div className="text-body-xs text-ink-400">Day {week.dayNumber}</div>
          </div>
          <div className="grid grid-cols-7 gap-1 mb-3">
            {week.days.map(d => (
              <div
                key={`${move.id}_week_${d.day}`}
                className={`h-8 rounded-lg flex items-center justify-center text-[11px] font-mono ${
                  d.day === week.dayNumber ? 'bg-primary/10 text-primary' : 'bg-paper-200 text-ink-400'
                }`}
                title={`Day ${ d.day }: ${ d.todo } tasks`}
              >
                {d.todo}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => onNavigate(`/app/moves/${move.id}`)}
              className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
            >
              Preview
            </button>
            <button
              onClick={() => onNavigate(`/app/moves/${move.id}`)}
              className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
            >
              Edit
            </button>
            <button
              onClick={() => onNavigate(`/app/moves/${move.id}`)}
              className="px-3 py-2 text-body-xs text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
            >
              Schedule
            </button>
          </div>
        </div>
      ) : null}
    </motion.div>
  )
}

// Quick action button
const QuickAction = ({ icon: Icon, label, description, onClick, accent = false }) => (
  <motion.button
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className={`flex items-center gap-4 p-4 rounded-xl border transition-editorial text-left ${
      accent
        ? 'bg-primary text-primary-foreground border-primary hover:opacity-95'
        : 'bg-card border-border hover:border-border-dark'
    }`}
  >
    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
      accent ? 'bg-white/20' : 'bg-paper-200'
    }`}>
      <Icon className={`w-5 h-5 ${accent ? 'text-white' : 'text-ink-400'}`} strokeWidth={1.5} />
    </div>
    <div>
      <div className={`text-body-sm font-medium ${accent ? 'text-white' : 'text-ink'}`}>{label}</div>
      <div className={`text-body-xs ${accent ? 'text-white/70' : 'text-ink-400'}`}>{description}</div>
    </div>
  </motion.button>
)

// Main Matrix Dashboard
const MatrixDashboard = () => {
  const navigate = useNavigate()
  const { 
    getTodayChecklist, 
    getActiveMoves, 
    getGeneratingMoves,
    getActiveCampaigns,
    getPrimaryCampaign,
    getCampaign,
    getMoveDayNumber,
    getMoveTasksForDay,
    toggleTaskDone,
    openMuseDrawer,
    getActiveDuels,
    usage,
    getPlanLimits
  } = useRaptorflowStore()

  const todayTasks = getTodayChecklist()
  const activeMoves = getActiveMoves()
  const generatingMoves = getGeneratingMoves?.() || []
  const activeCampaigns = getActiveCampaigns()
  const activeDuels = getActiveDuels()
  const planLimits = getPlanLimits()

  // Calculate overall stats
  const totalTasks = todayTasks.length
  const completedTasks = todayTasks.filter(t => t.done).length
  const taskProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  // Get primary campaign KPIs
  const primaryCampaign = getPrimaryCampaign?.() || activeCampaigns[0]

  const handleOpenMuse = (moveId) => {
    openMuseDrawer({ moveId })
  }

  const buildWeekPreview = (move) => {
    const dayNumber = getMoveDayNumber?.(move.id) || 1
    const durationDays = move?.plan?.durationDays || move?.durationDays || 7
    const end = Math.min(durationDays, dayNumber + 6)
    const days = []
    for (let day = dayNumber; day <= end; day += 1) {
      const tasks = getMoveTasksForDay?.(move.id, day) || []
      const todo = tasks.filter(t => t.status !== 'done').length
      days.push({ day, todo })
    }
    while (days.length < 7) {
      const last = days.length ? days[days.length - 1].day : dayNumber
      days.push({ day: last + 1, todo: 0 })
    }
    return { dayNumber, days }
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-serif text-headline-md text-ink">Matrix</h1>
        <p className="text-body-sm text-ink-400 mt-1">Your daily command center</p>
      </motion.div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - Today's tasks */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Checklist */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-card border border-border rounded-xl overflow-hidden"
          >
            <div className="p-4 border-b border-border-light flex items-center justify-between">
              <div>
                <h2 className="font-serif text-lg text-ink">Today's Checklist</h2>
                <p className="text-body-xs text-ink-400">{completedTasks} of {totalTasks} tasks complete</p>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${taskProgress}%` }}
                  />
                </div>
                <span className="text-body-xs text-ink font-mono">{taskProgress}%</span>
              </div>
            </div>
            
            <div className="p-4 space-y-2 max-h-[400px] overflow-auto">
              {todayTasks.length > 0 ? (
                todayTasks.map(task => (
                  <TaskItem 
                    key={task.id} 
                    task={task} 
                    onToggle={toggleTaskDone}
                    onNavigate={navigate}
                  />
                ))
              ) : (
                <div className="text-center py-8">
                  <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" strokeWidth={1.5} />
                  <h3 className="font-serif text-lg text-ink mb-1">All caught up!</h3>
                  <p className="text-body-sm text-ink-400">No pending tasks for today</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Active Moves */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-card border border-border rounded-xl overflow-hidden"
          >
            <div className="p-4 border-b border-border-light flex items-center justify-between">
              <div>
                <h2 className="font-serif text-lg text-ink">Active Moves</h2>
                <p className="text-body-xs text-ink-400">{activeMoves.length} moves in progress</p>
              </div>
              <button
                onClick={() => navigate('/app/moves')}
                className="text-body-xs text-primary hover:underline"
              >
                View all
              </button>
            </div>
            
            <div className="p-4">
              {generatingMoves.length > 0 && (
                <div className="mb-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-body-xs text-ink-400">Generating</div>
                    <div className="text-body-xs text-ink-400">{generatingMoves.length}</div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {generatingMoves.slice(0, 2).map(move => (
                      <div
                        key={move.id}
                        className="p-4 bg-paper-200 border border-border rounded-xl"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="text-body-sm text-ink font-medium">{move.name}</div>
                            <div className="text-body-xs text-ink-400">{getCampaign(move.campaignId)?.name || 'No campaign'}</div>
                          </div>
                          <span className="px-2 py-0.5 rounded text-body-xs bg-paper text-ink-400">generating</span>
                        </div>
                        <div className="text-body-xs text-ink-400">Planning & preparing tasks…</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeMoves.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {activeMoves.slice(0, 4).map(move => (
                    <MoveCard
                      key={move.id}
                      move={move}
                      campaign={getCampaign(move.campaignId)}
                      onNavigate={navigate}
                      onOpenMuse={handleOpenMuse}
                      week={buildWeekPreview(move)}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BrandIcon name="speed" className="w-12 h-12 text-ink-300 mx-auto mb-3" />
                  <h3 className="font-serif text-lg text-ink mb-1">No active moves</h3>
                  <p className="text-body-sm text-ink-400 mb-4">Create your first move to get started</p>
                  <button
                    onClick={() => navigate('/app/campaigns')}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-body-sm hover:opacity-95 transition-editorial"
                  >
                    Create Campaign
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Right column - Quick actions & Performance */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-3"
          >
            <h2 className="font-serif text-lg text-ink">Quick Actions</h2>
            <QuickAction
              icon={Box}
              label="Start Duel"
              description="Test variants in Black Box"
              onClick={() => navigate('/app/black-box/new')}
              accent
            />
            <QuickAction
              icon={Radio}
              label="Run Radar"
              description={`${ planLimits.radarScansPerDay - usage.radarScansToday } scans left today`}
              onClick={() => navigate('/app/radar')}
            />
            <QuickAction
              icon={Plus}
              label="Create Campaign"
              description="Launch a new war plan"
              onClick={() => navigate('/app/campaigns/new')}
            />
          </motion.div>

          {/* Performance */}
          {primaryCampaign && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-3"
            >
              <div className="flex items-center justify-between">
                <h2 className="font-serif text-lg text-ink">Performance</h2>
                <button
                  onClick={() => navigate(`/app/campaigns/${primaryCampaign.id}`)}
                  className="text-body-xs text-primary hover:underline"
                >
                  Details
                </button>
              </div>
              <div className="p-4 bg-card border border-border rounded-xl mb-3">
                <div className="flex items-center gap-2 mb-3">
                  <Target className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  <span className="text-body-sm text-ink font-medium">{primaryCampaign.name}</span>
                </div>
                <KPICard 
                  name={primaryCampaign.kpis.primary.name || 'Primary KPI'}
                  current={primaryCampaign.kpis.primary.current}
                  target={primaryCampaign.kpis.primary.target}
                  baseline={primaryCampaign.kpis.primary.baseline}
                  trend={15}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-card border border-border rounded-xl">
                  <div className="text-body-xs text-ink-400 mb-1">Reach</div>
                  <div className="text-lg font-mono text-ink">
                    {(primaryCampaign.kpis.reach.current / 1000).toFixed(1)}k
                  </div>
                </div>
                <div className="p-3 bg-card border border-border rounded-xl">
                  <div className="text-body-xs text-ink-400 mb-1">Clicks</div>
                  <div className="text-lg font-mono text-ink">
                    {primaryCampaign.kpis.click.current}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Active Duels */}
          {activeDuels.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="space-y-3"
            >
              <div className="flex items-center justify-between">
                <h2 className="font-serif text-lg text-ink">Active Duels</h2>
                <button
                  onClick={() => navigate('/app/black-box')}
                  className="text-body-xs text-primary hover:underline"
                >
                  View all
                </button>
              </div>
              {activeDuels.slice(0, 2).map(duel => (
                <div 
                  key={duel.id}
                  className="p-3 bg-card border border-border rounded-xl cursor-pointer hover:border-border-dark transition-editorial"
                  onClick={() => navigate(`/app/black-box/${duel.id}`)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-body-sm text-ink capitalize">{duel.variable} Duel</span>
                    <span className="px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded text-body-xs">
                      Running
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {duel.variants.map((v, i) => (
                      <div key={v.id} className="flex-1 text-center">
                        <div className="text-body-xs text-ink-400 mb-1">{v.label}</div>
                        <div className="text-body-sm font-mono text-ink">{v.clicks}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {/* Usage */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="p-4 bg-paper-200 border border-border-light rounded-xl"
          >
            <h3 className="text-body-xs text-ink-400 mb-3">Usage This Month</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-body-xs text-ink">Radar Scans</span>
                <span className="text-body-xs text-ink font-mono">{usage.radarScansToday}/{planLimits.radarScansPerDay}/day</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-body-xs text-ink">Black Box Duels</span>
                <span className="text-body-xs text-ink font-mono">{usage.blackBoxDuelsThisMonth}/{planLimits.blackBoxDuelsPerMonth}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-body-xs text-ink">Muse Generations</span>
                <span className="text-body-xs text-ink font-mono">{usage.museGenerationsThisMonth}/{planLimits.museGenerationsPerMonth}</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default MatrixDashboard
