"use client";

import { useRef, useEffect } from "react";
import gsap from "gsap";
import {
  CheckCircle,
  Activity,
  Server,
  Database,
  Cpu,
  Globe
} from "lucide-react";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";

const INFRASTRUCTURE = [
  { name: "Frontend App", icon: Globe, status: "operational", uptime: "99.9%" },
  { name: "Backend API", icon: Server, status: "operational", uptime: "99.9%" },
  { name: "Database Cluster", icon: Database, status: "operational", uptime: "100%" },
  { name: "AI Inference Engine", icon: Cpu, status: "operational", uptime: "98.5%" },
];

export default function StatusPage() {
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pageRef.current) return;
    const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
    tl.fromTo("[data-anim]", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.1 });
  }, []);

  return (
    <div ref={pageRef} className="max-w-3xl mx-auto pb-12">
      <div className="mb-8" data-anim>
        <div className="align-start gap-3 mb-2">
          <span className="font-technical text-[var(--blueprint)]">SYS-01</span>
          <div className="h-px w-8 bg-[var(--blueprint-line)]" />
          <span className="font-technical text-[var(--muted)]">STATUS</span>
        </div>
        <h1 className="font-serif text-3xl text-[var(--ink)]">System Status</h1>
      </div>

      <BlueprintCard padding="lg" showCorners className="mb-8 border-[var(--success)]/20 bg-[var(--success)]/5" data-anim>
        <div className="align-center gap-4">
          <div className="p-3 bg-[var(--success)] rounded-full text-white shadow-lg shadow-[var(--success)]/20">
            <span className="text-2xl">✅</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-[var(--ink)]">All Systems Operational</h2>
            <p className="text-sm text-[var(--success-dark)]">Last updated: Just now</p>
          </div>
        </div>
      </BlueprintCard>

      <div className="space-y-4" data-anim>
        {INFRASTRUCTURE.map((item, i) => {
          const Icon = item.icon;
          return (
            <BlueprintCard key={i} padding="md" showCorners>
              <div className="align-between">
                <div className="align-center gap-4">
                  <div className="p-2 bg-[var(--canvas)] rounded-[var(--radius-sm)] text-[var(--muted)]">
                    <Icon size={20} strokeWidth={1.5} />
                  </div>
                  <span className="font-semibold text-[var(--ink)]">{item.name}</span>
                </div>
                <div className="align-center gap-6">
                  <div className="text-right">
                    <span className="block text-xs font-technical text-[var(--muted)]">UPTIME</span>
                    <span className="text-sm font-mono text-[var(--ink)]">{item.uptime}</span>
                  </div>
                  <BlueprintBadge variant="success" dot>OPERATIONAL</BlueprintBadge>
                </div>
              </div>
            </BlueprintCard>
          );
        })}
      </div>

      <div className="mt-8" data-anim>
        <h3 className="font-technical text-[var(--muted)] mb-4">PAST INCIDENTS</h3>
        <div className="text-center py-12 border border-dashed border-[var(--border)] rounded-[var(--radius-md)]">
          <p className="text-sm text-[var(--muted)]">No incidents reported in the last 90 days.</p>
        </div>
      </div>
    </div>
  );
}
