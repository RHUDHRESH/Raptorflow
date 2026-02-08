"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

interface CompassLogoProps {
  size?: number;
  className?: string;
  animate?: boolean;
  variant?: "default" | "minimal" | "mark";
}

export function CompassLogo({
  size = 120,
  className = "",
  animate = true,
  variant = "default",
}: CompassLogoProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const needleRef = useRef<SVGGElement>(null);

  useEffect(() => {
    if (!animate || !svgRef.current) return;

    const ctx = gsap.context(() => {
      const paths = svgRef.current?.querySelectorAll("path, circle, line");
      if (paths) {
        gsap.fromTo(
          paths,
          { strokeDasharray: 300, strokeDashoffset: 300, opacity: 0 },
          {
            strokeDashoffset: 0,
            opacity: 1,
            duration: 1.5,
            stagger: 0.1,
            ease: "power2.out",
          }
        );
      }

      if (needleRef.current) {
        gsap.fromTo(
          needleRef.current,
          { rotation: -45, transformOrigin: "center center" },
          {
            rotation: 0,
            duration: 2,
            ease: "elastic.out(1, 0.5)",
            delay: 0.5,
          }
        );
      }
    }, svgRef);

    return () => ctx.revert();
  }, [animate]);

  if (variant === "mark") {
    return (
      <svg
        ref={svgRef}
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
      >
        <g ref={needleRef}>
          <path
            d="M50 15L55 50L50 85L45 50L50 15Z"
            fill="currentColor"
            className="text-[var(--accent)]"
          />
          <circle
            cx="50"
            cy="50"
            r="6"
            fill="var(--bg-primary)"
            stroke="currentColor"
            strokeWidth="2"
            className="text-[var(--text-primary)]"
          />
        </g>
      </svg>
    );
  }

  if (variant === "minimal") {
    return (
      <svg
        ref={svgRef}
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
      >
        <circle
          cx="50"
          cy="50"
          r="45"
          stroke="currentColor"
          strokeWidth="1.5"
          className="text-[var(--border-strong)]"
        />
        <circle
          cx="50"
          cy="50"
          r="38"
          stroke="currentColor"
          strokeWidth="0.5"
          className="text-[var(--border)]"
        />
        <g className="text-[var(--text-primary)]">
          <text x="50" y="12" textAnchor="middle" fontSize="8" fontFamily="Cormorant Garamond" fontWeight="600">N</text>
          <text x="88" y="53" textAnchor="middle" fontSize="8" fontFamily="Cormorant Garamond" fontWeight="600">E</text>
          <text x="50" y="92" textAnchor="middle" fontSize="8" fontFamily="Cormorant Garamond" fontWeight="600">S</text>
          <text x="12" y="53" textAnchor="middle" fontSize="8" fontFamily="Cormorant Garamond" fontWeight="600">W</text>
        </g>
        <g ref={needleRef}>
          <path
            d="M50 20L54 50L50 80L46 50L50 20Z"
            fill="currentColor"
            className="text-[var(--accent)]"
          />
          <path
            d="M50 80L54 50L50 20L46 50L50 80Z"
            fill="currentColor"
            className="text-[var(--text-muted)]"
            opacity="0.4"
          />
        </g>
        <circle
          cx="50"
          cy="50"
          r="5"
          fill="var(--bg-primary)"
          stroke="currentColor"
          strokeWidth="2"
          className="text-[var(--accent)]"
        />
      </svg>
    );
  }

  return (
    <svg
      ref={svgRef}
      width={size}
      height={size}
      viewBox="0 0 200 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <circle
        cx="100"
        cy="100"
        r="92"
        stroke="currentColor"
        strokeWidth="1"
        className="text-[var(--border-strong)]"
        strokeLinecap="round"
        strokeDasharray="4 2"
      />
      <circle
        cx="100"
        cy="100"
        r="85"
        stroke="currentColor"
        strokeWidth="2"
        className="text-[var(--text-primary)]"
        strokeLinecap="round"
      />
      <circle
        cx="100"
        cy="100"
        r="75"
        stroke="currentColor"
        strokeWidth="0.5"
        className="text-[var(--border)]"
      />

      {[...Array(12)].map((_, i) => {
        const angle = (i * 30 * Math.PI) / 180;
        const x1 = 100 + 78 * Math.cos(angle);
        const y1 = 100 + 78 * Math.sin(angle);
        const x2 = 100 + 82 * Math.cos(angle);
        const y2 = 100 + 82 * Math.sin(angle);
        return (
          <line
            key={i}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="currentColor"
            strokeWidth="1.5"
            className="text-[var(--accent)]"
            strokeLinecap="round"
          />
        );
      })}

      {[0, 90, 180, 270].map((deg, i) => {
        const angle = (deg * Math.PI) / 180;
        const x1 = 100 + 72 * Math.cos(angle);
        const y1 = 100 + 72 * Math.sin(angle);
        const x2 = 100 + 82 * Math.cos(angle);
        const y2 = 100 + 82 * Math.sin(angle);
        return (
          <line
            key={`cardinal-${i}`}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="currentColor"
            strokeWidth="3"
            className="text-[var(--accent)]"
            strokeLinecap="round"
          />
        );
      })}

      <g className="text-[var(--text-primary)]" style={{ fontFamily: "Cormorant Garamond, serif", fontWeight: 600 }}>
        <text x="100" y="28" textAnchor="middle" fontSize="14" letterSpacing="2">N</text>
        <text x="176" y="105" textAnchor="middle" fontSize="14" letterSpacing="2">E</text>
        <text x="100" y="182" textAnchor="middle" fontSize="14" letterSpacing="2">S</text>
        <text x="24" y="105" textAnchor="middle" fontSize="14" letterSpacing="2">W</text>
      </g>

      <circle
        cx="100"
        cy="100"
        r="55"
        stroke="currentColor"
        strokeWidth="0.5"
        className="text-[var(--border-strong)]"
        strokeDasharray="2 4"
      />

      {[45, 135, 225, 315].map((deg, i) => {
        const angle = (deg * Math.PI) / 180;
        const x2 = 100 + 55 * Math.cos(angle);
        const y2 = 100 + 55 * Math.sin(angle);
        return (
          <line
            key={`inter-${i}`}
            x1="100"
            y1="100"
            x2={x2}
            y2={y2}
            stroke="currentColor"
            strokeWidth="0.5"
            className="text-[var(--border)]"
            strokeLinecap="round"
          />
        );
      })}

      <g ref={needleRef}>
        <path
          d="M100 35L106 100L100 165L94 100L100 35Z"
          fill="currentColor"
          className="text-[var(--accent)]"
        />
        <path
          d="M100 165L106 100L100 35L94 100L100 165Z"
          fill="currentColor"
          className="text-[var(--text-muted)]"
          opacity="0.3"
        />
        <path
          d="M100 40L103 100L100 100L97 100L100 40Z"
          fill="white"
          opacity="0.2"
        />
      </g>

      <circle
        cx="100"
        cy="100"
        r="12"
        fill="var(--bg-primary)"
        stroke="currentColor"
        strokeWidth="2"
        className="text-[var(--text-primary)]"
      />
      <circle
        cx="100"
        cy="100"
        r="7"
        fill="currentColor"
        className="text-[var(--accent)]"
      />
      <circle
        cx="100"
        cy="100"
        r="3"
        fill="var(--bg-primary)"
      />

      <path
        d="M100 8C100 8 102 12 100 16C98 12 100 8 100 8"
        fill="currentColor"
        className="text-[var(--accent)]"
      />
      <path
        d="M100 192C100 192 98 188 100 184C102 188 100 192 100 192"
        fill="currentColor"
        className="text-[var(--accent)]"
      />
      <path
        d="M8 100C8 100 12 98 16 100C12 102 8 100 8 100"
        fill="currentColor"
        className="text-[var(--accent)]"
      />
      <path
        d="M192 100C192 100 188 102 184 100C188 98 192 100 192 100"
        fill="currentColor"
        className="text-[var(--accent)]"
      />
    </svg>
  );
}

export function CompassSpinner({ size = 40, className = "" }: { size?: number; className?: string }) {
  const spinnerRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!spinnerRef.current) return;

    const needle = spinnerRef.current.querySelector("#spinner-needle");
    if (!needle) return;

    const ctx = gsap.context(() => {
      gsap.to(needle, {
        rotation: 360,
        transformOrigin: "center center",
        duration: 2,
        repeat: -1,
        ease: "none",
      });
    }, spinnerRef);

    return () => ctx.revert();
  }, []);

  return (
    <svg
      ref={spinnerRef}
      width={size}
      height={size}
      viewBox="0 0 50 50"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <circle
        cx="25"
        cy="25"
        r="22"
        stroke="currentColor"
        strokeWidth="2"
        className="text-[var(--border)]"
      />
      <g id="spinner-needle">
        <path
          d="M25 8L28 25L25 42L22 25L25 8Z"
          fill="currentColor"
          className="text-[var(--accent)]"
        />
      </g>
      <circle
        cx="25"
        cy="25"
        r="4"
        fill="var(--bg-primary)"
        stroke="currentColor"
        strokeWidth="1.5"
        className="text-[var(--accent)]"
      />
    </svg>
  );
}

export default CompassLogo;
