"use client";

import type * as React from "react";
import { useEffect, useRef, useCallback, useState } from "react";
import { useOfficeStore } from "@/state/office-store";
import { officeFloorPlan, officeRoster } from "@/state/office-types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface PixiRef {
  destroy: () => void;
}

const ZONE_POSITIONS: Record<string, { x: number; y: number; w: number; h: number }> = {
  lobby: { x: 20, y: 20, w: 120, h: 80 },
  "strategist-office": { x: 20, y: 120, w: 140, h: 100 },
  "conference-room": { x: 200, y: 120, w: 180, h: 160 },
  "research-station": { x: 20, y: 240, w: 160, h: 100 },
  "creative-pod": { x: 200, y: 20, w: 140, h: 80 },
  "digital-pod": { x: 360, y: 20, w: 140, h: 80 },
  "debug-nook": { x: 420, y: 300, w: 80, h: 60 },
  "intern-bay": { x: 420, y: 120, w: 120, h: 100 },
};

const ZONE_COLORS: Record<string, number> = {
  entry: 0xfef3c7,
  workspace: 0xdbeafe,
  meeting: 0xd1fae5,
  research: 0xede9ff,
  debug: 0xf3f4f6,
};

const AGENT_COLORS: Record<string, number> = {
  strategist: 0x0f766e,
  ogilvy: 0x7c3aed,
  patel: 0x0369a1,
  sharp: 0x15803d,
  cialdini: 0xb45309,
  "qa-director": 0xbe123c,
};

export function OfficeCanvas(): React.ReactElement {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pixiRef = useRef<PixiRef | null>(null);

  const mode = useOfficeStore((s) => s.mode);
  const surface = useOfficeStore((s) => s.surface);
  const zoomLevel = useOfficeStore((s) => s.zoomLevel);
  const focusedZoneId = useOfficeStore((s) => s.focusedZoneId);
  const eventLog = useOfficeStore((s) => s.eventLog);
  const floorPlan = useOfficeStore((s) => s.floorPlan);
  const roster = useOfficeStore((s) => s.roster);

  const [pan, setPan] = useState({ x: 0, y: 0 });
  const isDragging = useRef(false);
  const lastMouse = useRef({ x: 0, y: 0 });

  const renderFrame = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const W = canvas.clientWidth;
    const H = canvas.clientHeight;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.translate(pan.x, pan.y);
    ctx.scale(zoomLevel, zoomLevel);

    // Background
    ctx.fillStyle = "#fefce8";
    ctx.strokeStyle = "#e7e5e4";
    ctx.lineWidth = 2 / zoomLevel;
    roundRect(ctx, 0, 0, 540, 360, 16);
    ctx.fill();
    ctx.stroke();

    // Zones
    floorPlan.forEach((zone) => {
      const pos = ZONE_POSITIONS[zone.id];
      if (!pos) return;

      const zoneColor = ZONE_COLORS[zone.kind] ?? 0xf5f5f4;
      const isFocused = focusedZoneId === zone.id;

      ctx.fillStyle = `#${zoneColor.toString(16).padStart(6, "0")}`;
      ctx.strokeStyle = isFocused ? "#0f766e" : "#d6d3d1";
      ctx.lineWidth = isFocused ? 2 / zoomLevel : 1 / zoomLevel;
      roundRect(ctx, pos.x, pos.y, pos.w, pos.h, 8);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#44403c";
      ctx.font = `600 ${10 / zoomLevel}px Inter, sans-serif`;
      ctx.fillText(zone.label, pos.x + 8, pos.y + 18);

      ctx.fillStyle = "#9ca3af";
      ctx.font = `${8 / zoomLevel}px Inter, sans-serif`;
      ctx.fillText(zone.capacity, pos.x + 8, pos.y + 32);
    });

    // Agents
    roster.forEach((agent) => {
      const pos = ZONE_POSITIONS[agent.zoneId];
      if (!pos) return;
      const color = AGENT_COLORS[agent.agentKey] ?? 0x6b7280;
      const agentIndex = roster.findIndex((a) => a.agentKey === agent.agentKey);
      const offsetX = (agentIndex % 3) * 24;
      const cx = pos.x + pos.w / 2 + offsetX;
      const cy = pos.y + pos.h / 2;

      ctx.beginPath();
      ctx.arc(cx, cy, 14 / zoomLevel, 0, Math.PI * 2);
      ctx.fillStyle = `#${color.toString(16).padStart(6, "0")}`;
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 2 / zoomLevel;
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.font = `700 ${9 / zoomLevel}px Inter, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(agent.displayName.slice(0, 2).toUpperCase(), cx, cy);
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";

      if (agent.status === "speaking") {
        const bw = 60 / zoomLevel;
        const bh = 28 / zoomLevel;
        const bx = cx - bw / 2;
        const by = cy - 36 / zoomLevel;
        roundRect(ctx, bx, by, bw, bh, 6);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.strokeStyle = "#e5e7eb";
        ctx.lineWidth = 1 / zoomLevel;
        ctx.stroke();
        ctx.fillStyle = "#374151";
        ctx.font = `${8 / zoomLevel}px Inter, sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        const words = agent.posture.split(" ");
        const line1 = words.slice(0, Math.ceil(words.length / 2)).join(" ");
        ctx.fillText(line1, cx, by + bh / 2 - 4 / zoomLevel);
        ctx.textAlign = "left";
        ctx.textBaseline = "alphabetic";
      }
    });

    ctx.restore();
  }, [floorPlan, roster, focusedZoneId, pan, zoomLevel]);

  useEffect(() => {
    let rafId: number;
    const loop = () => {
      renderFrame();
      rafId = requestAnimationFrame(loop);
    };
    rafId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafId);
  }, [renderFrame]);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    isDragging.current = true;
    lastMouse.current = { x: e.clientX, y: e.clientY };
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging.current) return;
    const dx = e.clientX - lastMouse.current.x;
    const dy = e.clientY - lastMouse.current.y;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    setPan((prev) => ({ x: prev.x + dx, y: prev.y + dy }));
  }, []);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
  }, []);

  const handleWheel = useCallback(
    (e: React.WheelEvent<HTMLCanvasElement>) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      useOfficeStore.getState().setZoomLevel(Math.min(1.5, Math.max(0.4, zoomLevel + delta)));
    },
    [zoomLevel],
  );

  const recentEvents = eventLog.slice(-6);

  return (
    <section className="office-surface space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-4 pb-2">
          <div className="space-y-1">
            <CardTitle className="text-base font-semibold">Office Canvas</CardTitle>
            <p className="text-xs text-[var(--muted-foreground)]">
              Canvas 2D · {roster.length} agents · {floorPlan.length} zones · drag to pan · # FIXED:
              stale comment said PixiJS scroll to zoom
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge>Mode: {mode}</Badge>
            <Badge>Surface: {surface}</Badge>
            <Badge>{zoomLevel.toFixed(1)}x</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[#faf7f2]">
            <canvas
              ref={canvasRef}
              className="w-full cursor-grab select-none"
              style={{ height: 520 }}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
            />
          </div>

          {focusedZoneId && (
            <div className="rounded-xl border border-[var(--border)] bg-white/70 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted-foreground)]">
                Focused zone
              </p>
              <p className="mt-1 font-semibold">
                {floorPlan.find((z) => z.id === focusedZoneId)?.label ?? focusedZoneId}
              </p>
              <p className="mt-0.5 text-sm text-[var(--muted-foreground)]">
                {floorPlan.find((z) => z.id === focusedZoneId)?.note}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Event Trail ({eventLog.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {recentEvents.length === 0 && (
              <p className="col-span-full text-center text-sm text-[var(--muted-foreground)] py-8">
                No events yet. Connect to see live office activity.
              </p>
            )}
            {recentEvents.map((event, i) => (
              <div
                key={`${event.eventType}-${i}`}
                className="space-y-1 rounded-xl border border-[var(--border)] bg-white/70 p-3"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="rounded-full bg-[var(--primary)]/10 px-2 py-0.5 text-xs font-medium text-[var(--primary)]">
                    {event.eventType}
                  </span>
                  <span className="text-xs text-[var(--muted-foreground)]">
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-xs leading-relaxed text-[var(--muted-foreground)]">
                  {Object.entries(event.payload)
                    .slice(0, 3)
                    .map(([k, v]) => `${k}: ${String(v)}`)
                    .join(" · ")}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </section>
  );
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
): void {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}
