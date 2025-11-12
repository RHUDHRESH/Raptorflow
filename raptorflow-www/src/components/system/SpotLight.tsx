"use client";

import { useEffect, useRef } from "react";

interface SpotLightProps {
  className?: string;
  animated?: boolean;
}

export function SpotLight({ className = "", animated = false }: SpotLightProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    };

    const draw = () => {
      resizeCanvas();
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);

      // Create radial gradient (spotlight effect)
      const gradient = ctx.createRadialGradient(
        width / 2,
        height / 2,
        0,
        width / 2,
        height / 2,
        Math.max(width, height) * 0.6
      );

      gradient.addColorStop(0, "rgba(139, 124, 249, 0.4)");
      gradient.addColorStop(0.5, "rgba(139, 124, 249, 0.2)");
      gradient.addColorStop(1, "rgba(139, 124, 249, 0)");

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);
    };

    draw();

    const resizeObserver = new ResizeObserver(() => {
      draw();
    });
    resizeObserver.observe(canvas);

    if (animated) {
      let animationFrame: number;
      const animate = () => {
        draw();
        animationFrame = requestAnimationFrame(animate);
      };
      animate();

      return () => {
        cancelAnimationFrame(animationFrame);
        resizeObserver.disconnect();
      };
    }

    return () => resizeObserver.disconnect();
  }, [animated]);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{ width: "100%", height: "100%" }}
    />
  );
}

