import { useEffect, useState } from 'react';

export interface SwarmHealth {
  status: 'healthy' | 'warning' | 'unhealthy';
  signals: string[];
  tool_failure_rates: {
    overall_failure_rate: number;
    total_executions: number;
    tools: Record<
      string,
      {
        success: number;
        failure: number;
        total: number;
        failure_rate: number;
        last_seen?: string;
      }
    >;
    updated_at?: string;
  };
  budget_overrun: {
    daily_burn: number;
    budget: number;
    usage_percentage: number;
    status: string;
    over_budget: boolean;
    timestamp?: string;
  };
  queue_backlog: {
    pending: number;
    status: string;
    updated_at?: string;
  };
  timestamp: string;
}

export function useSwarmHealth(workspaceId?: string) {
  const [data, setData] = useState<SwarmHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    async function fetchHealth() {
      try {
        const url = new URL(`${API_URL}/v1/matrix/swarm-health`);
        if (workspaceId) {
          url.searchParams.set('workspace_id', workspaceId);
        }

        const res = await fetch(url.toString());
        if (!res.ok) throw new Error('Failed to fetch swarm health');
        const json = await res.json();
        setData(json);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    }

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [workspaceId]);

  return { data, loading, error };
}
