"use client";

import React from "react";
import { useOfficeStore } from "@/state/office-store";
import { AGENTS } from "@/lib/agents";
import { OFFICE_ZONES, PLACEHOLDER_COLORS, type AgentKey } from "@/lib/office-constants";

/**
 * Office Mini-Strip (Passive View)
 *
 * The PixiJS thumbnail was crashing on route transitions in Next dev and
 * taking down the whole shell. Keep the affordance, but render it as static
 * DOM so it can never break protected pages.
 */
export function OfficeMiniStrip() {
  const { agentStatuses, eventLog } = useOfficeStore();
  const hasUnprocessedEvents = eventLog.some((e) => !e.processed);

  return (
    <div className="h-24 w-full border-t border-[#E5DED4] bg-[#FBF8F2] relative overflow-hidden group">
      <div className="absolute top-1.5 left-2 z-10 flex items-center gap-1.5 opacity-50 group-hover:opacity-100 transition-opacity">
        <span className="text-[7px] font-mono font-bold text-[#6B655E] uppercase tracking-widest">
          Passive_HQ_View
        </span>
        <span className="text-[7px] font-mono text-[#9A948C] uppercase tracking-widest">
          {AGENTS.length} agents
        </span>
      </div>

      <div className="absolute inset-0 grid grid-cols-4 gap-1 p-3 opacity-70">
        {Object.values(OFFICE_ZONES)
          .slice(0, 8)
          .map((zone) => (
            <div
              key={zone.id}
              className="flex items-center justify-center rounded-[8px] border border-[#E5DED4] bg-white/80 text-[7px] font-mono uppercase tracking-widest text-[#6B655E]"
            >
              {zone.label.slice(0, 8)}
            </div>
          ))}
      </div>

      <div className="absolute inset-x-2 bottom-2 flex items-center gap-1.5">
        {Object.entries(agentStatuses)
          .slice(0, 6)
          .map(([key, status]) => (
            <span
              key={key}
              className="h-2.5 w-2.5 rounded-full border border-white shadow-sm"
              style={{
                backgroundColor: PLACEHOLDER_COLORS[key as AgentKey] ?? "#9A948C",
                opacity: status.status === "speaking" ? 1 : 0.65,
              }}
              title={`${key}: ${status.status}`}
            />
          ))}
      </div>

      {hasUnprocessedEvents && (
        <div className="absolute top-1.5 right-1.5 w-1 h-1 bg-[#D97757] rounded-full animate-pulse shadow-[0_0_8px_rgba(217,119,87,0.8)]" />
      )}

      <div className="absolute inset-0 pointer-events-none border border-inset border-white/5" />
    </div>
  );
}
