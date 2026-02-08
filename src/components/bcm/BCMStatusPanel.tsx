"use client";

import { useEffect } from "react";
import { useBCMStore } from "@/stores/bcmStore";

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return "Never";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function statusBadge(
  createdAt: string | null,
  manifest: unknown
): { label: string; color: string } {
  if (!manifest) return { label: "MISSING", color: "#ef4444" };
  if (!createdAt) return { label: "UNKNOWN", color: "#6b7280" };
  const days = (Date.now() - new Date(createdAt).getTime()) / 86400000;
  if (days > 7) return { label: "STALE", color: "#f59e0b" };
  return { label: "ACTIVE", color: "#22c55e" };
}

export default function BCMStatusPanel({
  workspaceId,
}: {
  workspaceId: string;
}) {
  const {
    manifest,
    version,
    checksum,
    createdAt,
    completionPct,
    isLoading,
    isRebuilding,
    error,
    fetchBCM,
    rebuildBCM,
  } = useBCMStore();

  useEffect(() => {
    if (workspaceId) fetchBCM(workspaceId);
  }, [workspaceId, fetchBCM]);

  const badge = statusBadge(createdAt, manifest);
  const meta = manifest?.meta;

  return (
    <div
      style={{
        border: "1px solid var(--border, #27272a)",
        borderRadius: "var(--spacing-sm, 8px)",
        padding: "var(--spacing-lg, 16px)",
        background: "var(--card, #09090b)",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "var(--spacing-md, 12px)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-sm, 8px)" }}>
          <h3 style={{ margin: 0, fontSize: "14px", fontWeight: 600 }}>
            Business Context
          </h3>
          <span
            style={{
              fontSize: "10px",
              fontWeight: 700,
              padding: "2px 6px",
              borderRadius: "4px",
              background: badge.color + "20",
              color: badge.color,
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            {badge.label}
          </span>
        </div>
        <button
          onClick={() => workspaceId && rebuildBCM(workspaceId)}
          disabled={isRebuilding || isLoading}
          style={{
            fontSize: "12px",
            padding: "4px 10px",
            borderRadius: "4px",
            border: "1px solid var(--border, #27272a)",
            background: "transparent",
            color: "var(--foreground, #fafafa)",
            cursor: isRebuilding ? "wait" : "pointer",
            opacity: isRebuilding ? 0.5 : 1,
          }}
        >
          {isRebuilding ? "Rebuilding..." : "Rebuild"}
        </button>
      </div>

      {/* Loading / Error states */}
      {isLoading && (
        <p style={{ fontSize: "12px", color: "#6b7280" }}>Loading BCM...</p>
      )}
      {error && !isLoading && (
        <p style={{ fontSize: "12px", color: "#ef4444" }}>{error}</p>
      )}

      {/* Content */}
      {manifest && !isLoading && (
        <>
          {/* Progress bar */}
          <div
            style={{
              height: "4px",
              borderRadius: "2px",
              background: "#27272a",
              marginBottom: "var(--spacing-md, 12px)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${completionPct}%`,
                background: completionPct === 100 ? "#22c55e" : "#3b82f6",
                borderRadius: "2px",
                transition: "width 0.3s ease",
              }}
            />
          </div>

          {/* Metrics grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "var(--spacing-sm, 8px)",
              fontSize: "12px",
            }}
          >
            <div>
              <div style={{ color: "#6b7280", marginBottom: "2px" }}>Version</div>
              <div style={{ fontWeight: 600 }}>v{version}</div>
            </div>
            <div>
              <div style={{ color: "#6b7280", marginBottom: "2px" }}>Updated</div>
              <div style={{ fontWeight: 600 }}>{timeAgo(createdAt)}</div>
            </div>
            <div>
              <div style={{ color: "#6b7280", marginBottom: "2px" }}>Tokens</div>
              <div style={{ fontWeight: 600 }}>~{meta?.token_estimate ?? 0}</div>
            </div>
            <div>
              <div style={{ color: "#6b7280", marginBottom: "2px" }}>ICPs</div>
              <div style={{ fontWeight: 600 }}>{meta?.icps_count ?? 0}</div>
            </div>
            <div>
              <div style={{ color: "#6b7280", marginBottom: "2px" }}>Competitors</div>
              <div style={{ fontWeight: 600 }}>{meta?.competitors_count ?? 0}</div>
            </div>
            <div>
              <div style={{ color: "#6b7280", marginBottom: "2px" }}>Checksum</div>
              <div
                style={{ fontWeight: 600, fontFamily: "monospace", fontSize: "11px" }}
              >
                {checksum?.slice(0, 8) ?? "—"}
              </div>
            </div>
          </div>

          {/* Company one-liner */}
          {manifest.messaging?.one_liner && (
            <div
              style={{
                marginTop: "var(--spacing-md, 12px)",
                padding: "var(--spacing-sm, 8px)",
                borderRadius: "4px",
                background: "#18181b",
                fontSize: "12px",
                color: "#a1a1aa",
                fontStyle: "italic",
              }}
            >
              {manifest.messaging.one_liner}
            </div>
          )}
        </>
      )}
    </div>
  );
}
