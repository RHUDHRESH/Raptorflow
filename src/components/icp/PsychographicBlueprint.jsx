/**
 * Psychographic Blueprint Visualization
 * Displays B=MAP psychographic scores as an interactive radar/grid chart
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const DIMENSIONS = [
  { key: 'motivation', label: 'Motivation', description: 'Drive to take action' },
  { key: 'ability', label: 'Ability', description: 'Capability to execute' },
  { key: 'prompt_receptiveness', label: 'Prompt Receptiveness', description: 'Openness to triggers' },
  { key: 'risk_tolerance', label: 'Risk Tolerance', description: 'Comfort with uncertainty' },
  { key: 'status_drive', label: 'Status Drive', description: 'Desire for recognition' },
  { key: 'community_orientation', label: 'Community Orientation', description: 'Social influence factor' },
  { key: 'decision_speed', label: 'Decision Speed', description: 'Time to commit' }
];

export default function PsychographicBlueprint({ scores = {}, onEdit, readOnly = false }) {
  const [hoveredDimension, setHoveredDimension] = useState(null);

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 5) return 'text-blue-600';
    return 'text-neutral-600';
  };

  const getScoreTrend = (score) => {
    if (score >= 8) return TrendingUp;
    if (score <= 3) return TrendingDown;
    return Minus;
  };

  const handleScoreChange = (key, delta) => {
    if (readOnly || !onEdit) return;
    const currentScore = scores[key] || 5;
    const newScore = Math.max(1, Math.min(10, currentScore + delta));
    onEdit(key, newScore);
  };

  return (
    <div className="runway-card p-6">
      <div className="mb-6">
        <h3 className="font-serif text-2xl mb-2">Psychographic Blueprint</h3>
        <p className="text-sm text-neutral-600">
          B=MAP framework: Behavior = Motivation × Ability × Prompt
        </p>
      </div>

      {/* Grid View */}
      <div className="space-y-4">
        {DIMENSIONS.map((dimension) => {
          const score = scores[dimension.key] || 5;
          const TrendIcon = getScoreTrend(score);
          const isHovered = hoveredDimension === dimension.key;

          return (
            <motion.div
              key={dimension.key}
              className="relative"
              onMouseEnter={() => setHoveredDimension(dimension.key)}
              onMouseLeave={() => setHoveredDimension(null)}
              whileHover={{ scale: readOnly ? 1 : 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <TrendIcon className={`w-4 h-4 ${getScoreColor(score)}`} />
                  <div>
                    <h4 className="font-semibold text-sm">{dimension.label}</h4>
                    {isHovered && (
                      <p className="text-xs text-neutral-600">{dimension.description}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {!readOnly && (
                    <>
                      <button
                        onClick={() => handleScoreChange(dimension.key, -1)}
                        className="w-6 h-6 rounded-full bg-neutral-100 hover:bg-neutral-200 flex items-center justify-center text-neutral-600"
                        disabled={score <= 1}
                      >
                        −
                      </button>
                    </>
                  )}
                  <span className={`font-bold text-lg ${getScoreColor(score)} min-w-[2rem] text-center`}>
                    {score}
                  </span>
                  {!readOnly && (
                    <button
                      onClick={() => handleScoreChange(dimension.key, 1)}
                      className="w-6 h-6 rounded-full bg-neutral-100 hover:bg-neutral-200 flex items-center justify-center text-neutral-600"
                      disabled={score >= 10}
                    >
                      +
                    </button>
                  )}
                </div>
              </div>

              {/* Score bar */}
              <div className="relative h-2 bg-neutral-100 rounded-full overflow-hidden">
                <motion.div
                  className="absolute left-0 top-0 h-full bg-gradient-to-r from-blue-500 to-green-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${score * 10}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>

              {/* Score labels */}
              <div className="flex justify-between text-xs text-neutral-400 mt-1">
                <span>Low (1)</span>
                <span>Medium (5)</span>
                <span>High (10)</span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-sm text-blue-900 mb-2">Profile Summary</h4>
        <div className="grid grid-cols-3 gap-4 text-xs">
          <div>
            <p className="text-neutral-600">Avg Score</p>
            <p className="font-bold text-blue-900">
              {(
                Object.values(scores).reduce((sum, val) => sum + val, 0) /
                Math.max(Object.values(scores).length, 1)
              ).toFixed(1)}
            </p>
          </div>
          <div>
            <p className="text-neutral-600">Strengths</p>
            <p className="font-bold text-green-900">
              {Object.values(scores).filter(v => v >= 8).length}
            </p>
          </div>
          <div>
            <p className="text-neutral-600">Gaps</p>
            <p className="font-bold text-red-900">
              {Object.values(scores).filter(v => v <= 3).length}
            </p>
          </div>
        </div>
      </div>

      {!readOnly && (
        <div className="mt-4 text-sm text-neutral-600">
          💡 Tip: High Motivation + High Ability + High Prompt Receptiveness = Ideal Customer
        </div>
      )}
    </div>
  );
}

