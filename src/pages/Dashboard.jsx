import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Target, 
  TrendingUp, 
  Clock, 
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  PlayCircle,
  Shield,
  Zap,
  Eye,
  Plus,
  Calendar,
  ChevronRight,
  Award,
  Trophy,
  Star
} from 'lucide-react'
import { cn } from '../utils/cn'
import { useState, useEffect } from 'react'
import { Posture, SeasonType } from '../utils/moveSystemTypes'

// Hero line generators - ruthlessly editorial, luxury magazine vibes
const getHeroLine = (posture, season, movesCount) => {
  const lines = {
    'Offensive': {
      'High_Season': [
        "Strike season. Three moves in motion.",
        "Offensive posture. Market heat rising.",
        "Maximum velocity. Peak attention window.",
        "Three campaigns live. Momentum building."
      ],
      'Low_Season': [
        "Planting season. Offensive positioning.",
        "Building in silence. Positioning for spring.",
        "Quiet offensive. Long game in play.",
        "Seeds planted. Patience rewarded."
      ],
      'Shoulder': [
        "Transition week. Offensive momentum.",
        "Shoulder season. Building toward peak.",
        "Offensive stance. Timing the wave.",
        "Pre-season positioning. Ready state."
      ]
    },
    'Defensive': {
      'High_Season': [
        "Hold the line. Peak season defense.",
        "Defensive stance. Protecting altitude.",
        "Vigilance mode. High season watch.",
        "Securing gains. Territory locked."
      ],
      'Low_Season': [
        "Low season defense. Foundations firm.",
        "Holding quiet ground. Stability mode.",
        "Defensive posture. Resilience building.",
        "Winter fortress. Protected position."
      ],
      'Shoulder': [
        "Transition defense. Maintaining ground.",
        "Shoulder season hold. Position secure.",
        "Defensive watch. Shift management.",
        "Protected stance. Stable transition."
      ]
    },
    'Logistical': {
      'High_Season': [
        "Infrastructure sprint. Peak efficiency.",
        "Logistics mode. Maximum throughput.",
        "System build. High season capacity.",
        "Operations peak. Scaling live."
      ],
      'Low_Season': [
        "Foundation work. System refinement.",
        "Quiet build. Capacity expansion.",
        "Logistics focus. Infrastructure mode.",
        "Off-season prep. Systems optimized."
      ],
      'Shoulder': [
        "Transition build. Systems preparing.",
        "Shoulder logistics. Infrastructure ready.",
        "Setup phase. Pre-launch systems.",
        "Building capacity. Readiness mode."
      ]
    },
    'Recon': {
      'High_Season': [
        "Intelligence mode. Peak market signals.",
        "Reconnaissance sprint. Data gathering.",
        "Signal collection. Pattern watch.",
        "Eyes open. Peak season intel."
      ],
      'Low_Season': [
        "Deep research. Off-season intelligence.",
        "Quiet observation. Map building.",
        "Recon mode. Market cartography.",
        "Analysis phase. Knowledge gathering."
      ],
      'Shoulder': [
        "Shift observation. Pattern tracking.",
        "Transition recon. Signal mapping.",
        "Intelligence phase. Watching movement.",
        "Pre-season reconnaissance. Eyes up."
      ]
    }
  }

  const postureKey = posture || 'Offensive'
  const seasonKey = season || 'High_Season'
  
  const postureLines = lines[postureKey] || lines['Offensive']
  const seasonLines = postureLines[seasonKey] || postureLines['High_Season']
  
  if (movesCount === 0) {
    return "Define your first line of operation."
  }
  
  const index = movesCount % seasonLines.length
  return seasonLines[index]
}

// Subheadline - gives context to the hero
const getSubheadline = (posture, season, movesCount) => {
  if (movesCount === 0) return "Begin with ICP definition, strategy selection, or move generation."
  if (movesCount === 1) return "One line of operation active. Room for expansion."
  if (movesCount === 2) return "Two lines engaged. Strategic balance maintained."
  return `${movesCount} lines in play. Full operational tempo.`
}

// Mock data - in production, fetch from Supabase
const mockMoves = [
  { id: 1, name: 'Authority Sprint – Enterprise CTOs', posture: 'Offensive', status: 'OODA_Act', progress: 75 },
  { id: 2, name: 'Garrison – High-Value Accounts', posture: 'Defensive', status: 'OODA_Act', progress: 45 },
  { id: 3, name: 'Asset Forge – Security Proof Pack', posture: 'Logistical', status: 'OODA_Decide', progress: 90 },
]

const mockTodayActions = [
  { id: 1, text: 'Approve LI post #1 draft', move: 'Authority Sprint', priority: 'high', icon: Target },
  { id: 2, text: 'Record 90s security risk video', move: 'Authority Sprint', priority: 'high', icon: PlayCircle },
  { id: 3, text: 'Review 4 at-risk accounts', move: 'Garrison', priority: 'medium', icon: Shield },
  { id: 4, text: 'Upload latest uptime graph', move: 'Asset Forge', priority: 'low', icon: TrendingUp },
]

const mockSentinelAlerts = [
  { id: 1, message: 'Tone Clash alert.', move: 'Authority Sprint', severity: 4 },
  { id: 2, message: 'Fatigue detected.', move: 'Garrison', severity: 3 },
]

// Posture icon mapping
const getPostureIcon = (posture) => {
  const icons = {
    'Offensive': Target,
    'Defensive': Shield,
    'Logistical': Zap,
    'Recon': Eye,
  }
  return icons[posture] || Target
}

// Helper to format last updated time
const getLastUpdated = () => {
  const now = new Date()
  return now.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  })
}

// Get current sprint info (mock)
const getCurrentSprint = () => {
  return {
    name: 'Sprint 10',
    dates: '12–26 Apr',
    season: SeasonType.HIGH_SEASON,
    posture: Posture.OFFENSIVE
  }
}

export default function Dashboard() {
  const [lastUpdated, setLastUpdated] = useState(getLastUpdated())
  const [moves] = useState(mockMoves)
  const [todayActions] = useState(mockTodayActions)
  const [sentinelAlerts] = useState(mockSentinelAlerts)
  
  const currentSprint = getCurrentSprint()
  const movesCount = moves.length
  const heroLine = getHeroLine(
    currentSprint.posture,
    currentSprint.season,
    movesCount
  )
  const subheadline = getSubheadline(
    currentSprint.posture,
    currentSprint.season,
    movesCount
  )

  // Group moves by posture - max 4 displayed
  const movesByPosture = moves.reduce((acc, move) => {
    const posture = move.posture || 'Offensive'
    if (!acc[posture]) acc[posture] = []
    acc[posture].push(move)
    return acc
  }, {})

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(getLastUpdated())
    }, 60000)
    return () => clearInterval(interval)
  }, [])

  // Empty state - luxury editorial zero state
  if (movesCount === 0) {
    return (
      <div className="space-y-12 animate-fade-in-up">
        {/* Hero - Empty State - Pure Monochrome */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          className="relative overflow-hidden border border-black/10 bg-white"
        >
          <div className="relative z-10 px-12 py-16 md:px-20 md:py-24">
            {/* Micro metadata bar */}
            <div className="flex items-center gap-4 mb-12">
              <span className="text-micro text-gray-400">Command Center</span>
              <span className="h-px w-20 bg-black/10" />
            </div>

            {/* Editorial headline - Didot serif */}
            <h1 className="text-hero mb-6 max-w-5xl">
              {heroLine}
            </h1>

            {/* Subheadline */}
            <p className="text-body max-w-2xl mb-12">
              {subheadline}
            </p>

            {/* Action buttons - monochrome */}
            <div className="flex flex-wrap items-center gap-3">
              <Link to="/cohorts" className="btn-primary">
                <Plus className="w-3.5 h-3.5" strokeWidth={1.5} />
                Define ICP
              </Link>
              <Link to="/strategy/wizard" className="btn-secondary">
                <Sparkles className="w-3.5 h-3.5" strokeWidth={1.5} />
                Strategy
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="space-y-12 animate-fade-in-up">
      {/* Hero Section - Luxury Editorial Cover - Pure Monochrome */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="relative overflow-hidden border border-black/10 bg-white"
      >
        <div className="relative z-10 px-12 py-16 md:px-20 md:py-24">
          {/* Micro metadata bar */}
          <div className="flex items-center justify-between mb-12">
            <div className="flex items-center gap-4">
              <span className="text-micro text-gray-400">Command Center</span>
              <span className="h-px w-12 bg-black/10" />
              <span className="text-xs font-sans text-gray-500">
                {currentSprint.name} • {currentSprint.dates}
              </span>
            </div>
            <span className="text-xs font-mono text-gray-300">
              {lastUpdated}
            </span>
          </div>

          {/* Editorial headline - HUGE Didot serif */}
          <h1 className="text-hero mb-6 max-w-5xl">
            {heroLine}
          </h1>

          {/* Subheadline */}
          <p className="text-body max-w-2xl">
            {subheadline}
          </p>
        </div>
      </motion.div>

      {/* Move Summary - Maximum 4 Cards, Monochrome */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {Object.entries(movesByPosture).slice(0, 4).map(([posture, postureMoves], index) => {
          const Icon = getPostureIcon(posture)
          const totalProgress = Math.round(
            postureMoves.reduce((sum, m) => sum + (m.progress || 0), 0) / postureMoves.length
          )
          
          return (
            <motion.div
              key={posture}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08, duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
              className="card-hover"
            >
              <div className="block p-8">
                <div className="flex items-start justify-between mb-6">
                  <div className="w-10 h-10 border border-black/10 bg-white flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-black" strokeWidth={1.5} />
                  </div>
                  <span className="text-micro text-gray-400">
                    {postureMoves.length} {postureMoves.length === 1 ? 'Line' : 'Lines'}
                  </span>
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-title">{posture}</h3>
                  
                  {/* Progress bar - minimal, monochrome */}
                  <div className="w-full h-px bg-black/5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${totalProgress}%` }}
                      transition={{ duration: 0.8, delay: index * 0.15, ease: [0.4, 0, 0.2, 1] }}
                      className="h-full bg-black"
                    />
                  </div>
                  
                  <div className="text-micro text-gray-400">
                    {totalProgress}% Progress
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Main Content Grid - Today's Actions + Sentinel */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Today's Actions - Left Column (2/3 width) */}
        <div className="xl:col-span-2">
          <div className="card p-8 md:p-10">
            {/* Section header */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-black/5">
              <div>
                <span className="text-micro text-gray-400 block mb-2">Decisive</span>
                <h2 className="text-heading">
                  Today's actions.
                </h2>
              </div>
              <Link
                to="/today"
                className="btn-ghost flex items-center gap-2"
              >
                All
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform duration-180" strokeWidth={1.5} />
              </Link>
            </div>

            {/* Actions list - max 7, no clutter */}
            <div className="space-y-1">
              <AnimatePresence>
                {todayActions.slice(0, 7).map((action, index) => {
                  const ActionIcon = action.icon || Target
                  // Only use oxblood for high priority (5% accent rule)
                  const isHighPriority = action.priority === 'high'
                  
                  return (
                    <motion.div
                      key={action.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.04, duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
                      className="group flex items-center gap-4 py-4 px-3 border-b border-black/5 hover:bg-gray-50 transition-colors duration-180 cursor-pointer"
                    >
                      {/* Minimal icon */}
                      <div 
                        className={cn(
                          "w-7 h-7 border flex items-center justify-center flex-shrink-0",
                          isHighPriority ? "border-oxblood/20 bg-oxblood/5" : "border-black/10 bg-white"
                        )}
                      >
                        <ActionIcon 
                          className={cn("w-3.5 h-3.5", isHighPriority ? "text-oxblood" : "text-black")} 
                          strokeWidth={1.5} 
                        />
                      </div>
                      
                      {/* Action text */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-black leading-tight">{action.text}</p>
                        <p className="text-micro text-gray-500 mt-1">{action.move}</p>
                      </div>
                      
                      <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-gray-600 group-hover:translate-x-0.5 transition-all duration-180" strokeWidth={1.5} />
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Right Column - Sentinel Alerts + Quick Wins */}
        <div className="xl:col-span-1 space-y-6">
          {/* Sentinel Alerts */}
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-black/5">
              <div className="w-8 h-8 border border-black/10 bg-gray-50 flex items-center justify-center">
                <AlertCircle className="w-4 h-4 text-black" strokeWidth={1.5} />
              </div>
              <div>
                <span className="text-micro text-gray-400 block">System</span>
                <h3 className="text-xl font-serif text-black tracking-tight">Sentinel</h3>
              </div>
            </div>

            <div className="space-y-2">
              <AnimatePresence>
                {sentinelAlerts.length === 0 ? (
                  <div className="text-center py-10">
                    <CheckCircle2 className="w-5 h-5 mx-auto mb-3 text-black" strokeWidth={1.5} />
                    <p className="text-micro text-gray-400">All Clear</p>
                  </div>
                ) : (
                  sentinelAlerts.slice(0, 5).map((alert, index) => {
                    // Only use oxblood for severity >= 4 (5% accent rule)
                    const isHighSeverity = alert.severity >= 4
                    return (
                      <motion.div
                        key={alert.id}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05, duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
                        className={cn(
                          "group flex items-start gap-3 py-3 px-3 border-l-2 hover:bg-gray-50 transition-colors duration-180 cursor-pointer",
                          isHighSeverity ? "border-oxblood" : "border-gray-300"
                        )}
                      >
                        <div 
                          className={cn(
                            "w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0",
                            isHighSeverity ? "bg-oxblood" : "bg-gray-400"
                          )}
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium text-black leading-tight mb-1">
                            {alert.message}
                          </p>
                          {alert.move && (
                            <p className="text-micro text-gray-500">
                              {alert.move}
                            </p>
                          )}
                        </div>
                      </motion.div>
                    )
                  })
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Quick Wins Teaser */}
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 border border-black/10 bg-white flex items-center justify-center">
                <Trophy className="w-4 h-4 text-black" strokeWidth={1.5} />
              </div>
              <div>
                <span className="text-micro text-gray-400 block">Available</span>
                <h3 className="text-xl font-serif text-black tracking-tight">Quick Wins</h3>
              </div>
            </div>
            <p className="text-caption mb-4">
              Unlock capabilities by completing moves and achieving milestones.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
