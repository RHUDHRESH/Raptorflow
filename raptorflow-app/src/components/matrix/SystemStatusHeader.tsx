"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, AlertCircle, ShieldAlert, Loader2 } from "lucide-react";
import { useMatrixOverview } from "@/hooks/useMatrixOverview";

export function SystemStatusHeader() {
  const { data, loading, error } = useMatrixOverview("verify_ws");

  if (loading) {
    return (
      <Card className="rounded-2xl border-border animate-pulse">
        <CardContent className="p-12 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground mr-2" />
          <span className="text-muted-foreground font-sans uppercase tracking-widest text-xs font-bold">
            Pulse Initializing...
          </span>
        </CardContent>
      </Card>
    );
  }

  // Map API status to UI config
  const status = data?.health_report?.status || "healthy";
  
  const statusConfig = {
    healthy: {
      label: "SYSTEM ONLINE",
      sub: "All services operating within surgical parameters.",
      icon: CheckCircle2,
      color: "text-green-600 bg-green-50 border-green-200",
    },
    warning: {
      label: "DEGRADED PERFORMANCE",
      sub: "Latency spikes or partial service failures detected.",
      icon: AlertCircle,
      color: "text-amber-600 bg-amber-50 border-amber-200",
    },
    unhealthy: {
      label: "SYSTEM CRITICAL",
      sub: "Critical service outage. Automated guardrails active.",
      icon: ShieldAlert,
      color: "text-red-600 bg-red-50 border-red-200",
    },
  };

  // Fallback for unexpected status
  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.healthy;
  const Icon = config.icon;

  if (error) {
    return (
      <Card className="rounded-2xl border-red-200 bg-red-50">
        <CardContent className="p-6 flex items-center justify-between text-red-600">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-5 w-5" />
            <span className="font-bold text-sm">TELEMETRY OFFLINE: {error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="rounded-2xl border-border overflow-hidden shadow-sm">
      <CardContent className="p-0">
        <div className={`flex items-center justify-between p-6 ${config.color.split(' ')[1]}`}>
          <div className="flex items-center space-x-4">
            <div className={`p-3 rounded-full bg-white shadow-sm ${config.color.split(' ')[0]}`}>
              <Icon className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm font-bold tracking-widest uppercase font-sans">
                  {config.label}
                </h2>
                <Badge variant="outline" className={`font-mono text-[10px] bg-white ${config.color.split(' ')[0]}`}>
                  v1.0.0-industrial
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mt-1 font-sans">
                {config.sub}
              </p>
            </div>
          </div>
          <div className="hidden md:block text-right">
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">
              Last Pulse
            </div>
            <div className="text-sm font-mono font-medium">
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
