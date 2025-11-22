/**
 * Quests Page - Integrated with Real Data
 * Gamified move sequences with goals and rewards
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, Target, Clock, CheckCircle, Plus, X, 
  ChevronRight, Star, Zap, TrendingUp 
} from 'lucide-react';
import { questService } from '../lib/services/quest-service';
import { moveService } from '../lib/services/move-service';
import { useAuth } from '../context/AuthContext';
import { PageLoading } from '../components/LoadingStates';
import { toast } from '../components/Toast';
import { cn } from '../utils/cn';

export default function QuestsIntegrated() {
  const { user } = useAuth();
  const [quests, setQuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedQuest, setSelectedQuest] = useState(null);

  useEffect(() => {
    if (user?.id) {
      loadQuests();
    }
  }, [user]);

  const loadQuests = async () => {
    try {
      setLoading(true);
      const data = await questService.getQuests(user.id);
      setQuests(data);
    } catch (error) {
      console.error('Error loading quests:', error);
      toast.error('Failed to load quests');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuest = async (questData) => {
    try {
      const newQuest = await questService.createQuest({
        ...questData,
        workspace_id: user.id,
      });
      
      if (newQuest) {
        setQuests(prev => [newQuest, ...prev]);
        toast.success('Quest created!', 'Your new quest is ready to start.');
        setShowCreateModal(false);
      }
    } catch (error) {
      console.error('Error creating quest:', error);
      toast.error('Failed to create quest');
    }
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      Beginner: 'bg-green-100 text-green-900 border-green-200',
      Intermediate: 'bg-amber-100 text-amber-900 border-amber-200',
      Advanced: 'bg-red-100 text-red-900 border-red-200',
    };
    return colors[difficulty] || colors.Beginner;
  };

  const getStatusColor = (status) => {
    const colors = {
      Not_Started: 'bg-neutral-100 text-neutral-700 border-neutral-200',
      In_Progress: 'bg-blue-100 text-blue-900 border-blue-200',
      Completed: 'bg-green-100 text-green-900 border-green-200',
      Failed: 'bg-red-100 text-red-900 border-red-200',
    };
    return colors[status] || colors.Not_Started;
  };

  if (loading) {
    return <PageLoading message="Loading quests..." />;
  }

  const stats = {
    total: quests.length,
    inProgress: quests.filter(q => q.status === 'In_Progress').length,
    completed: quests.filter(q => q.status === 'Completed').length,
    totalXP: quests
      .filter(q => q.status === 'Completed')
      .reduce((sum, q) => sum + (q.xp_reward || 0), 0),
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-purple-50 via-white to-blue-50" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <Trophy className="w-8 h-8 text-purple-600" />
            <p className="micro-label">Gamified Campaigns</p>
          </div>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-tight mb-3">
            Quest Log
          </h1>
          <p className="text-base text-neutral-600 max-w-2xl mb-6">
            Complete quest sequences to level up your strategy execution and earn XP rewards.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 flex items-center gap-2 font-medium"
          >
            <Plus className="w-5 h-5" />
            Create Quest
          </button>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-neutral-900 mb-1">{stats.total}</div>
          <div className="text-sm text-neutral-600">Total Quests</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-blue-600 mb-1">{stats.inProgress}</div>
          <div className="text-sm text-neutral-600">In Progress</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-green-600 mb-1">{stats.completed}</div>
          <div className="text-sm text-neutral-600">Completed</div>
        </div>
        <div className="runway-card p-4">
          <div className="flex items-center gap-2 text-2xl font-bold text-purple-600 mb-1">
            <Star className="w-6 h-6" />
            {stats.totalXP}
          </div>
          <div className="text-sm text-neutral-600">Total XP Earned</div>
        </div>
      </div>

      {/* Quests List */}
      {quests.length === 0 ? (
        <div className="runway-card p-12 text-center">
          <Trophy className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-neutral-900 mb-2">No Quests Yet</h3>
          <p className="text-neutral-600 mb-6">
            Create your first quest to start your strategic campaign.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 inline-flex items-center gap-2 font-medium"
          >
            <Plus className="w-5 h-5" />
            Create First Quest
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {quests.map((quest) => (
            <QuestCard
              key={quest.id}
              quest={quest}
              onSelect={setSelectedQuest}
              onUpdate={loadQuests}
            />
          ))}
        </div>
      )}

      {/* Create Quest Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <CreateQuestModal
            onClose={() => setShowCreateModal(false)}
            onCreate={handleCreateQuest}
          />
        )}
      </AnimatePresence>

      {/* Quest Detail Modal */}
      <AnimatePresence>
        {selectedQuest && (
          <QuestDetailModal
            quest={selectedQuest}
            onClose={() => setSelectedQuest(null)}
            onUpdate={loadQuests}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function QuestCard({ quest, onSelect, onUpdate }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="runway-card p-6 cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => onSelect(quest)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-neutral-900 mb-2">{quest.name}</h3>
          <p className="text-sm text-neutral-600 mb-3">{quest.description}</p>
        </div>
        <div className="flex items-center gap-2 text-purple-600">
          <Star className="w-5 h-5" />
          <span className="font-bold">{quest.xp_reward}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs text-neutral-600 mb-1">
          <span>Progress</span>
          <span className="font-medium">{quest.progress_percentage}%</span>
        </div>
        <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${quest.progress_percentage}%` }}
            className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
          />
        </div>
      </div>

      {/* Meta */}
      <div className="flex flex-wrap items-center gap-2">
        <span className={cn(
          "px-2 py-1 text-xs font-medium border rounded",
          quest.status && getStatusColor(quest.status)
        )}>
          {quest.status?.replace('_', ' ')}
        </span>
        <span className={cn(
          "px-2 py-1 text-xs font-medium border rounded",
          quest.difficulty && getDifficultyColor(quest.difficulty)
        )}>
          {quest.difficulty}
        </span>
        {quest.estimated_duration_weeks && (
          <span className="flex items-center gap-1 text-xs text-neutral-600">
            <Clock className="w-3 h-3" />
            {quest.estimated_duration_weeks} weeks
          </span>
        )}
      </div>
    </motion.div>
  );
}

function getDifficultyColor(difficulty) {
  const colors = {
    Beginner: 'bg-green-100 text-green-900 border-green-200',
    Intermediate: 'bg-amber-100 text-amber-900 border-amber-200',
    Advanced: 'bg-red-100 text-red-900 border-red-200',
  };
  return colors[difficulty] || colors.Beginner;
}

function getStatusColor(status) {
  const colors = {
    Not_Started: 'bg-neutral-100 text-neutral-700 border-neutral-200',
    In_Progress: 'bg-blue-100 text-blue-900 border-blue-200',
    Completed: 'bg-green-100 text-green-900 border-green-200',
    Failed: 'bg-red-100 text-red-900 border-red-200',
  };
  return colors[status] || colors.Not_Started;
}

function CreateQuestModal({ onClose, onCreate }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    goal: '',
    difficulty: 'Beginner',
    estimated_duration_weeks: 4,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const template = questService.generateQuestTemplate(formData.goal, formData.difficulty);
    onCreate({ ...formData, ...template });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        exit={{ scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-8"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-neutral-900">Create New Quest</h2>
          <button onClick={onClose} className="p-2 hover:bg-neutral-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Quest Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
              placeholder="Market Domination Campaign"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
              rows={3}
              placeholder="A coordinated campaign to establish authority..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Goal</label>
            <input
              type="text"
              required
              value={formData.goal}
              onChange={(e) => setFormData(prev => ({ ...prev, goal: e.target.value }))}
              className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
              placeholder="Increase brand authority by 50%"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Difficulty</label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData(prev => ({ ...prev, difficulty: e.target.value }))}
                className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
              >
                <option value="Beginner">Beginner (4 weeks)</option>
                <option value="Intermediate">Intermediate (8 weeks)</option>
                <option value="Advanced">Advanced (12 weeks)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Duration (weeks)</label>
              <input
                type="number"
                min="1"
                value={formData.estimated_duration_weeks}
                onChange={(e) => setFormData(prev => ({ ...prev, estimated_duration_weeks: parseInt(e.target.value) }))}
                className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-neutral-200 text-neutral-900 rounded-lg hover:bg-neutral-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 font-medium"
            >
              Create Quest
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
}

function QuestDetailModal({ quest, onClose, onUpdate }) {
  // Simplified - full implementation would show moves, milestones, etc.
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        exit={{ scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full p-8 max-h-[80vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold text-neutral-900">{quest.name}</h2>
          <button onClick={onClose} className="p-2 hover:bg-neutral-100 rounded">
            <X className="w-6 h-6" />
          </button>
        </div>

        <p className="text-neutral-600 mb-6">{quest.description}</p>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-neutral-50 rounded-lg">
            <div className="text-sm text-neutral-600 mb-1">Progress</div>
            <div className="text-2xl font-bold">{quest.progress_percentage}%</div>
          </div>
          <div className="p-4 bg-neutral-50 rounded-lg">
            <div className="text-sm text-neutral-600 mb-1">XP Reward</div>
            <div className="flex items-center gap-2 text-2xl font-bold text-purple-600">
              <Star className="w-6 h-6" />
              {quest.xp_reward}
            </div>
          </div>
          <div className="p-4 bg-neutral-50 rounded-lg">
            <div className="text-sm text-neutral-600 mb-1">Status</div>
            <div className="text-lg font-bold">{quest.status?.replace('_', ' ')}</div>
          </div>
        </div>

        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 text-blue-900 font-medium mb-1">
            <Target className="w-5 h-5" />
            Goal
          </div>
          <p className="text-blue-800">{quest.goal}</p>
        </div>
      </motion.div>
    </motion.div>
  );
}



