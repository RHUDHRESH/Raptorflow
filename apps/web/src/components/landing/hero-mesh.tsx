"use client";

import * as React from "react";
import { useEffect, useRef } from "react";
import { createNoise2D } from "simplex-noise";

export function HeroMesh() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const isVisibleRef = useRef(true);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const noise2D = createNoise2D();

    const colors = [
      { r: 232, g: 90, b: 44 }, // #E85A2C
      { r: 233, g: 160, b: 60 }, // #E9A03C
      { r: 247, g: 198, b: 99 }, // #F7C663
      { r: 31, g: 58, b: 95 }, // #1F3A5F
    ];

    let time = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    function resize() {
      if (!canvas) return;
      const parent = canvas.parentElement;
      if (!parent) return;
      const w = parent.offsetWidth;
      const h = parent.offsetHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx!.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    resize();
    window.addEventListener("resize", resize);

    // IntersectionObserver to pause when not visible
    const observer = new IntersectionObserver(
      ([entry]) => {
        isVisibleRef.current = entry.isIntersecting;
      },
      { threshold: 0 },
    );
    observer.observe(canvas);

    function draw() {
      if (!ctx || !canvas) return;
      const w = canvas.width / dpr;
      const h = canvas.height / dpr;

      if (!isVisibleRef.current) {
        animRef.current = requestAnimationFrame(draw);
        return;
      }

      time += 0.003;

      const imageData = ctx.createImageData(w, h);
      const data = imageData.data;

      const scale = 0.002;

      for (let y = 0; y < h; y += 2) {
        for (let x = 0; x < w; x += 2) {
          const nx = x * scale;
          const ny = y * scale;

          const n1 = noise2D(nx + time, ny);
          const n2 = noise2D(nx * 1.5 - time * 0.7, ny * 1.5 + time * 0.3);
          const n3 = noise2D(nx * 2 + time * 0.5, ny * 2 - time * 0.5);

          const t1 = (n1 + 1) * 0.5;
          const t2 = (n2 + 1) * 0.5;
          const t3 = (n3 + 1) * 0.5;

          // Blend between colors based on noise
          let r = 0,
            g = 0,
            b = 0;

          if (t1 < 0.33) {
            const localT = t1 / 0.33;
            r = colors[0]!.r * (1 - localT) + colors[1]!.r * localT;
            g = colors[0]!.g * (1 - localT) + colors[1]!.g * localT;
            b = colors[0]!.b * (1 - localT) + colors[1]!.b * localT;
          } else if (t1 < 0.66) {
            const localT = (t1 - 0.33) / 0.33;
            r = colors[1]!.r * (1 - localT) + colors[2]!.r * localT;
            g = colors[1]!.g * (1 - localT) + colors[2]!.g * localT;
            b = colors[1]!.b * (1 - localT) + colors[2]!.b * localT;
          } else {
            const localT = (t1 - 0.66) / 0.34;
            r = colors[2]!.r * (1 - localT) + colors[3]!.r * localT;
            g = colors[2]!.g * (1 - localT) + colors[3]!.g * localT;
            b = colors[2]!.b * (1 - localT) + colors[3]!.b * localT;
          }

          // Add subtle variation from other noise layers
          r += (t2 - 0.5) * 20;
          g += (t2 - 0.5) * 15;
          b += (t3 - 0.5) * 25;

          // Fade edges
          const edgeFadeX = Math.min(1, x / (w * 0.15), (w - x) / (w * 0.15));
          const edgeFadeY = Math.min(1, y / (h * 0.15), (h - y) / (h * 0.15));
          const edgeFade = Math.min(edgeFadeX, edgeFadeY);

          const alpha = 0.12 * edgeFade;

          const ir = Math.max(0, Math.min(255, Math.round(r)));
          const ig = Math.max(0, Math.min(255, Math.round(g)));
          const ib = Math.max(0, Math.min(255, Math.round(b)));
          const ia = Math.round(alpha * 255);

          // Fill 2x2 block for performance
          for (let dy = 0; dy < 2 && y + dy < h; dy++) {
            for (let dx = 0; dx < 2 && x + dx < w; dx++) {
              const idx = ((y + dy) * w + (x + dx)) * 4;
              data[idx] = ir;
              data[idx + 1] = ig;
              data[idx + 2] = ib;
              data[idx + 3] = ia;
            }
          }
        }
      }

      ctx.putImageData(imageData, 0, 0);
      animRef.current = requestAnimationFrame(draw);
    }

    animRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener("resize", resize);
      observer.disconnect();
    };
  }, []);

  return (
    <div
      className="absolute inset-0 overflow-hidden"
      style={{ transform: "skewY(-5deg)", transformOrigin: "top left" }}
    >
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ mixBlendMode: "multiply" }}
      />
    </div>
  );
}
