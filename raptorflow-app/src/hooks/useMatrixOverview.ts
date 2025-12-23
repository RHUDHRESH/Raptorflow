import { useState, useEffect } from "react";

export interface MatrixOverview {
  system_state: {
    kill_switch_engaged: boolean;
    system_status: string;
    active_agents: Record<string, {
      status: string;
      last_heartbeat: string;
      current_task?: string;
      metadata?: Record<string, any>;
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
  recent_events?: Array<{
    event_id: string;
    timestamp: string;
    event_type: string;
    source: string;
    metadata: Record<string, any>;
  }>;
}

export function useMatrixOverview(workspaceId: string) {
  const [data, setData] = useState<MatrixOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchOverview() {
      try {
        // In a real build, this would be an absolute URL or use a base config
        const res = await fetch(`/api/v1/matrix/overview?workspace_id=${workspaceId}`);
        if (!res.ok) throw new Error("Failed to fetch matrix overview");
        const json = await res.json();
        setData(json);
      } catch (err: any) {
        setError(err.message);
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
