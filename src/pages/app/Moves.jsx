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

import { Modal } from '@/components/system/Modal'

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

// Status configuration - Editorial styling
const STATUS_CONFIG = {
  planned: { label: 'Planned', color: 'pill-neutral', kanbanOrder: 0 },
  generating_assets: { label: 'Generating', color: 'pill-accent', kanbanOrder: 1 },
  ready: { label: 'Ready', color: 'pill-accent', kanbanOrder: 2 },
  running: { label: 'Running', color: 'pill-success', kanbanOrder: 3 },
  paused: { label: 'Paused', color: 'pill-warning', kanbanOrder: 3 },
  completed: { label: 'Completed', color: 'pill-success', kanbanOrder: 4 },
  failed: { label: 'Failed', color: 'pill-error', kanbanOrder: 4 }
}

// Move card component - Editorial styling
const MoveCard = ({ move, onClick, view }) => {
  const protocol = PROTOCOLS[move.protocol] || {}
  const statusConfig = STATUS_CONFIG[move.status] || STATUS_CONFIG.planned
  const ProtocolIcon = protocol.icon || Zap

  const progressColor = move.progress_percentage >= 100 
    ? 'bg-success' 
    : move.progress_percentage >= 50 
      ? 'bg-accent' 
      : 'bg-ink-200'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.98 }}
      onClick={onClick}
      className={`card-editorial card-editorial-interactive p-5 ${
        view === 'list' ? 'flex items-center gap-5' : ''
      }`}
    >
      {/* Header */}
      <div className={`${view === 'list' ? 'flex items-center gap-4 flex-1' : ''}`}>
        <div className={`w-10 h-10 rounded-editorial bg-paper-200 flex items-center justify-center ${view === 'list' ? '' : 'mb-4'}`}>
          <ProtocolIcon className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
        </div>
        
        <div className={view === 'list' ? 'flex-1' : ''}>
          <h3 className="font-medium text-ink">{move.name}</h3>
          {view !== 'list' && (
            <p className="text-body-sm text-ink-400 mt-1 line-clamp-2">{move.description}</p>
          )}
        </div>
      </div>

      {/* Protocol & Status */}
      <div className={`flex items-center gap-2 ${view === 'list' ? '' : 'mt-4'}`}>
        <span className="pill-editorial pill-neutral">
          {protocol.label || move.protocol}
        </span>
        <span className={`pill-editorial ${statusConfig.color}`}>
          {statusConfig.label}
        </span>
      </div>

      {/* Progress */}
      {view !== 'list' && (
        <div className="mt-5">
          <div className="flex items-center justify-between text-body-xs text-ink-400 mb-2">
            <span>Progress</span>
            <span>{move.progress_percentage || 0}%</span>
          </div>
          <div className="h-1.5 bg-paper-300 rounded-full overflow-hidden">
            <div 
              className={`h-full ${progressColor} rounded-full transition-all duration-300`}
              style={{ width: `${move.progress_percentage || 0}%` }}
            />
          </div>
        </div>
      )}

      {/* Tasks summary */}
      {view !== 'list' && move.tasks?.length > 0 && (
        <div className="flex items-center gap-2 mt-4 text-body-xs text-ink-400">
          <CheckCircle2 className="w-3.5 h-3.5" strokeWidth={1.5} />
          {move.tasks.filter(t => t.status === 'completed').length}/{move.tasks.length} tasks
        </div>
      )}

      {/* EV Score */}
      {view === 'list' && (
        <div className="text-right">
          <div className="text-caption text-ink-400">EV Score</div>
          <div className="font-serif text-xl text-ink">{move.ev_score?.toFixed(1) || '-'}</div>
        </div>
      )}
    </motion.div>
  )
}

// Template card for library - Editorial styling
const TemplateCard = ({ template, onSelect }) => {
  const protocol = PROTOCOLS[template.protocol] || {}
  const ProtocolIcon = protocol.icon || Zap

  return (
    <motion.div
      whileHover={{ y: -2 }}
      onClick={() => onSelect(template)}
      className="card-editorial card-editorial-interactive p-5"
    >
      <div className="w-12 h-12 rounded-card bg-paper-200 flex items-center justify-center mb-4">
        <ProtocolIcon className="w-6 h-6 text-ink-400" strokeWidth={1.5} />
      </div>
      
      <h3 className="font-medium text-ink mb-1">{template.name}</h3>
      <p className="text-body-sm text-ink-400 mb-4">{protocol.description}</p>
      
      <div className="flex items-center justify-between">
        <span className="pill-editorial pill-neutral">
          {protocol.label}
        </span>
        <div className="flex items-center gap-3 text-body-xs text-ink-400">
          <span>Impact: {template.impact}</span>
          <span>Effort: {template.effort}</span>
        </div>
      </div>
    </motion.div>
  )
}

// Kanban column - Editorial styling
const KanbanColumn = ({ title, moves, onMoveClick }) => {
  return (
    <div className="flex-1 min-w-[280px] max-w-[320px]">
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-medium text-ink-500">{title}</h3>
        <span className="pill-editorial pill-neutral">
          {moves.length}
        </span>
      </div>
      <div className="space-y-4">
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
          <div className="p-8 border border-dashed border-border rounded-card text-center text-ink-400 text-body-sm">
            No moves
          </div>
        )}
      </div>
    </div>
  )
}

// New move modal - Editorial styling
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

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose()
      }}
      title="Create move"
      description={step === 1 ? 'Select a template from the library.' : 'Customize your move.'}
      contentClassName="max-w-4xl"
    >
      <div className="space-y-6">
        <div className="max-h-[60vh] overflow-y-auto pr-1">
          {step === 1 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
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
              <div className="p-5 bg-paper-200 rounded-card border border-border-light">
                <div className="flex items-center gap-4">
                  {selectedTemplate && (() => {
                    const IconComponent = PROTOCOLS[selectedTemplate.protocol]?.icon
                    return (
                      <>
                        <div className="w-12 h-12 rounded-card bg-paper-300 flex items-center justify-center">
                          {IconComponent && <IconComponent className="w-6 h-6 text-ink-500" strokeWidth={1.5} />}
                        </div>
                        <div>
                          <div className="font-medium text-ink">{selectedTemplate.name}</div>
                          <div className="text-body-sm text-ink-400">{PROTOCOLS[selectedTemplate.protocol]?.label}</div>
                        </div>
                      </>
                    )
                  })()}
                </div>
              </div>

              <div>
                <label className="block text-body-sm text-ink-500 mb-2">Move name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Custom move name..."
                  className="input-editorial"
                />
              </div>

              <div className="p-4 bg-signal-muted border border-primary/20 rounded-card">
                <div className="flex items-center gap-2 text-primary text-body-sm">
                  <CheckCircle2 className="w-4 h-4" strokeWidth={1.5} />
                  Tasks and assets will be generated from the template
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => step === 1 ? onClose() : setStep(1)}
            className="btn-editorial btn-ghost"
          >
            {step === 1 ? 'Cancel' : 'Back'}
          </button>

          {step === 2 ? (
            <button
              type="button"
              onClick={handleSubmit}
              className="btn-editorial btn-primary"
            >
              Create move
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : null}
        </div>
      </div>
    </Modal>
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
    <div className="max-w-6xl mx-auto">
      {/* Header - Editorial styling */}
      <div className="flex items-center justify-between mb-10">
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
        >
          <h1 className="font-serif text-headline-lg text-ink">Moves</h1>
          <p className="text-body-md text-ink-400 mt-2">
            Tactical playbooks executing your campaigns
          </p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={() => setShowNewModal(true)}
          className="btn-editorial btn-primary"
        >
          <Plus className="w-4 h-4" />
          New Move
        </motion.button>
      </div>

      {/* Toolbar - Editorial styling */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="flex items-center justify-between mb-8"
      >
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-400" strokeWidth={1.5} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search moves..."
            className="pl-10 pr-4 py-2.5 bg-white border border-border rounded-editorial text-ink placeholder:text-ink-300 focus:border-accent focus:ring-0 outline-none w-64 text-body-sm transition-editorial"
          />
        </div>

        <div className="flex items-center gap-5">
          {/* Filter */}
          <div className="flex items-center gap-1">
            {['all', 'planned', 'running', 'completed'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-3 py-2 rounded-editorial text-body-sm transition-editorial ${
                  filter === status
                    ? 'bg-paper-300 text-ink'
                    : 'text-ink-400 hover:text-ink hover:bg-paper-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>

          {/* View toggle */}
          <div className="flex items-center bg-paper-200 rounded-editorial p-1">
            <button
              onClick={() => setView('kanban')}
              className={`p-2 rounded-editorial transition-editorial ${view === 'kanban' ? 'bg-white shadow-editorial-sm' : ''}`}
            >
              <Layers className={`w-4 h-4 ${view === 'kanban' ? 'text-ink' : 'text-ink-400'}`} strokeWidth={1.5} />
            </button>
            <button
              onClick={() => setView('grid')}
              className={`p-2 rounded-editorial transition-editorial ${view === 'grid' ? 'bg-white shadow-editorial-sm' : ''}`}
            >
              <LayoutGrid className={`w-4 h-4 ${view === 'grid' ? 'text-ink' : 'text-ink-400'}`} strokeWidth={1.5} />
            </button>
            <button
              onClick={() => setView('list')}
              className={`p-2 rounded-editorial transition-editorial ${view === 'list' ? 'bg-white shadow-editorial-sm' : ''}`}
            >
              <List className={`w-4 h-4 ${view === 'list' ? 'text-ink' : 'text-ink-400'}`} strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Content */}
      {loading ? (
        <div className="grid grid-cols-3 gap-5">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-48 skeleton rounded-card" />
          ))}
        </div>
      ) : view === 'kanban' ? (
        <div className="flex gap-8 overflow-x-auto pb-4 scrollbar-hide">
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
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
        <div className="space-y-3">
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

      {/* Empty state - Editorial styling */}
      {!loading && filteredMoves.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="empty-state py-20"
        >
          <div className="w-16 h-16 bg-paper-200 rounded-card flex items-center justify-center mx-auto mb-5">
            <Zap className="w-7 h-7 text-ink-300" strokeWidth={1.5} />
          </div>
          <h3 className="font-serif text-headline-xs text-ink mb-2">No moves yet</h3>
          <p className="text-body-md text-ink-400 mb-6 max-w-sm">Create your first move from the template library</p>
          <button
            onClick={() => setShowNewModal(true)}
            className="btn-editorial btn-primary"
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
