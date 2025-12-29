'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { DollarSign } from 'lucide-react';

interface CostItem {
  module: string;
  tokens: number;
  cost: number;
}

interface CostHeatmapProps {
  data?: CostItem[];
}

const DEFAULT_DATA: CostItem[] = [
  { module: 'Foundation', tokens: 12500, cost: 0.25 },
  { module: 'Cohorts', tokens: 45000, cost: 0.9 },
  { module: 'Moves', tokens: 88000, cost: 1.76 },
  { module: 'Muse', tokens: 156000, cost: 3.12 },
  { module: 'Matrix', tokens: 22000, cost: 0.44 },
  { module: 'Blackbox', tokens: 210000, cost: 4.2 },
];

export function CostHeatmap({ data = DEFAULT_DATA }: CostHeatmapProps) {
  const maxCost = Math.max(...data.map((d) => d.cost));

  return (
    <div className="p-6 rounded-2xl bg-card border border-border">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground font-sans">
          Resource Distribution
        </h3>
        <div className="flex items-center gap-1.5 text-emerald-500 font-mono text-[10px]">
          <DollarSign size={10} />
          <span>
            Total: ${data.reduce((acc, d) => acc + d.cost, 0).toFixed(2)}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {data.map((item, i) => {
          const intensity = item.cost / maxCost;

          return (
            <motion.div
              key={item.module}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className="relative group p-3 rounded-xl border border-border/50 bg-muted/20 overflow-hidden"
            >
              {/* Heatmap intensity background */}
              <div
                className="absolute inset-0 bg-accent/20 origin-left transition-transform duration-500"
                style={{ transform: `scaleX(${intensity})` }}
              />

              <div className="relative flex flex-col gap-0.5">
                <span className="text-[10px] font-semibold text-muted-foreground font-sans uppercase tracking-tighter">
                  {item.module}
                </span>
                <div className="flex items-baseline justify-between">
                  <span className="text-sm font-bold font-mono">
                    ${item.cost.toFixed(2)}
                  </span>
                  <span className="text-[9px] text-muted-foreground/60 font-mono">
                    {(item.tokens / 1000).toFixed(1)}k tokens
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-border flex items-center justify-between">
        <span className="text-[10px] text-muted-foreground font-sans italic">
          Based on current Vertex AI pricing
        </span>
        <div className="flex items-center gap-1">
          {[0.2, 0.4, 0.6, 0.8, 1].map((v) => (
            <div
              key={v}
              className="h-1.5 w-1.5 rounded-full bg-accent"
              style={{ opacity: v }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
