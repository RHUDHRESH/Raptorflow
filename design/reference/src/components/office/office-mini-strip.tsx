"use client";

import React, { useEffect, useRef } from "react";
import * as PIXI from "pixi.js";
import { useOfficeStore } from "@/state/office-store";
import { CANVAS_COLORS, AGENT_MAP } from "@/lib/agents"; // Assuming we keep AGENT_MAP for metadata
import { 
  PLACEHOLDER_COLORS, 
  OFFICE_ZONES,
  type AgentKey 
} from "@/lib/office-constants";

/**
 * Office Mini-Strip (Passive View)
 * 
 * Logic: A read-only, h-24 thumbnail of the office floor.
 * Uses a secondary, low-overhead PixiJS renderer.
 */
export function OfficeMiniStrip() {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const { agentStatuses, eventLog } = useOfficeStore();

  const hasUnprocessedEvents = eventLog.some(e => !e.processed);

  useEffect(() => {
    if (!containerRef.current) return;

    const app = new PIXI.Application();
    appRef.current = app;

    async function init() {
      await app.init({
        background: '#0a0a0a', // Darker for sidebar
        width: 280,
        height: 96,
        resolution: 1,
        antialias: false, // Save perf for thumbnail
      });

      containerRef.current?.appendChild(app.canvas);

      // Simple Floor
      const floor = new PIXI.Graphics();
      floor.rect(0, 0, 280, 96);
      floor.fill('#111111');
      app.stage.addChild(floor);

      // Render miniature zones
      Object.values(OFFICE_ZONES).forEach(zone => {
        const z = new PIXI.Graphics();
        // Scale down world coords (1000x1000) to 280x96
        const sx = zone.defaultPosition.x * 0.28;
        const sy = zone.defaultPosition.y * 0.096;
        z.rect(sx, sy, 50, 20);
        z.fill('#1a1a1a');
        z.stroke({ color: '#222222', width: 1 });
        app.stage.addChild(z);
      });
    }

    init();

    return () => {
      app.destroy(true, { children: true });
    };
  }, []);

  // Update Agent Dots (Miniature)
  useEffect(() => {
    if (!appRef.current) return;
    const stage = appRef.current.stage;

    // Clear existing agent dots (except floor/zones)
    const childrenToRemove = stage.children.filter(c => c.label === 'agent-dot');
    childrenToRemove.forEach(c => stage.removeChild(c));

    Object.entries(agentStatuses).forEach(([key, status]) => {
      const zone = OFFICE_ZONES[status.currentZone] || OFFICE_ZONES.reception;
      const dot = new PIXI.Graphics();
      dot.label = 'agent-dot';
      
      const x = (zone.defaultPosition.x + 25) * 0.28;
      const y = (zone.defaultPosition.y + 10) * 0.096;
      
      dot.circle(x, y, 2.5);
      dot.fill(PLACEHOLDER_COLORS[key as AgentKey]);
      
      if (status.status === 'speaking') {
        dot.stroke({ color: '#ffffff', width: 1 });
      }
      
      stage.addChild(dot);
    });
  }, [agentStatuses]);

  return (
    <div className="h-24 w-full border-t border-zinc-800 bg-[#0f0f0f] relative overflow-hidden group">
      {/* Title / Status */}
      <div className="absolute top-1.5 left-2 z-10 flex items-center gap-1.5 opacity-50 group-hover:opacity-100 transition-opacity">
        <span className="text-[7px] font-mono font-bold text-zinc-500 uppercase tracking-widest">
          Passive_HQ_View
        </span>
      </div>

      {/* Pixi Canvas Container */}
      <div ref={containerRef} className="w-full h-full grayscale opacity-40 group-hover:grayscale-0 group-hover:opacity-80 transition-all duration-700" />

      {/* Amber Event Pulse */}
      {hasUnprocessedEvents && (
        <div className="absolute top-1.5 right-1.5 w-1 h-1 bg-amber-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.8)]" />
      )}

      {/* Static Overlay Accents */}
      <div className="absolute inset-0 pointer-events-none border border-inset border-white/5" />
    </div>
  );
}
