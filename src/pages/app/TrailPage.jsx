import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Crosshair, 
  Plus, 
  Search, 
  Filter,
  MoreHorizontal,
  User,
  Building2,
  Mail,
  MessageSquare,
  Linkedin,
  Phone,
  ChevronDown,
  Trash2,
  Edit2,
  X
} from 'lucide-react'
import useRaptorflowStore from '../../store/raptorflowStore'
import { Modal } from '@/components/system/Modal'

// Status options
const TARGET_STATUSES = [
  { id: 'new', label: 'New', color: 'bg-ink-300' },
  { id: 'contacted', label: 'Contacted', color: 'bg-ink-300' },
  { id: 'replied', label: 'Replied', color: 'bg-ink-300' },
  { id: 'booked', label: 'Booked', color: 'bg-ink-300' },
  { id: 'qualified', label: 'Qualified', color: 'bg-ink-300' },
  { id: 'lost', label: 'Lost', color: 'bg-ink-300' }
]

// Channel icons
const CHANNEL_ICONS = {
  linkedin: Linkedin,
  email: Mail,
  whatsapp: MessageSquare,
  phone: Phone
}

// Status badge
const StatusBadge = ({ status, onChange }) => {
  const [isOpen, setIsOpen] = useState(false)
  const rootRef = useRef(null)
  const currentStatus = TARGET_STATUSES.find(s => s.id === status) || TARGET_STATUSES[0]

  useEffect(() => {
    if (!isOpen) return

    const onKeyDown = (e) => {
      if (e.key === 'Escape') setIsOpen(false)
    }

    const onPointerDown = (e) => {
      if (!rootRef.current) return
      if (!rootRef.current.contains(e.target)) setIsOpen(false)
    }

    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('pointerdown', onPointerDown)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('pointerdown', onPointerDown)
    }
  }, [isOpen])
  
  return (
    <div ref={rootRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        className={`flex items-center gap-2 px-2 py-1 rounded text-body-xs text-white ${currentStatus.color}`}
      >
        {currentStatus.label}
        <ChevronDown className="w-3 h-3" strokeWidth={1.5} />
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              role="menu"
              className="absolute right-0 top-full mt-1 w-32 bg-card border border-border rounded-lg shadow-lg z-20 py-1"
            >
              {TARGET_STATUSES.map(s => (
                <button
                  key={s.id}
                  onClick={() => {
                    onChange(s.id)
                    setIsOpen(false)
                  }}
                  role="menuitem"
                  className="w-full flex items-center gap-2 px-3 py-2 text-body-xs text-ink hover:bg-paper-200 transition-editorial"
                >
                  <div className={`w-2 h-2 rounded-full ${s.color}`} />
                  {s.label}
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// Target row
const TargetRow = ({ target, onStatusChange, onDelete }) => {
  const ChannelIcon = CHANNEL_ICONS[target.channel] || Mail
  const [showMenu, setShowMenu] = useState(false)
  
  return (
    <motion.tr
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="border-b border-border-light hover:bg-paper-200 transition-editorial"
    >
      <td className="px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-paper-200 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
          </div>
          <div>
            <div className="text-body-sm text-ink font-medium">{target.name}</div>
            <div className="text-body-xs text-ink-400">{target.handle}</div>
          </div>
        </div>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
          <span className="text-body-sm text-ink">{target.company}</span>
        </div>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <ChannelIcon className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
          <span className="text-body-sm text-ink capitalize">{target.channel}</span>
        </div>
      </td>
      <td className="px-4 py-3">
        <StatusBadge 
          status={target.status} 
          onChange={(status) => onStatusChange(target.id, status)} 
        />
      </td>
      <td className="px-4 py-3">
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 text-ink-400 hover:text-ink hover:bg-paper-200 rounded transition-editorial"
          >
            <MoreHorizontal className="w-4 h-4" strokeWidth={1.5} />
          </button>
          
          <AnimatePresence>
            {showMenu && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="absolute right-0 top-full mt-1 w-36 bg-card border border-border rounded-lg shadow-lg z-20 py-1"
                >
                  <button
                    onClick={() => {
                      setShowMenu(false)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-body-xs text-ink hover:bg-paper-200 transition-editorial"
                  >
                    <Edit2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      onDelete(target.id)
                      setShowMenu(false)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-body-xs text-ink hover:bg-paper-200 transition-editorial"
                  >
                    <Trash2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Delete
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </td>
    </motion.tr>
  )
}

// Add Target Modal
const AddTargetModal = ({ isOpen, onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    channel: 'linkedin',
    handle: ''
  })

  const handleSubmit = () => {
    if (!formData.name || !formData.company) return
    onAdd(formData)
    setFormData({ name: '', company: '', channel: 'linkedin', handle: '' })
    onClose()
  }

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => !open && onClose()}
      title="Add Target"
      description="Add a new pursuit target"
      contentClassName="max-w-md"
    >
      <div className="space-y-4">
        <div>
          <label className="block text-body-sm text-ink mb-2">Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="John Smith"
            className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>
        
        <div>
          <label className="block text-body-sm text-ink mb-2">Company</label>
          <input
            type="text"
            value={formData.company}
            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
            placeholder="Acme Inc"
            className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>
        
        <div>
          <label className="block text-body-sm text-ink mb-2">Channel</label>
          <select
            value={formData.channel}
            onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
            className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="email">Email</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="phone">Phone</option>
          </select>
        </div>
        
        <div>
          <label className="block text-body-sm text-ink mb-2">Handle / Contact</label>
          <input
            type="text"
            value={formData.handle}
            onChange={(e) => setFormData({ ...formData, handle: e.target.value })}
            placeholder="@johnsmith or john@acme.com"
            className="w-full px-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={!formData.name || !formData.company}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial disabled:opacity-50"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          Add Target
        </button>
      </div>
    </Modal>
  )
}

// Main Trail Page
const TrailPage = () => {
  const { trailTargets, addTrailTarget, updateTargetStatus, deleteTrailTarget } = useRaptorflowStore()
  const [showAddModal, setShowAddModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  // Filter targets
  const filteredTargets = trailTargets.filter(target => {
    const matchesSearch = target.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         target.company.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || target.status === statusFilter
    return matchesSearch && matchesStatus
  })

  // Status counts
  const statusCounts = TARGET_STATUSES.reduce((acc, status) => {
    acc[status.id] = trailTargets.filter(t => t.status === status.id).length
    return acc
  }, {})

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-serif text-headline-md text-ink">Trail</h1>
          <p className="text-body-sm text-ink-400 mt-1">Track and pursue your targets</p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial"
        >
          <Plus className="w-4 h-4" strokeWidth={1.5} />
          Add Target
        </motion.button>
      </div>

      {/* Status summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-6 gap-4 mb-6"
      >
        {TARGET_STATUSES.map(status => (
          <button
            key={status.id}
            onClick={() => setStatusFilter(statusFilter === status.id ? 'all' : status.id)}
            className={`p-3 rounded-xl border transition-editorial ${
              statusFilter === status.id 
                ? 'border-primary bg-signal-muted' 
                : 'border-border bg-card hover:border-border-dark'
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              <div className={`w-2 h-2 rounded-full ${status.color}`} />
              <span className="text-body-xs text-ink-400">{status.label}</span>
            </div>
            <div className="text-xl font-mono text-ink">{statusCounts[status.id] || 0}</div>
          </button>
        ))}
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex items-center gap-4 mb-6"
      >
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-400" strokeWidth={1.5} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search targets..."
            className="w-full pl-10 pr-4 py-2.5 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>
        {statusFilter !== 'all' && (
          <button
            onClick={() => setStatusFilter('all')}
            className="flex items-center gap-1 px-3 py-2 text-body-xs text-ink-400 hover:text-ink border border-border rounded-lg hover:bg-paper-200 transition-editorial"
          >
            Clear filter
            <X className="w-3.5 h-3.5" strokeWidth={1.5} />
          </button>
        )}
      </motion.div>

      {/* Targets table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-card border border-border rounded-xl overflow-hidden"
      >
        {filteredTargets.length > 0 ? (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-paper-200">
                <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400">Name</th>
                <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400">Company</th>
                <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400">Channel</th>
                <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400">Status</th>
                <th className="px-4 py-3 text-left text-body-xs font-medium text-ink-400 w-12"></th>
              </tr>
            </thead>
            <tbody>
              {filteredTargets.map(target => (
                <TargetRow
                  key={target.id}
                  target={target}
                  onStatusChange={updateTargetStatus}
                  onDelete={deleteTrailTarget}
                />
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-16">
            <Crosshair className="w-16 h-16 text-ink-300 mx-auto mb-4" strokeWidth={1.5} />
            <h2 className="font-serif text-xl text-ink mb-2">
              {searchQuery || statusFilter !== 'all' ? 'No targets found' : 'No targets yet'}
            </h2>
            <p className="text-body-sm text-ink-400 mb-6">
              {searchQuery || statusFilter !== 'all' 
                ? 'Try adjusting your search or filters' 
                : 'Add your first target to start pursuing'}
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <button
                onClick={() => setShowAddModal(true)}
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-95 transition-editorial"
              >
                Add your first target
              </button>
            )}
          </div>
        )}
      </motion.div>

      {/* Add Target Modal */}
      <AddTargetModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)}
        onAdd={addTrailTarget}
      />
    </div>
  )
}

export default TrailPage
