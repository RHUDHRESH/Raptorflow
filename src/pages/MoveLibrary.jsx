import { useState, useMemo, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { 
  Target, 
  Search, 
  Filter, 
  Lock, 
  Eye, 
  Plus,
  Sparkles,
  Zap,
  Bell,
  ArrowRight,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { cn } from '../utils/cn'
import { 
  generateMockManeuverTypes,
  generateMockCapabilityNodes,
  Posture,
  FoggRole,
  CapabilityTier,
  createMove,
  MoveStatus
} from '../utils/moveSystemTypes'

export default function MoveLibrary() {
  const navigate = useNavigate()
  const [maneuverTypes] = useState(generateMockManeuverTypes())
  const [capabilityNodes] = useState(generateMockCapabilityNodes())
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPosture, setSelectedPosture] = useState('all')
  const [selectedTier, setSelectedTier] = useState('all')
  const [selectedFogg, setSelectedFogg] = useState('all')
  const [previewManeuver, setPreviewManeuver] = useState(null)
  const [showInstantiateModal, setShowInstantiateModal] = useState(false)
  const [selectedManeuverForInstantiate, setSelectedManeuverForInstantiate] = useState(null)
  const unlockedScrollRef = useRef(null)
  const lockedScrollRef = useRef(null)
  const [showUnlockedLeftArrow, setShowUnlockedLeftArrow] = useState(false)
  const [showUnlockedRightArrow, setShowUnlockedRightArrow] = useState(true)
  const [showLockedLeftArrow, setShowLockedLeftArrow] = useState(false)
  const [showLockedRightArrow, setShowLockedRightArrow] = useState(true)

  // Check scroll position on mount and when filtered maneuvers change
  useEffect(() => {
    const checkScroll = () => {
      if (unlockedScrollRef.current) {
        handleScroll(unlockedScrollRef.current, setShowUnlockedLeftArrow, setShowUnlockedRightArrow)
      }
      if (lockedScrollRef.current) {
        handleScroll(lockedScrollRef.current, setShowLockedLeftArrow, setShowLockedRightArrow)
      }
    }
    
    checkScroll()
    // Also check after a short delay to ensure DOM is ready
    const timeout = setTimeout(checkScroll, 100)
    return () => clearTimeout(timeout)
  }, [filteredManeuvers, lockedManeuvers])

  const unlockedCapabilityIds = useMemo(() => {
    return capabilityNodes
      .filter(node => node.status === 'Unlocked')
      .map(node => node.id)
  }, [capabilityNodes])

  // Check if maneuver is unlocked
  const isManeuverUnlocked = (mt) => {
    // If no requirements, it's unlocked
    if (!mt.required_capability_ids || mt.required_capability_ids.length === 0) {
      return true
    }
    // Check if all required capabilities are unlocked
    return mt.required_capability_ids.every(id => 
      unlockedCapabilityIds.includes(id)
    )
  }

  // Apply filters to maneuvers
  const applyFilters = (mt) => {
    const matchesSearch = !searchQuery || 
      mt.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (mt.description && mt.description.toLowerCase().includes(searchQuery.toLowerCase()))
    
    const matchesPosture = selectedPosture === 'all' || mt.category === selectedPosture
    const matchesTier = selectedTier === 'all' || mt.tier === selectedTier
    
    // Fogg role filter: if 'all', show all. Otherwise, only show maneuvers with matching fogg_role
    const matchesFogg = selectedFogg === 'all' || mt.fogg_role === selectedFogg

    return matchesSearch && matchesPosture && matchesTier && matchesFogg
  }

  const filteredManeuvers = useMemo(() => {
    return maneuverTypes.filter(mt => {
      return applyFilters(mt) && isManeuverUnlocked(mt)
    })
  }, [maneuverTypes, searchQuery, selectedPosture, selectedTier, selectedFogg, unlockedCapabilityIds])

  const lockedManeuvers = useMemo(() => {
    return maneuverTypes.filter(mt => {
      return applyFilters(mt) && !isManeuverUnlocked(mt)
    })
  }, [maneuverTypes, searchQuery, selectedPosture, selectedTier, selectedFogg, unlockedCapabilityIds])

  const getPostureColor = (posture) => {
    const colors = {
      [Posture.OFFENSIVE]: 'bg-red-100 text-red-900 border-red-200',
      [Posture.DEFENSIVE]: 'bg-blue-100 text-blue-900 border-blue-200',
      [Posture.LOGISTICAL]: 'bg-purple-100 text-purple-900 border-purple-200',
      [Posture.RECON]: 'bg-green-100 text-green-900 border-green-200'
    }
    return colors[posture] || 'bg-neutral-100 text-neutral-900 border-neutral-200'
  }

  const getFoggIcon = (role) => {
    const icons = {
      [FoggRole.SPARK]: Sparkles,
      [FoggRole.FACILITATOR]: Zap,
      [FoggRole.SIGNAL]: Bell
    }
    return icons[role] || Target
  }

  const getMissingCapabilities = (maneuverType) => {
    return maneuverType.required_capability_ids.filter(id => 
      !unlockedCapabilityIds.includes(id)
    ).map(id => {
      const node = capabilityNodes.find(n => n.id === id)
      return node?.name || id
    })
  }

  const handlePreview = (maneuverType) => {
    setPreviewManeuver(maneuverType)
  }

  const handleInstantiate = (maneuverType) => {
    setSelectedManeuverForInstantiate(maneuverType)
    setShowInstantiateModal(true)
  }

  const confirmInstantiate = () => {
    if (selectedManeuverForInstantiate) {
      // Create a new Move instance from the ManeuverType
      const newMove = {
        ...createMove({
          maneuver_type_id: selectedManeuverForInstantiate.id,
          status: MoveStatus.PLANNING
        }),
        name: `${selectedManeuverForInstantiate.name} – New Move`
      }
      
      // In production, this would save to backend/state management
      // For now, navigate to War Room or Move Detail
      setShowInstantiateModal(false)
      setSelectedManeuverForInstantiate(null)
      
      // Navigate to War Room to add the move to a sprint
      navigate('/moves/war-room', { 
        state: { 
          newMove: newMove,
          maneuverType: selectedManeuverForInstantiate
        } 
      })
    }
  }

  const scrollLeft = (ref) => {
    if (ref?.current) {
      ref.current.scrollBy({ left: -400, behavior: 'smooth' })
    }
  }

  const scrollRight = (ref) => {
    if (ref?.current) {
      ref.current.scrollBy({ left: 400, behavior: 'smooth' })
    }
  }

  const handleScroll = (element, setLeftArrow, setRightArrow) => {
    if (element) {
      const { scrollLeft, scrollWidth, clientWidth } = element
      setLeftArrow(scrollLeft > 0)
      setRightArrow(scrollLeft < scrollWidth - clientWidth - 10)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <span className="micro-label tracking-[0.5em]">Move Library</span>
            <span className="h-px w-16 bg-neutral-200" />
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-400">Maneuver Templates</span>
          </div>
          <div className="space-y-4">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Maneuver Arsenal
            </h1>
            <p className="font-sans text-base text-neutral-600 max-w-2xl leading-relaxed">
              Browse and instantiate tactical maneuvers. Locked maneuvers require capability unlocks from the Tech Tree.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="runway-card p-4">
          <div className="text-sm text-neutral-600 mb-1">Total Maneuvers</div>
          <div className="text-2xl font-bold text-neutral-900">{maneuverTypes.length}</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-sm text-neutral-600 mb-1">Available</div>
          <div className="text-2xl font-bold text-green-600">{filteredManeuvers.length}</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-sm text-neutral-600 mb-1">Locked</div>
          <div className="text-2xl font-bold text-neutral-600">{lockedManeuvers.length}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="runway-card p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              placeholder="Search maneuvers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent"
            />
          </div>

          {/* Posture Filter */}
          <div className="relative">
            <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <select
              value={selectedPosture}
              onChange={(e) => setSelectedPosture(e.target.value)}
              className="pl-12 pr-8 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent appearance-none"
            >
              <option value="all">All Postures</option>
              {Object.values(Posture).map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          {/* Tier Filter */}
          <div className="relative">
            <select
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              className="pl-4 pr-8 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent appearance-none"
            >
              <option value="all">All Tiers</option>
              {Object.values(CapabilityTier).map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          {/* Fogg Role Filter */}
          <div className="relative">
            <select
              value={selectedFogg}
              onChange={(e) => setSelectedFogg(e.target.value)}
              className="pl-4 pr-8 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent appearance-none"
            >
              <option value="all">All Fogg Roles</option>
              {Object.values(FoggRole).map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Unlocked Maneuvers */}
      <div>
        <h2 className="text-xl font-bold text-neutral-900 mb-4">
          Available Maneuvers {filteredManeuvers.length > 0 && `(${filteredManeuvers.length})`}
        </h2>
        {filteredManeuvers.length === 0 ? (
          <div className="runway-card p-12 text-center">
            <Target className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-neutral-900 mb-2">No maneuvers match your filters</h3>
            <p className="text-sm text-neutral-600 mb-6">
              Try adjusting your search or filter criteria
            </p>
            <button
              onClick={() => {
                setSearchQuery('')
                setSelectedPosture('all')
                setSelectedTier('all')
                setSelectedFogg('all')
              }}
              className="inline-flex items-center gap-2 px-4 py-2 border border-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="relative group">
            {/* Left Arrow */}
            {showUnlockedLeftArrow && (
              <button
                onClick={() => scrollLeft(unlockedScrollRef)}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white border-2 border-neutral-200 shadow-lg flex items-center justify-center hover:bg-neutral-50 hover:border-neutral-900 transition-all"
                aria-label="Scroll left"
              >
                <ChevronLeft className="w-5 h-5 text-neutral-900" />
              </button>
            )}
            
            {/* Right Arrow */}
            {showUnlockedRightArrow && (
              <button
                onClick={() => scrollRight(unlockedScrollRef)}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white border-2 border-neutral-200 shadow-lg flex items-center justify-center hover:bg-neutral-50 hover:border-neutral-900 transition-all"
                aria-label="Scroll right"
              >
                <ChevronRight className="w-5 h-5 text-neutral-900" />
              </button>
            )}

            {/* Horizontal Scrollable Container */}
            <div 
              ref={unlockedScrollRef}
              onScroll={() => handleScroll(unlockedScrollRef.current, setShowUnlockedLeftArrow, setShowUnlockedRightArrow)}
              className="overflow-x-auto pb-4 -mx-2 px-2 custom-scrollbar"
            >
              <div className="flex gap-6 min-w-max">
                {filteredManeuvers.map((mt, index) => {
                const FoggIcon = mt.fogg_role ? getFoggIcon(mt.fogg_role) : Target
                
                return (
                  <motion.div
                    key={mt.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="runway-card p-6 hover:shadow-xl transition-all group flex-shrink-0 w-80"
                  >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-neutral-900 mb-2">{mt.name}</h3>
                    <div className="flex items-center gap-2 flex-wrap mb-2">
                      <span className={cn(
                        "px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] border rounded",
                        getPostureColor(mt.category)
                      )}>
                        {mt.category}
                      </span>
                      {mt.fogg_role && (
                        <span className="flex items-center gap-1 px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                          <FoggIcon className="w-3 h-3" />
                          {mt.fogg_role}
                        </span>
                      )}
                      <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                        {mt.tier}
                      </span>
                    </div>
                  </div>
                  <Target className="w-6 h-6 text-neutral-400 group-hover:text-neutral-900 transition-colors" />
                </div>

                {/* Description */}
                <p className="text-sm text-neutral-600 mb-4">{mt.description}</p>

                {/* Details */}
                <div className="space-y-2 mb-4 text-xs text-neutral-600">
                  <div className="flex items-center justify-between">
                    <span>Duration:</span>
                    <span className="font-medium">{mt.base_duration_days} days</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Intensity:</span>
                    <span className="font-medium">{mt.intensity_score}/10</span>
                  </div>
                  {mt.typical_icps && mt.typical_icps.length > 0 && (
                    <div>
                      <span className="text-neutral-500">Good for: </span>
                      <span className="font-medium">{mt.typical_icps.join(', ')}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-4 border-t border-neutral-200">
                  <button 
                    onClick={() => handlePreview(mt)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    Preview
                  </button>
                  <button 
                    onClick={() => handleInstantiate(mt)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium bg-neutral-900 text-white hover:bg-neutral-800 rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    Instantiate
                  </button>
                </div>
                  </motion.div>
                )
              })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Locked Maneuvers */}
      {lockedManeuvers.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <Lock className="w-5 h-5" />
            Locked Maneuvers ({lockedManeuvers.length})
          </h2>
          <div className="relative group">
            {/* Left Arrow */}
            {showLockedLeftArrow && (
              <button
                onClick={() => scrollLeft(lockedScrollRef)}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white border-2 border-neutral-200 shadow-lg flex items-center justify-center hover:bg-neutral-50 hover:border-neutral-900 transition-all"
                aria-label="Scroll left"
              >
                <ChevronLeft className="w-5 h-5 text-neutral-900" />
              </button>
            )}
            
            {/* Right Arrow */}
            {showLockedRightArrow && (
              <button
                onClick={() => scrollRight(lockedScrollRef)}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white border-2 border-neutral-200 shadow-lg flex items-center justify-center hover:bg-neutral-50 hover:border-neutral-900 transition-all"
                aria-label="Scroll right"
              >
                <ChevronRight className="w-5 h-5 text-neutral-900" />
              </button>
            )}

            {/* Horizontal Scrollable Container */}
            <div 
              ref={lockedScrollRef}
              onScroll={() => handleScroll(lockedScrollRef.current, setShowLockedLeftArrow, setShowLockedRightArrow)}
              className="overflow-x-auto pb-4 -mx-2 px-2 custom-scrollbar"
            >
              <div className="flex gap-6 min-w-max">
                {lockedManeuvers.map((mt, index) => {
              const missingCaps = getMissingCapabilities(mt)
              
              return (
                <motion.div
                  key={mt.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="runway-card p-6 opacity-60 relative"
                >
                  <div className="absolute top-4 right-4">
                    <Lock className="w-5 h-5 text-neutral-400" />
                  </div>
                  
                  <h3 className="text-lg font-bold text-neutral-900 mb-2">{mt.name}</h3>
                  <p className="text-sm text-neutral-600 mb-4">{mt.description}</p>
                  
                  <div className="pt-4 border-t border-neutral-200">
                    <p className="text-xs font-medium text-neutral-700 mb-2">Unlock Requirements:</p>
                    <ul className="space-y-1">
                      {missingCaps.map((cap, i) => (
                        <li key={i} className="text-xs text-neutral-600 flex items-center gap-1">
                          <span className="w-1 h-1 rounded-full bg-neutral-400" />
                          {cap}
                        </li>
                      ))}
                    </ul>
                    <button
                      onClick={() => navigate('/tech-tree')}
                      className="inline-flex items-center gap-1 mt-3 text-xs font-medium text-neutral-900 hover:underline"
                    >
                      View Tech Tree
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                  </motion.div>
                )
              })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      <AnimatePresence>
        {previewManeuver && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setPreviewManeuver(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="runway-card p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-neutral-900 mb-2">{previewManeuver.name}</h2>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={cn(
                      "px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] border rounded",
                      getPostureColor(previewManeuver.category)
                    )}>
                      {previewManeuver.category}
                    </span>
                    {previewManeuver.fogg_role && (
                      <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                        {previewManeuver.fogg_role}
                      </span>
                    )}
                    <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded">
                      {previewManeuver.tier}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setPreviewManeuver(null)}
                  className="text-neutral-400 hover:text-neutral-900 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-neutral-700 mb-2">Description</h3>
                  <p className="text-sm text-neutral-600">{previewManeuver.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-neutral-700 mb-2">Duration</h3>
                    <p className="text-sm text-neutral-900">{previewManeuver.base_duration_days} days</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-neutral-700 mb-2">Intensity</h3>
                    <p className="text-sm text-neutral-900">{previewManeuver.intensity_score}/10</p>
                  </div>
                </div>

                {previewManeuver.typical_icps && previewManeuver.typical_icps.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-neutral-700 mb-2">Good For</h3>
                    <p className="text-sm text-neutral-900">{previewManeuver.typical_icps.join(', ')}</p>
                  </div>
                )}

                {previewManeuver.required_capability_ids && previewManeuver.required_capability_ids.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-neutral-700 mb-2">Required Capabilities</h3>
                    <div className="flex flex-wrap gap-2">
                      {previewManeuver.required_capability_ids.map((capId) => {
                        const cap = capabilityNodes.find(n => n.id === capId)
                        return (
                          <span
                            key={capId}
                            className={cn(
                              "px-2 py-1 text-xs rounded",
                              unlockedCapabilityIds.includes(capId)
                                ? "bg-green-100 text-green-900"
                                : "bg-neutral-100 text-neutral-600"
                            )}
                          >
                            {cap?.name || capId}
                          </span>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button
                  onClick={() => {
                    setPreviewManeuver(null)
                    handleInstantiate(previewManeuver)
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Instantiate This Maneuver
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Instantiate Modal */}
      <AnimatePresence>
        {showInstantiateModal && selectedManeuverForInstantiate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowInstantiateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="runway-card p-8 max-w-md w-full"
            >
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-neutral-900 mb-2">Instantiate Maneuver</h2>
                  <p className="text-sm text-neutral-600">{selectedManeuverForInstantiate.name}</p>
                </div>
                <button
                  onClick={() => setShowInstantiateModal(false)}
                  className="text-neutral-400 hover:text-neutral-900 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <p className="text-sm text-neutral-600 mb-6">
                This will create a new Move instance from the {selectedManeuverForInstantiate.name} maneuver template. 
                You'll be taken to the War Room to schedule it in a Sprint.
              </p>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowInstantiateModal(false)}
                  className="flex-1 px-4 py-2 border border-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmInstantiate}
                  className="flex-1 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors"
                >
                  Create Move
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

