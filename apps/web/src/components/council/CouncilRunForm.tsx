"use client";

import { useState } from "react";
import { CreateCouncilOrchestrationRequest } from "@/lib/api";

const AVATAR_OPTIONS = [
  { key: "strategist", label: "Strategist", color: "var(--violet)" },
  { key: "researcher", label: "Researcher", color: "var(--blue)" },
  { key: "copywriter", label: "Copywriter", color: "var(--amber)" },
  { key: "growth_operator", label: "Growth Operator", color: "var(--green)" },
  { key: "analyst", label: "Analyst", color: "var(--cyan)" },
  { key: "creative_director", label: "Creative Director", color: "var(--pink)" },
  { key: "proof_collector", label: "Proof Collector", color: "var(--orange)" },
];

interface Props {
  onSubmit: (body: CreateCouncilOrchestrationRequest) => void;
  isPending: boolean;
}

export function CouncilRunForm({ onSubmit, isPending }: Props) {
  const [requestSummary, setRequestSummary] = useState("");
  const [contextSummary, setContextSummary] = useState("");
  const [selectedAvatars, setSelectedAvatars] = useState<string[]>(
    AVATAR_OPTIONS.map((a) => a.key),
  );
  const [maxChallengeRounds, setMaxChallengeRounds] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (requestSummary.length < 10) {
      setError("Request summary must be at least 10 characters");
      return;
    }
    if (selectedAvatars.length === 0) {
      setError("Select at least one avatar");
      return;
    }

    onSubmit({
      request_summary: requestSummary,
      context_summary: contextSummary,
      mode: "dry_run",
      requested_avatar_keys: selectedAvatars,
      max_challenge_rounds: maxChallengeRounds,
    });
  };

  const toggleAvatar = (key: string) => {
    setSelectedAvatars((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key],
    );
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="card-elevated p-6 space-y-5 border border-[var(--border)]"
    >
      <div>
        <p className="eyebrow mb-1">Summon Council</p>
        <h3 className="h3">New Orchestration Run</h3>
      </div>

      <div className="space-y-2">
        <label className="mono-label text-[var(--ink-500)]">Request Summary *</label>
        <textarea
          value={requestSummary}
          onChange={(e) => setRequestSummary(e.target.value)}
          placeholder="e.g. Create a founder-led campaign direction for RaptorFlow"
          className="w-full min-h-[80px] p-3 bg-[var(--paper-150)] border border-[var(--border)] rounded-[var(--radius)] text-sm resize-y focus:outline-none focus:border-[var(--primary)]"
          maxLength={2000}
        />
        <p className="mono-label text-[var(--ink-400)] text-right">{requestSummary.length}/2000</p>
      </div>

      <div className="space-y-2">
        <label className="mono-label text-[var(--ink-500)]">Context Summary</label>
        <textarea
          value={contextSummary}
          onChange={(e) => setContextSummary(e.target.value)}
          placeholder="ICP: SMB founders. Pain: scattered marketing. Wedge: daily operating rhythm."
          className="w-full min-h-[60px] p-3 bg-[var(--paper-150)] border border-[var(--border)] rounded-[var(--radius)] text-sm resize-y focus:outline-none focus:border-[var(--primary)]"
          maxLength={8000}
        />
      </div>

      <div className="space-y-2">
        <label className="mono-label text-[var(--ink-500)]">Avatar Roster</label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {AVATAR_OPTIONS.map((avatar) => (
            <label
              key={avatar.key}
              className="flex items-center gap-2 p-2 rounded-[var(--radius-sm)] border cursor-pointer transition-all hover:bg-[var(--paper-150)]"
              style={{
                borderColor: selectedAvatars.includes(avatar.key) ? avatar.color : "var(--border)",
                background: selectedAvatars.includes(avatar.key)
                  ? `${avatar.color}08`
                  : "transparent",
              }}
            >
              <input
                type="checkbox"
                checked={selectedAvatars.includes(avatar.key)}
                onChange={() => toggleAvatar(avatar.key)}
                className="accent-[var(--primary)]"
              />
              <span className="text-xs font-medium">{avatar.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="mono-label text-[var(--ink-500)]">Challenge Rounds</label>
        <select
          value={maxChallengeRounds}
          onChange={(e) => setMaxChallengeRounds(Number(e.target.value))}
          className="p-2 bg-[var(--paper-150)] border border-[var(--border)] rounded-[var(--radius)] text-sm focus:outline-none focus:border-[var(--primary)]"
        >
          <option value={0}>0 — No challenges</option>
          <option value={1}>1 — Single round (default)</option>
          <option value={2}>2 — Two rounds max</option>
        </select>
      </div>

      {error && (
        <div
          className="p-3 rounded-[var(--radius-sm)] text-sm"
          style={{ background: "rgba(239,68,68,0.08)", color: "var(--destructive)" }}
        >
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isPending}
        className="btn-mono h-12 px-6 w-full disabled:opacity-50"
      >
        {isPending ? "Summoning Council..." : "Summon Council"}
      </button>
    </form>
  );
}
