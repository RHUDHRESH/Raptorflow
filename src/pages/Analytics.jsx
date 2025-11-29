import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp, Target, CheckCircle2, AlertCircle, Zap, ArrowRight,
  Clock, Scale, Wrench, X, Archive, Loader2, ArrowLeft, Sparkles,
  ChevronDown, ChevronUp, BarChart3
} from 'lucide-react'
import { cn } from '../utils/cn'
import { MoveService } from '../lib/services/move-service'
import { sprintService } from '../lib/services/sprint-service'
import { useNavigate } from 'react-router-dom'
import {
  HeroSection,
  StatCard,
  LuxeCard,
  LuxeButton,
  LuxeBadge,
  LuxeSkeleton,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI'

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
      green: 'success',
      amber: 'warning',
      red: 'error'
    };
    return colors[status] || 'neutral';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <LuxeCard
        className={cn("p-8 transition-all duration-300", isCurrentMove && "ring-2 ring-neutral-900")}
      >
        {/* Move Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <h3 className="font-display text-3xl font-medium text-neutral-900 mb-2">{move.name}</h3>
              <p className="text-neutral-500 text-lg">{move.goal || 'No goal specified'}</p>
            </div>
            <LuxeBadge variant={getHealthColor(move.health_status)}>
              {move.health_status}
            </LuxeBadge>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          <div className="p-5 bg-neutral-50 rounded-xl border border-neutral-100">
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Progress</p>
            <p className="text-3xl font-display font-medium text-neutral-900">{move.progress_percentage || 0}%</p>
            <div className="mt-3 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-neutral-900 transition-all duration-1000"
                style={{ width: `${move.progress_percentage || 0}%` }}
              />
            </div>
          </div>
          <div className="p-5 bg-neutral-50 rounded-xl border border-neutral-100">
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Velocity</p>
            <p className="text-3xl font-display font-medium text-neutral-900">{move.velocity || 0}</p>
            <p className="text-xs text-neutral-500 mt-1">tasks/week</p>
          </div>
          <div className="p-5 bg-neutral-50 rounded-xl border border-neutral-100">
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Blockers</p>
            <p className="text-3xl font-display font-medium text-neutral-900">{move.blockers || 0}</p>
            <p className="text-xs text-neutral-500 mt-1">active issues</p>
          </div>
        </div>

        {/* AI Recommendation */}
        {recommendation && (
          <div className="mb-8 p-6 bg-gradient-to-br from-neutral-900 to-neutral-800 rounded-xl text-white shadow-lg">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0 backdrop-blur-sm">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-white text-lg">AI Recommendation</h4>
                  <span className="text-xs font-medium text-neutral-300 bg-white/10 px-2 py-1 rounded-full">
                    {Math.round(recommendation.confidence * 100)}% confidence
                  </span>
                </div>
                <div className="flex items-center gap-3 mb-3">
                  <span className="px-3 py-1 bg-white text-neutral-900 text-sm font-bold rounded-full uppercase tracking-wider">
                    {recommendation.decision}
                  </span>
                </div>
                <p className="text-neutral-300 leading-relaxed">{recommendation.reasoning}</p>
              </div>
            </div>
          </div>
        )}

        {/* Decision Buttons */}
        <div className="mb-8">
          <h4 className="font-medium text-neutral-900 mb-4">Your Decision</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {DECISIONS.map(({ value, label, icon: Icon, color }) => (
              <button
                key={value}
                onClick={() => setDecision(value)}
                className={cn(
                  "p-4 rounded-xl border-2 transition-all duration-200 flex flex-col items-center justify-center gap-3 hover:shadow-md",
                  decision === value
                    ? "border-neutral-900 bg-neutral-50"
                    : "border-neutral-100 bg-white hover:border-neutral-300"
                )}
              >
                <Icon className={cn(
                  "w-6 h-6",
                  decision === value ? "text-neutral-900" : "text-neutral-400"
                )} />
                <p className={cn(
                  "font-medium text-sm",
                  decision === value ? "text-neutral-900" : "text-neutral-500"
                )}>
                  {label}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Notes */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-neutral-900 mb-2">
            Notes (optional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Add context for your decision..."
            className="w-full px-4 py-3 bg-neutral-50 border border-neutral-200 rounded-xl focus:outline-none focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900 transition-all resize-none"
          />
        </div>

        {/* Submit Button */}
        <LuxeButton
          onClick={handleSubmit}
          disabled={!decision}
          className="w-full justify-center py-4 text-base"
          size="lg"
        >
          Confirm Decision
          <ArrowRight className="w-4 h-4 ml-2" />
        </LuxeButton>
      </LuxeCard>
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
          title="Read the Pulse"
          subtitle="Analytics, insights & weekly review ceremony."
          metrics={[
            { label: 'Total Moves', value: '12' },
            { label: 'Completion Rate', value: '87%' },
            { label: 'Avg Velocity', value: '8.5' }
          ]}
        />
      </motion.div>

      {/* Key Metrics */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
        variants={staggerContainer}
      >
        <StatCard
          label="Total Moves"
          value="12"
          change="+3"
          trend="up"
          icon={Target}
        />
        <StatCard
          label="Completion Rate"
          value="87%"
          change="+5%"
          trend="up"
          icon={CheckCircle2}
        />
        <StatCard
          label="Avg Velocity"
          value="8.5"
          change="+1.2"
          trend="up"
          icon={TrendingUp}
        />
        <StatCard
          label="Active Reviews"
          value="8"
          change="+2"
          trend="down"
          icon={AlertCircle}
        />
      </motion.div>

      {/* AI Recommendations */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-12 h-12 rounded-2xl bg-neutral-900 flex items-center justify-center text-white shadow-lg shadow-neutral-900/20">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1">Editor's Picks</p>
              <h2 className="text-2xl font-display font-medium text-neutral-900">AI Recommendations</h2>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {insights.map((insight, index) => (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={cn(
                  "p-6 rounded-xl border transition-all cursor-pointer group h-full flex flex-col justify-between",
                  selectedInsight === insight.id
                    ? "border-neutral-900 bg-neutral-50 shadow-md"
                    : "border-neutral-200 bg-white hover:border-neutral-300 hover:shadow-sm"
                )}
                onClick={() => setSelectedInsight(selectedInsight === insight.id ? null : insight.id)}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <LuxeBadge variant={insight.impact === 'high' ? 'dark' : 'neutral'}>
                      {insight.impact === 'high' ? 'High Impact' : 'Medium Impact'}
                    </LuxeBadge>
                  </div>
                  <h3 className="text-lg font-medium text-neutral-900 mb-2 group-hover:text-neutral-700 transition-colors">{insight.title}</h3>
                  <p className="text-neutral-500 text-sm leading-relaxed mb-6">{insight.description}</p>
                </div>

                <div className={cn(
                  "overflow-hidden transition-all duration-300",
                  selectedInsight === insight.id ? "max-h-20 opacity-100" : "max-h-0 opacity-0"
                )}>
                  <LuxeButton size="sm" className="w-full justify-center">
                    {insight.action}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </LuxeButton>
                </div>
              </motion.div>
            ))}
          </div>
        </LuxeCard>
      </motion.div>

      {/* Charts Placeholder */}
      <motion.div variants={fadeInUp} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LuxeCard className="p-8 h-[400px] flex flex-col">
          <h3 className="font-display text-xl font-medium text-neutral-900 mb-6">Move Progress Over Time</h3>
          <div className="flex-1 flex items-center justify-center border-2 border-dashed border-neutral-100 rounded-xl bg-neutral-50/50">
            <div className="text-center">
              <BarChart3 className="w-8 h-8 text-neutral-300 mx-auto mb-2" />
              <p className="text-neutral-400 text-sm">Chart visualization would go here</p>
            </div>
          </div>
        </LuxeCard>
        <LuxeCard className="p-8 h-[400px] flex flex-col">
          <h3 className="font-display text-xl font-medium text-neutral-900 mb-6">Completion Rate by Category</h3>
          <div className="flex-1 flex items-center justify-center border-2 border-dashed border-neutral-100 rounded-xl bg-neutral-50/50">
            <div className="text-center">
              <BarChart3 className="w-8 h-8 text-neutral-300 mx-auto mb-2" />
              <p className="text-neutral-400 text-sm">Chart visualization would go here</p>
            </div>
          </div>
        </LuxeCard>
      </motion.div>

      {/* Weekly Review Ceremony Section */}
      {!isLoadingMoves && currentSprintMoves.length > 0 && (
        <motion.div variants={fadeInUp} className="space-y-6">
          {/* Review Section Header */}
          <LuxeCard
            className="p-8 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => setShowReviewSection(!showReviewSection)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 rounded-2xl bg-neutral-900 flex items-center justify-center text-white shadow-lg shadow-neutral-900/20">
                  <Clock className="w-8 h-8" />
                </div>
                <div>
                  <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1">Weekly Ceremony</p>
                  <h2 className="text-3xl font-display font-medium text-neutral-900">Scale · Tweak · Retire</h2>
                  <p className="text-neutral-500 mt-1">
                    {currentSprintMoves.length} move{currentSprintMoves.length !== 1 ? 's' : ''} to review
                  </p>
                </div>
              </div>
              <div className="w-10 h-10 rounded-full bg-neutral-50 flex items-center justify-center text-neutral-400">
                {showReviewSection ? (
                  <ChevronUp className="w-6 h-6" />
                ) : (
                  <ChevronDown className="w-6 h-6" />
                )}
              </div>
            </div>

            {/* Progress Bar */}
            <AnimatePresence>
              {showReviewSection && (
                <motion.div
                  initial={{ height: 0, opacity: 0, marginTop: 0 }}
                  animate={{ height: 'auto', opacity: 1, marginTop: 24 }}
                  exit={{ height: 0, opacity: 0, marginTop: 0 }}
                  className="overflow-hidden"
                >
                  <div className="flex justify-between text-sm mb-3">
                    <span className="font-medium text-neutral-900">
                      Move {currentMoveIndex + 1} of {currentSprintMoves.length}
                    </span>
                    <span className="text-neutral-500">
                      {Math.round(reviewProgress)}% complete
                    </span>
                  </div>
                  <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-neutral-900"
                      initial={{ width: 0 }}
                      animate={{ width: `${reviewProgress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </LuxeCard>

          {/* Current Move Review */}
          <AnimatePresence mode="wait">
            {showReviewSection && currentMove && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <MoveReviewCard
                  move={currentMove}
                  recommendation={aiRecommendations[currentMove.id]}
                  onDecide={handleDecision}
                  isCurrentMove={true}
                />

                {/* Navigation */}
                <div className="flex justify-between items-center px-4">
                  <LuxeButton
                    variant="ghost"
                    onClick={() => setCurrentMoveIndex(Math.max(0, currentMoveIndex - 1))}
                    disabled={currentMoveIndex === 0}
                    className="text-neutral-500 hover:text-neutral-900"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous Move
                  </LuxeButton>
                  <button
                    onClick={() => setShowReviewSection(false)}
                    className="text-sm text-neutral-400 hover:text-neutral-600 transition-colors"
                  >
                    Collapse review section
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Loading indicator for AI recommendations */}
      {isGeneratingRecs && (
        <div className="fixed bottom-8 right-8 bg-white shadow-xl shadow-neutral-900/10 rounded-full px-6 py-3 flex items-center gap-3 border border-neutral-100 z-50 animate-in fade-in slide-in-from-bottom-4">
          <Loader2 className="w-4 h-4 animate-spin text-neutral-900" />
          <span className="text-sm font-medium text-neutral-900">Generating AI recommendations...</span>
        </div>
      )}
    </motion.div>
  )
}
