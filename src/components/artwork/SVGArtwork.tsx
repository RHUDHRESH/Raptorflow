"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

/* ═══════════════════════════════════════════════════════════════════
   SVG Artwork — Hand-crafted, GSAP-animated
   Topographic contours, constellation map, origami bird draw-in
   ═══════════════════════════════════════════════════════════════════ */

/** Origami bird that draws itself with GSAP stroke animation */
export function OrigamiBirdSVG({
  size = 120,
  animate = true,
  className = "",
}: {
  size?: number;
  animate?: boolean;
  className?: string;
}) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!animate || !svgRef.current) return;

    const paths = svgRef.current.querySelectorAll(".bird-stroke");
    const fills = svgRef.current.querySelectorAll(".bird-fill");

    const ctx = gsap.context(() => {
      // Set initial stroke dash
      paths.forEach((path) => {
        const length = (path as SVGPathElement).getTotalLength();
        gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
      });
      gsap.set(fills, { opacity: 0 });

      const tl = gsap.timeline({ delay: 0.2 });

      // Draw strokes
      paths.forEach((path, i) => {
        const length = (path as SVGPathElement).getTotalLength();
        tl.to(path, {
          strokeDashoffset: 0,
          duration: 0.8,
          ease: "power2.inOut",
        }, i * 0.15);
      });

      // Fade in fills
      tl.to(fills, {
        opacity: 0.08,
        duration: 0.6,
        stagger: 0.1,
        ease: "power2.out",
      }, "-=0.3");
    }, svgRef);

    return () => ctx.revert();
  }, [animate]);

  return (
    <svg
      ref={svgRef}
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      className={className}
    >
      {/* Left wing */}
      <path className="bird-fill" d="M60 15 L15 85 L60 70 Z" fill="#2A2529" />
      <path className="bird-stroke" d="M60 15 L15 85 L60 70 Z" stroke="#2A2529" strokeWidth="1.5" strokeLinejoin="round" />
      {/* Right wing */}
      <path className="bird-fill" d="M60 15 L105 85 L60 70 Z" fill="#2A2529" />
      <path className="bird-stroke" d="M60 15 L105 85 L60 70 Z" stroke="#2A2529" strokeWidth="1.5" strokeLinejoin="round" />
      {/* Center fold */}
      <path className="bird-stroke" d="M60 15 V70" stroke="#2A2529" strokeWidth="1" strokeLinecap="round" />
      {/* Wing creases */}
      <path className="bird-stroke" d="M60 15 L37 55" stroke="#2A2529" strokeWidth="0.5" strokeLinecap="round" opacity="0.4" />
      <path className="bird-stroke" d="M60 15 L83 55" stroke="#2A2529" strokeWidth="0.5" strokeLinecap="round" opacity="0.4" />
    </svg>
  );
}

/** Generative topographic contour lines */
export function TopographicArt({
  width = 600,
  height = 400,
  className = "",
}: {
  width?: number;
  height?: number;
  className?: string;
}) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const paths = svgRef.current.querySelectorAll(".topo-line");

    const ctx = gsap.context(() => {
      paths.forEach((path) => {
        const length = (path as SVGPathElement).getTotalLength();
        gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
      });

      gsap.to(paths, {
        strokeDashoffset: 0,
        duration: 3,
        stagger: 0.15,
        ease: "power1.inOut",
      });
    }, svgRef);

    return () => ctx.revert();
  }, []);

  // Generate concentric contour paths
  const contours = Array.from({ length: 12 }, (_, i) => {
    const cx = width * 0.45 + Math.sin(i * 0.7) * 30;
    const cy = height * 0.5 + Math.cos(i * 0.5) * 20;
    const rx = 40 + i * 22 + Math.sin(i * 1.3) * 15;
    const ry = 30 + i * 16 + Math.cos(i * 0.9) * 10;
    const rotation = i * 5 + Math.sin(i) * 8;
    return { cx, cy, rx, ry, rotation, opacity: 0.08 + (12 - i) * 0.015 };
  });

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      fill="none"
      className={className}
    >
      {contours.map((c, i) => (
        <ellipse
          key={i}
          className="topo-line"
          cx={c.cx}
          cy={c.cy}
          rx={c.rx}
          ry={c.ry}
          transform={`rotate(${c.rotation} ${c.cx} ${c.cy})`}
          stroke="#2A2529"
          strokeWidth="0.8"
          opacity={c.opacity}
        />
      ))}
    </svg>
  );
}

/** Animated constellation map */
export function ConstellationMap({
  width = 500,
  height = 500,
  className = "",
}: {
  width?: number;
  height?: number;
  className?: string;
}) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const dots = svgRef.current.querySelectorAll(".const-dot");
    const lines = svgRef.current.querySelectorAll(".const-line");

    const ctx = gsap.context(() => {
      gsap.set(dots, { scale: 0, transformOrigin: "center" });
      lines.forEach((line) => {
        const length = (line as SVGLineElement).getTotalLength?.() || 100;
        gsap.set(line, { strokeDasharray: length, strokeDashoffset: length });
      });

      const tl = gsap.timeline({ delay: 0.5 });
      tl.to(dots, { scale: 1, duration: 0.3, stagger: 0.04, ease: "back.out(2)" });
      tl.to(lines, { strokeDashoffset: 0, duration: 0.6, stagger: 0.03, ease: "power2.out" }, "-=0.5");

      // Subtle pulse on dots
      dots.forEach((dot, i) => {
        gsap.to(dot, {
          opacity: 0.3 + Math.random() * 0.4,
          duration: 1.5 + Math.random(),
          repeat: -1,
          yoyo: true,
          delay: i * 0.1,
          ease: "sine.inOut",
        });
      });
    }, svgRef);

    return () => ctx.revert();
  }, []);

  // Generate random star positions and connections
  const stars = Array.from({ length: 30 }, (_, i) => ({
    x: Math.random() * width,
    y: Math.random() * height,
    r: 1.5 + Math.random() * 2,
  }));

  // Connect nearby stars
  const connections: { x1: number; y1: number; x2: number; y2: number }[] = [];
  const threshold = width * 0.25;
  for (let i = 0; i < stars.length; i++) {
    for (let j = i + 1; j < stars.length; j++) {
      const dx = stars[i].x - stars[j].x;
      const dy = stars[i].y - stars[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < threshold && connections.length < 40) {
        connections.push({
          x1: stars[i].x,
          y1: stars[i].y,
          x2: stars[j].x,
          y2: stars[j].y,
        });
      }
    }
  }

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      fill="none"
      className={className}
    >
      {connections.map((c, i) => (
        <line
          key={`l-${i}`}
          className="const-line"
          x1={c.x1}
          y1={c.y1}
          x2={c.x2}
          y2={c.y2}
          stroke="#2A2529"
          strokeWidth="0.5"
          opacity="0.1"
        />
      ))}
      {stars.map((s, i) => (
        <circle
          key={`d-${i}`}
          className="const-dot"
          cx={s.x}
          cy={s.y}
          r={s.r}
          fill="#2A2529"
          opacity="0.6"
        />
      ))}
    </svg>
  );
}
