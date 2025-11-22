/**
 * Tech Tree - Integrated with Real Supabase Data
 * Interactive capability tree with unlocking functionality
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Unlock, CheckCircle, Target, TrendingUp } from 'lucide-react';
import { useCapabilityNodes } from '../hooks/useMoveSystem';
import { cn } from '../utils/cn';

export default function TechTreeIntegrated() {
  const { capabilityNodes, loading, unlockNode } = useCapabilityNodes();
  const [selectedNode, setSelectedNode] = useState(null);
  const [showUnlockModal, setShowUnlockModal] = useState(false);
  const [unlocking, setUnlocking] = useState(false);

  const tierOrder = ['Foundation', 'Traction', 'Scale', 'Dominance'];

  // Group nodes by tier
  const nodesByTier = tierOrder.reduce((acc, tier) => {
    acc[tier] = capabilityNodes.filter(node => node.tier === tier);
    return acc;
  }, {});

  // Calculate progress
  const totalNodes = capabilityNodes.length;
  const unlockedNodes = capabilityNodes.filter(n => n.status === 'Unlocked').length;
  const progressPercentage = totalNodes > 0 ? Math.round((unlockedNodes / totalNodes) * 100) : 0;

  // Check if node can be unlocked
  const canUnlock = (node) => {
    if (node.status === 'Unlocked') return false;
    
    // Check if all parent nodes are unlocked
    if (!node.parent_node_ids || node.parent_node_ids.length === 0) {
      return true; // Foundation nodes with no parents
    }
    
    return node.parent_node_ids.every(parentId => {
      const parent = capabilityNodes.find(n => n.id === parentId);
      return parent && parent.status === 'Unlocked';
    });
  };

  const handleUnlock = async () => {
    if (!selectedNode) return;
    
    try {
      setUnlocking(true);
      await unlockNode(selectedNode.id);
      setShowUnlockModal(false);
      setSelectedNode(null);
    } catch (error) {
      console.error('Error unlocking node:', error);
      alert('Failed to unlock capability');
    } finally {
      setUnlocking(false);
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      'Foundation': 'from-blue-500 to-blue-600',
      'Traction': 'from-purple-500 to-purple-600',
      'Scale': 'from-amber-500 to-amber-600',
      'Dominance': 'from-red-500 to-red-600',
    };
    return colors[tier] || colors.Foundation;
  };

  const getStatusIcon = (node) => {
    if (node.status === 'Unlocked') {
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    } else if (canUnlock(node)) {
      return <Unlock className="w-5 h-5 text-amber-600" />;
    } else {
      return <Lock className="w-5 h-5 text-neutral-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading Tech Tree...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10">
          <p className="micro-label mb-2">Tech Tree</p>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-tight mb-3">
            Capability Progression
          </h1>
          <p className="text-base text-neutral-600 max-w-2xl">
            Unlock capabilities to access advanced tactical maneuvers. Each tier builds on the previous.
          </p>
        </div>
      </motion.div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="runway-card p-6">
          <div className="flex items-center justify-between mb-4">
            <Target className="w-6 h-6 text-neutral-400" />
            <span className="text-2xl font-bold text-neutral-900">{totalNodes}</span>
          </div>
          <p className="text-sm text-neutral-600">Total Capabilities</p>
        </div>
        
        <div className="runway-card p-6">
          <div className="flex items-center justify-between mb-4">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <span className="text-2xl font-bold text-green-600">{unlockedNodes}</span>
          </div>
          <p className="text-sm text-neutral-600">Unlocked</p>
        </div>
        
        <div className="runway-card p-6">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp className="w-6 h-6 text-neutral-400" />
            <span className="text-2xl font-bold text-neutral-900">{progressPercentage}%</span>
          </div>
          <p className="text-sm text-neutral-600">Progress</p>
          <div className="mt-3 h-2 bg-neutral-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-green-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Tech Tree by Tier */}
      <div className="space-y-8">
        {tierOrder.map((tier) => (
          <div key={tier} className="space-y-4">
            <div className={cn(
              "inline-block px-4 py-2 rounded-lg font-bold text-white bg-gradient-to-r",
              getTierColor(tier)
            )}>
              {tier}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {nodesByTier[tier]?.map((node) => {
                const unlockable = canUnlock(node);
                const isUnlocked = node.status === 'Unlocked';
                
                return (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: unlockable && !isUnlocked ? 1.02 : 1 }}
                    className={cn(
                      "runway-card p-6 cursor-pointer transition-all",
                      isUnlocked && "border-2 border-green-500",
                      !unlockable && !isUnlocked && "opacity-50"
                    )}
                    onClick={() => {
                      setSelectedNode(node);
                      if (unlockable && !isUnlocked) {
                        setShowUnlockModal(true);
                      }
                    }}
                  >
                    <div className="flex items-start justify-between mb-3">
                      {getStatusIcon(node)}
                      {isUnlocked && node.unlocked_at && (
                        <span className="text-[10px] text-neutral-500">
                          {new Date(node.unlocked_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    
                    <h3 className="text-sm font-bold text-neutral-900 mb-2 line-clamp-2">
                      {node.name}
                    </h3>
                    
                    <p className="text-xs text-neutral-600 line-clamp-3 mb-3">
                      {node.description || 'No description'}
                    </p>
                    
                    {node.parent_node_ids && node.parent_node_ids.length > 0 && (
                      <div className="flex items-center gap-1 text-[10px] text-neutral-500">
                        <Lock className="w-3 h-3" />
                        Requires {node.parent_node_ids.length} prerequisite(s)
                      </div>
                    )}
                    
                    {unlockable && !isUnlocked && (
                      <div className="mt-3 pt-3 border-t border-neutral-200">
                        <button className="w-full px-3 py-1.5 text-xs font-medium bg-neutral-900 text-white rounded hover:bg-neutral-800">
                          Unlock Now
                        </button>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Unlock Confirmation Modal */}
      <AnimatePresence>
        {showUnlockModal && selectedNode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowUnlockModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="runway-card p-8 max-w-lg w-full"
            >
              <h2 className="text-2xl font-bold text-neutral-900 mb-4">
                Unlock Capability
              </h2>
              
              <div className="mb-6">
                <h3 className="text-lg font-bold text-neutral-900 mb-2">
                  {selectedNode.name}
                </h3>
                <p className="text-neutral-600 mb-4">
                  {selectedNode.description}
                </p>
                
                {selectedNode.completion_criteria && (
                  <div className="p-4 bg-neutral-50 rounded-lg">
                    <p className="text-sm font-medium text-neutral-700 mb-2">Criteria:</p>
                    <pre className="text-xs text-neutral-600 overflow-auto">
                      {JSON.stringify(selectedNode.completion_criteria, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
              
              <p className="text-sm text-neutral-600 mb-6">
                Unlocking this capability will make new tactical maneuvers available in the Move Library.
              </p>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowUnlockModal(false)}
                  disabled={unlocking}
                  className="flex-1 px-6 py-3 border border-neutral-200 text-neutral-900 rounded-lg hover:bg-neutral-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUnlock}
                  disabled={unlocking}
                  className="flex-1 px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {unlocking ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Unlocking...
                    </>
                  ) : (
                    <>
                      <Unlock className="w-4 h-4" />
                      Unlock Now
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Detail View (when node selected but not unlocking) */}
      <AnimatePresence>
        {selectedNode && !showUnlockModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedNode(null)}
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="runway-card p-8 max-w-lg w-full"
            >
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                    {selectedNode.name}
                  </h2>
                  <span className={cn(
                    "px-3 py-1 text-sm rounded",
                    selectedNode.status === 'Unlocked' 
                      ? "bg-green-100 text-green-900" 
                      : "bg-neutral-100 text-neutral-900"
                  )}>
                    {selectedNode.status}
                  </span>
                </div>
                {getStatusIcon(selectedNode)}
              </div>
              
              <p className="text-neutral-600 mb-6">
                {selectedNode.description}
              </p>
              
              {selectedNode.parent_node_ids && selectedNode.parent_node_ids.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-bold text-neutral-700 mb-2">Prerequisites:</h3>
                  <div className="space-y-2">
                    {selectedNode.parent_node_ids.map(parentId => {
                      const parent = capabilityNodes.find(n => n.id === parentId);
                      return parent ? (
                        <div key={parentId} className="flex items-center gap-2 text-sm">
                          {parent.status === 'Unlocked' ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <Lock className="w-4 h-4 text-neutral-400" />
                          )}
                          <span className={parent.status === 'Unlocked' ? 'text-neutral-900' : 'text-neutral-500'}>
                            {parent.name}
                          </span>
                        </div>
                      ) : null;
                    })}
                  </div>
                </div>
              )}
              
              <button
                onClick={() => setSelectedNode(null)}
                className="w-full px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800"
              >
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}


