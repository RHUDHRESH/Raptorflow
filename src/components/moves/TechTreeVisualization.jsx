import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Target, 
  Lock, 
  CheckCircle2, 
  ArrowDown,
  ArrowRight,
  Sparkles,
  Link as LinkIcon,
  Zap
} from 'lucide-react'
import { cn } from '../../utils/cn'
import { CapabilityTier, CapabilityStatus } from '../../utils/moveSystemTypes'

export default function TechTreeVisualization({ nodes = [] }) {
  const [selectedNode, setSelectedNode] = useState(null)
  const [hoveredNode, setHoveredNode] = useState(null)

  // Organize nodes by tier
  const nodesByTier = useMemo(() => {
    const tiers = {
      [CapabilityTier.FOUNDATION]: [],
      [CapabilityTier.TRACTION]: [],
      [CapabilityTier.SCALE]: [],
      [CapabilityTier.DOMINANCE]: []
    }
    
    nodes.forEach(node => {
      if (tiers[node.tier]) {
        tiers[node.tier].push(node)
      }
    })
    
    return tiers
  }, [nodes])

  // Build dependency graph
  const dependencyGraph = useMemo(() => {
    const graph = new Map()
    
    nodes.forEach(node => {
      node.parentNodeIds?.forEach(parentId => {
        if (!graph.has(parentId)) {
          graph.set(parentId, [])
        }
        graph.get(parentId).push(node.id)
      })
    })
    
    return graph
  }, [nodes])

  // Get node by ID
  const getNode = (id) => nodes.find(n => n.id === id)

  // Calculate node positions for DAG layout
  const nodePositions = useMemo(() => {
    const positions = new Map()
    const tierOrder = [
      CapabilityTier.FOUNDATION,
      CapabilityTier.TRACTION,
      CapabilityTier.SCALE,
      CapabilityTier.DOMINANCE
    ]
    
    tierOrder.forEach((tier, tierIndex) => {
      const tierNodes = nodesByTier[tier] || []
      tierNodes.forEach((node, nodeIndex) => {
        positions.set(node.id, {
          x: (nodeIndex + 1) * (100 / (tierNodes.length + 1)),
          y: tierIndex * 30 + 10,
          tier: tierIndex
        })
      })
    })
    
    return positions
  }, [nodesByTier, nodes])

  const getStatusColor = (status) => {
    if (status === CapabilityStatus.UNLOCKED) return 'bg-green-500'
    if (status === CapabilityStatus.IN_PROGRESS) return 'bg-yellow-500'
    return 'bg-neutral-300'
  }

  const getStatusIcon = (status) => {
    if (status === CapabilityStatus.UNLOCKED) return CheckCircle2
    if (status === CapabilityStatus.IN_PROGRESS) return Zap
    return Lock
  }

  // Render connection lines between nodes
  const renderConnections = () => {
    const connections = []
    
    nodes.forEach(node => {
      node.parentNodeIds?.forEach(parentId => {
        const parentPos = nodePositions.get(parentId)
        const childPos = nodePositions.get(parentId)
        
        if (parentPos && childPos) {
          connections.push({
            from: parentId,
            to: node.id,
            fromPos: parentPos,
            toPos: childPos
          })
        }
      })
    })
    
    return (
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
        {connections.map((conn, idx) => {
          const parentNode = getNode(conn.from)
          const isUnlocked = parentNode?.status === CapabilityStatus.UNLOCKED
          
          return (
            <line
              key={`${conn.from}-${conn.to}-${idx}`}
              x1={`${conn.fromPos.x}%`}
              y1={`${conn.fromPos.y}%`}
              x2={`${conn.toPos.x}%`}
              y2={`${conn.toPos.y}%`}
              stroke={isUnlocked ? '#10b981' : '#d4d4d4'}
              strokeWidth="2"
              strokeDasharray={isUnlocked ? '0' : '4'}
              className="transition-all duration-300"
            />
          )
        })}
      </svg>
    )
  }

  return (
    <div className="relative runway-card p-8 min-h-[600px]">
      {/* DAG Visualization */}
      <div className="relative w-full h-full">
        {renderConnections()}
        
        {/* Render nodes by tier */}
        {Object.entries(nodesByTier).map(([tier, tierNodes]) => (
          <div key={tier} className="mb-12">
            <h3 className="text-lg font-bold text-neutral-900 mb-6 pb-2 border-b-2 border-neutral-200">
              {tier === CapabilityTier.FOUNDATION ? 'T1: Foundation' :
               tier === CapabilityTier.TRACTION ? 'T2: Traction' :
               tier === CapabilityTier.SCALE ? 'T3: Scale' :
               'T4: Dominance'}
            </h3>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {tierNodes.map((node) => {
                const StatusIcon = getStatusIcon(node.status)
                const isUnlocked = node.status === CapabilityStatus.UNLOCKED
                const isHovered = hoveredNode === node.id
                
                return (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: 1.05 }}
                    transition={{ duration: 0.18 }}
                    onHoverStart={() => setHoveredNode(node.id)}
                    onHoverEnd={() => setHoveredNode(null)}
                    onClick={() => setSelectedNode(node)}
                    className={cn(
                      "relative p-4 rounded-lg border-2 cursor-pointer transition-all duration-180",
                      isUnlocked 
                        ? "bg-green-50 border-green-200 hover:border-green-400 hover:shadow-lg" 
                        : "bg-neutral-50 border-neutral-200 opacity-60 hover:opacity-80",
                      isHovered && "ring-2 ring-neutral-900 ring-offset-2"
                    )}
                  >
                    {/* Status Indicator */}
                    <div className="absolute top-2 right-2">
                      <div className={cn(
                        "w-6 h-6 rounded-full flex items-center justify-center",
                        getStatusColor(node.status)
                      )}>
                        <StatusIcon className={cn(
                          "w-4 h-4",
                          isUnlocked ? "text-white" : "text-neutral-600"
                        )} />
                      </div>
                    </div>

                    {/* Node Content */}
                    <div className="pr-8">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className={cn(
                          "w-5 h-5",
                          isUnlocked ? "text-green-600" : "text-neutral-400"
                        )} />
                        <h4 className="font-bold text-neutral-900 text-sm">{node.name}</h4>
                      </div>
                      
                      {node.description && (
                        <p className="text-xs text-neutral-600 mb-2 line-clamp-2">
                          {node.description}
                        </p>
                      )}

                      {/* Prerequisites */}
                      {node.parentNodeIds && node.parentNodeIds.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-neutral-200">
                          <p className="text-[10px] font-medium text-neutral-500 mb-1">Requires:</p>
                          <div className="flex flex-wrap gap-1">
                            {node.parentNodeIds.slice(0, 2).map((parentId) => {
                              const parent = getNode(parentId)
                              const parentUnlocked = parent?.status === CapabilityStatus.UNLOCKED
                              return parent ? (
                                <span
                                  key={parentId}
                                  className={cn(
                                    "px-1.5 py-0.5 text-[9px] rounded",
                                    parentUnlocked 
                                      ? "bg-green-100 text-green-900" 
                                      : "bg-neutral-100 text-neutral-600"
                                  )}
                                >
                                  {parent.name}
                                </span>
                              ) : null
                            })}
                          </div>
                        </div>
                      )}

                      {/* Unlocks */}
                      {node.unlocksManeuverIds && node.unlocksManeuverIds.length > 0 && isUnlocked && (
                        <div className="mt-2 pt-2 border-t border-green-200">
                          <div className="flex items-center gap-1 text-[10px] text-green-700">
                            <Sparkles className="w-3 h-3" />
                            <span>Unlocks {node.unlocksManeuverIds.length} maneuver{node.unlocksManeuverIds.length > 1 ? 's' : ''}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Node Detail Panel */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.18 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedNode(null)}
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              transition={{ duration: 0.18 }}
              onClick={(e) => e.stopPropagation()}
              className="runway-card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-2xl font-bold text-neutral-900 mb-2">{selectedNode.name}</h3>
                  <span className={cn(
                    "px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border rounded",
                    selectedNode.status === CapabilityStatus.UNLOCKED
                      ? "bg-green-100 text-green-900 border-green-200"
                      : selectedNode.status === CapabilityStatus.IN_PROGRESS
                      ? "bg-yellow-100 text-yellow-900 border-yellow-200"
                      : "bg-neutral-100 text-neutral-900 border-neutral-200"
                  )}>
                    {selectedNode.status.replace(/_/g, ' ')}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-neutral-400 hover:text-neutral-900 transition-colors duration-180"
                >
                  ×
                </button>
              </div>

              {selectedNode.description && (
                <p className="text-sm text-neutral-600 mb-4">{selectedNode.description}</p>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Prerequisites */}
                {selectedNode.parentNodeIds && selectedNode.parentNodeIds.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-neutral-700 mb-2">Prerequisites</p>
                    <div className="space-y-2">
                      {selectedNode.parentNodeIds.map((parentId) => {
                        const parent = getNode(parentId)
                        return parent ? (
                          <div
                            key={parentId}
                            className="flex items-center gap-2 p-2 bg-neutral-50 rounded-lg"
                          >
                            <LinkIcon className="w-4 h-4 text-neutral-400" />
                            <span className="text-sm text-neutral-900">{parent.name}</span>
                            {parent.status === CapabilityStatus.UNLOCKED && (
                              <CheckCircle2 className="w-4 h-4 text-green-600 ml-auto" />
                            )}
                          </div>
                        ) : null
                      })}
                    </div>
                  </div>
                )}

                {/* Unlocks */}
                {selectedNode.unlocksManeuverIds && selectedNode.unlocksManeuverIds.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-neutral-700 mb-2">Unlocks Maneuvers</p>
                    <div className="space-y-2">
                      {selectedNode.unlocksManeuverIds.map((maneuverId) => (
                        <div
                          key={maneuverId}
                          className="flex items-center gap-2 p-2 bg-green-50 rounded-lg"
                        >
                          <Sparkles className="w-4 h-4 text-green-600" />
                          <span className="text-sm text-neutral-900">{maneuverId.replace(/-/g, ' ')}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

