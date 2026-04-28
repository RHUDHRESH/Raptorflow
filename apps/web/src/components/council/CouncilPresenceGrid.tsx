"use client";

import { CouncilPresenceState } from "@/lib/api";

interface Props {
  presenceStates: CouncilPresenceState[];
  isLoading: boolean;
}

const AVATAR_COLORS: Record<string, string> = {
  muse: "var(--violet)",
  aperture: "var(--blue)",
  forge: "var(--amber)",
  lens: "var(--emerald)",
  nexus: "var(--cyan)",
  prism: "var(--rose)",
  axis: "var(--slate)",
};

const STATE_ICONS: Record<string, string> = {
  active: "●",
  idle: "○",
  thinking: "◐",
  waiting: "◎",
  challenged: "◆",
};

export function CouncilPresenceGrid({ presenceStates, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse bg-slate-800/50 rounded-lg" />
        ))}
      </div>
    );
  }

  if (presenceStates.length === 0) {
    return (
      <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Presence Grid</h3>
        <p className="text-slate-500 text-sm">No presence data yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-slate-300">Presence Grid</h3>
      <div className="grid grid-cols-2 gap-3">
        {presenceStates.map((state) => {
          const color = AVATAR_COLORS[state.avatar_id] ?? "var(--slate)";
          const icon = STATE_ICONS[state.state] ?? "○";
          return (
            <div
              key={state.presence_id}
              className="p-3 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-center gap-2 mb-2">
                <span style={{ color }}>{icon}</span>
                <span className="text-sm font-medium text-slate-200">{state.avatar_id}</span>
                <span className="ml-auto text-xs text-slate-500 uppercase">{state.state}</span>
              </div>
              <p className="text-xs text-slate-400 mb-1 line-clamp-1">
                {state.visible_summary || "No summary"}
              </p>
              {state.current_focus && (
                <p className="text-xs text-slate-500 truncate">Focus: {state.current_focus}</p>
              )}
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 h-1 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${(state.confidence ?? 0) * 100}%`, background: color }}
                  />
                </div>
                <span className="text-xs text-slate-500">
                  {((state.confidence ?? 0) * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
