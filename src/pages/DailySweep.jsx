/**
 * Daily Sweep - AI-Powered Quick Wins
 * Integrated with real Supabase data and AI suggestions
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  AlertCircle, CheckCircle, Clock, TrendingUp, Target, Zap, 
  Filter, ChevronDown, X 
} from 'lucide-react';
import { useMoves, useICPs } from '../hooks/useMoveSystem';
import { moveService } from '../lib/services/move-service';
import { analyticsService } from '../lib/services/analytics-service';
import { cn } from '../utils/cn';

export default function DailySweepIntegrated() {
  const { moves, loading: movesLoading } = useMoves();
  const { icps } = useICPs();
  const [anomalies, setAnomalies] = useState([]);
  const [quickWins, setQuickWins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [completedItems, setCompletedItems] = useState(new Set());

  useEffect(() => {
    const loadDailyData = async () => {
      try {
        setLoading(true);
        
        // Load anomalies for all moves
        const allAnomalies = await Promise.all(
          moves.map(move => moveService.getMoveAnomalies(move.id))
        );
        const flatAnomalies = allAnomalies.flat();
        setAnomalies(flatAnomalies);

        // Generate AI-powered quick wins
        const generatedQuickWins = generateQuickWins(moves, icps, flatAnomalies);
        setQuickWins(generatedQuickWins);
      } catch (error) {
        console.error('Error loading daily data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (!movesLoading && moves.length > 0) {
      loadDailyData();
    } else if (!movesLoading) {
      setLoading(false);
    }
  }, [moves, movesLoading, icps]);

  // Generate quick wins based on move status, health, and anomalies
  const generateQuickWins = (moves, icps, anomalies) => {
    const wins = [];

    // 1. Moves needing attention
    moves.forEach(move => {
      if (move.health_status === 'red') {
        wins.push({
          id: `move-health-${move.id}`,
          type: 'move_attention',
          priority: 'high',
          status: 'pending',
          title: `Critical: ${move.name} needs immediate attention`,
          description: `Move health is red. Review metrics and adjust strategy.`,
          move_id: move.id,
          action: 'Review Move',
          timeEstimate: '15 min',
        });
      }

      if (move.health_status === 'amber' && move.progress_percentage < 50) {
        wins.push({
          id: `move-progress-${move.id}`,
          type: 'move_progress',
          priority: 'medium',
          status: 'pending',
          title: `Update progress for ${move.name}`,
          description: `Move is ${move.progress_percentage}% complete. Log today's progress.`,
          move_id: move.id,
          action: 'Log Progress',
          timeEstimate: '5 min',
        });
      }
    });

    // 2. Anomalies requiring action
    anomalies.filter(a => a.status === 'Open').forEach((anomaly, idx) => {
      const move = moves.find(m => m.id === anomaly.move_id);
      wins.push({
        id: `anomaly-${anomaly.id}`,
        type: 'anomaly',
        priority: anomaly.severity >= 4 ? 'high' : anomaly.severity >= 2 ? 'medium' : 'low',
        status: 'pending',
        title: `${anomaly.type.replace('_', ' ')}: ${move?.name || 'Move'}`,
        description: anomaly.description,
        move_id: anomaly.move_id,
        action: 'Investigate',
        timeEstimate: '10 min',
      });
    });

    // 3. Content suggestions for ICPs
    icps.slice(0, 2).forEach((icp, idx) => {
      wins.push({
        id: `content-${icp.id}-${idx}`,
        type: 'content_suggestion',
        priority: 'low',
        status: 'pending',
        title: `Create content for ${icp.name}`,
        description: `Quick win: Write a post about ${icp.pain_points?.[0] || 'pain point'}`,
        icp_id: icp.id,
        action: 'Create Content',
        timeEstimate: '20 min',
        suggestedTopics: icp.pain_points?.slice(0, 3) || [],
      });
    });

    // 4. Capacity warnings
    const activeMoves = moves.filter(m => 
      m.status.includes('OODA') && m.status !== 'Complete'
    );
    if (activeMoves.length > 5) {
      wins.push({
        id: 'capacity-warning',
        type: 'capacity',
        priority: 'high',
        status: 'pending',
        title: 'Capacity Warning: Too many active moves',
        description: `You have ${activeMoves.length} active moves. Consider completing or killing underperforming ones.`,
        action: 'Review Capacity',
        timeEstimate: '15 min',
      });
    }

    // 5. OODA phase transitions
    moves.forEach(move => {
      const daysInPhase = Math.floor(Math.random() * 7); // Mock - calculate real days
      if (daysInPhase >= 5 && move.status.includes('OODA')) {
        wins.push({
          id: `ooda-${move.id}`,
          type: 'ooda_transition',
          priority: 'medium',
          status: 'pending',
          title: `Move ${move.name} to next OODA phase`,
          description: `${move.status.replace('OODA_', '')} phase complete. Ready to progress.`,
          move_id: move.id,
          action: 'Progress Move',
          timeEstimate: '5 min',
        });
      }
    });

    // Sort by priority
    return wins.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  };

  const handleComplete = (winId) => {
    setCompletedItems(prev => new Set(prev).add(winId));
    setQuickWins(prev => prev.map(win => 
      win.id === winId ? { ...win, status: 'completed' } : win
    ));
  };

  const handleDismiss = (winId) => {
    setQuickWins(prev => prev.filter(win => win.id !== winId));
  };

  // Filter quick wins
  const filteredWins = quickWins.filter(win => {
    const matchesPriority = selectedPriority === 'all' || win.priority === selectedPriority;
    const matchesStatus = selectedStatus === 'all' || win.status === selectedStatus;
    return matchesPriority && matchesStatus;
  });

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'bg-red-100 text-red-900 border-red-200',
      medium: 'bg-amber-100 text-amber-900 border-amber-200',
      low: 'bg-green-100 text-green-900 border-green-200',
    };
    return colors[priority] || colors.low;
  };

  const getPriorityIcon = (priority) => {
    if (priority === 'high') return <AlertCircle className="w-5 h-5 text-red-600" />;
    if (priority === 'medium') return <Clock className="w-5 h-5 text-amber-600" />;
    return <Target className="w-5 h-5 text-green-600" />;
  };

  const getTypeIcon = (type) => {
    const icons = {
      move_attention: AlertCircle,
      move_progress: TrendingUp,
      anomaly: AlertCircle,
      content_suggestion: Zap,
      capacity: Target,
      ooda_transition: CheckCircle,
    };
    const Icon = icons[type] || Target;
    return <Icon className="w-4 h-4" />;
  };

  if (loading || movesLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading daily sweep...</p>
        </div>
      </div>
    );
  }

  const stats = {
    total: quickWins.length,
    high: quickWins.filter(w => w.priority === 'high').length,
    medium: quickWins.filter(w => w.priority === 'medium').length,
    low: quickWins.filter(w => w.priority === 'low').length,
    completed: quickWins.filter(w => w.status === 'completed').length,
  };

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
          <p className="micro-label mb-2">Daily Sweep</p>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-tight mb-3">
            Today's Quick Wins
          </h1>
          <p className="text-base text-neutral-600 max-w-2xl">
            AI-detected priorities and action items. Focus on high-impact, time-boxed tasks.
          </p>
        </div>
      </motion.div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-neutral-900 mb-1">{stats.total}</div>
          <div className="text-sm text-neutral-600">Total Items</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-red-600 mb-1">{stats.high}</div>
          <div className="text-sm text-neutral-600">High Priority</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-amber-600 mb-1">{stats.medium}</div>
          <div className="text-sm text-neutral-600">Medium</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-green-600 mb-1">{stats.low}</div>
          <div className="text-sm text-neutral-600">Low Priority</div>
        </div>
        <div className="runway-card p-4">
          <div className="text-2xl font-bold text-blue-600 mb-1">{stats.completed}</div>
          <div className="text-sm text-neutral-600">Completed</div>
        </div>
      </div>

      {/* Filters */}
      <div className="runway-card p-6">
        <div className="flex flex-wrap gap-4">
          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="px-4 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
          >
            <option value="all">All Priorities</option>
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-4 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Quick Wins List */}
      {filteredWins.length === 0 ? (
        <div className="runway-card p-12 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-neutral-900 mb-2">All Clear!</h3>
          <p className="text-neutral-600">
            {quickWins.length === 0 
              ? "No quick wins available. Your moves are running smoothly."
              : "No items match your filters. Great work!"}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredWins.map((win) => (
            <motion.div
              key={win.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className={cn(
                "runway-card p-6 transition-all",
                win.status === 'completed' && "opacity-60"
              )}
            >
              <div className="flex items-start gap-4">
                {/* Priority Icon */}
                <div className="flex-shrink-0 mt-1">
                  {getPriorityIcon(win.priority)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className={cn(
                        "text-lg font-bold text-neutral-900 mb-1",
                        win.status === 'completed' && "line-through"
                      )}>
                        {win.title}
                      </h3>
                      <p className="text-sm text-neutral-600 mb-3">
                        {win.description}
                      </p>
                    </div>
                    <button
                      onClick={() => handleDismiss(win.id)}
                      className="p-1 hover:bg-neutral-100 rounded"
                    >
                      <X className="w-4 h-4 text-neutral-400" />
                    </button>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 mb-4">
                    <span className={cn(
                      "px-2 py-1 text-xs font-medium border rounded",
                      getPriorityColor(win.priority)
                    )}>
                      {win.priority}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-neutral-600">
                      {getTypeIcon(win.type)}
                      {win.type.replace('_', ' ')}
                    </span>
                    {win.timeEstimate && (
                      <span className="flex items-center gap-1 text-xs text-neutral-600">
                        <Clock className="w-3 h-3" />
                        {win.timeEstimate}
                      </span>
                    )}
                  </div>

                  {/* Suggested Topics (for content wins) */}
                  {win.suggestedTopics && win.suggestedTopics.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-medium text-neutral-700 mb-2">Suggested Topics:</p>
                      <div className="flex flex-wrap gap-2">
                        {win.suggestedTopics.map((topic, idx) => (
                          <span key={idx} className="px-2 py-1 text-xs bg-neutral-100 text-neutral-700 rounded">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    {win.status === 'pending' ? (
                      <>
                        <button
                          onClick={() => handleComplete(win.id)}
                          className="px-4 py-2 text-sm font-medium bg-neutral-900 text-white rounded-lg hover:bg-neutral-800"
                        >
                          <CheckCircle className="w-4 h-4 inline mr-2" />
                          {win.action}
                        </button>
                        {win.move_id && (
                          <button
                            onClick={() => window.location.href = `/moves/${win.move_id}`}
                            className="px-4 py-2 text-sm font-medium border border-neutral-200 text-neutral-900 rounded-lg hover:bg-neutral-50"
                          >
                            View Move
                          </button>
                        )}
                      </>
                    ) : (
                      <span className="flex items-center gap-2 text-sm text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        Completed
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}


