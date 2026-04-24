import { prisma } from "@raptorflow/database";
import { qdrant, COLLECTION } from "@/lib/qdrant/client";
import { embedText } from "@/lib/qdrant/embed";

export type RippleType =
  | "foundation_save"
  | "campaign_created"
  | "campaign_evaluated"
  | "move_generated"
  | "council_complete"
  | "muse_exchange"
  | "task_complete";

export async function ingestRipple(params: {
  userId: string;
  type: RippleType;
  sourceId: string;
  content: string;
}): Promise<void> {
  try {
    const ripple = await prisma.ripple.create({
      data: {
        userId: params.userId,
        type: params.type,
        sourceId: params.sourceId,
        content: params.content,
        salience: 1.0,
        qdrantId: null,
        embeddedAt: null,
      },
    });

    const vector = await embedText(params.content);

    const pointId = `ripple_${ripple.id}`;
    await qdrant.upsert(COLLECTION, {
      wait: true,
      points: [
        {
          id: pointId,
          vector,
          payload: {
            rippleId: ripple.id,
            userId: params.userId,
            type: params.type,
            sourceId: params.sourceId,
            content: params.content,
            createdAt: ripple.createdAt.toISOString(),
          },
        },
      ],
    });

    await prisma.ripple.update({
      where: { id: ripple.id },
      data: { qdrantId: pointId, embeddedAt: new Date() },
    });
  } catch (err) {
    console.error("[ingestRipple] failed:", err);
  }
}
