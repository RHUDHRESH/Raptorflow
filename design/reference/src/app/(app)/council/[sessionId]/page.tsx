"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeftIcon,
  AvatarIcon,
  ClockIcon,
  ChevronDownIcon,
} from "@radix-ui/react-icons";
import { AGENTS } from "@/lib/agents";
import { AgentPortrait } from "@/components/ui/agent-portrait";
import { AgentPill } from "@/components/ui/agent-portrait";

/* ─── Mock transcript data ────────────────────────────────────── */
const MOCK_ROUNDS = [
  {
    round: 1,
    label: "Opening Positions",
    messages: [
      {
        agentKey: "strategist",
        type: "synthesis",
        content: "We have a positioning gap. Diya Organics is messaging on ingredients, but the ICP responds to outcomes. The question is whether we lead with clinical proof or emotional resonance.",
      },
      {
        agentKey: "ogilvy",
        type: "position",
        content: "Research always precedes creativity. We need to know what the customer already believes about organic skincare before we choose a creative angle. Run a survey first.",
      },
      {
        agentKey: "vaynerchuk",
        type: "challenge",
        content: "We don't have time for surveys. Instagram is moving. The answer is in the comments on our top 3 posts — I can read the sentiment in 20 minutes.",
      },
      {
        agentKey: "godin",
        type: "position",
        content: "Both of you are right and missing the point. The ICP doesn't want skincare — they want to feel like the kind of person who uses conscious skincare. Lead with identity.",
      },
    ],
  },
  {
    round: 2,
    label: "Evidence Exchange",
    messages: [
      {
        agentKey: "patel",
        type: "position",
        content: "Data check: branded search for 'organic skincare India' is up 22% MoM. The demand exists. The question is which message captures it. Godin's identity angle tests better in A/B on awareness campaigns.",
      },
      {
        agentKey: "ogilvy",
        type: "updated",
        content: "Updating my position. If Patel's data shows identity resonates, we build the headline around aspiration, then validate with the ingredient proof as the hero detail in copy.",
      },
      {
        agentKey: "cialdini",
        type: "position",
        content: "Social proof is the missing lever. The ICP needs to see people like them using this product. Testimonials, ideally video, with specific before/after outcomes. Not celebrity — peer.",
      },
    ],
  },
  {
    round: 3,
    label: "Strategist Synthesis",
    messages: [
      {
        agentKey: "strategist",
        type: "synthesis",
        content: "Synthesis: Lead with identity (Godin/Ogilvy updated), anchor with peer social proof (Cialdini), and use Patel's search data to validate timing. Move 3 creative brief: 'Conscious Skin. Confident Identity.' — brief Bernbach on execution. Council is adjourned.",
      },
    ],
  },
];

const MOCK_META = {
  sessionType:  "council_war_room",
  status:       "completed",
  duration:     "34m 12s",
  agentCount:   8,
  modelUsed:    "Gemini 1.5 Pro",
  tokenCost:    "~18,400 tokens",
  createdAt:    new Date(Date.now() - 86400000).toISOString(),
};

const MOCK_STANCES: Record<string, string> = {
  strategist:   "synthesis",
  ogilvy:       "updated",
  vaynerchuk:   "challenged",
  godin:        "agreed",
  patel:        "agreed",
  cialdini:     "agreed",
};

/* ─── Message Card ────────────────────────────────────────────── */
function MessageCard({
  agentKey,
  type,
  content,
}: {
  agentKey: string;
  type: string;
  content: string;
}): React.ReactElement {
  const config = AGENTS.find((a) => a.key === agentKey);
  const isSynthesis = type === "synthesis";

  if (isSynthesis) {
    return (
      <div
        className="w-full px-6 py-5"
        style={{ background: "var(--foreground)", color: "var(--background)" }}
      >
        <div className="flex items-center gap-3 mb-4">
          {config && <AgentPortrait agent={config} size={32} />}
          <div>
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", opacity: 0.5 }}>
              Strategist Synthesis
            </p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 600, color: "var(--primary-foreground)", marginTop: 2 }}>
              {config?.displayName ?? agentKey}
            </p>
          </div>
        </div>
        <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 18, lineHeight: 1.5, fontStyle: "italic" }}>
          &ldquo;{content}&rdquo;
        </p>
      </div>
    );
  }

  const typeStyles: Record<string, { label: string; color: string }> = {
    position:  { label: "Position",  color: "var(--agent-" + agentKey + ", var(--muted-foreground))" },
    challenge: { label: "Challenge", color: "var(--signal-red)" },
    updated:   { label: "Updated",   color: "var(--amber-war)" },
  };
  const ts = typeStyles[type] ?? typeStyles.position;

  return (
    <div className="flex items-start gap-4">
      {/* Color stripe */}
      <div className="w-0.5 self-stretch shrink-0" style={{ background: config?.color ?? "var(--border)", minHeight: 60 }} />

      {config && (
        <AgentPortrait agent={config} size={32} className="shrink-0 mt-1" />
      )}

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 600, color: "var(--foreground)" }}>
            {config?.displayName ?? agentKey}
          </span>
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 8,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: ts.color,
              border: `1px solid ${ts.color}`,
              padding: "1px 5px",
            }}
          >
            {ts.label}
          </span>
        </div>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, lineHeight: 1.6, color: "var(--foreground)", margin: 0 }}>
          {content}
        </p>
      </div>
    </div>
  );
}

/* ─── Session Detail Page ──────────────────────────────────────── */
export default function CouncilSessionPage(): React.ReactElement {
  const params = useParams();
  const sessionId = params.sessionId as string;

  const meta = MOCK_META;

  return (
    <div className="flex flex-col gap-0 py-2">
      {/* ── Back nav ──────────────────────────────────── */}
      <Link
        href="/council"
        className="flex items-center gap-2 mb-8 hover:underline w-fit"
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: "0.16em",
          color: "var(--muted-foreground)",
        }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Council Archive
      </Link>

      {/* ── Split layout ──────────────────────────────── */}
      <div className="grid xl:grid-cols-[1fr_320px] gap-8 items-start">

        {/* ── LEFT: Transcript ──────────────────────── */}
        <div className="border-2 border-[var(--foreground)]" style={{ background: "var(--card)" }}>

          {/* Session header */}
          <div className="border-b-2 border-[var(--foreground)] p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.18em",
                  color: "var(--muted-foreground)",
                  marginBottom: 8,
                }}>
                  {meta.sessionType.replace(/_/g, " ")}
                </p>
                <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 32, margin: 0, lineHeight: 1.1 }}>
                  Diya Organics Q2
                </h1>
              </div>
              <div
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  background: "var(--leaf-confirm-dim)",
                  color: "var(--leaf-confirm)",
                  border: "1px solid var(--leaf-confirm)",
                  padding: "4px 10px",
                }}
              >
                {meta.status}
              </div>
            </div>
          </div>

          {/* Rounds */}
          <div className="divide-y divide-[var(--border)]">
            {MOCK_ROUNDS.map((round) => (
              <div key={round.round}>
                {/* Round divider */}
                <div
                  className="flex items-center gap-3 px-6 py-3"
                  style={{ background: "var(--muted)" }}
                >
                  <div className="h-px flex-1" style={{ background: "var(--border)" }} />
                  <span style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 9,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.2em",
                    color: "var(--muted-foreground)",
                    whiteSpace: "nowrap",
                  }}>
                    — ROUND {round.round}: {round.label} —
                  </span>
                  <div className="h-px flex-1" style={{ background: "var(--border)" }} />
                </div>

                {/* Messages in round */}
                <div className="divide-y divide-[var(--border)]">
                  {round.messages.map((msg, i) => (
                    <div key={i} className={msg.type === "synthesis" ? "" : "p-6"}>
                      <MessageCard {...msg} />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── RIGHT: Intelligence Panel ──────────────── */}
        <div className="space-y-4 xl:sticky xl:top-6">

          {/* Session metadata card */}
          <div
            className="border border-[var(--border)] divide-y divide-[var(--border)]"
            style={{ background: "var(--card)" }}
          >
            <div className="px-4 py-3">
              <p style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                color: "var(--muted-foreground)",
              }}>
                Session Intelligence
              </p>
            </div>
            {[
              { label: "Type",       value: meta.sessionType.replace(/_/g, " ") },
              { label: "Duration",   value: meta.duration },
              { label: "Agents",     value: `${meta.agentCount} participating` },
              { label: "Model",      value: meta.modelUsed },
              { label: "Tokens",     value: meta.tokenCost },
              { label: "Date",       value: new Date(meta.createdAt).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) },
            ].map((row) => (
              <div key={row.label} className="flex justify-between items-center px-4 py-2.5">
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted-foreground)" }}>
                  {row.label}
                </span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 600, color: "var(--foreground)" }}>
                  {row.value}
                </span>
              </div>
            ))}
          </div>

          {/* Agent stances card */}
          <div
            className="border border-[var(--border)]"
            style={{ background: "var(--card)" }}
          >
            <div className="px-4 py-3 border-b border-[var(--border)]">
              <p style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                color: "var(--muted-foreground)",
              }}>
                Agent Stances
              </p>
            </div>
            <div className="divide-y divide-[var(--border)]">
              {Object.entries(MOCK_STANCES).map(([key, stance]) => {
                const config = AGENTS.find((a) => a.key === key);
                if (!config) return null;
                return (
                  <div key={key} className="flex items-center justify-between px-4 py-2.5">
                    <AgentPill agent={config} size={18} />
                    <span
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 8,
                        fontWeight: 700,
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        color:
                          stance === "agreed"    ? "var(--leaf-confirm)" :
                          stance === "challenged" ? "var(--signal-red)" :
                          stance === "updated"   ? "var(--amber-war)" :
                          stance === "synthesis" ? "var(--foreground)" :
                          "var(--muted-foreground)",
                      }}
                    >
                      {stance}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* CTA */}
          <Link
            href="/muse"
            className="flex items-center justify-center gap-2 py-3 border border-[var(--border)] hover:border-[var(--foreground)] hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all w-full"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "var(--foreground)",
            }}
          >
            Ask Muse about this session
          </Link>
        </div>
      </div>
    </div>
  );
}
