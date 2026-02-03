"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

interface LottieCompassProps {
  size?: number;
  className?: string;
  autoplay?: boolean;
  loop?: boolean;
}

// Custom SVG animation that mimics Lottie behavior
export function LottieCompass({
  size = 200,
  className = "",
  autoplay = true,
  loop = true,
}: LottieCompassProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const outerRef = useRef<SVGCircleElement>(null);
  const innerRef = useRef<SVGCircleElement>(null);
  const needleRef = useRef<SVGGElement>(null);
  const [isPlaying, setIsPlaying] = useState(autoplay);

  useEffect(() => {
    if (!isPlaying || !containerRef.current) return;

    const ctx = gsap.context(() => {
      // Outer ring pulse
      if (outerRef.current) {
        gsap.to(outerRef.current, {
          strokeDashoffset: -100,
          duration: 3,
          ease: "none",
          repeat: -1,
        });
      }

      // Inner ring counter-rotation
      if (innerRef.current) {
        gsap.to(innerRef.current, {
          rotation: -360,
          transformOrigin: "center center",
          duration: 20,
          ease: "none",
          repeat: -1,
        });
      }

      // Needle gentle sway
      if (needleRef.current) {
        gsap.to(needleRef.current, {
          rotation: 15,
          transformOrigin: "center center",
          duration: 2,
          ease: "sine.inOut",
          repeat: -1,
          yoyo: true,
        });
      }

      // Floating animation for entire compass
      gsap.to(containerRef.current, {
        y: -10,
        duration: 2,
        ease: "sine.inOut",
        repeat: -1,
        yoyo: true,
      });
    }, containerRef);

    return () => ctx.revert();
  }, [isPlaying]);

  return (
    <div
      ref={containerRef}
      className={`inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      onMouseEnter={() => setIsPlaying(true)}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Outer animated ring */}
        <circle
          ref={outerRef}
          cx="100"
          cy="100"
          r="90"
          stroke="var(--accent)"
          strokeWidth="2"
          strokeDasharray="20 10 5 10"
          strokeLinecap="round"
          opacity="0.5"
        />

        {/* Static outer ring */}
        <circle
          cx="100"
          cy="100"
          r="80"
          stroke="var(--text-primary)"
          strokeWidth="1.5"
          strokeLinecap="round"
        />

        {/* Rotating inner ring with markers */}
        <g ref={innerRef}>
          {[...Array(8)].map((_, i) => {
            const angle = (i * 45 * Math.PI) / 180;
            const x = 100 + 70 * Math.cos(angle);
            const y = 100 + 70 * Math.sin(angle);
            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r="3"
                fill="var(--accent)"
                opacity="0.6"
              />
            );
          })}
        </g>

        {/* Cardinal markers */}
        {["N", "E", "S", "W"].map((dir, i) => {
          const angle = (i * 90 * Math.PI) / 180;
          const x = 100 + 60 * Math.cos(angle);
          const y = 100 + 60 * Math.sin(angle);
          return (
            <text
              key={dir}
              x={x}
              y={y + 4}
              textAnchor="middle"
              fontSize="10"
              fontFamily="Cormorant Garamond"
              fontWeight="600"
              fill="var(--text-primary)"
            >
              {dir}
            </text>
          );
        })}

        {/* Decorative circles */}
        <circle
          cx="100"
          cy="100"
          r="50"
          stroke="var(--border-strong)"
          strokeWidth="1"
          strokeDasharray="4 8"
          opacity="0.5"
        />

        {/* Animated needle */}
        <g ref={needleRef}>
          {/* North half */}
          <path
            d="M100 30 L107 100 L100 100 L93 100 Z"
            fill="var(--accent)"
          />
          {/* South half */}
          <path
            d="M100 170 L107 100 L100 100 L93 100 Z"
            fill="var(--text-muted)"
            opacity="0.3"
          />
          {/* Shine effect */}
          <path
            d="M100 35 L103 100 L100 100 Z"
            fill="white"
            opacity="0.3"
          />
        </g>

        {/* Center hub */}
        <circle
          cx="100"
          cy="100"
          r="12"
          fill="var(--bg-primary)"
          stroke="var(--text-primary)"
          strokeWidth="2"
        />
        <circle cx="100" cy="100" r="6" fill="var(--accent)" />
        <circle cx="100" cy="100" r="2" fill="var(--bg-primary)" />
      </svg>
    </div>
  );
}

// Loading spinner version
export function LottieSpinner({
  size = 60,
  className = "",
}: {
  size?: number;
  className?: string;
}) {
  const spinnerRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!spinnerRef.current) return;

    const ctx = gsap.context(() => {
      gsap.to(spinnerRef.current, {
        rotation: 360,
        transformOrigin: "center center",
        duration: 1.5,
        ease: "none",
        repeat: -1,
      });
    });

    return () => ctx.revert();
  }, []);

  return (
    <svg
      ref={spinnerRef}
      width={size}
      height={size}
      viewBox="0 0 60 60"
      className={className}
    >
      <circle
        cx="30"
        cy="30"
        r="25"
        stroke="var(--border)"
        strokeWidth="4"
        fill="none"
      />
      <path
        d="M30 5 A25 25 0 0 1 55 30"
        stroke="var(--accent)"
        strokeWidth="4"
        fill="none"
        strokeLinecap="round"
      />
      <circle cx="30" cy="30" r="4" fill="var(--accent)" />
    </svg>
  );
}

export default LottieCompass;
