/**
 * Move Library - Integrated with Real Supabase Data
 * This is a simplified version that connects to the actual services
 * Replace the existing MoveLibrary.jsx with this once tested
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Target, Search, Filter, Lock, Eye, Plus, X, ArrowRight
} from 'lucide-react';
import { cn } from '../utils/cn';
import { useManeuverTypes, useCapabilityNodes, useMoves, useSprints, useICPs } from '../hooks/useMoveSystem';

export default function MoveLibraryIntegrated() {
  const navigate = useNavigate();
  
  // Fetch real data
  const { maneuverTypes, loading: maneuversLoading } = useManeuverTypes();
  const { capabilityNodes, loading: capabilitiesLoading, unlockNode } = useCapabilityNodes();
  const { createMove } = useMoves();
  const { activeSprint } = useSprints();
  const { icps } = useICPs();
  
  // Local state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [previewManeuver, setPreviewManeuver] = useState(null);
  const [showInstantiateModal, setShowInstantiateModal] = useState(false);
  const [selectedManeuver, setSelectedManeuver] = useState(null);

  const loading = maneuversLoading || capabilitiesLoading;

  // Check if maneuver is unlocked
  const isManeuverUnlocked = (maneuverType) => {
    // Get required capabilities from database (maneuver_prerequisites table)
    // For now, simplified check - Foundation tier maneuvers are always unlocked
    const unlockedCapIds = capabilityNodes
      .filter(node => node.status === 'Unlocked')
      .map(node => node.id);
    
    // Check if all required capabilities are unlocked
    // This would need to query maneuver_prerequisites table in production
    return true; // Simplified for now
  };

  // Filter maneuvers
  const filteredManeuvers = maneuverTypes.filter(mt => {
    const matchesSearch = !searchQuery || 
      mt.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (mt.description || '').toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || mt.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const unlockedManeuvers = filteredManeuvers.filter(isManeuverUnlocked);
  const lockedManeuvers = filteredManeuvers.filter(mt => !isManeuverUnlocked(mt));

  const handleInstantiate = (maneuverType) => {
    setSelectedManeuver(maneuverType);
    setShowInstantiateModal(true);
  };

  const confirmInstantiate = async () => {
    if (!selectedManeuver) return;
    
    try {
      // Check if we have required data
      if (icps.length === 0) {
        alert('Please create an ICP/Cohort first');
        navigate('/cohorts');
        return;
      }

      // Create the move
      const today = new Date();
      const endDate = new Date(today);
      endDate.setDate(endDate.getDate() + (selectedManeuver.base_duration_days || 14));

      const newMove = await createMove({
        maneuver_type_id: selectedManeuver.id,
        name: `${selectedManeuver.name} - ${today.toLocaleDateString()}`,
        primary_icp_id: icps[0].id,
        status: 'Planning',
        start_date: today.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        sprint_id: activeSprint?.id || null,
        progress_percentage: 0,
        health_status: 'green',
        ooda_config: {
          observe_sources: [],
          orient_rules: '',
          decide_logic: '',
          act_tasks: []
        }
      });

      setShowInstantiateModal(false);
      setSelectedManeuver(null);

      // Navigate to War Room or Move Detail
      if (activeSprint) {
        navigate('/moves/war-room');
      } else {
        navigate(`/moves/${newMove.id}`);
      }
    } catch (error) {
      console.error('Error creating move:', error);
      alert('Error creating move. Check console for details.');
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Offensive': 'bg-red-100 text-red-900 border-red-200',
      'Defensive': 'bg-blue-100 text-blue-900 border-blue-200',
      'Logistical': 'bg-purple-100 text-purple-900 border-purple-200',
      'Recon': 'bg-green-100 text-green-900 border-green-200'
    };
    return colors[category] || 'bg-neutral-100 text-neutral-900 border-neutral-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading Move Library...</p>
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
          <p className="micro-label mb-2">Move Library</p>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-tight mb-3">
            Maneuver Arsenal
          </h1>
          <p className="text-base text-neutral-600 max-w-2xl">
            Browse and instantiate tactical maneuvers. Locked maneuvers require capability unlocks from the Tech Tree.
          </p>
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
          <div className="text-2xl font-bold text-green-600">{unlockedManeuvers.length}</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-sm text-neutral-600 mb-1">Locked</div>
          <div className="text-2xl font-bold text-neutral-600">{lockedManeuvers.length}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="runway-card p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              placeholder="Search maneuvers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
          >
            <option value="all">All Categories</option>
            <option value="Offensive">Offensive</option>
            <option value="Defensive">Defensive</option>
            <option value="Logistical">Logistical</option>
            <option value="Recon">Recon</option>
          </select>
        </div>
      </div>

      {/* Available Maneuvers */}
      <div>
        <h2 className="text-xl font-bold text-neutral-900 mb-4">
          Available Maneuvers ({unlockedManeuvers.length})
        </h2>
        {unlockedManeuvers.length === 0 ? (
          <div className="runway-card p-12 text-center">
            <Target className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No maneuvers match your filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {unlockedManeuvers.map((mt) => (
              <motion.div
                key={mt.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="runway-card p-6 hover:shadow-xl transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-neutral-900 mb-2">{mt.name}</h3>
                    <span className={cn(
                      "px-2 py-1 text-[10px] font-mono uppercase tracking-wider border rounded",
                      getCategoryColor(mt.category)
                    )}>
                      {mt.category}
                    </span>
                  </div>
                  <Target className="w-6 h-6 text-neutral-400" />
                </div>
                <p className="text-sm text-neutral-600 mb-4">{mt.description || 'No description'}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPreviewManeuver(mt)}
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
            ))}
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lockedManeuvers.map((mt) => (
              <div key={mt.id} className="runway-card p-6 opacity-60 relative">
                <Lock className="absolute top-4 right-4 w-5 h-5 text-neutral-400" />
                <h3 className="text-lg font-bold text-neutral-900 mb-2">{mt.name}</h3>
                <p className="text-sm text-neutral-600 mb-4">{mt.description}</p>
                <button
                  onClick={() => navigate('/tech-tree')}
                  className="text-xs font-medium text-neutral-900 hover:underline flex items-center gap-1"
                >
                  View Tech Tree
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
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
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="runway-card p-8 max-w-2xl w-full"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold mb-2">{previewManeuver.name}</h2>
                  <span className={cn(
                    "px-2 py-1 text-xs uppercase border rounded",
                    getCategoryColor(previewManeuver.category)
                  )}>
                    {previewManeuver.category}
                  </span>
                </div>
                <button onClick={() => setPreviewManeuver(null)}>
                  <X className="w-6 h-6" />
                </button>
              </div>
              <p className="text-neutral-600 mb-4">{previewManeuver.description}</p>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm font-medium text-neutral-700">Duration</p>
                  <p className="text-neutral-900">{previewManeuver.base_duration_days} days</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-neutral-700">Intensity</p>
                  <p className="text-neutral-900">{previewManeuver.intensity_score || 'N/A'}/10</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setPreviewManeuver(null);
                  handleInstantiate(previewManeuver);
                }}
                className="w-full px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800"
              >
                <Plus className="w-4 h-4 inline mr-2" />
                Instantiate This Maneuver
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Instantiate Modal */}
      <AnimatePresence>
        {showInstantiateModal && selectedManeuver && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowInstantiateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="runway-card p-8 max-w-md w-full"
            >
              <h2 className="text-xl font-bold mb-4">Create New Move</h2>
              <p className="text-neutral-600 mb-6">
                This will create a new move instance from <strong>{selectedManeuver.name}</strong>.
                {activeSprint ? ` It will be added to the active sprint.` : ` Create a sprint first to add it to your planning.`}
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowInstantiateModal(false)}
                  className="flex-1 px-4 py-2 border border-neutral-200 rounded-lg hover:bg-neutral-50"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmInstantiate}
                  className="flex-1 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800"
                >
                  Create Move
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}





