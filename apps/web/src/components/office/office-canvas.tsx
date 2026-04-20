"use client";

import React, { useEffect, useRef, useCallback } from "react";
import * as PIXI from "pixi.js";
import { Viewport } from "pixi-viewport";
import { gsap } from "gsap";
import { useOfficeStore } from "@/state/office-store";
import { useFoundationStore } from "@/state/foundation-store";
import { 
  CANVAS_COLORS, 
  OFFICE_ZONES, 
  PLACEHOLDER_COLORS, 
  ZOOM_LEVELS,
  ANIMATION_DURATIONS,
  type AgentKey
} from "@/lib/office-constants";

/**
 * RaptorFlow Office Canvas (PixiJS v8 Implementation)
 * 
 * This component manages the WebGL rendering of the 1980s office environment.
 * It strictly separates Layer 1 (Canvas) from Layer 2 (UI Chrome).
 */
export function OfficeCanvas({ onAgentClick }: { onAgentClick?: (key: AgentKey) => void }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const viewportRef = useRef<Viewport | null>(null);
  const agentSprites = useRef(new Map<AgentKey, PIXI.Container>());

  const { zoom, setZoom, setCanvasReady, agentStatuses } = useOfficeStore();
  const { sectionData } = useFoundationStore();
  const strategistName = sectionData.primary_goal?.strategistName || "Strategist";

  /* ─────────────────────────────────────────────────────────────────────────────
     INITIALIZATION (PixiJS v8)
     ───────────────────────────────────────────────────────────────────────────── */

  useEffect(() => {
    if (!containerRef.current) return;

    const app = new PIXI.Application();
    appRef.current = app;

    async function init() {
      await app.init({
        background: CANVAS_COLORS.env.wall,
        resizeTo: containerRef.current!,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true,
      });

      containerRef.current?.appendChild(app.canvas);

      // Setup Viewport (v5 API)
      const viewport = new Viewport({
        screenWidth: app.screen.width,
        screenHeight: app.screen.height,
        worldWidth: 1000,
        worldHeight: 1000,
        events: app.renderer.events,
      });

      app.stage.addChild(viewport);
      viewportRef.current = viewport;

      viewport
        .drag()
        .pinch()
        .wheel()
        .decelerate();

      viewport.setZoom(zoom, true);

      // Render Floor
      renderEnvironment(viewport);

      setCanvasReady(true);
    }

    init();

    return () => {
      app.destroy(true, { children: true, texture: true });
      appRef.current = null;
    };
  }, []);

  /* ─── Environment Rendering ─── */
  const renderEnvironment = (viewport: Viewport) => {
    const floor = new PIXI.Graphics();
    
    // Draw Carpet
    floor.poly([
      0, 0,
      1000, 0,
      1000, 1000,
      0, 1000
    ]);
    floor.fill(CANVAS_COLORS.env.carpet_b);
    
    // Draw Zones
    Object.values(OFFICE_ZONES).forEach(zone => {
      const zoneGfx = new PIXI.Graphics();
      const label = zone.id === 'strategist_office' ? `${strategistName.toUpperCase()}'S ${zone.label}` : zone.label;
      
      zoneGfx.rect(zone.defaultPosition.x, zone.defaultPosition.y, 250, 180);
      zoneGfx.fill(zone.isPrivate ? CANVAS_COLORS.env.wood : CANVAS_COLORS.env.wall);
      zoneGfx.stroke({ color: CANVAS_COLORS.env.carpet_a, width: 2 });
      
      const text = new PIXI.Text({
        text: label,
        style: {
          fontFamily: 'JetBrains Mono',
          fontSize: 12,
          fill: zone.isPrivate ? CANVAS_COLORS.env.light_wash : CANVAS_COLORS.env.carpet_a,
          fontWeight: 'bold',
        }
      });
      text.position.set(zone.defaultPosition.x + 10, zone.defaultPosition.y + 10);
      
      viewport.addChild(zoneGfx);
      viewport.addChild(text);
    });

    viewport.addChild(floor);
    floor.zIndex = -1;
  };

  /* ─── Agent Lifecycle ─── */
  useEffect(() => {
    if (!viewportRef.current) return;
    const viewport = viewportRef.current;

    Object.entries(agentStatuses).forEach(([key, status]) => {
      let agent = agentSprites.current.get(key as AgentKey);

      if (!agent) {
        agent = new PIXI.Container();
        const body = new PIXI.Graphics();
        body.rect(-16, -16, 32, 32);
        body.fill(PLACEHOLDER_COLORS[key as AgentKey]);
        body.stroke({ color: '#000000', width: 2 });
        
        agent.addChild(body);
        agent.interactive = true;
        agent.cursor = 'pointer';
        agent.on('pointerdown', () => onAgentClick?.(key as AgentKey));

        viewport.addChild(agent);
        agentSprites.current.set(key as AgentKey, agent);

        // GSAP Breathing Animation
        gsap.to(agent.scale, {
          x: 1.05,
          y: 1.05,
          duration: ANIMATION_DURATIONS.BREATHE + Math.random(),
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut"
        } as const);
      }

      // Update Position
      const zone = OFFICE_ZONES[status.currentZone] || OFFICE_ZONES.reception;
      gsap.to(agent.position, {
        x: zone.defaultPosition.x + 50,
        y: zone.defaultPosition.y + 50,
        duration: 1.5,
        ease: "power2.inOut"
      } as const);

      // Speaking Glow
      const glow = agent.getChildAt(0) as PIXI.Graphics;
      if (status.status === 'speaking') {
        gsap.to(glow, {
          alpha: 0.5,
          duration: 0.4,
          repeat: -1,
          yoyo: true
        } as const);
      } else {
        gsap.killTweensOf(glow);
        glow.alpha = 1;
      }
    });
  }, [agentStatuses, strategistName]);

  /* ─── Sync Zoom ─── */
  useEffect(() => {
    viewportRef.current?.setZoom(zoom, true);
  }, [zoom]);

  return (
    <div 
      ref={containerRef} 
      className="w-full h-full min-h-[500px] bg-[#FBF8F2] relative overflow-hidden" 
      style={{ cursor: 'crosshair' }}
    />
  );
}
