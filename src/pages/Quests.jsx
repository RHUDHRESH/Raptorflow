import { useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Target, 
  Lock, 
  CheckCircle2, 
  PlayCircle,
  ArrowRight,
  Sparkles,
  TrendingUp
} from 'lucide-react'
import { cn } from '../utils/cn'
import { createQuest } from '../utils/moveSystemTypes'

// Mock quests
const mockQuests = [
  createQuest({
    id: 'quest-1',
    name: 'Operation First Five',
    objective: 'Acquire 5 Beta Clients',
    prerequisite_node_ids: ['icp-definition'],
    recommended_move_ids: ['authority-sprint', 'asset-forge'],
    reward_node_id: 'paid-ads',
    progress: 67,
    status: 'active'
  }),
  createQuest({
    id: 'quest-2',
    name: 'Build First Lead Magnet',
    objective: 'Capture 100 emails from cohort: Startup Founders',
    prerequisite_node_ids: ['icp-definition'],
    recommended_move_ids: ['asset-forge'],
    reward_node_id: 'lead-magnet',
    progress: 0,
    status: 'locked'
  }),
  createQuest({
    id: 'quest-3',
    name: 'Establish Authority',
    objective: 'Publish 10 high-value content pieces',
    prerequisite_node_ids: ['lead-magnet', 'email-nurture'],
    recommended_move_ids: ['authority-sprint'],
    reward_node_id: 'paid-ads',
    progress: 100,
    status: 'complete'
  })
]

export default function Quests() {
  const [quests] = useState(mockQuests)

  const getQuestStatusColor = (status) => {
    if (status === 'complete') return 'bg-green-100 text-green-900 border-green-200'
    if (status === 'active') return 'bg-blue-100 text-blue-900 border-blue-200'
    return 'bg-neutral-100 text-neutral-900 border-neutral-200 opacity-60'
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
            <span className="micro-label tracking-[0.5em]">Quests & Tech Tree</span>
            <span className="h-px w-16 bg-neutral-200" />
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-400">Capability Progression</span>
          </div>
          <div className="space-y-4">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Quest Lines
            </h1>
            <p className="font-sans text-base text-neutral-600 max-w-2xl leading-relaxed">
              Complete quests to unlock new capabilities and maneuvers. Each quest wraps a Line of Operation with clear objectives and rewards.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Active Quests */}
      <div>
        <h2 className="text-xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
          <PlayCircle className="w-5 h-5" />
          Active Quests
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {quests.filter(q => q.status === 'active').map((quest, index) => (
            <motion.div
              key={quest.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="runway-card p-6 hover:shadow-xl transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-neutral-900 mb-2">{quest.name}</h3>
                  <p className="text-sm text-neutral-600">{quest.objective}</p>
                </div>
                <PlayCircle className="w-6 h-6 text-blue-600 flex-shrink-0" />
              </div>

              {/* Progress */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-neutral-600">Progress</span>
                  <span className="text-sm font-bold text-neutral-900">{quest.progress}%</span>
                </div>
                <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${quest.progress}%` }}
                    transition={{ duration: 1, delay: index * 0.2 }}
                    className="h-full bg-gradient-to-r from-blue-600 to-blue-800 rounded-full"
                  />
                </div>
              </div>

              {/* Recommended Moves */}
              <div className="mb-4 pt-4 border-t border-neutral-200">
                <p className="text-xs font-medium text-neutral-700 mb-2">Recommended Moves:</p>
                <div className="flex flex-wrap gap-2">
                  {quest.recommended_move_ids.slice(0, 2).map((moveId) => (
                    <span
                      key={moveId}
                      className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.1em] bg-neutral-100 text-neutral-700 rounded"
                    >
                      {moveId.replace(/-/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>

              {/* Reward */}
              {quest.reward_node_id && (
                <div className="pt-4 border-t border-neutral-200">
                  <div className="flex items-center gap-2 text-xs text-neutral-600">
                    <Sparkles className="w-4 h-4 text-yellow-600" />
                    <span>Reward: Unlock <span className="font-medium text-neutral-900">{quest.reward_node_id.replace(/-/g, ' ')}</span></span>
                  </div>
                </div>
              )}

              <Link
                to={`/quests/${quest.id}`}
                className="inline-flex items-center gap-2 mt-4 text-sm font-medium text-neutral-900 hover:underline"
              >
                View Details
                <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Completed Quests */}
      {quests.filter(q => q.status === 'complete').length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            Completed
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {quests.filter(q => q.status === 'complete').map((quest, index) => (
              <motion.div
                key={quest.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="runway-card p-6 opacity-75"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-neutral-900 mb-2">{quest.name}</h3>
                    <p className="text-sm text-neutral-600">{quest.objective}</p>
                  </div>
                  <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
                </div>
                <div className="w-full h-2 bg-green-200 rounded-full">
                  <div className="h-full bg-green-600 rounded-full" style={{ width: '100%' }} />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Locked Quests */}
      {quests.filter(q => q.status === 'locked').length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <Lock className="w-5 h-5" />
            Locked
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {quests.filter(q => q.status === 'locked').map((quest, index) => (
              <motion.div
                key={quest.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="runway-card p-6 opacity-60 relative"
              >
                <div className="absolute top-4 right-4">
                  <Lock className="w-5 h-5 text-neutral-400" />
                </div>
                <h3 className="text-lg font-bold text-neutral-900 mb-2">{quest.name}</h3>
                <p className="text-sm text-neutral-600 mb-4">{quest.objective}</p>
                <div className="pt-4 border-t border-neutral-200">
                  <p className="text-xs font-medium text-neutral-700 mb-2">Prerequisites:</p>
                  <ul className="space-y-1">
                    {quest.prerequisite_node_ids.map((prereq, i) => (
                      <li key={i} className="text-xs text-neutral-600 flex items-center gap-1">
                        <span className="w-1 h-1 rounded-full bg-neutral-400" />
                        {prereq.replace(/-/g, ' ')}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Link to Tech Tree */}
      <div className="runway-card p-6 bg-gradient-to-r from-neutral-50 to-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-neutral-900 mb-2">Explore Tech Tree</h3>
            <p className="text-sm text-neutral-600">
              Visualize capability dependencies and unlock paths
            </p>
          </div>
          <Link
            to="/tech-tree"
            className="inline-flex items-center gap-2 px-6 py-3 border border-neutral-900 text-neutral-900 hover:bg-neutral-900 hover:text-white transition-colors rounded-lg"
          >
            View Tech Tree
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  )
}


