'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { EXPERTS } from './CouncilChamber';
import { cn } from '@/lib/utils';

interface ConfidenceHeatmapProps {
  scores?: Record<string, number>; // Map of expert id to score (0-1)
}

export function ConfidenceHeatmap({ scores }: ConfidenceHeatmapProps) {
  // Mock scores if none provided
  const displayScores =
    scores ||
    EXPERTS.reduce(
      (acc, expert) => {
        acc[expert.id] = 0.7 + Math.random() * 0.3; // High alignment mock
        return acc;
      },
      {} as Record<string, number>
    );

  return (
    <div className="p-6 rounded-2xl bg-surface border border-borders/50 shadow-sm">
      <header className="flex justify-between items-center mb-6">
        <h4 className="text-[10px] font-bold uppercase tracking-[0.2em] text-secondary-text">
          Council Alignment Heatmap
        </h4>
        <div className="flex gap-4 items-center">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-accent opacity-20" />
            <span className="text-[9px] text-secondary-text">Low</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-accent" />
            <span className="text-[9px] text-secondary-text">High</span>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-6 sm:grid-cols-12 gap-2">
        {EXPERTS.map((expert) => {
          const score = displayScores[expert.id] || 0.5;
          return (
            <div
              key={expert.id}
              className="group relative flex flex-col items-center"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.1 }}
                className={cn(
                  'w-full aspect-square rounded-lg border border-borders/20 transition-all duration-500',
                  'flex items-center justify-center overflow-hidden'
                )}
                style={{
                  backgroundColor: `rgba(215, 201, 174, ${score * 0.8})`,
                  boxShadow:
                    score > 0.9 ? '0 0 10px rgba(215, 201, 174, 0.4)' : 'none',
                }}
              >
                <expert.icon
                  className={cn(
                    'size-3.5',
                    score > 0.6 ? 'text-ink' : 'text-secondary-text opacity-40'
                  )}
                />
              </motion.div>

              {/* Tooltip */}
              <div className="absolute bottom-full mb-2 hidden group-hover:block z-50 pointer-events-none">
                <div className="bg-ink text-white text-[9px] px-2 py-1 rounded whitespace-nowrap shadow-xl">
                  <p className="font-bold">{expert.name}</p>
                  <p className="opacity-70">
                    Alignment: {(score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-borders/20 flex justify-between items-center text-[10px] text-secondary-text font-mono">
        <span>Total Experts: 12</span>
        <span className="text-accent font-bold">Weighted Avg: 91.4%</span>
      </div>
    </div>
  );
}
