"use client";

import { useEffect, useRef } from "react";
import { Application } from "pixi.js";
import { AvatarSprite, type AvatarConfig } from "./AvatarSprite";
import { AmbientOrbs } from "./AmbientOrbs";
import { ConnectionWeb } from "./ConnectionWeb";

const AVATAR_CONFIGS: Omit<AvatarConfig, "x" | "y">[] = [
  { key: "cortex", label: "Cortex", color: 0x8b5cf6 },
  { key: "sentinel", label: "Sentinel", color: 0x3b82f6 },
  { key: "maven", label: "Maven", color: 0x10b981 },
  { key: "oracle", label: "Oracle", color: 0xf59e0b },
  { key: "wraith", label: "Wraith", color: 0xef4444 },
  { key: "axiom", label: "Axiom", color: 0x06b6d6 },
];

function hexPositions(cx: number, cy: number, radius: number): { x: number; y: number }[] {
  return Array.from({ length: 6 }, (_, i) => {
    const angle = (Math.PI / 3) * i - Math.PI / 2;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  });
}

export default function OfficeCanvas() {
  const mountRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<Application | null>(null);
  const spritesRef = useRef<AvatarSprite[]>([]);
  const orbsRef = useRef<AmbientOrbs | null>(null);
  const webRef = useRef<ConnectionWeb | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;
    const mount = mountRef.current;

    let destroyed = false;

    (async () => {
      const app = new Application();
      if (destroyed) return;
      await app.init({
        background: 0x08081a,
        resizeTo: mount,
        antialias: true,
        resolution: window.devicePixelRatio ?? 1,
        autoDensity: true,
      });
      if (destroyed) {
        app.destroy(true);
        return;
      }
      appRef.current = app;
      mount.appendChild(app.canvas);

      const orbs = new AmbientOrbs(app);
      orbsRef.current = orbs;

      const cx = app.screen.width / 2;
      const cy = app.screen.height / 2;
      const radius = Math.min(app.screen.width, app.screen.height) * 0.28;
      const positions = hexPositions(cx, cy, radius);

      const web = new ConnectionWeb(app, []);
      webRef.current = web;

      const sprites = AVATAR_CONFIGS.map((cfg, i) => {
        const sprite = new AvatarSprite(app, {
          ...cfg,
          x: positions[i].x,
          y: positions[i].y,
        });
        app.stage.addChild(sprite.container);
        return sprite;
      });

      web.sprites = sprites;
      spritesRef.current = sprites;
    })();

    const resizeObserver = new ResizeObserver(() => {
      if (!appRef.current || !mountRef.current) return;
      const { width, height } = mountRef.current.getBoundingClientRect();
      const cx = width / 2;
      const cy = height / 2;
      const radius = Math.min(width, height) * 0.28;
      const positions = hexPositions(cx, cy, radius);
      spritesRef.current.forEach((sprite, i) => {
        sprite.container.x = positions[i].x;
        sprite.baseY = positions[i].y;
        sprite.container.y = positions[i].y;
      });
      orbsRef.current?.resize();
    });
    resizeObserver.observe(mount);

    return () => {
      destroyed = true;
      resizeObserver.disconnect();
      orbsRef.current?.destroy();
      webRef.current?.destroy();
      spritesRef.current.forEach((s) => s.destroy());
      spritesRef.current = [];
      appRef.current?.destroy(true);
      appRef.current = null;
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="absolute inset-0 w-full h-full"
      style={{ background: "#08081a" }}
    />
  );
}
