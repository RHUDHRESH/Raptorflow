"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, AlertCircle, ShieldAlert } from "lucide-react";

export function SystemStatusHeader() {
  // SOTA: In a real build, this would fetch from /v1/matrix/overview
  const status = "healthy"; // healthy, warning, critical

  const statusConfig = {
    healthy: {
      label: "SYSTEM ONLINE",
      sub: "All services operating within surgical parameters.",
      icon: CheckCircle2,
      color: "text-green-600 bg-green-50 border-green-200",
    },
    warning: {
      label: "DEGRADED PERFORMANCE",
      sub: "Latency spikes detected in secondary agents.",
      icon: AlertCircle,
      color: "text-amber-600 bg-amber-50 border-amber-200",
    },
    critical: {
      label: "SYSTEM HALTED",
      sub: "Global kill-switch engaged. Manual intervention required.",
      icon: ShieldAlert,
      color: "text-red-600 bg-red-50 border-red-200",
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Card className="rounded-2xl border-border overflow-hidden">
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
