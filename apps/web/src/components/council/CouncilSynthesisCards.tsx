"use client";

interface SynthesisCard {
  id: string;
  type: string;
  title: string;
  summary: string;
  confidence: number;
  avatar_key?: string;
  concerns?: string[];
}

interface Props {
  synthesis: Record<string, unknown>;
  isLoading: boolean;
}

export function CouncilSynthesisCards({ synthesis, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-24 animate-pulse bg-slate-800/50 rounded-lg" />
        ))}
      </div>
    );
  }

  const cards: SynthesisCard[] = [];
  if (synthesis.cards) {
    (synthesis.cards as SynthesisCard[]).forEach((c: unknown) => {
      const card = c as SynthesisCard;
      cards.push({
        id: card.id ?? Math.random().toString(36),
        type: card.type ?? "recommendation",
        title: card.title ?? "Recommendation",
        summary: card.summary ?? "",
        confidence: card.confidence ?? 0.5,
        avatar_key: card.avatar_key,
        concerns: card.concerns,
      });
    });
  } else if (synthesis.recommendations) {
    const recs = synthesis.recommendations as Record<string, unknown>[];
    recs.forEach((r, i) => {
      cards.push({
        id: `rec-${i}`,
        type: "recommendation",
        title: (r.title as string) ?? `Recommendation ${i + 1}`,
        summary: (r.summary as string) ?? "",
        confidence: (r.confidence as number) ?? 0.5,
        avatar_key: r.avatar_key as string,
        concerns: r.concerns as string[],
      });
    });
  }

  if (cards.length === 0) {
    return (
      <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Synthesis</h3>
        <p className="text-slate-500 text-sm">No synthesis available yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-slate-300">Synthesis</h3>
      <div className="space-y-2">
        {cards.map((card) => (
          <div
            key={card.id}
            className="p-4 rounded-lg bg-slate-800/50 border border-violet-500/30 hover:border-violet-500/60 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <span className="text-xs font-medium text-violet-400 uppercase">{card.type}</span>
              {card.avatar_key && <span className="text-xs text-slate-500">{card.avatar_key}</span>}
            </div>
            <h4 className="text-sm font-medium text-slate-200 mb-1">{card.title}</h4>
            <p className="text-xs text-slate-400 leading-relaxed">{card.summary}</p>
            {card.concerns && card.concerns.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {card.concerns.map((concern, i) => (
                  <span
                    key={i}
                    className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30"
                  >
                    {concern}
                  </span>
                ))}
              </div>
            )}
            <div className="mt-3 flex items-center gap-2">
              <div className="flex-1 h-1 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-violet-500 rounded-full"
                  style={{ width: `${card.confidence * 100}%` }}
                />
              </div>
              <span className="text-xs text-slate-500">
                {card.confidence > 0 ? `${(card.confidence * 100).toFixed(0)}%` : "—"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
