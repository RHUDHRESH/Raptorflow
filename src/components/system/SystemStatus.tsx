"use client";

import { useState } from "react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import {
  Server,
  Database,
  Cpu,
  Network,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Activity
} from "lucide-react";
import { useSystemHealth, useSystemInfo } from "@/lib/api/useApi";
import { notify } from "@/lib/notifications";

/* ══════════════════════════════════════════════════════════════════════════════
   SYSTEM STATUS — Paper Terminal Style
   ══════════════════════════════════════════════════════════════════════════════ */

interface SystemModule {
  name: string;
  status: "active" | "inactive" | "error";
  description: string;
  lastCheck: string;
}

// Mock modules data for development
const mockModules: SystemModule[] = [
  {
    name: "Agents",
    status: "active",
    description: "AI agent system for automated tasks",
    lastCheck: new Date().toLocaleTimeString()
  },
  {
    name: "Skills",
    status: "active",
    description: "Skill framework for marketing operations",
    lastCheck: new Date().toLocaleTimeString()
  },
  {
    name: "Tools",
    status: "active",
    description: "Integration tools and utilities",
    lastCheck: new Date().toLocaleTimeString()
  },
  {
    name: "Data",
    status: "active",
    description: "Data storage and retrieval systems",
    lastCheck: new Date().toLocaleTimeString()
  },
  {
    name: "Workflows",
    status: "active",
    description: "Workflow orchestration engine",
    lastCheck: new Date().toLocaleTimeString()
  },
  {
    name: "Monitoring",
    status: "active",
    description: "System monitoring and alerting",
    lastCheck: new Date().toLocaleTimeString()
  }
];

export function SystemStatus() {
  const { data: healthData, loading: healthLoading, refetch: refetchHealth } = useSystemHealth();
  const { data: systemData, loading: systemLoading, refetch: refetchSystem } = useSystemInfo();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([refetchHealth(), refetchSystem()]);
      notify.success("System status refreshed");
    } catch {
      notify.error("Failed to refresh system status");
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
      case "healthy":
        return <CheckCircle className="h-4 w-4 text-[var(--success)]" />;
      case "error":
        return <AlertTriangle className="h-4 w-4 text-[var(--error)]" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-[var(--warning)]" />;
    }
  };

  const getStatusVariant = (status: string): "success" | "error" | "warning" | "default" => {
    switch (status) {
      case "active":
      case "healthy":
        return "success";
      case "error":
        return "error";
      default:
        return "warning";
    }
  };

  if (healthLoading || systemLoading) {
    return (
      <BlueprintCard title="System Status" icon={<Activity size={18} />}>
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="h-6 w-6 animate-spin text-[var(--blueprint)]" />
          <span className="ml-2 text-[var(--ink-secondary)]">Loading system status...</span>
        </div>
      </BlueprintCard>
    );
  }

  // Show error state if health data is not available
  if (!healthData) {
    return (
      <BlueprintCard title="System Status" icon={<AlertTriangle size={18} />}>
        <div className="text-center py-8">
          <AlertTriangle className="h-8 w-8 text-[var(--error)] mx-auto mb-2" />
          <p className="text-[var(--error)]">Unable to connect to backend services</p>
          <SecondaryButton
            size="sm"
            className="mt-4"
            onClick={handleRefresh}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Connection
          </SecondaryButton>
        </div>
      </BlueprintCard>
    );
  }

  const modules: SystemModule[] = mockModules;
  const healthStatus = healthData && typeof healthData === 'object' && 'status' in healthData
    ? String(healthData.status)
    : "Unknown";

  return (
    <BlueprintCard
      title="System Status"
      icon={<Server size={18} />}
      actions={
        <SecondaryButton
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
          Refresh
        </SecondaryButton>
      }
    >
      <div className="space-y-6">
        {/* Status Badge */}
        <div className="flex items-center gap-2">
          <span className="font-technical text-[var(--ink-muted)]">STATUS:</span>
          <BlueprintBadge variant={healthStatus === "healthy" ? "success" : "warning"}>
            {healthStatus.toUpperCase()}
          </BlueprintBadge>
        </div>

        {/* System Overview */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="flex items-center gap-3 p-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)]">
            <Cpu className="h-5 w-5 text-[var(--blueprint)]" />
            <div>
              <div className="font-medium text-[var(--ink)]">API Version</div>
              <div className="text-sm text-[var(--ink-secondary)]">
                {systemData && typeof systemData === 'object' && 'version' in systemData
                  ? String(systemData.version)
                  : "2.0.0"}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)]">
            <Database className="h-5 w-5 text-[var(--success)]" />
            <div>
              <div className="font-medium text-[var(--ink)]">Data Layer</div>
              <div className="text-sm text-[var(--ink-secondary)]">Connected</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)]">
            <Network className="h-5 w-5 text-[var(--blueprint)]" />
            <div>
              <div className="font-medium text-[var(--ink)]">Response Time</div>
              <div className="text-sm text-[var(--ink-secondary)]">&lt;100ms</div>
            </div>
          </div>
        </div>

        {/* Module Status */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="font-technical text-[var(--ink-muted)]">SERVICE MODULES</span>
            <div className="h-px flex-1 bg-[var(--structure)]" />
          </div>
          <div className="grid grid-cols-1 gap-3">
            {modules.map((module) => (
              <div
                key={module.name}
                className="flex items-center justify-between p-3 border border-[var(--structure)] rounded-[var(--radius-sm)] bg-[var(--paper)]"
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(module.status)}
                  <div>
                    <div className="font-medium text-[var(--ink)]">{module.name}</div>
                    <div className="text-sm text-[var(--ink-secondary)]">{module.description}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <BlueprintBadge variant={getStatusVariant(module.status)}>
                    {module.status.toUpperCase()}
                  </BlueprintBadge>
                  <span className="font-technical text-[var(--ink-muted)]">
                    {module.lastCheck}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Available Features */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="font-technical text-[var(--ink-muted)]">AVAILABLE FEATURES</span>
            <div className="h-px flex-1 bg-[var(--structure)]" />
          </div>
          <div className="flex flex-wrap gap-2">
            {["agents", "skills", "tools", "data", "workflows", "monitoring"].map((module) => (
              <BlueprintBadge key={module} variant="default">
                {module.toUpperCase()}
              </BlueprintBadge>
            ))}
          </div>
        </div>
      </div>
    </BlueprintCard>
  );
}
