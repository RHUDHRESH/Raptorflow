"use client";

import { useState, useEffect, useRef } from "react";
import gsap from "gsap";
import { Shield, Activity, BarChart3, Brain, Rocket } from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — SystemOverview
   System health dashboard with blueprint styling
   ══════════════════════════════════════════════════════════════════════════════ */

interface SystemModule {
  name: string;
  status: "operational" | "degraded" | "down";
  description: string;
  lastCheck: string;
  responseTime?: string;
  uptime?: string;
  code: string;
}

interface SystemMetric {
  label: string;
  value: string;
  change?: string;
  trend?: "up" | "down" | "stable";
  code: string;
}

export function SystemOverview() {
  const [modules] = useState<SystemModule[]>([
    { name: "Frontend Application", status: "operational", description: "Next.js application server", lastCheck: "Just now", responseTime: "45ms", uptime: "99.9%", code: "SYS-01" },
    { name: "API Gateway", status: "operational", description: "Backend API services", lastCheck: "30 seconds ago", responseTime: "120ms", uptime: "99.7%", code: "SYS-02" },
    { name: "Database", status: "operational", description: "PostgreSQL database cluster", lastCheck: "1 minute ago", responseTime: "12ms", uptime: "99.8%", code: "SYS-03" },
    { name: "Authentication", status: "operational", description: "JWT authentication service", lastCheck: "Just now", responseTime: "23ms", uptime: "100%", code: "SYS-04" },
    { name: "Notification Service", status: "operational", description: "Real-time notification system", lastCheck: "2 minutes ago", responseTime: "67ms", uptime: "99.7%", code: "SYS-05" },
    { name: "Analytics Engine", status: "operational", description: "Data processing and analytics", lastCheck: "45 seconds ago", responseTime: "89ms", uptime: "99.6%", code: "SYS-06" },
  ]);

  const [metrics] = useState<SystemMetric[]>([
    { label: "Active Users", value: "1,247", change: "+12%", trend: "up", code: "M-01" },
    { label: "API Requests", value: "45.2K/hr", change: "+8%", trend: "up", code: "M-02" },
    { label: "Response Time", value: "85ms", change: "-5%", trend: "down", code: "M-03" },
    { label: "Error Rate", value: "0.12%", change: "stable", trend: "stable", code: "M-04" },
    { label: "System Load", value: "42%", change: "+2%", trend: "up", code: "M-05" },
    { label: "Storage Used", value: "234GB", change: "+1%", trend: "up", code: "M-06" },
  ]);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
  }, []);

  const getStatusBadge = (status: SystemModule['status']) => {
    if (status === "operational") return <BlueprintBadge variant="success" dot>OPERATIONAL</BlueprintBadge>;
    if (status === "degraded") return <BlueprintBadge variant="warning" dot>DEGRADED</BlueprintBadge>;
    return <BlueprintBadge variant="error" dot>DOWN</BlueprintBadge>;
  };

  const operationalCount = modules.filter(m => m.status === "operational").length;
  const systemHealth = Math.round((operationalCount / modules.length) * 100);

  return (
    <div ref={containerRef} className="space-y-6">
      {/* Header */}
      <BlueprintCard data-animate showCorners variant="elevated" padding="lg" className="border-[var(--success)]/30 bg-gradient-to-r from-[var(--success-light)] via-[var(--paper)] to-[var(--paper)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-[var(--radius-md)] bg-[var(--success)] flex items-center justify-center ink-bleed-sm">
              <Activity size={22} className="text-[var(--paper)]" />
            </div>
            <div>
              <h2 className="font-serif text-xl text-[var(--ink)]">System Operational</h2>
              <p className="text-sm text-[var(--secondary)]">All systems running normally</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-[var(--success)]">{systemHealth}%</div>
            <div className="font-technical text-[var(--muted)]">HEALTH</div>
          </div>
        </div>
      </BlueprintCard>

      {/* Metrics */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <span className="font-technical text-[var(--blueprint)]">FIG. 01</span>
          <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
          <span className="font-technical text-[var(--muted)]">KEY METRICS</span>
        </div>
        <KPIGrid data-animate columns={3}>
          {metrics.map((metric) => (
            <BlueprintKPI
              key={metric.code}
              label={metric.label}
              value={metric.value}
              code={metric.code}
              trend={metric.trend === "up" ? "up" : metric.trend === "down" ? "down" : undefined}
              trendValue={metric.change}
            />
          ))}
        </KPIGrid>
      </div>

      {/* Components */}
      <BlueprintCard data-animate figure="FIG. 02" title="System Components" code="COMP" showCorners padding="lg">
        <div className="space-y-3">
          {modules.map((module) => (
            <div key={module.code} className="flex items-center justify-between p-4 rounded-[var(--radius-sm)] border border-[var(--border-subtle)] bg-[var(--canvas)] hover:bg-[var(--paper)] transition-colors">
              <div className="flex items-center gap-4">
                <span className="font-technical text-[var(--blueprint)]">{module.code}</span>
                <div>
                  <div className="text-sm font-medium text-[var(--ink)]">{module.name}</div>
                  <div className="text-xs text-[var(--muted)]">{module.description}</div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right font-technical">
                  {module.responseTime && <div className="text-sm text-[var(--ink)]">{module.responseTime}</div>}
                  {module.uptime && <div className="text-xs text-[var(--muted)]">{module.uptime} UPTIME</div>}
                </div>
                {getStatusBadge(module.status)}
              </div>
            </div>
          ))}
        </div>
      </BlueprintCard>

      {/* Quick Actions */}
      <BlueprintCard data-animate figure="FIG. 03" title="Quick Actions" code="ACT" showCorners padding="lg">
        <div className="grid grid-cols-4 gap-4">
          {[
            { icon: Brain, label: "AI Services", desc: "Manage AI models", code: "A-01" },
            { icon: Shield, label: "Security", desc: "View security logs", code: "A-02" },
            { icon: BarChart3, label: "Analytics", desc: "System metrics", code: "A-03" },
            { icon: Rocket, label: "Deploy", desc: "Deploy updates", code: "A-04" },
          ].map((action) => (
            <button key={action.code} className="p-4 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--paper)] hover:border-[var(--blueprint)] hover:bg-[var(--blueprint-light)] transition-all text-center group">
              <div className="w-10 h-10 mx-auto mb-3 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center group-hover:bg-[var(--blueprint)] group-hover:border-[var(--blueprint)] transition-all">
                <action.icon size={18} strokeWidth={1.5} className="text-[var(--muted)] group-hover:text-[var(--paper)] transition-colors" />
              </div>
              <div className="font-medium text-sm text-[var(--ink)]">{action.label}</div>
              <div className="font-technical text-[var(--muted)]">{action.desc}</div>
            </button>
          ))}
        </div>
      </BlueprintCard>

      {/* Document Footer */}
      <div className="flex justify-center pt-4">
        <span className="font-technical text-[var(--muted)]">DOCUMENT: SYSTEM-OVERVIEW | LAST UPDATED: {new Date().toISOString().split('T')[0]}</span>
      </div>
    </div>
  );
}
