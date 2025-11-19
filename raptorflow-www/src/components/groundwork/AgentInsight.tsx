'use client';

import React from 'react';
import { Sparkles, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { AgentQuestion } from '@/lib/groundwork/types';

interface AgentInsightProps {
  question: AgentQuestion;
  onDismiss?: () => void;
  onAnswer?: (answer: string) => void;
  className?: string;
}

export function AgentInsight({ question, onDismiss, onAnswer, className }: AgentInsightProps) {
  const [answer, setAnswer] = React.useState('');

  const handleSubmit = () => {
    if (answer.trim() && onAnswer) {
      onAnswer(answer);
      setAnswer('');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={cn(
        'p-4 rounded-lg border border-rf-cloud bg-rf-cloud/30 mb-6',
        className
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-rf-primary/10 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-rf-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <h4 className="text-sm font-semibold text-rf-ink">Strategist Insight</h4>
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="p-1 text-rf-subtle hover:text-rf-ink transition-colors flex-shrink-0"
                aria-label="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <p className="text-sm text-rf-ink mb-3 leading-relaxed">{question.question}</p>
          {question.context && (
            <p className="text-xs text-rf-subtle mb-4 italic">{question.context}</p>
          )}

          <div className="space-y-2">
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Your answer..."
              rows={2}
              className="w-full px-3 py-2 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm resize-none"
            />
            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!answer.trim()}
                className={cn(
                  'px-4 py-1.5 rounded-lg text-sm font-medium transition-colors',
                  answer.trim()
                    ? 'bg-rf-primary text-white hover:bg-rf-primary/90'
                    : 'bg-rf-cloud text-rf-subtle cursor-not-allowed'
                )}
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

