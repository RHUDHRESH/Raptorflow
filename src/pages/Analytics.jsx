import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp, Target, CheckCircle2, AlertCircle, Zap, ArrowRight,
  Clock, Scale, Wrench, X, Archive, Loader2, ArrowLeft, Sparkles,
  ChevronDown, ChevronUp
} from 'lucide-react'
import { cn } from '../utils/cn'
import { MoveService } from '../lib/services/move-service'
import { sprintService } from '../lib/services/sprint-service'
import { useNavigate } from 'react-router-dom'

const insights = [
  {
    id: 1,
    title: 'Increase Move Completion Rate',
    description: 'Your completion rate is 15% below target. Consider breaking down larger moves into smaller tasks.',
    type: 'optimization',
    action: 'Apply Recommendation',
    impact: 'high',
  },
  {
    id: 2,
    title: 'Optimize Weekly Review Frequency',
    description: 'Moves reviewed weekly show 30% better outcomes. Consider increasing review frequency.',
    type: 'suggestion',
    action: 'View Details',
    impact: 'medium',
  },
  {
    id: 3,
    title: 'Focus on High-Impact Moves',
    description: '3 moves account for 60% of your progress. Consider prioritizing similar moves.',
    type: 'insight',
    action: 'See Analysis',
    impact: 'high',
  },
]

const DECISIONS = [
  {
    value: 'Scale',
    label: 'Scale',
    icon: TrendingUp,
    color: 'dark',
    description: 'Double down - increase investment and expand scope'
  },
  {
    value: 'Tweak',
    label: 'Tweak',
    icon: Wrench,
    color: 'neutral',
    description: 'Iterate - adjust approach and continue'
  },
  {
    value: 'Kill',
    label: 'Kill',
    icon: X,
    color: 'neutral',
    description: 'Stop immediately - reallocate resources'
  },
  {
    value: 'Archive',
    label: 'Archive',
    icon: Archive,
    color: 'neutral',
    description: 'Complete - capture learnings and archive'
  }
];

// Mock AI recommendation function - replace with actual AI integration
const generateAIRecommendation = async (move) => {
  // Simulate AI analysis delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Simple heuristic - replace with actual AI
  const progress = move.progress_percentage || 0;
  const hasBlockers = (move.blockers || 0) > 2;
  const isHealthy = move.health_status === 'green';

  if (progress > 75 && isHealthy) {
    return {
      decision: 'Scale',
      reasoning: 'Strong performance with high completion rate and no major blockers. Recommend increasing investment.',
      confidence: 0.85
    };
  }

  if (hasBlockers || progress < 30) {
    return {
      decision: 'Kill',
      reasoning: 'Multiple blockers and low progress suggest fundamental issues. Consider reallocating resources.',
      confidence: 0.7
    };
  }

  return {
    decision: 'Tweak',
    reasoning: 'Moderate progress with room for improvement. Adjust approach and continue monitoring.',
    confidence: 0.75
  };
};

const MoveReviewCard = ({ move, recommendation, onDecide, isCurrentMove }) => {
  const [decision, setDecision] = useState(null);
  const [notes, setNotes] = useState('');

  const handleSubmit = () => {
    if (decision) {
      onDecide(move.id, decision, notes);
    }
  };

  const getHealthColor = (status) => {
    const colors = {
      green: 'text-neutral-900 bg-neutral-100',
      amber: 'text-neutral-700 bg-neutral-50',
      red: 'text-neutral-600 bg-neutral-50'
    };
    return colors[status] || colors.green;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={cn(
        "runway-card p-8",
        isCurrentMove && "border-2 border-neutral-900"
      )}
    >
      {/* Move Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h3 className="font-serif text-3xl mb-2">{move.name}</h3>
            <p className="text-neutral-600">{move.goal || 'No goal specified'}</p>
          </div>
          <div className={cn(
            "px-3 py-1 rounded-full text-sm font-semibold uppercase tracking-wider",
            getHealthColor(move.health_status)
          )}>
            {move.health_status}
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-neutral-50 rounded-lg">
          <p className="text-xs text-neutral-600 uppercase tracking-wider mb-1">Progress</p>
          <p className="text-2xl font-bold">{move.progress_percentage || 0}%</p>
          <div className="mt-2 h-1 bg-neutral-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-neutral-900 transition-all"
              style={{ width: `${move.progress_percentage || 0}%` }}
            />
          </div>
        </div>
        <div className="p-4 bg-neutral-50 rounded-lg">
          <p className="text-xs text-neutral-600 uppercase tracking-wider mb-1">Velocity</p>
          <p className="text-2xl font-bold">{move.velocity || 0}</p>
          <p className="text-xs text-neutral-500 mt-1">tasks/week</p>
        </div>
        <div className="p-4 bg-neutral-50 rounded-lg">
          <p className="text-xs text-neutral-600 uppercase tracking-wider mb-1">Blockers</p>
          <p className="text-2xl font-bold text-neutral-900">{move.blockers || 0}</p>
          <p className="text-xs text-neutral-500 mt-1">active issues</p>
        </div>
      </div>

      {/* AI Recommendation */}
      {recommendation && (
        <div className="mb-6 p-4 bg-neutral-50 border-2 border-neutral-200 rounded-lg">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-neutral-900 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-neutral-900">AI Recommendation</h4>
                <span className="text-xs text-neutral-600">
                  {Math.round(recommendation.confidence * 100)}% confidence
                </span>
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-3 py-1 bg-neutral-900 text-white text-sm font-semibold rounded-full uppercase tracking-wider">
                  {recommendation.decision}
                </span>
              </div>
              <p className="text-sm text-neutral-700">{recommendation.reasoning}</p>
            </div>
          </div>
        </div>
      )}

      {/* Decision Buttons */}
      <div className="mb-6">
        <h4 className="font-semibold mb-3">Your Decision</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {DECISIONS.map(({ value, label, icon: Icon, color }) => (
            <button
              key={value}
              onClick={() => setDecision(value)}
              className={cn(
                "p-4 rounded-lg border-2 transition-all",
                decision === value
                  ? "border-neutral-900 bg-neutral-50"
                  : "border-neutral-200 hover:border-neutral-400"
              )}
            >
              <Icon className={cn(
                "w-6 h-6 mx-auto mb-2",
                decision === value ? "text-neutral-900" : "text-neutral-400"
              )} />
              <p className={cn(
                "font-semibold text-sm",
                decision === value ? "text-neutral-900" : "text-neutral-600"
              )}>
                {label}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Notes */}
      <div className="mb-6">
        <label className="block text-sm font-semibold mb-2">
          Notes (optional)
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          placeholder="Add context for your decision..."
          className="w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
        />
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={!decision}
        className="runway-button-primary w-full py-3 disabled:opacity-50"
      >
        Confirm Decision
        <ArrowRight className="w-4 h-4 ml-2" />
      </button>
    </motion.div>
  );
};

export default function Analytics() {
  const navigate = useNavigate();
  const [selectedInsight, setSelectedInsight] = useState(null)

  // Weekly Review state
  const [currentSprintMoves, setMoves] = useState([]);
  const [aiRecommendations, setRecommendations] = useState({});
  const [currentMoveIndex, setCurrentMoveIndex] = useState(0);
  const [decisions, setDecisions] = useState({});
  const [isLoadingMoves, setIsLoadingMoves] = useState(true);
  const [isGeneratingRecs, setIsGeneratingRecs] = useState(false);
  const [showReviewSection, setShowReviewSection] = useState(true);

  useEffect(() => {
    loadMovesAndRecommendations();
  }, []);

  const loadMovesAndRecommendations = async () => {
    try {
      setIsLoadingMoves(true);

      // Get current sprint
      const sprints = await sprintService.getActiveSprint();
      if (!sprints || sprints.length === 0) {
        setMoves([]);
        return;
      }

      const currentSprint = sprints[0];

      // Get moves for this sprint
      const moveService = new MoveService();
      const moves = await moveService.getBySprintId(currentSprint.id);
      setMoves(moves || []);

      // Generate AI recommendations for each move
      if (moves && moves.length > 0) {
        setIsGeneratingRecs(true);
        const recs = {};
        for (const move of moves) {
          recs[move.id] = await generateAIRecommendation(move);
        }
        setRecommendations(recs);
        setIsGeneratingRecs(false);
      }
    } catch (error) {
      console.error('Error loading moves:', error);
    } finally {
      setIsLoadingMoves(false);
    }
  };

  const handleDecision = async (moveId, decision, notes) => {
    try {
      const moveService = new MoveService();

      // Record decision
      await moveService.recordDecision(moveId, {
        decision,
        rationale: notes,
        ai_recommendation: aiRecommendations[moveId]?.decision,
        ai_reasoning: aiRecommendations[moveId]?.reasoning
      });

      // Update move status based on decision
      if (decision === 'Kill') {
        await moveService.updateStatus(moveId, 'Killed');
      } else if (decision === 'Archive') {
        await moveService.updateStatus(moveId, 'Complete');
      }

      // Store decision locally
      setDecisions({ ...decisions, [moveId]: { decision, notes } });

      // Move to next move or complete
      if (currentMoveIndex < currentSprintMoves.length - 1) {
        setCurrentMoveIndex(currentMoveIndex + 1);
      } else {
        // Review complete
        alert('Weekly review complete!');
        // Reload moves to update the list
        loadMovesAndRecommendations();
      }
    } catch (error) {
      console.error('Error recording decision:', error);
      alert('Failed to save decision. Please try again.');
    }
  };

  const currentMove = currentSprintMoves[currentMoveIndex];
  const reviewProgress = ((currentMoveIndex + Object.keys(decisions).length) / Math.max(currentSprintMoves.length, 1)) * 100;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-b from-white via-neutral-50 to-white" />
        <div className="relative z-10 flex items-center gap-6">
          <div className="w-16 h-16 rounded-full border border-neutral-200 bg-white flex items-center justify-center">
            <TrendingUp className="w-7 h-7 text-neutral-900" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="micro-label tracking-[0.5em]">Performance Hub</span>
              <span className="h-px w-16 bg-neutral-200" />
            </div>
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Read the Pulse
            </h1>
            <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
              Analytics, insights & weekly review ceremony
            </p>
          </div>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total Moves', value: 12, change: '+3', icon: Target },
          { label: 'Completion Rate', value: '87%', change: '+5%', icon: CheckCircle2 },
          { label: 'Avg Velocity', value: '8.5', change: '+1.2', icon: TrendingUp },
          { label: 'Active Reviews', value: 8, change: '+2', icon: AlertCircle },
        ].map((metric, index) => {
          const Icon = metric.icon
          return (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="runway-card p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-neutral-100 text-neutral-900 flex items-center justify-center">
                  <Icon className="w-6 h-6" />
                </div>
                <span className="text-sm font-medium text-neutral-900">{metric.change}</span>
              </div>
              <div className="text-3xl font-bold text-neutral-900 mb-1">{metric.value}</div>
              <div className="text-sm text-neutral-600">{metric.label}</div>
            </motion.div>
          )
        })}
      </div>

      {/* AI Recommendations */}
      <div className="runway-card p-8">
        <div className="flex items-center gap-3 mb-2">
          <Zap className="w-6 h-6 text-neutral-900" />
          <div>
            <p className="micro-label mb-1">Editor's Picks</p>
            <h2 className="text-2xl font-display font-bold">AI Recommendations</h2>
          </div>
        </div>
        <div className="space-y-4">
          {insights.map((insight, index) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "p-6 rounded-xl border-2 transition-all cursor-pointer",
                selectedInsight === insight.id
                  ? "border-neutral-900 bg-neutral-50"
                  : "border-neutral-200 hover:border-neutral-400 hover:bg-neutral-50"
              )}
              onClick={() => setSelectedInsight(selectedInsight === insight.id ? null : insight.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-bold text-neutral-900">{insight.title}</h3>
                    <span className={cn(
                      "px-2 py-1 text-xs font-medium rounded-lg",
                      insight.impact === 'high'
                        ? "bg-neutral-900 text-white"
                        : "bg-neutral-200 text-neutral-900"
                    )}>
                      {insight.impact === 'high' ? 'High Impact' : 'Medium Impact'}
                    </span>
                  </div>
                  <p className="text-neutral-600">{insight.description}</p>
                </div>
              </div>
              {selectedInsight === insight.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 pt-4 border-t border-neutral-200"
                >
                  <button className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors">
                    {insight.action}
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="runway-card p-8">
          <h3 className="text-xl font-bold mb-4">Move Progress Over Time</h3>
          <div className="h-64 flex items-center justify-center text-neutral-400">
            Chart visualization would go here
          </div>
        </div>
        <div className="runway-card p-8">
          <h3 className="text-xl font-bold mb-4">Completion Rate by Category</h3>
          <div className="h-64 flex items-center justify-center text-neutral-400">
            Chart visualization would go here
          </div>
        </div>
      </div>

      {/* Weekly Review Ceremony Section */}
      {!isLoadingMoves && currentSprintMoves.length > 0 && (
        <div className="space-y-6">
          {/* Review Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="runway-card p-8 cursor-pointer"
            onClick={() => setShowReviewSection(!showReviewSection)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full border border-neutral-200 bg-white flex items-center justify-center">
                  <Clock className="w-6 h-6 text-neutral-900" />
                </div>
                <div>
                  <p className="micro-label mb-1">Weekly Ceremony</p>
                  <h2 className="text-2xl font-display font-bold">Scale · Tweak · Retire</h2>
                  <p className="text-sm text-neutral-600 mt-1">
                    {currentSprintMoves.length} move{currentSprintMoves.length !== 1 ? 's' : ''} to review
                  </p>
                </div>
              </div>
              {showReviewSection ? (
                <ChevronUp className="w-6 h-6 text-neutral-400" />
              ) : (
                <ChevronDown className="w-6 h-6 text-neutral-400" />
              )}
            </div>

            {/* Progress Bar */}
            {showReviewSection && (
              <div className="mt-6">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-semibold">
                    Move {currentMoveIndex + 1} of {currentSprintMoves.length}
                  </span>
                  <span className="text-neutral-600">
                    {Math.round(reviewProgress)}% complete
                  </span>
                </div>
                <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-neutral-900"
                    initial={{ width: 0 }}
                    animate={{ width: `${reviewProgress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>
            )}
          </motion.div>

          {/* Current Move Review */}
          <AnimatePresence>
            {showReviewSection && currentMove && (
              <>
                <MoveReviewCard
                  move={currentMove}
                  recommendation={aiRecommendations[currentMove.id]}
                  onDecide={handleDecision}
                  isCurrentMove={true}
                />

                {/* Navigation */}
                <div className="flex justify-between items-center">
                  <button
                    onClick={() => setCurrentMoveIndex(Math.max(0, currentMoveIndex - 1))}
                    disabled={currentMoveIndex === 0}
                    className="runway-button-secondary px-4 py-2 disabled:opacity-50"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous
                  </button>
                  <button
                    onClick={() => setShowReviewSection(false)}
                    className="text-neutral-600 hover:text-neutral-900 text-sm"
                  >
                    Collapse review section
                  </button>
                </div>
              </>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Loading indicator for AI recommendations */}
      {isGeneratingRecs && (
        <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 flex items-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-neutral-900" />
          <span className="text-sm">Generating AI recommendations...</span>
        </div>
      )}
    </div>
  )
}
