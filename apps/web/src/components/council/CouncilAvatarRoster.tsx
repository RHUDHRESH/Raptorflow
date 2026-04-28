"use client";

import { CouncilPresenceState } from "@/lib/api";

interface Props {
  avatarKeys: string[];
  presenceStates?: CouncilPresenceState[];
  isLoading?: boolean;
}

const AVATAR_META: Record<string, { label: string; color: string; role: string }> = {
  strategist: { label: "Strategist", color: "var(--violet)", role: "Strategic Direction" },
  researcher: { label: "Researcher", color: "var(--blue)", role: "Evidence & Sources" },
  copywriter: { label: "Copywriter", color: "var(--amber)", role: "Language & Conversion" },
  growth_operator: { label: "Growth Operator", color: "var(--green)", role: "Execution Cadence" },
  analyst: { label: "Analyst", color: "var(--cyan)", role: "Signal & Metrics" },
  creative_director: { label: "Creative Director", color: "var(--pink)", role: "Creative Quality" },
  proof_collector: {
    label: "Proof Collector",
    color: "var(--orange)",
    role: "Proof & Substantiation",
  },
};

export function CouncilAvatarRoster({ avatarKeys, presenceStates = [], isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {Array.from({ length: Math.min(avatarKeys.length, 7) }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse bg-slate-800/50 rounded-lg" />
        ))}
      </div>
    );
  }

  if (avatarKeys.length === 0) {
    return (
      <div className="card-elevated p-4">
        <p className="mono-label text-slate-500">No avatars in roster</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
      {avatarKeys.map((key) => {
        const meta = AVATAR_META[key] ?? { label: key, color: "var(--ink-400)", role: "" };
        const presence = presenceStates.find((p) => p.avatar_id === key);
        const isActive = presence?.state === "active";
        return (
          <div
            key={key}
            className="card-elevated p-3 text-center border border-[var(--border)] relative"
          >
            {isActive && (
              <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-emerald-500" />
            )}
            <div
              className="w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center text-white text-xs font-bold"
              style={{ background: meta.color }}
            >
              {meta.label.charAt(0)}
            </div>
            <p className="text-xs font-medium">{meta.label}</p>
            <p className="mono-label text-slate-500 text-[9px] mt-0.5">{meta.role}</p>
            {presence && (
              <p className="mono-label text-slate-600 text-[8px] mt-1 uppercase">
                {presence.state}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
