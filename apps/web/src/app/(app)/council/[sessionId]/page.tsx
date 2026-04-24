"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeftIcon } from "@radix-ui/react-icons";
import { councilApi } from "@/lib/api";
import { ApiError } from "@/lib/api";

interface Position {
  id: string;
  avatarKey: string;
  avatarName: string;
  avatarRole: string;
  position: string;
  confidence: number;
  createdAt: string;
}

interface Synthesis {
  verdict: string;
  rationale: string;
  immediate_actions: string[];
  watch_outs: string[];
  dissenting_view: string;
  confidence?: number;
}

const POLLING_INTERVAL_MS = 2000;

const TERMINAL_STATUSES = new Set([
  "positions_ready",
  "synthesized",
  "failed",
  "partial",
  "complete",
  "completed",
]);

export default function CouncilSessionPage(): React.ReactElement {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;

  const [status, setStatus] = React.useState<string>("pending");
  const [positions, setPositions] = React.useState<Position[]>([]);
  const [synthesis, setSynthesis] = React.useState<Synthesis | null>(null);
  const [connectionState, setConnectionState] = React.useState<"connecting" | "polling" | "complete" | "error">("connecting");
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const pollingRef = React.useRef<ReturnType<typeof setInterval> | null>(null);
  const isPollingRef = React.useRef<boolean>(false);
  const synthesisCalledRef = React.useRef<boolean>(false);

  const clearPolling = React.useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    isPollingRef.current = false;
  }, []);

  const fetchSessionAndMessages = React.useCallback(async () => {
    if (!sessionId || isPollingRef.current) return;
    
    try {
      isPollingRef.current = true;
      
      const [sessionData, messagesData] = await Promise.all([
        councilApi.getSession(sessionId),
        councilApi.getMessages(sessionId),
      ]);
      
      setStatus(sessionData.status);
      
      const normalizedPositions: Position[] = (messagesData as unknown as Array<{
        position_id: string;
        avatar_key: string;
        round_number: number;
        content: string;
        created_at: string;
      }>).map((msg) => ({
        id: msg.position_id,
        avatarKey: msg.avatar_key,
        avatarName: msg.avatar_key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        avatarRole: msg.avatar_key,
        position: msg.content,
        confidence: 0.5,
        createdAt: msg.created_at,
      }));
      
      setPositions(normalizedPositions);
      
      const isTerminal = TERMINAL_STATUSES.has(sessionData.status);
      if (isTerminal) {
        setConnectionState("complete");
        clearPolling();
        
        if (sessionData.status !== "failed" && !synthesisCalledRef.current) {
          synthesisCalledRef.current = true;
          try {
            const synthRes = await councilApi.synthesizeSession(sessionId);
            if (synthRes.synthesis) {
              setSynthesis({
                verdict: synthRes.synthesis.decision,
                rationale: synthRes.synthesis.rationale,
                immediate_actions: synthRes.synthesis.next_actions,
                watch_outs: synthRes.synthesis.risks,
                dissenting_view: "",
              });
            }
          } catch (synthErr) {
            console.error("Failed to fetch synthesis:", synthErr);
          }
        }
      } else {
        setConnectionState("polling");
      }
      
      setErrorMessage(null);
    } catch (err) {
      console.error("Polling error:", err);
      setConnectionState("error");
      setErrorMessage(err instanceof ApiError ? err.message : "Failed to load session");
      clearPolling();
    } finally {
      isPollingRef.current = false;
    }
  }, [sessionId, clearPolling]);

  const startPolling = React.useCallback(() => {
    clearPolling();
    setConnectionState("polling");
    pollingRef.current = setInterval(fetchSessionAndMessages, POLLING_INTERVAL_MS);
  }, [clearPolling, fetchSessionAndMessages]);

  React.useEffect(() => {
    if (!sessionId) return;
    
    fetchSessionAndMessages();
    startPolling();
    
    return () => {
      clearPolling();
    };
  }, [sessionId, fetchSessionAndMessages, startPolling, clearPolling]);

  const statusLabel = {
    pending: "Waiting…",
    generating: "Council deliberating…",
    synthesizing: "Strategist synthesizing…",
    complete: "Complete",
    failed: "Failed",
    running: "Council deliberating…",
    positions_ready: "Positions ready",
    synthesized: "Synthesized",
  }[status] ?? status;

  const progressPct = status === "generating" || status === "running" 
    ? Math.min((positions.length / 6) * 100, 100) 
    : status === "synthesizing" ? 90 
    : status === "positions_ready" || status === "synthesized" || status === "complete" ? 100 
    : 0;

  return (
    <div className="flex flex-col gap-8 py-2">
      <Link
        href="/council"
        className="flex w-fit items-center gap-2 hover:underline"
        style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)" }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Council Archive
      </Link>

      <div className="flex items-center gap-2">
        <div
          className="h-2 w-2 rounded-full"
          style={{
            background: connectionState === "polling" ? "var(--leaf-confirm)" : connectionState === "complete" ? "var(--muted-foreground)" : connectionState === "error" ? "var(--destructive)" : "var(--amber-war)",
            animation: connectionState === "polling" || connectionState === "connecting" ? "pulse 1.5s infinite" : undefined,
          }}
        />
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>
          {connectionState === "connecting" && "Loading…"}
          {connectionState === "polling" && `Polling — ${positions.length} positions`}
          {connectionState === "complete" && "Session complete"}
          {connectionState === "error" && "Connection lost — refresh to reconnect"}
        </span>
      </div>

      <div className="border border-[var(--border)] bg-[var(--card)]">
        <div className="border-b border-[var(--border)] p-6">
          {(status === "generating" || status === "running") && (
            <div>
              <div className="mb-2 flex justify-between text-sm" style={{ color: "var(--muted-foreground)", fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.12em" }}>
                <span>Council deliberating…</span>
                <span>{positions.length}/6</span>
              </div>
              <div className="h-2 w-full rounded-full" style={{ background: "var(--border)" }}>
                <div
                  className="h-2 rounded-full transition-all"
                  style={{ width: `${progressPct}%`, background: "var(--amber-war)" }}
                />
              </div>
            </div>
          )}
          {status === "synthesizing" && (
            <div style={{ color: "var(--amber-war)", fontFamily: "'JetBrains Mono', monospace", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.14em", animation: "pulse 1.5s infinite" }}>
              Strategist is synthesizing all positions…
            </div>
          )}
          {(status === "complete" || status === "positions_ready" || status === "synthesized") && (
            <div style={{ color: "var(--leaf-confirm)", fontFamily: "'JetBrains Mono', monospace", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.14em", fontWeight: 700 }}>
              Council complete — {positions.length} positions + synthesis ready
            </div>
          )}
          {status === "failed" && (
            <div style={{ color: "var(--destructive)", fontFamily: "'JetBrains Mono', monospace", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.14em" }}>
              Session failed
              {errorMessage && (
                <>
                  <div className="mt-2 text-xs font-normal" style={{ color: "var(--destructive)", textTransform: "none", letterSpacing: 0 }}>
                    {errorMessage}
                  </div>
                  <Link href="/foundation" className="mt-3 inline-block border border-[var(--destructive)] px-4 py-2 text-xs font-bold uppercase tracking-widest hover:opacity-80" style={{ color: "var(--destructive)" }}>
                    Complete Foundation
                  </Link>
                </>
              )}
            </div>
          )}
          {status === "pending" && (
            <div style={{ color: "var(--muted-foreground)", fontFamily: "'JetBrains Mono', monospace", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.14em" }}>
              Waiting for session to begin…
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 p-6 md:grid-cols-2 lg:grid-cols-3">
          {positions.map((position, index) => (
            <div
              key={position.id}
              className="border border-[var(--border)] p-4"
              style={{ animation: `fadeIn 0.3s ease-out ${index * 50}ms both` }}
            >
              <div className="mb-2 flex items-start justify-between">
                <div>
                  <div className="font-semibold text-sm" style={{ color: "var(--foreground)" }}>{position.avatarName}</div>
                  <div className="text-xs" style={{ color: "var(--muted-foreground)" }}>{position.avatarRole}</div>
                </div>
                <div className="text-xs" style={{ fontFamily: "'JetBrains Mono', monospace", color: "var(--muted-foreground)", background: "var(--border)", padding: "2px 6px", borderRadius: 4 }}>
                  {(position.confidence * 100).toFixed(0)}% confident
                </div>
              </div>
              <div className="mb-3 h-1 w-full rounded-full" style={{ background: "var(--border)" }}>
                <div className="h-1 rounded-full" style={{ width: `${position.confidence * 100}%`, background: "var(--amber-war)" }} />
              </div>
              <p className="text-sm leading-relaxed" style={{ color: "var(--foreground)" }}>{position.position}</p>
            </div>
          ))}

          {(status === "generating" || status === "running") && Array.from({ length: Math.max(0, 6 - positions.length) }).map((_, i) => (
            <div key={`ghost-${i}`} className="border border-dashed p-4" style={{ borderColor: "var(--border)", animation: "pulse 1.5s infinite" }}>
              <div className="mb-2 h-4 w-1/2 rounded" style={{ background: "var(--border)" }} />
              <div className="mb-4 h-3 w-1/3 rounded" style={{ background: "var(--border)" }} />
              <div className="space-y-2">
                <div className="h-3 rounded" style={{ background: "var(--border)" }} />
                <div className="h-3 w-5/6 rounded" style={{ background: "var(--border)" }} />
                <div className="h-3 w-4/6 rounded" style={{ background: "var(--border)" }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {synthesis && (
        <div className="border-t border-[var(--border)] pt-8">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full" style={{ background: "rgba(139,92,246,0.1)" }}>
              <span style={{ fontSize: 18 }}>⚡</span>
            </div>
            <div>
              <div className="font-bold" style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16 }}>The Strategist</div>
              <div className="text-xs" style={{ color: "var(--muted-foreground)" }}>Master synthesis</div>
            </div>
            {synthesis.confidence !== undefined && (
              <div className="ml-auto text-2xl font-bold" style={{ color: "var(--leaf-confirm)", fontFamily: "'JetBrains Mono', monospace" }}>
                {(synthesis.confidence * 10).toFixed(1)}/10
              </div>
            )}
          </div>

          <div className="mb-6 rounded-xl p-6" style={{ background: "rgba(139,92,246,0.05)", border: "1px solid rgba(139,92,246,0.2)" }}>
            <div className="mb-1 text-sm font-semibold" style={{ fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>Verdict</div>
            <div className="text-xl" style={{ fontFamily: "'DM Serif Display', serif" }}>{synthesis.verdict}</div>
          </div>

          {synthesis.rationale && (
            <p className="mb-6 text-sm leading-relaxed" style={{ color: "var(--muted-foreground)" }}>{synthesis.rationale}</p>
          )}

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {Array.isArray(synthesis.immediate_actions) && synthesis.immediate_actions.length > 0 && (
              <div>
                <div className="mb-3 font-semibold" style={{ fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: "0.14em", fontSize: 9 }}>Immediate Actions</div>
                <ol className="space-y-2">
                  {synthesis.immediate_actions.map((action, i) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <span className="font-bold" style={{ color: "var(--leaf-confirm)", fontFamily: "'JetBrains Mono', monospace" }}>{i + 1}.</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {Array.isArray(synthesis.watch_outs) && synthesis.watch_outs.length > 0 && (
              <div>
                <div className="mb-3 font-semibold" style={{ fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: "0.14em", fontSize: 9 }}>Watch-outs</div>
                <ul className="space-y-2">
                  {synthesis.watch_outs.map((risk, i) => (
                    <li key={i} className="flex gap-2 rounded p-2 text-sm" style={{ background: "rgba(234,179,8,0.08)" }}>
                      <span>⚠️</span>
                      <span style={{ color: "var(--amber-war)" }}>{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {synthesis.dissenting_view && (
            <details className="mt-4 cursor-pointer rounded-lg border p-4" style={{ borderColor: "var(--border)" }}>
              <summary className="text-sm font-medium" style={{ color: "var(--muted-foreground)" }}>Minority view (dissenting argument)</summary>
              <p className="mt-3 text-sm" style={{ color: "var(--muted-foreground)" }}>{synthesis.dissenting_view}</p>
            </details>
          )}
        </div>
      )}

      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      `}</style>
    </div>
  );
}
