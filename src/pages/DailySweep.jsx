import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertCircle, CheckCircle, Clock, TrendingUp, Target, Zap,
  Filter, ChevronDown, X, CheckCircle2, ArrowRight
} from 'lucide-react';
import { useMoves, useICPs } from '../hooks/useMoveSystem';
import { moveService } from '../lib/services/move-service';
import { analyticsService } from '../lib/services/analytics-service';
import { cn } from '../utils/cn';
import {
  HeroSection,
  StatCard,
  LuxeCard,
  LuxeButton,
  LuxeBadge,
  FilterPills,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI';

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
      high: 'error',
      medium: 'warning',
      low: 'neutral',
    };
    return colors[priority] || 'neutral';
  };

  const getPriorityIcon = (priority) => {
    if (priority === 'high') return <AlertCircle className="w-5 h-5 text-red-500" />;
    if (priority === 'medium') return <Clock className="w-5 h-5 text-amber-500" />;
    return <Target className="w-5 h-5 text-neutral-500" />;
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

  const priorityFilters = [
    { value: 'all', label: 'All Priorities' },
    { value: 'high', label: 'High Priority', count: stats.high },
    { value: 'medium', label: 'Medium Priority', count: stats.medium },
    { value: 'low', label: 'Low Priority', count: stats.low },
  ];

  return (
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-12"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {/* Header */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Today's Quick Wins"
          subtitle="AI-detected priorities and action items. Focus on high-impact, time-boxed tasks."
          metrics={[
            { label: 'Total Items', value: stats.total.toString() },
            { label: 'High Priority', value: stats.high.toString() },
            { label: 'Completed', value: stats.completed.toString() }
          ]}
        />
      </motion.div>

      {/* Stats Overview */}
      <motion.div
        className="grid grid-cols-2 md:grid-cols-5 gap-4"
        variants={staggerContainer}
      >
        <StatCard
          label="Total Items"
          value={stats.total}
          icon={Target}
          trend="neutral"
          className="p-6"
        />
        <StatCard
          label="High Priority"
          value={stats.high}
          icon={AlertCircle}
          trend={stats.high > 0 ? 'down' : 'neutral'}
          className="p-6"
        />
        <StatCard
          label="Medium"
          value={stats.medium}
          icon={Clock}
          trend="neutral"
          className="p-6"
        />
        <StatCard
          label="Low Priority"
          value={stats.low}
          icon={CheckCircle}
          trend="neutral"
          className="p-6"
        />
        <StatCard
          label="Completed"
          value={stats.completed}
          icon={CheckCircle2}
          trend="up"
          className="p-6"
        />
      </motion.div>

      {/* Filters */}
      <motion.div variants={fadeInUp} className="flex flex-col md:flex-row justify-between items-center gap-4">
        <FilterPills
          filters={priorityFilters}
          activeFilter={selectedPriority}
          onFilterChange={setSelectedPriority}
        />

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-neutral-400" />
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-transparent border-none text-sm font-medium text-neutral-600 focus:ring-0 cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </motion.div>

      {/* Quick Wins List */}
      <motion.div variants={staggerContainer} className="space-y-4">
        <AnimatePresence>
          {filteredWins.length === 0 ? (
            <motion.div variants={fadeInUp}>
              <LuxeCard className="p-16 text-center flex flex-col items-center justify-center border-dashed">
                <div className="w-16 h-16 rounded-full bg-neutral-50 flex items-center justify-center mb-6">
                  <CheckCircle className="w-8 h-8 text-neutral-400" />
                </div>
                <h3 className="text-2xl font-display font-medium text-neutral-900 mb-2">All Clear!</h3>
                <p className="text-neutral-500 max-w-md">
                  {quickWins.length === 0
                    ? "No quick wins available. Your moves are running smoothly."
                    : "No items match your filters. Great work!"}
                </p>
              </LuxeCard>
            </motion.div>
          ) : (
            filteredWins.map((win) => (
              <motion.div
                key={win.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className={cn(
                  "transition-all duration-300",
                  win.status === 'completed' && "opacity-60 grayscale"
                )}
              >
                <LuxeCard className="p-6 hover:shadow-md transition-shadow group">
                  <div className="flex items-start gap-6">
                    {/* Priority Icon */}
                    <div className={cn(
                      "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors",
                      win.priority === 'high' ? "bg-red-50 text-red-600" :
                        win.priority === 'medium' ? "bg-amber-50 text-amber-600" :
                          "bg-neutral-50 text-neutral-600"
                    )}>
                      {getPriorityIcon(win.priority)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <h3 className={cn(
                              "text-lg font-medium text-neutral-900",
                              win.status === 'completed' && "line-through text-neutral-500"
                            )}>
                              {win.title}
                            </h3>
                            <LuxeBadge variant={getPriorityColor(win.priority)} className="text-[10px] py-0.5 px-2">
                              {win.priority}
                            </LuxeBadge>
                          </div>
                          <p className="text-neutral-500 leading-relaxed">
                            {win.description}
                          </p>
                        </div>
                        <button
                          onClick={() => handleDismiss(win.id)}
                          className="p-2 text-neutral-400 hover:text-neutral-900 hover:bg-neutral-100 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="flex flex-wrap items-center gap-4 mt-4 pt-4 border-t border-neutral-100">
                        <div className="flex items-center gap-2 text-xs font-medium text-neutral-500 bg-neutral-50 px-2 py-1 rounded-md">
                          {getTypeIcon(win.type)}
                          <span className="capitalize">{win.type.replace('_', ' ')}</span>
                        </div>

                        {win.timeEstimate && (
                          <div className="flex items-center gap-2 text-xs font-medium text-neutral-500 bg-neutral-50 px-2 py-1 rounded-md">
                            <Clock className="w-3 h-3" />
                            {win.timeEstimate}
                          </div>
                        )}

                        {/* Suggested Topics (for content wins) */}
                        {win.suggestedTopics && win.suggestedTopics.length > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-neutral-400">Topics:</span>
                            {win.suggestedTopics.map((topic, idx) => (
                              <span key={idx} className="text-xs text-neutral-600 bg-neutral-50 px-2 py-1 rounded-md border border-neutral-100">
                                {topic}
                              </span>
                            ))}
                          </div>
                        )}

                        <div className="flex-1" />

                        {/* Actions */}
                        <div className="flex gap-3">
                          {win.status === 'pending' ? (
                            <>
                              {win.move_id && (
                                <LuxeButton
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => window.location.href = `/moves/${win.move_id}`}
                                >
                                  View Move
                                </LuxeButton>
                              )}
                              <LuxeButton
                                size="sm"
                                onClick={() => handleComplete(win.id)}
                                className="bg-neutral-900 text-white hover:bg-neutral-800"
                              >
                                <CheckCircle className="w-4 h-4 mr-2" />
                                {win.action}
                              </LuxeButton>
                            </>
                          ) : (
                            <span className="flex items-center gap-2 text-sm font-medium text-green-600 bg-green-50 px-3 py-1.5 rounded-full">
                              <CheckCircle2 className="w-4 h-4" />
                              Completed
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </LuxeCard>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}
