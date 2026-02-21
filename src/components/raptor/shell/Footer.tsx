"use client";

import React, { useRef, useEffect } from "react";
import gsap from "gsap";
import { Cloud, CloudCheck, AlertTriangle, HelpCircle } from "lucide-react";

interface FooterProps {
  autosaveState?: "saving" | "saved" | "error";
  lastSync?: string;
  warnings?: number;
  version?: string;
}

export function Footer({
  autosaveState = "saved",
  lastSync = "Just now",
  warnings = 2,
  version = "v2.4.1",
}: FooterProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const leftRef = useRef<HTMLDivElement>(null);
  const centerRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initial state
      gsap.set([leftRef.current, centerRef.current, rightRef.current], {
        opacity: 0,
        y: 5,
      });

      // Entrance animation
      gsap.to([leftRef.current, centerRef.current, rightRef.current], {
        opacity: 1,
        y: 0,
        duration: 0.4,
        ease: "power2.out",
        stagger: 0.05,
        delay: 0.3,
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  // Autosave state animation
  useEffect(() => {
    if (autosaveState === "saving") {
      gsap.to(".sync-icon", {
        rotation: 360,
        duration: 1,
        repeat: -1,
        ease: "none",
      });
    } else {
      gsap.killTweensOf(".sync-icon");
      gsap.set(".sync-icon", { rotation: 0 });
    }
  }, [autosaveState]);

  // Warning pulse animation
  useEffect(() => {
    if (warnings > 0) {
      gsap.to(".warning-badge", {
        scale: 1.05,
        duration: 0.5,
        yoyo: true,
        repeat: -1,
        ease: "power1.inOut",
      });
    } else {
      gsap.killTweensOf(".warning-badge");
      gsap.set(".warning-badge", { scale: 1 });
    }
  }, [warnings]);

  const getAutosaveIcon = () => {
    switch (autosaveState) {
      case "saving":
        return <Cloud size={12} className="sync-icon" />;
      case "saved":
        return <CloudCheck size={12} />;
      case "error":
        return <AlertTriangle size={12} />;
      default:
        return <CloudCheck size={12} />;
    }
  };

  const getAutosaveColor = () => {
    switch (autosaveState) {
      case "saving":
        return "var(--ink-2)";
      case "saved":
        return "#3D5A42";
      case "error":
        return "#8B4545";
      default:
        return "var(--ink-3)";
    }
  };

  return (
    <footer
      ref={containerRef}
      className="flex items-center justify-between px-4 flex-shrink-0"
      style={{
        height: "40px",
        backgroundColor: "var(--bg-canvas)",
        borderTop: "1px solid var(--border-1)",
        fontFamily: "'JetBrains Mono', monospace",
      }}
    >
      {/* Left: Autosave & Last Sync */}
      <div ref={leftRef} className="flex items-center gap-4">
        <div
          className="flex items-center gap-1.5 text-xs"
          style={{ color: getAutosaveColor() }}
        >
          {getAutosaveIcon()}
          <span className="capitalize">{autosaveState}</span>
        </div>
        <span
          className="text-xs"
          style={{ color: "var(--ink-3)" }}
        >
          Synced {lastSync}
        </span>
      </div>

      {/* Center: Warnings */}
      <div ref={centerRef} className="flex items-center">
        {warnings > 0 ? (
          <div
            className="warning-badge flex items-center gap-1.5 px-2 py-1 rounded text-xs"
            style={{
              backgroundColor: "rgba(139, 107, 61, 0.15)",
              color: "#8B6B3D",
            }}
          >
            <AlertTriangle size={12} />
            <span>
              {warnings} assumption{warnings !== 1 ? "s" : ""} unvalidated
            </span>
          </div>
        ) : (
          <span
            className="text-xs"
            style={{ color: "var(--ink-3)" }}
          >
            All validations complete
          </span>
        )}
      </div>

      {/* Right: Version & Help */}
      <div ref={rightRef} className="flex items-center gap-4">
        <span
          className="text-xs"
          style={{ color: "var(--ink-3)" }}
        >
          {version}
        </span>
        <a
          href="/help"
          className="flex items-center gap-1 text-xs transition-opacity hover:opacity-70"
          style={{ color: "var(--ink-2)" }}
        >
          <HelpCircle size={12} />
          <span>Help</span>
        </a>
      </div>
    </footer>
  );
}
