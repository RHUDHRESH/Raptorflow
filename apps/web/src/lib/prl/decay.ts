import { prisma } from "@raptorflow/database";
import { qdrant, COLLECTION } from "@/lib/qdrant/client";

const HALF_LIVES: Record<string, number> = {
  foundation_save: 90,
  council_complete: 60,
  campaign_evaluated: 45,
  move_generated: 30,
  campaign_created: 30,
  muse_exchange: 14,
  task_complete: 7,
};

export async function decayRipples(userId: string): Promise<{
  processed: number;
  decayed: number;
  pruned: number;
}> {
  const ripples = await prisma.ripple.findMany({
    where: { userId, salience: { gt: 0.05 } },
  });

  let decayed = 0;
  let pruned = 0;
  const toUpdate: Array<{ id: string; newSalience: number }> = [];
  const toDelete: Array<{ id: string; qdrantId: string | null }> = [];

  for (const ripple of ripples) {
    const ageMs = Date.now() - ripple.createdAt.getTime();
    const ageDays = ageMs / (1000 * 60 * 60 * 24);
    const halfLife = HALF_LIVES[ripple.type] ?? 30;
    const newSalience = Math.max(0, ripple.salience * Math.pow(0.5, ageDays / halfLife));

    if (newSalience < 0.05) {
      toDelete.push({ id: ripple.id, qdrantId: ripple.qdrantId });
    } else {
      toUpdate.push({ id: ripple.id, newSalience });
    }
  }

  for (const update of toUpdate) {
    await prisma.ripple.update({
      where: { id: update.id },
      data: { salience: update.newSalience },
    });
    decayed++;
  }

  for (const del of toDelete) {
    if (del.qdrantId) {
      try {
        await qdrant.delete(COLLECTION, { points: [del.qdrantId] });
      } catch (err) {
        console.error(`[decay] Qdrant delete failed for ${del.qdrantId}:`, err);
      }
    }
    await prisma.ripple.delete({ where: { id: del.id } });
    pruned++;
  }

  return { processed: ripples.length, decayed, pruned };
}
