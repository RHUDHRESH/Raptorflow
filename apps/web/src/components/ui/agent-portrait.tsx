"use client";

import * as React from "react";
import Image from "next/image";
import type { AgentConfig } from "@/lib/agents";
import { cn } from "@/lib/cn";

interface AgentPortraitProps {
  agent: AgentConfig;
  size?: number;           // px (default 48)
  showName?: boolean;
  showStatus?: boolean;
  status?: "idle" | "thinking" | "speaking" | "away";
  className?: string;
  onClick?: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  idle:     "var(--leaf-confirm)",
  thinking: "var(--indigo-muse)",
  speaking: "var(--amber-war)",
  away:     "var(--muted-foreground)",
};

/**
 * AgentPortrait
 * If agent.portrait is set → renders the real PNG from /public/agents/.
 * If agent.portrait is null → renders a brutalist monogram filler:
 *   a solid color rectangle with the 2-char initials in white mono.
 * Both variants support status dot, hover states, and click.
 */
export function AgentPortrait({
  agent,
  size = 48,
  showName = false,
  showStatus = false,
  status = "idle",
  className,
  onClick,
}: AgentPortraitProps): React.ReactElement {
  const fontSize = Math.max(9, Math.round(size * 0.28));
  const dotSize = Math.max(6, Math.round(size * 0.16));

  return (
    <div
      className={cn("flex flex-col items-center gap-1 select-none", onClick && "cursor-pointer", className)}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === "Enter" && onClick() : undefined}
      aria-label={agent.displayName}
    >
      {/* Portrait Container */}
      <div
        className="relative shrink-0"
        style={{ width: size, height: size }}
      >
        {agent.portrait ? (
          /* ── Real portrait ─────────────────────────────── */
          <Image
            src={agent.portrait}
            alt={agent.displayName}
            width={size}
            height={size}
            className="block object-cover"
            style={{ imageRendering: "pixelated" }} // preserve pixel art crispness
            priority={false}
            draggable={false}
          />
        ) : (
          /* ── Brutalist monogram filler ──────────────────── */
          <div
            className="flex items-center justify-center w-full h-full"
            style={{ background: agent.color }}
          >
            <span
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize,
                fontWeight: 700,
                color: "#ffffff",
                letterSpacing: "0.05em",
                userSelect: "none",
              }}
            >
              {agent.shortName}
            </span>
          </div>
        )}

        {/* ── Status dot (bottom-right corner) ─────── */}
        {showStatus && (
          <span
            className="absolute bottom-0 right-0 rounded-full border-2 border-[var(--background)]"
            style={{
              width: dotSize,
              height: dotSize,
              background: STATUS_COLORS[status] ?? STATUS_COLORS.idle,
            }}
          />
        )}

        {/* ── Speaking pulse ring ──────────────────── */}
        {status === "speaking" && (
          <span
            className="absolute inset-0 animate-ping opacity-30"
            style={{
              border: `2px solid ${agent.color}`,
              animationDuration: "1.2s",
            }}
          />
        )}
      </div>

      {/* Optional name label */}
      {showName && (
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 9,
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            color: "var(--muted-foreground)",
            maxWidth: size + 16,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {agent.shortName}
        </span>
      )}
    </div>
  );
}

/**
 * AgentPill — inline horizontal chip for lists, chat attribution, etc.
 */
export function AgentPill({
  agent,
  size = 20,
  status,
  className,
  onClick,
}: {
  agent: AgentConfig;
  size?: number;
  status?: "idle" | "thinking" | "speaking" | "away";
  className?: string;
  onClick?: () => void;
}): React.ReactElement {
  return (
    <div
      className={cn(
        "agent-pill",
        onClick && "cursor-pointer hover:border-[var(--foreground)] transition-colors",
        className
      )}
      onClick={onClick}
      role={onClick ? "button" : undefined}
    >
      {/* Mini avatar */}
      <div
        className="agent-pill-avatar shrink-0"
        style={{
          width: size,
          height: size,
          background: agent.portrait ? undefined : agent.color,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {agent.portrait ? (
          <Image
            src={agent.portrait}
            alt={agent.displayName}
            width={size}
            height={size}
            style={{ imageRendering: "pixelated", objectFit: "cover" }}
          />
        ) : (
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, fontWeight: 700, color: "#fff" }}>
            {agent.shortName}
          </span>
        )}
      </div>

      <span className="agent-pill-name">{agent.displayName}</span>

      {status && (
        <span
          className="agent-pill-dot shrink-0"
          style={{ background: STATUS_COLORS[status] ?? STATUS_COLORS.idle }}
        />
      )}
    </div>
  );
}
