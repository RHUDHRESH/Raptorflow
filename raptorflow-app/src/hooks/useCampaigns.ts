'use client';

import { useState, useEffect, useCallback } from 'react';
import { Campaign, Move } from '@/lib/campaigns-types';
import { getCampaigns, getMoves } from '@/lib/campaigns';

/**
 * SOTA Hook for Campaign & Move State
 * Prevents flickering by using proper loading states and stale-while-revalidate pattern.
 */
export function useCampaigns(pollInterval: number = 10000) {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [moves, setMoves] = useState<Move[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [cData, mData] = await Promise.all([getCampaigns(), getMoves()]);
      setCampaigns(cData);
      setMoves(mData);
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error('Failed to refresh data')
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();

    if (pollInterval > 0) {
      const timer = setInterval(refresh, pollInterval);
      return () => clearInterval(timer);
    }
  }, [refresh, pollInterval]);

  return { campaigns, moves, isLoading, error, refresh };
}
