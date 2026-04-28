"use client";

import { CouncilSynthesis } from "@/lib/api";

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
  synthesis: unknown;
  isLoading: boolean;
}

function isCouncilSynthesis(obj: unknown): obj is CouncilSynthesis {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "known_facts" in obj &&
    "strategic_recommendation" in obj
  );
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
  if (!synthesis || typeof synthesis !== "object") {
    return (
      <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Synthesis</h3>
        <p className="text-slate-500 text-sm">No synthesis available yet.</p>
      </div>
    );
  }

  const syn = synthesis as Record<string, unknown>;
  if (isCouncilSynthesis(synthesis)) {
    const s = synthesis as CouncilSynthesis;
    cards.push({
      id: "strategic_recommendation",
      type: "strategic_recommendation",
      title: "Strategic Recommendation",
      summary: s.strategic_recommendation,
      confidence: 0.9,
    });
    if (s.known_facts.length > 0) {
      cards.push({
        id: "known_facts",
        type: "known_facts",
        title: "Known Facts",
        summary: s.known_facts.join("; "),
        confidence: 0.85,
      });
    }
    if (s.assumptions.length > 0) {
      cards.push({
        id: "assumptions",
        type: "assumptions",
        title: "Assumptions",
        summary: s.assumptions.join("; "),
        confidence: 0.7,
      });
    }
    if (s.risks.length > 0) {
      cards.push({
        id: "risks",
        type: "risks",
        title: "Risks",
        summary: s.risks.join("; "),
        confidence: 0.75,
      });
    }
    if (s.next_actions.length > 0) {
      cards.push({
        id: "next_actions",
        type: "next_actions",
        title: "Next Actions",
        summary: s.next_actions.join("; "),
        confidence: 0.8,
      });
    }
    if (s.open_questions.length > 0) {
      cards.push({
        id: "open_questions",
        type: "open_questions",
        title: "Open Questions",
        summary: s.open_questions.join("; "),
        confidence: 0.5,
      });
    }
  } else if (Array.isArray(syn.cards)) {
    for (const item of syn.cards) {
      if (item && typeof item === "object") {
        const c = item as Record<string, unknown>;
        cards.push({
          id: typeof c.id === "string" ? c.id : Math.random().toString(36),
          type: typeof c.type === "string" ? c.type : "recommendation",
          title: typeof c.title === "string" ? c.title : "Recommendation",
          summary: typeof c.summary === "string" ? c.summary : "",
          confidence: typeof c.confidence === "number" ? c.confidence : 0.5,
          avatar_key: typeof c.avatar_key === "string" ? c.avatar_key : undefined,
          concerns: Array.isArray(c.concerns) ? (c.concerns as string[]) : undefined,
        });
      }
    }
  } else if (Array.isArray(syn.recommendations)) {
    for (let i = 0; i < syn.recommendations.length; i++) {
      const r = syn.recommendations[i];
      if (r && typeof r === "object") {
        const rec = r as Record<string, unknown>;
        cards.push({
          id: `rec-${i}`,
          type: "recommendation",
          title: typeof rec.title === "string" ? rec.title : `Recommendation ${i + 1}`,
          summary: typeof rec.summary === "string" ? rec.summary : "",
          confidence: typeof rec.confidence === "number" ? rec.confidence : 0.5,
          avatar_key: typeof rec.avatar_key === "string" ? rec.avatar_key : undefined,
          concerns: Array.isArray(rec.concerns) ? (rec.concerns as string[]) : undefined,
        });
      }
    }
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
