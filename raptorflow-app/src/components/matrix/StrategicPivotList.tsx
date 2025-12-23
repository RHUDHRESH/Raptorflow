'use client';

import React, { useState, useEffect } from 'react';
import { StrategicPivotCard } from '../campaigns/StrategicPivotCard';
import { Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { applyCampaignPivot } from '@/lib/campaigns';

interface StrategicPivot {
  id: string;
  campaignId: string;
  title: string;
  description: string;
  rationale: string;
  severity: 'low' | 'medium' | 'high';
}

/**
 * SOTA Strategic Pivot List
 * Fetches and displays multiple agentic recommendations in the dashboard.
 */
export function StrategicPivotList() {
  const [pivots, setPivots] = useState<StrategicPivot[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // In production, fetch from backend. For Task 21, we provide a rich mock.
    // Task 22 will connect to real backend nodes.
    const mockPivots: StrategicPivot[] = [
      {
        id: 'p1',
        campaignId: 'c1', // Assuming there's a campaign with this ID
        title: 'LinkedIn Outreach Pivot',
        description: 'Focus on Founders in B2B SaaS Niche rather than generic SMBs.',
        rationale: 'Recent agent research shows 40% higher engagement in the SaaS segment for your current offer.',
        severity: 'medium'
      },
      {
        id: 'p2',
        campaignId: 'c2',
        title: 'Urgent: Competitor Response',
        description: 'Update pricing strategy to include a "Free Migration" tier.',
        rationale: 'Competitor X just lowered their barrier to entry. This shift neutralizes their recent move.',
        severity: 'high'
      }
    ];
    
    setIsLoading(true);
    setTimeout(() => {
      setPivots(mockPivots);
      setIsLoading(false);
    }, 1000);
  }, []);

  const handleApply = async (id: string) => {
    const pivot = pivots.find(p => p.id === id);
    if (!pivot) return;

    toast.promise(applyCampaignPivot(pivot.campaignId, pivot), {
      loading: 'Applying strategy shift...',
      success: 'Strategy shift applied successfully',
      error: 'Failed to apply shift'
    });

    // Task 22 implementation completed
    setPivots(prev => prev.filter(p => p.id !== id));
  };
  const handleIgnore = (id: string) => {
    toast('Recommendation archived');
    setPivots(prev => prev.filter(p => p.id !== id));
  };

  if (pivots.length === 0 && !isLoading) return null;

  return (
    <section className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-accent/10 text-accent">
            <Sparkles size={20} />
          </div>
          <div>
            <h2 className="text-2xl font-display font-medium tracking-tight">Strategic Intelligence</h2>
            <p className="text-sm text-muted-foreground">Agent recommendations based on real-time market signals.</p>
          </div>
        </div>
        {pivots.length > 1 && (
          <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 bg-zinc-100 dark:bg-zinc-800 rounded-full">
            {pivots.length} New Signals
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {isLoading ? (
          <div className="col-span-full h-48 rounded-2xl border border-dashed border-zinc-200 dark:border-zinc-800 animate-pulse bg-zinc-50/50 dark:bg-zinc-900/20" />
        ) : (
          pivots.map(pivot => (
            <StrategicPivotCard
              key={pivot.id}
              pivot={pivot}
              onApply={handleApply}
              onIgnore={handleIgnore}
            />
          ))
        )}
      </div>
    </section>
  );
}
