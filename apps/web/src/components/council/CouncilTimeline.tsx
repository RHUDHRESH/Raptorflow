"use client";

import { CouncilAvatarTurn, AvatarDebateEvent } from "@/lib/api";

interface Props {
  turns: CouncilAvatarTurn[];
  debateEvents: AvatarDebateEvent[];
  isLoading: boolean;
}

const TURN_TYPE_COLORS: Record<string, string> = {
  instinct: "var(--violet)",
  position: "var(--blue)",
  challenge: "var(--destructive)",
};

const EVENT_TYPE_LABELS: Record<string, string> = {
  instinct: "Forming Instinct",
  position: "Position",
  challenge: "Challenge",
  proof_review: "Proof Review",
};

export function CouncilTimeline({ turns, debateEvents, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-16 animate-pulse bg-[var(--paper-150)] rounded-[var(--radius)]"
          />
        ))}
      </div>
    );
  }

  const positionEvents = debateEvents.filter((e) => e.eventType === "position");
  const challengeEvents = debateEvents.filter((e) => e.eventType === "challenge");

  if (positionEvents.length === 0 && challengeEvents.length === 0 && turns.length === 0) {
    return (
      <div className="card-elevated p-6 text-center">
        <p className="mono-label text-[var(--ink-400)]">No events yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {positionEvents.length > 0 && (
        <div>
          <h4 className="mono-label text-[var(--ink-500)] mb-3">Positions</h4>
          <div className="space-y-2">
            {positionEvents.map((event) => (
              <div
                key={event.debateEventId}
                className="card-elevated p-4 border border-[var(--border)]"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-2 h-2 rounded-full" style={{ background: "var(--blue)" }} />
                  <span className="text-xs font-medium">{event.speakerAvatarId ?? "Unknown"}</span>
                  <span className="mono-label text-[var(--ink-400)] text-[10px]">
                    {event.eventType}
                  </span>
                  {event.confidence > 0 && (
                    <span className="mono-label text-[var(--ink-400)] text-[10px] ml-auto">
                      {(event.confidence * 100).toFixed(0)}% confident
                    </span>
                  )}
                </div>
                <div className="text-xs text-[var(--ink-600)] leading-relaxed">
                  {renderContent(event.content)}
                </div>
                <details className="mt-2">
                  <summary className="mono-label text-[var(--ink-300)] text-[9px] cursor-pointer">
                    Raw JSON
                  </summary>
                  <pre className="mt-1 p-2 bg-[var(--paper-150)] rounded text-[9px] overflow-x-auto max-h-32">
                    {JSON.stringify(event.content, null, 2)}
                  </pre>
                </details>
              </div>
            ))}
          </div>
        </div>
      )}

      {challengeEvents.length > 0 && (
        <div>
          <h4 className="mono-label text-[var(--ink-500)] mb-3">Challenges</h4>
          <div className="space-y-2">
            {challengeEvents.map((event) => (
              <div
                key={event.debateEventId}
                className="card-elevated p-4 border"
                style={{ borderColor: "rgba(239,68,68,0.2)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ background: "var(--destructive)" }}
                  />
                  <span className="text-xs font-medium">{event.speakerAvatarId ?? "?"}</span>
                  <span className="mono-label text-[var(--ink-400)] text-[10px]">→</span>
                  <span className="text-xs font-medium">{event.targetAvatarId ?? "?"}</span>
                  <span className="mono-label text-[var(--ink-400)] text-[10px] ml-auto">
                    {(event.confidence * 100).toFixed(0)}% confident
                  </span>
                </div>
                <p className="text-xs text-[var(--ink-600)] leading-relaxed">
                  {event.stance ?? "No reason provided"}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {turns.length > 0 && (
        <div>
          <h4 className="mono-label text-[var(--ink-500)] mb-3">Avatar Turns</h4>
          <div className="space-y-1">
            {turns.map((turn) => (
              <div
                key={turn.turn_id}
                className="flex items-center gap-3 p-2 rounded-[var(--radius-sm)] bg-[var(--paper-100)]"
              >
                <span
                  className="w-1.5 h-1.5 rounded-full"
                  style={{
                    background:
                      turn.status === "completed" ? "var(--leaf-confirm)" : "var(--ink-400)",
                  }}
                />
                <span className="text-xs font-medium w-28 truncate">{turn.avatar_key}</span>
                <span className="mono-label text-[var(--ink-400)] text-[10px]">
                  {turn.turn_type}
                </span>
                <span className="mono-label text-[var(--ink-400)] text-[10px] ml-auto">
                  #{turn.sequence_number}
                </span>
                <span
                  className="mono-label text-[10px]"
                  style={{
                    color: turn.status === "completed" ? "var(--leaf-confirm)" : "var(--ink-400)",
                  }}
                >
                  {turn.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function renderContent(content: Record<string, unknown>): React.ReactNode {
  const text = content.text as string | undefined;
  const dominantConcern = content.dominant_concern as string | undefined;
  const challengeReason = content.challenge_reason as string | undefined;
  const strategicConcern = content.strategic_concern as string | undefined;
  const evidenceConcern = content.evidence_concern as string | undefined;
  const languageConcern = content.language_concern as string | undefined;
  const executionConcern = content.execution_concern as string | undefined;
  const measurementConcern = content.measurement_concern as string | undefined;
  const creativeConcern = content.creative_concern as string | undefined;
  const proofConcern = content.proof_concern as string | undefined;

  return (
    <>
      {text && <p className="mb-1">{text}</p>}
      {dominantConcern && <p className="mb-1">{dominantConcern}</p>}
      {challengeReason && <p className="mb-1">{challengeReason}</p>}
      {strategicConcern && <p className="mb-1">Strategic: {strategicConcern}</p>}
      {evidenceConcern && <p className="mb-1">Evidence: {evidenceConcern}</p>}
      {languageConcern && <p className="mb-1">Language: {languageConcern}</p>}
      {executionConcern && <p className="mb-1">Execution: {executionConcern}</p>}
      {measurementConcern && <p className="mb-1">Measurement: {measurementConcern}</p>}
      {creativeConcern && <p className="mb-1">Creative: {creativeConcern}</p>}
      {proofConcern && <p className="mb-1">Proof: {proofConcern}</p>}
    </>
  );
}
