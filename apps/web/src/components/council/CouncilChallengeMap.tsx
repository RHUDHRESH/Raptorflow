"use client";

import { CouncilDebateEvent, CouncilChallengeContent } from "@/lib/api";

interface Props {
  debateEvents: CouncilDebateEvent[];
}

const EVENT_STYLES: Record<string, { border: string; bg: string; label: string }> = {
  challenge: { border: "border-amber-500", bg: "bg-amber-500/10", label: "Challenge" },
  inquiry: { border: "border-blue-500", bg: "bg-blue-500/10", label: "Inquiry" },
  objection: { border: "border-red-500", bg: "bg-red-500/10", label: "Objection" },
  support: { border: "border-emerald-500", bg: "bg-emerald-500/10", label: "Support" },
  synthesis: { border: "border-violet-500", bg: "bg-violet-500/10", label: "Synthesis" },
};

export function CouncilChallengeMap({ debateEvents }: Props) {
  const challengeEvents = debateEvents.filter(
    (e) =>
      e.event_type === "challenge" ||
      e.event_type === "inquiry" ||
      e.event_type === "objection" ||
      e.event_type === "support" ||
      e.event_type === "synthesis",
  );

  if (challengeEvents.length === 0) {
    return (
      <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Challenge Map</h3>
        <p className="text-slate-500 text-sm">No challenges recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-slate-300">Challenge Map</h3>
      <div className="space-y-2">
        {challengeEvents.map((event) => {
          const style = EVENT_STYLES[event.event_type] ?? EVENT_STYLES.challenge;
          const rawContent =
            event.content && typeof event.content === "object"
              ? (event.content as CouncilChallengeContent)
              : null;
          const contentSummary =
            rawContent?.summary ?? rawContent?.topic ?? event.stance ?? "No summary";
          return (
            <div
              key={event.debate_event_id}
              className={`p-3 rounded-lg border ${style.border} ${style.bg}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-slate-200 uppercase">{style.label}</span>
                <span className="text-xs text-slate-500">
                  {event.speaker_avatar_id ?? "?"} → {event.target_avatar_id ?? "?"}
                </span>
              </div>
              <p className="text-xs text-slate-300">{contentSummary}</p>
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 h-1 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-slate-400 rounded-full"
                    style={{ width: `${(event.confidence ?? 0) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-slate-500">
                  {((event.confidence ?? 0) * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
