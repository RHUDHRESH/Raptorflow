import { prisma } from "@raptorflow/database";
import { qdrant, COLLECTION } from "@/lib/qdrant/client";
import { embedText } from "@/lib/qdrant/embed";

const TYPE_WEIGHTS: Record<string, number> = {
  foundation_save: 1.5,
  council_complete: 1.4,
  campaign_evaluated: 1.3,
  move_generated: 1.2,
  campaign_created: 1.1,
  muse_exchange: 1.0,
  task_complete: 0.8,
};

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const seconds = Math.floor((now - then) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  const weeks = Math.floor(days / 7);
  return `${weeks}w ago`;
}

function recencyFactor(createdAt: string): number {
  const ageMs = Date.now() - new Date(createdAt).getTime();
  const ageHours = ageMs / (1000 * 60 * 60);
  if (ageHours < 24) return 1.0;
  if (ageHours < 24 * 7) return 0.5;
  return 0.1;
}

export interface CortexResult {
  ripples: Array<{
    content: string;
    type: string;
    salience: number;
    score: number;
    createdAt: string;
  }>;
  contextBlock: string;
}

export async function cortexSearch(params: {
  userId: string;
  query: string;
  limit?: number;
  minSalience?: number;
}): Promise<CortexResult> {
  const { userId, query, limit = 5, minSalience = 0.2 } = params;

  const queryVector = await embedText(query);

  const searchResults = await qdrant.search(COLLECTION, {
    vector: queryVector,
    limit: 10,
    filter: {
      must: [{ key: "userId", match: { value: userId } }],
    },
    with_payload: true,
  });

  if (searchResults.length === 0) {
    return { ripples: [], contextBlock: "" };
  }

  const qdrantIds = searchResults.map((r) => String(r.id));
  const rippleRows = await prisma.ripple.findMany({
    where: { id: { in: qdrantIds.map((id) => id.replace("ripple_", "")) } },
  });

  const rippleMap = new Map(rippleRows.map((r) => [r.id, r]));

  const scored = searchResults
    .map((result) => {
      const rippleId = String(result.id).replace("ripple_", "");
      const ripple = rippleMap.get(rippleId);
      if (!ripple) return null;

      const baseScore = result.score ?? 0;
      const recency = recencyFactor(ripple.createdAt.toISOString());
      const typeWeight = TYPE_WEIGHTS[ripple.type] ?? 1.0;
      const salienceScore = ripple.salience;

      const finalScore = baseScore * (1 + 0.3 * recency) * typeWeight * salienceScore;

      return {
        content: ripple.content,
        type: ripple.type,
        salience: ripple.salience,
        score: baseScore,
        finalScore,
        createdAt: ripple.createdAt.toISOString(),
        qdrantId: ripple.qdrantId,
      };
    })
    .filter((r): r is NonNullable<typeof r> => r !== null && r.finalScore >= minSalience)
    .sort((a, b) => b.finalScore - a.finalScore)
    .slice(0, limit);

  const contextBlock =
    scored.length > 0
      ? `Relevant memory context (most relevant first):\n${scored
          .map(
            (r, i) =>
              `[${i + 1}] (${r.type}, ${timeAgo(r.createdAt)}, relevance: ${r.score.toFixed(2)}): ${r.content}`,
          )
          .join("\n")}`
      : "";

  return {
    ripples: scored.map((r) => ({
      content: r.content,
      type: r.type,
      salience: r.salience,
      score: r.score,
      createdAt: r.createdAt,
    })),
    contextBlock,
  };
}
