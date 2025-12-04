import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, 
  Play, 
  Pause, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  ChevronRight,
  Filter,
  Search,
  LayoutGrid,
  List,
  Zap,
  Target,
  Shield,
  Users,
  TrendingUp,
  AlertTriangle,
  X,
  ArrowRight,
  Layers
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

// Protocol configuration
const PROTOCOLS = {
  A_AUTHORITY_BLITZ: { 
    label: 'Authority Blitz', 
    color: 'purple',
    icon: Zap,
    description: 'Build thought leadership through content'
  },
  B_TRUST_ANCHOR: { 
    label: 'Trust Anchor', 
    color: 'blue',
    icon: Shield,
    description: 'Build credibility with social proof'
  },
  C_COST_OF_INACTION: { 
    label: 'Cost of Inaction', 
    color: 'amber',
    icon: Clock,
    description: 'Create urgency through consequences'
  },
  D_HABIT_HARDCODE: { 
    label: 'Habit Hardcode', 
    color: 'green',
    icon: Target,
    description: 'Drive activation and retention'
  },
  E_ENTERPRISE_WEDGE: { 
    label: 'Enterprise Wedge', 
    color: 'cyan',
    icon: Users,
    description: 'Enable expansion within accounts'
  },
  F_CHURN_INTERCEPT: { 
    label: 'Churn Intercept', 
    color: 'red',
    icon: AlertTriangle,
    description: 'Prevent and recover churning users'
  }
}

// Move templates
const MOVE_TEMPLATES = [
  { slug: 'content-waterfall', name: 'Content Waterfall', protocol: 'A_AUTHORITY_BLITZ', impact: 75, effort: 60 },
  { slug: 'validation-loop', name: 'Validation Loop', protocol: 'B_TRUST_ANCHOR', impact: 80, effort: 70 },
  { slug: 'spear-attack', name: 'Spear Attack', protocol: 'C_COST_OF_INACTION', impact: 85, effort: 80 },
  { slug: 'facilitator-nudge', name: 'Facilitator Nudge', protocol: 'D_HABIT_HARDCODE', impact: 70, effort: 65 },
  { slug: 'champions-armory', name: "Champion's Armory", protocol: 'E_ENTERPRISE_WEDGE', impact: 90, effort: 75 },
  { slug: 'churn-intercept-sequence', name: 'Churn Intercept', protocol: 'F_CHURN_INTERCEPT', impact: 85, effort: 60 }
]

// Status configuration
const STATUS_CONFIG = {
  planned: { label: 'Planned', color: 'bg-white/10 text-white/60', kanbanOrder: 0 },
  generating_assets: { label: 'Generating', color: 'bg-purple-500/20 text-purple-400', kanbanOrder: 1 },
  ready: { label: 'Ready', color: 'bg-blue-500/20 text-blue-400', kanbanOrder: 2 },
  running: { label: 'Running', color: 'bg-emerald-500/20 text-emerald-400', kanbanOrder: 3 },
  paused: { label: 'Paused', color: 'bg-amber-500/20 text-amber-400', kanbanOrder: 3 },
  completed: { label: 'Completed', color: 'bg-emerald-500/20 text-emerald-400', kanbanOrder: 4 },
  failed: { label: 'Failed', color: 'bg-red-500/20 text-red-400', kanbanOrder: 4 }
}

// Move card component
const MoveCard = ({ move, onClick, view }) => {
  const protocol = PROTOCOLS[move.protocol] || {}
  const statusConfig = STATUS_CONFIG[move.status] || STATUS_CONFIG.planned
  const ProtocolIcon = protocol.icon || Zap

  const progressColor = move.progress_percentage >= 100 
    ? 'bg-emerald-500' 
    : move.progress_percentage >= 50 
      ? 'bg-blue-500' 
      : 'bg-white/30'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 cursor-pointer hover:border-white/20 transition-all ${
        view === 'list' ? 'flex items-center gap-4' : ''
      }`}
    >
      {/* Header */}
      <div className={`${view === 'list' ? 'flex items-center gap-3 flex-1' : ''}`}>
        <div className={`w-10 h-10 rounded-lg bg-${protocol.color || 'white'}-500/20 flex items-center justify-center ${view === 'list' ? '' : 'mb-3'}`}>
          <ProtocolIcon className={`w-5 h-5 text-${protocol.color || 'white'}-400`} />
        </div>
        
        <div className={view === 'list' ? 'flex-1' : ''}>
          <h3 className="font-medium text-white">{move.name}</h3>
          {view !== 'list' && (
            <p className="text-sm text-white/40 mt-1 line-clamp-2">{move.description}</p>
          )}
        </div>
      </div>

      {/* Protocol & Status */}
      <div className={`flex items-center gap-2 ${view === 'list' ? '' : 'mt-3'}`}>
        <span className={`px-2 py-0.5 rounded text-xs border border-${protocol.color || 'white'}-500/30 bg-${protocol.color || 'white'}-500/20 text-${protocol.color || 'white'}-400`}>
          {protocol.label || move.protocol}
        </span>
        <span className={`px-2 py-0.5 rounded text-xs ${statusConfig.color}`}>
          {statusConfig.label}
        </span>
      </div>

      {/* Progress */}
      {view !== 'list' && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-white/40 mb-1">
            <span>Progress</span>
            <span>{move.progress_percentage || 0}%</span>
          </div>
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div 
              className={`h-full ${progressColor} rounded-full transition-all`}
              style={{ width: `${move.progress_percentage || 0}%` }}
            />
          </div>
        </div>
      )}

      {/* Tasks summary */}
      {view !== 'list' && move.tasks?.length > 0 && (
        <div className="flex items-center gap-2 mt-3 text-xs text-white/40">
          <CheckCircle2 className="w-3 h-3" />
          {move.tasks.filter(t => t.status === 'completed').length}/{move.tasks.length} tasks
        </div>
      )}

      {/* EV Score */}
      {view === 'list' && (
        <div className="text-right">
          <div className="text-xs text-white/40">EV Score</div>
          <div className="text-lg font-medium text-white">{move.ev_score?.toFixed(1) || '-'}</div>
        </div>
      )}
    </motion.div>
  )
}

// Template card for library
const TemplateCard = ({ template, onSelect }) => {
  const protocol = PROTOCOLS[template.protocol] || {}
  const ProtocolIcon = protocol.icon || Zap

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      onClick={() => onSelect(template)}
      className="bg-white/5 border border-white/10 rounded-xl p-4 cursor-pointer hover:border-white/20 transition-all"
    >
      <div className={`w-12 h-12 rounded-xl bg-${protocol.color || 'white'}-500/20 flex items-center justify-center mb-3`}>
        <ProtocolIcon className={`w-6 h-6 text-${protocol.color || 'white'}-400`} />
      </div>
      
      <h3 className="font-medium text-white mb-1">{template.name}</h3>
      <p className="text-sm text-white/40 mb-3">{protocol.description}</p>
      
      <div className="flex items-center justify-between text-sm">
        <span className={`px-2 py-0.5 rounded text-xs border border-${protocol.color || 'white'}-500/30 bg-${protocol.color || 'white'}-500/20 text-${protocol.color || 'white'}-400`}>
          {protocol.label}
        </span>
        <div className="flex items-center gap-3 text-white/40">
          <span>Impact: {template.impact}</span>
          <span>Effort: {template.effort}</span>
        </div>
      </div>
    </motion.div>
  )
}

// Kanban column
const KanbanColumn = ({ title, moves, onMoveClick }) => {
  return (
    <div className="flex-1 min-w-[280px] max-w-[320px]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-white/60">{title}</h3>
        <span className="px-2 py-0.5 bg-white/10 rounded text-xs text-white/40">
          {moves.length}
        </span>
      </div>
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {moves.map(move => (
            <MoveCard 
              key={move.id} 
              move={move} 
              onClick={() => onMoveClick(move)}
              view="kanban"
            />
          ))}
        </AnimatePresence>
        {moves.length === 0 && (
          <div className="p-6 border border-dashed border-white/20 rounded-xl text-center text-white/30 text-sm">
            No moves
          </div>
        )}
      </div>
    </div>
  )
}

// New move modal
const NewMoveModal = ({ isOpen, onClose, templates, onSubmit }) => {
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [name, setName] = useState('')
  const [step, setStep] = useState(1)

  const handleSubmit = () => {
    onSubmit({
      template_slug: selectedTemplate?.slug,
      name: name || selectedTemplate?.name,
      protocol: selectedTemplate?.protocol
    })
    onClose()
    setSelectedTemplate(null)
    setName('')
    setStep(1)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-[#0a0a0f] border border-white/10 rounded-2xl w-full max-w-4xl max-h-[80vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h2 className="text-xl font-medium text-white">Create Move</h2>
            <p className="text-sm text-white/40">
              {step === 1 ? 'Select a template from the library' : 'Customize your move'}
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
            <X className="w-5 h-5 text-white/60" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {step === 1 ? (
            <div className="grid grid-cols-2 gap-4">
              {templates.map(template => (
                <TemplateCard
                  key={template.slug}
                  template={template}
                  onSelect={(t) => {
                    setSelectedTemplate(t)
                    setName(t.name)
                    setStep(2)
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                <div className="flex items-center gap-3">
                  {selectedTemplate && (() => {
                    const IconComponent = PROTOCOLS[selectedTemplate.protocol]?.icon
                    const color = PROTOCOLS[selectedTemplate.protocol]?.color || 'white'
                    return (
                      <>
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center`} style={{ backgroundColor: `var(--${color}-500, rgba(255,255,255,0.2))` }}>
                          {IconComponent && <IconComponent className="w-5 h-5 text-white" />}
                        </div>
                        <div>
                          <div className="font-medium text-white">{selectedTemplate.name}</div>
                          <div className="text-sm text-white/40">{PROTOCOLS[selectedTemplate.protocol]?.label}</div>
                        </div>
                      </>
                    )
                  })()}
                </div>
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">Move Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Custom move name..."
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none"
                />
              </div>

              <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                <div className="flex items-center gap-2 text-emerald-400 text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  Tasks and assets will be generated from the template
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-white/10 bg-white/5">
          <button
            onClick={() => step === 1 ? onClose() : setStep(1)}
            className="px-4 py-2 text-white/60 hover:text-white transition-colors"
          >
            {step === 1 ? 'Cancel' : 'Back'}
          </button>
          
          {step === 2 && (
            <button
              onClick={handleSubmit}
              className="px-6 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors flex items-center gap-2"
            >
              Create Move
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </motion.div>
    </div>
  )
}

// Main Moves page
const Moves = () => {
  const { user } = useAuth()
  const [moves, setMoves] = useState([])
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState('kanban') // 'kanban', 'grid', 'list'
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [showNewModal, setShowNewModal] = useState(false)

  useEffect(() => {
    const fetchMoves = async () => {
      setLoading(true)
      try {
        // Start with empty - user creates their own moves
        setMoves([])
      } catch (error) {
        console.error('Error fetching moves:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMoves()
  }, [])

  const handleCreateMove = (data) => {
    console.log('Creating move:', data)
    const newMove = {
      id: `move-${Date.now()}`,
      name: data.name,
      description: `New move from ${data.template_slug} template`,
      protocol: data.protocol,
      status: 'planned',
      progress_percentage: 0,
      ev_score: 1.0,
      tasks: []
    }
    setMoves([newMove, ...moves])
  }

  // Filter moves
  const filteredMoves = moves.filter(move => {
    if (filter !== 'all' && move.status !== filter) return false
    if (search && !move.name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  // Group moves by status for kanban
  const kanbanGroups = {
    'Planned': filteredMoves.filter(m => m.status === 'planned'),
    'In Progress': filteredMoves.filter(m => ['generating_assets', 'ready', 'running'].includes(m.status)),
    'Paused': filteredMoves.filter(m => m.status === 'paused'),
    'Completed': filteredMoves.filter(m => ['completed', 'failed'].includes(m.status))
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">Moves</h1>
          <p className="text-white/40 mt-1">
            Tactical playbooks executing your campaigns
          </p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={() => setShowNewModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Move
        </motion.button>
      </div>

      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex items-center justify-between mb-6"
      >
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search moves..."
            className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none w-64"
          />
        </div>

        <div className="flex items-center gap-4">
          {/* Filter */}
          <div className="flex items-center gap-2">
            {['all', 'planned', 'running', 'completed'].map((status) => (
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
          </div>

          {/* View toggle */}
          <div className="flex items-center bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setView('kanban')}
              className={`p-2 rounded ${view === 'kanban' ? 'bg-white/10' : ''}`}
            >
              <Layers className={`w-4 h-4 ${view === 'kanban' ? 'text-white' : 'text-white/40'}`} />
            </button>
            <button
              onClick={() => setView('grid')}
              className={`p-2 rounded ${view === 'grid' ? 'bg-white/10' : ''}`}
            >
              <LayoutGrid className={`w-4 h-4 ${view === 'grid' ? 'text-white' : 'text-white/40'}`} />
            </button>
            <button
              onClick={() => setView('list')}
              className={`p-2 rounded ${view === 'list' ? 'bg-white/10' : ''}`}
            >
              <List className={`w-4 h-4 ${view === 'list' ? 'text-white' : 'text-white/40'}`} />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Content */}
      {loading ? (
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-48 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : view === 'kanban' ? (
        <div className="flex gap-6 overflow-x-auto pb-4">
          {Object.entries(kanbanGroups).map(([title, groupMoves]) => (
            <KanbanColumn
              key={title}
              title={title}
              moves={groupMoves}
              onMoveClick={(move) => console.log('Selected:', move)}
            />
          ))}
        </div>
      ) : view === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence mode="popLayout">
            {filteredMoves.map(move => (
              <MoveCard
                key={move.id}
                move={move}
                onClick={() => console.log('Selected:', move)}
                view="grid"
              />
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <div className="space-y-2">
          <AnimatePresence mode="popLayout">
            {filteredMoves.map(move => (
              <MoveCard
                key={move.id}
                move={move}
                onClick={() => console.log('Selected:', move)}
                view="list"
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Empty state */}
      {!loading && filteredMoves.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Zap className="w-8 h-8 text-white/20" />
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No moves yet</h3>
          <p className="text-white/40 mb-6">Create your first move from the template library</p>
          <button
            onClick={() => setShowNewModal(true)}
            className="px-4 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors"
          >
            Create Move
          </button>
        </motion.div>
      )}

      {/* New Move Modal */}
      <AnimatePresence>
        {showNewModal && (
          <NewMoveModal
            isOpen={showNewModal}
            onClose={() => setShowNewModal(false)}
            templates={MOVE_TEMPLATES}
            onSubmit={handleCreateMove}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default Moves
