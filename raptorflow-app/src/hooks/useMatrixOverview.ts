import { useState, useEffect } from "react";

export interface MatrixOverview {
  system_state: {
    kill_switch_engaged: boolean;
    system_status: string;
    active_agents: Record<string, {
      status: string;
      last_heartbeat: string;
      current_task?: string;
      metadata?: Record<string, unknown>;
    }>;
  };
  health_report: {
    status: "healthy" | "warning" | "unhealthy";
    services: Record<string, boolean>;
  };
  cost_report: {
    daily_burn: number;
    budget: number;
    status: string;
  };
  p95_latency_ms?: number;
  recent_events?: Array<{
    event_id: string;
    timestamp: string;
    event_type: string;
    source: string;
    metadata: Record<string, unknown>;
  }>;
}

export function useMatrixOverview(workspaceId: string) {
  const [data, setData] = useState<MatrixOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    async function fetchOverview() {
      try {
        const res = await fetch(`${API_URL}/v1/matrix/overview?workspace_id=${workspaceId}`);
        if (!res.ok) throw new Error("Failed to fetch matrix overview");
        const json = await res.json();
        setData(json);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    }

    fetchOverview();
    const interval = setInterval(fetchOverview, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [workspaceId]);

  return { data, loading, error };
}
