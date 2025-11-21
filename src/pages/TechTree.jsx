import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Target, 
  Lock, 
  CheckCircle2, 
  ArrowDown,
  Sparkles,
  Link as LinkIcon
} from 'lucide-react'
import { cn } from '../utils/cn'
import { generateMockCapabilityNodes, CapabilityTier, CapabilityStatus } from '../utils/moveSystemTypes'
import TechTreeVisualization from '../components/moves/TechTreeVisualization'

export default function TechTree() {
  const [nodes] = useState(generateMockCapabilityNodes())
  const [selectedNode, setSelectedNode] = useState(null)

  const nodesByTier = {
    [CapabilityTier.FOUNDATION]: nodes.filter(n => n.tier === CapabilityTier.FOUNDATION),
    [CapabilityTier.TRACTION]: nodes.filter(n => n.tier === CapabilityTier.TRACTION),
    [CapabilityTier.SCALE]: nodes.filter(n => n.tier === CapabilityTier.SCALE),
    [CapabilityTier.DOMINANCE]: nodes.filter(n => n.tier === CapabilityTier.DOMINANCE)
  }

  const getStatusColor = (status) => {
    if (status === CapabilityStatus.UNLOCKED) return 'bg-green-100 text-green-900 border-green-200'
    if (status === CapabilityStatus.IN_PROGRESS) return 'bg-yellow-100 text-yellow-900 border-yellow-200'
    return 'bg-neutral-100 text-neutral-900 border-neutral-200 opacity-60'
  }

  const getTierLabel = (tier) => {
    const labels = {
      [CapabilityTier.FOUNDATION]: 'T1: Foundation',
      [CapabilityTier.TRACTION]: 'T2: Traction',
      [CapabilityTier.SCALE]: 'T3: Scale',
      [CapabilityTier.DOMINANCE]: 'T4: Dominance'
    }
    return labels[tier] || tier
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
            <span className="micro-label tracking-[0.5em]">Tech Tree</span>
            <span className="h-px w-16 bg-neutral-200" />
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-400">Capability Dependency Graph</span>
          </div>
          <div className="space-y-4">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Capability Maturity
            </h1>
            <p className="font-sans text-base text-neutral-600 max-w-2xl leading-relaxed">
              Visual DAG showing capability dependencies. Click nodes to see prerequisites and unlocks.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Tech Tree Visualization - DAG */}
      <TechTreeVisualization nodes={nodes} />

      {/* Legacy Grid View (Fallback) */}
      <div className="runway-card p-8 overflow-x-auto hidden">
        <div className="space-y-12 min-w-max">
          {Object.entries(nodesByTier).map(([tier, tierNodes], tierIndex) => (
            <div key={tier} className="relative">
              {/* Tier Label */}
              <div className="mb-6 pb-4 border-b-2 border-neutral-200">
                <h2 className="text-2xl font-bold text-neutral-900">{getTierLabel(tier)}</h2>
              </div>

              {/* Nodes Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {tierNodes.map((node, nodeIndex) => {
                  const isUnlocked = node.status === CapabilityStatus.UNLOCKED
                  const isInProgress = node.status === CapabilityStatus.IN_PROGRESS
                  
                  return (
                    <motion.div
                      key={node.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: (tierIndex * 0.1) + (nodeIndex * 0.05) }}
                      onClick={() => setSelectedNode(node)}
                      className={cn(
                        "runway-card p-4 cursor-pointer hover:shadow-xl transition-all relative",
                        !isUnlocked && "opacity-60"
                      )}
                    >
                      {/* Status Indicator */}
                      <div className="absolute top-2 right-2">
                        {isUnlocked ? (
                          <CheckCircle2 className="w-5 h-5 text-green-600" />
                        ) : isInProgress ? (
                          <div className="w-5 h-5 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Lock className="w-5 h-5 text-neutral-400" />
                        )}
                      </div>

                      {/* Node Content */}
                      <div className="pr-8">
                        <div className="flex items-center gap-2 mb-2">
                          <Target className={cn(
                            "w-5 h-5",
                            isUnlocked ? "text-green-600" : "text-neutral-400"
                          )} />
                          <h3 className="font-bold text-neutral-900">{node.name}</h3>
                        </div>
                        
                        {node.description && (
                          <p className="text-xs text-neutral-600 mb-3">{node.description}</p>
                        )}

                        {/* Prerequisites */}
                        {node.parent_nodes && node.parent_nodes.length > 0 && (
                          <div className="mb-2">
                            <p className="text-[10px] font-medium text-neutral-500 mb-1">Requires:</p>
                            <div className="flex flex-wrap gap-1">
                              {node.parent_nodes.slice(0, 2).map((parentId) => {
                                const parent = nodes.find(n => n.id === parentId)
                                return parent ? (
                                  <span
                                    key={parentId}
                                    className="px-1.5 py-0.5 text-[9px] bg-neutral-100 text-neutral-700 rounded"
                                  >
                                    {parent.name}
                                  </span>
                                ) : null
                              })}
                            </div>
                          </div>
                        )}

                        {/* Unlocks */}
                        {node.unlocks_maneuver_ids && node.unlocks_maneuver_ids.length > 0 && isUnlocked && (
                          <div className="pt-2 border-t border-neutral-200">
                            <p className="text-[10px] font-medium text-green-700 mb-1">Unlocks:</p>
                            <div className="flex flex-wrap gap-1">
                              {node.unlocks_maneuver_ids.slice(0, 2).map((moveId) => (
                                <span
                                  key={moveId}
                                  className="px-1.5 py-0.5 text-[9px] bg-green-100 text-green-900 rounded"
                                >
                                  {moveId.replace(/-/g, ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>

              {/* Connector Lines (Visual) */}
              {tierIndex < Object.keys(nodesByTier).length - 1 && (
                <div className="flex justify-center my-8">
                  <ArrowDown className="w-8 h-8 text-neutral-300" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Node Detail Panel */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="runway-card p-6"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold text-neutral-900 mb-2">{selectedNode.name}</h3>
                <span className={cn(
                  "px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border rounded",
                  getStatusColor(selectedNode.status)
                )}>
                  {selectedNode.status.replace(/_/g, ' ')}
                </span>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-neutral-400 hover:text-neutral-900"
              >
                ×
              </button>
            </div>

            {selectedNode.description && (
              <p className="text-sm text-neutral-600 mb-4">{selectedNode.description}</p>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Prerequisites */}
              {selectedNode.parent_nodes && selectedNode.parent_nodes.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-neutral-700 mb-2">Prerequisites</p>
                  <div className="space-y-2">
                    {selectedNode.parent_nodes.map((parentId) => {
                      const parent = nodes.find(n => n.id === parentId)
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
              {selectedNode.unlocks_maneuver_ids && selectedNode.unlocks_maneuver_ids.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-neutral-700 mb-2">Unlocks Maneuvers</p>
                  <div className="space-y-2">
                    {selectedNode.unlocks_maneuver_ids.map((moveId) => (
                      <div
                        key={moveId}
                        className="flex items-center gap-2 p-2 bg-green-50 rounded-lg"
                      >
                        <Sparkles className="w-4 h-4 text-green-600" />
                        <span className="text-sm text-neutral-900">{moveId.replace(/-/g, ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}


