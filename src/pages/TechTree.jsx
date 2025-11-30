/**
 * Tech Tree - Integrated with Real Supabase Data
 * Interactive capability tree with unlocking functionality
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Unlock, CheckCircle, Target, TrendingUp } from 'lucide-react';
import { useCapabilityNodes } from '../hooks/useMoveSystem';
import { cn } from '../utils/cn';
import {
  HeroSection,
  LuxeCard,
  LuxeButton,
  LuxeBadge,
  LuxeModal,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI';

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

    if (!node.parent_node_ids || node.parent_node_ids.length === 0) {
      return true;
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
      return <CheckCircle className="w-5 h-5 text-emerald-600" />;
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
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {/* Header */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Tech Tree"
          subtitle="Unlock capabilities to access advanced tactical maneuvers. Each tier builds on the previous."
          metrics={[
            { label: 'Total', value: totalNodes.toString() },
            { label: 'Unlocked', value: unlockedNodes.toString() },
            { label: 'Progress', value: `${progressPercentage}%` }
          ]}
        />
      </motion.div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-center justify-between mb-4">
              <Target className="w-6 h-6 text-neutral-400" />
              <span className="text-2xl font-display font-medium text-neutral-900">{totalNodes}</span>
            </div>
            <p className="text-sm text-neutral-600">Total Capabilities</p>
          </LuxeCard>
        </motion.div>

        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-center justify-between mb-4">
              <CheckCircle className="w-6 h-6 text-emerald-500" />
              <span className="text-2xl font-display font-medium text-emerald-600">{unlockedNodes}</span>
            </div>
            <p className="text-sm text-neutral-600">Unlocked</p>
          </LuxeCard>
        </motion.div>

        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-6 h-6 text-neutral-400" />
              <span className="text-2xl font-display font-medium text-neutral-900">{progressPercentage}%</span>
            </div>
            <p className="text-sm text-neutral-600">Progress</p>
            <div className="mt-3 h-2 bg-neutral-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-emerald-500"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </LuxeCard>
        </motion.div>
      </div>

      {/* Tech Tree by Tier */}
      <div className="space-y-8">
        {tierOrder.map((tier) => (
          <motion.div key={tier} variants={fadeInUp} className="space-y-4">
            <div className={cn(
              "inline-block px-4 py-2 rounded-xl font-bold text-white bg-gradient-to-r",
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
                    whileHover={{ scale: unlockable && !isUnlocked ? 1.02 : 1 }}
                    className={cn(
                      "cursor-pointer transition-all",
                      !unlockable && !isUnlocked && "opacity-50"
                    )}
                    onClick={() => {
                      setSelectedNode(node);
                      if (unlockable && !isUnlocked) {
                        setShowUnlockModal(true);
                      }
                    }}
                  >
                    <LuxeCard className={cn(
                      "p-6",
                      isUnlocked && "border-2 border-emerald-500"
                    )}>
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
                          <LuxeButton size="sm" className="w-full">
                            Unlock Now
                          </LuxeButton>
                        </div>
                      )}
                    </LuxeCard>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Unlock Confirmation Modal */}
      {showUnlockModal && selectedNode && (
        <LuxeModal
          isOpen={showUnlockModal}
          onClose={() => setShowUnlockModal(false)}
          title="Unlock Capability"
        >
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-bold text-neutral-900 mb-2">
                {selectedNode.name}
              </h3>
              <p className="text-neutral-600">
                {selectedNode.description}
              </p>
            </div>

            <p className="text-sm text-neutral-600">
              Unlocking this capability will make new tactical maneuvers available in the Move Library.
            </p>

            <div className="flex gap-3">
              <LuxeButton
                variant="outline"
                onClick={() => setShowUnlockModal(false)}
                disabled={unlocking}
                className="flex-1"
              >
                Cancel
              </LuxeButton>
              <LuxeButton
                onClick={handleUnlock}
                disabled={unlocking}
                loading={unlocking}
                className="flex-1"
              >
                <Unlock className="w-4 h-4 mr-2" />
                Unlock Now
              </LuxeButton>
            </div>
          </div>
        </LuxeModal>
      )}
    </motion.div>
  );
}
