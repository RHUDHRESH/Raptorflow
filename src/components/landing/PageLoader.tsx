"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

interface PageLoaderProps {
  onComplete?: () => void;
}

export function PageLoader({ onComplete }: PageLoaderProps) {
  const [isLoading, setIsLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const birdRef = useRef<SVGSVGElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline({
      onComplete: () => {
        // Exit animation
        gsap.to(containerRef.current, {
          yPercent: -100,
          duration: 0.8,
          ease: "power4.inOut",
          onComplete: () => {
            setIsLoading(false);
            onComplete?.();
          },
        });
      },
    });

    // Bird draw animation
    tl.fromTo(
      ".loader-bird-path",
      { strokeDashoffset: 200 },
      { strokeDashoffset: 0, duration: 1.5, ease: "power2.inOut" }
    )
      .fromTo(
        ".loader-bird-fill",
        { opacity: 0 },
        { opacity: 1, duration: 0.5 },
        "-=0.5"
      )
      .fromTo(
        ".loader-text",
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5 },
        "-=0.3"
      )
      .to(
        progressRef.current,
        { width: "100%", duration: 1.5, ease: "power2.inOut" },
        "-=0.5"
      )
      .to({}, { duration: 0.3 }); // Hold

    return () => {
      tl.kill();
    };
  }, [onComplete]);

  if (!isLoading) return null;

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[100] bg-[var(--bg-canvas)] flex flex-col items-center justify-center"
    >
      {/* Animated grid background */}
      <div className="absolute inset-0 opacity-[0.02]">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `linear-gradient(var(--ink-1) 1px, transparent 1px), linear-gradient(90deg, var(--ink-1) 1px, transparent 1px)`,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      {/* Center content */}
      <div className="relative flex flex-col items-center">
        {/* Origami Bird with draw animation */}
        <svg
          ref={birdRef}
          width="80"
          height="80"
          viewBox="0 0 48 48"
          fill="none"
          className="text-[var(--ink-1)] mb-8"
        >
          {/* Outer stroke */}
          <path
            className="loader-bird-path"
            d="M24 4L4 44L24 36L44 44L24 4Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinejoin="round"
            fill="none"
            strokeDasharray="200"
            strokeDashoffset="200"
          />
          {/* Inner fold line */}
          <path
            className="loader-bird-path"
            d="M24 4V36"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
            strokeDasharray="200"
            strokeDashoffset="200"
          />
          {/* Fill overlay */}
          <path
            className="loader-bird-fill"
            d="M24 4L4 44L24 36L44 44L24 4Z"
            fill="currentColor"
            fillOpacity="0.1"
            opacity="0"
          />
        </svg>

        {/* Brand text */}
        <div className="loader-text text-center">
          <p className="text-2xl font-bold text-[var(--ink-1)] tracking-tight mb-2">
            RaptorFlow
          </p>
          <p className="rf-mono-xs text-[var(--ink-3)] uppercase tracking-[0.3em]">
            Loading Experience
          </p>
        </div>

        {/* Progress bar */}
        <div className="mt-8 w-48 h-0.5 bg-[var(--border-1)] rounded-full overflow-hidden">
          <div
            ref={progressRef}
            className="h-full bg-[var(--ink-1)] rounded-full"
            style={{ width: "0%" }}
          />
        </div>

        {/* Percentage */}
        <div className="mt-4 rf-mono-xs text-[var(--ink-3)]">
          <Counter />
        </div>
      </div>

      {/* Corner decorations */}
      <div className="absolute top-8 left-8 w-16 h-16 border-l-2 border-t-2 border-[var(--border-1)]" />
      <div className="absolute top-8 right-8 w-16 h-16 border-r-2 border-t-2 border-[var(--border-1)]" />
      <div className="absolute bottom-8 left-8 w-16 h-16 border-l-2 border-b-2 border-[var(--border-1)]" />
      <div className="absolute bottom-8 right-8 w-16 h-16 border-r-2 border-b-2 border-[var(--border-1)]" />
    </div>
  );
}

// Counter component for loader
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const duration = 2500;
    const steps = 100;
    const increment = 100 / steps;
    const interval = duration / steps;

    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= 100) {
        setCount(100);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, interval);

    return () => clearInterval(timer);
  }, []);

  return <span>{count}%</span>;
}
