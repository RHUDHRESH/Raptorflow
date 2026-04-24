import { prisma } from "@raptorflow/database";
import { broadcast, channels } from "@/lib/pusher/server";
import { harnessPrompt } from "@/lib/harness/buildPrompt";
import { convergeFast } from "@/lib/bedrock";

interface NudgeData {
  userId: string;
  type: string;
  title: string;
  body: string;
  cta?: string;
  ctaHref?: string;
  priority: number;
  isDismissed: boolean;
  isActioned: boolean;
  expiresAt: Date | null;
  trigger: string;
}

export async function generateNudges(userId: string): Promise<unknown[]> {
  const [campaigns, councilSessions, recentRipples, existingNudges] = await Promise.all([
    prisma.campaign.findMany({
      where: { clerkUserId: userId },
      include: { moves: { include: { tasks: true } } },
      orderBy: { updatedAt: "desc" },
      take: 5,
    }),
    prisma.councilSession.findMany({
      where: { clerkUserId: userId, status: "complete" },
      orderBy: { createdAt: "desc" },
      take: 3,
    }),
    prisma.ripple.findMany({
      where: { userId, createdAt: { gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } },
      orderBy: { createdAt: "desc" },
    }),
    prisma.nudge.findMany({
      where: { userId, isDismissed: false, isActioned: false },
      select: { trigger: true },
    }),
  ]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const activeTriggers = new Set(existingNudges.map((n: any) => n.trigger));
  const nudgesToCreate: NudgeData[] = [];

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const campaignsWithNoMoves = (campaigns as any[]).filter(
    (c: any) => c.moves.length === 0 && c.status === "active",
  );
  for (const campaign of campaignsWithNoMoves) {
    const trigger = `no_moves_${campaign.id}`;
    if (!activeTriggers.has(trigger)) {
      nudgesToCreate.push({
        userId,
        type: "action",
        title: `"${campaign.title}" has no move ladder yet`,
        body: "This campaign has been evaluated but has no execution moves. Generate the move ladder to turn the strategy into action.",
        cta: "Generate moves",
        ctaHref: `/app/campaigns/${campaign.id}`,
        priority: 7,
        isDismissed: false,
        isActioned: false,
        expiresAt: null,
        trigger,
      });
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const stalledCampaigns = (campaigns as any[]).filter((c: any) => {
    if (c.status !== "active" || !c.moves.length) return false;
    const allTasks = c.moves.flatMap((m: any) => m.tasks);
    const recentlyCompleted = allTasks.filter(
      (t: any) =>
        t.status === "complete" &&
        new Date(t.updatedAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    );
    return recentlyCompleted.length === 0 && allTasks.length > 0;
  });

  for (const campaign of stalledCampaigns) {
    const trigger = `stalled_${campaign.id}`;
    if (!activeTriggers.has(trigger)) {
      const pendingTasks = campaign.moves
        .flatMap((m: any) => m.tasks)
        .filter((t: any) => t.status === "pending");
      nudgesToCreate.push({
        userId,
        type: "warning",
        title: `"${campaign.title}" hasn't moved in 7 days`,
        body: `${pendingTasks.length} tasks are waiting. The next one: "${pendingTasks[0]?.title ?? "Review move ladder"}".`,
        cta: "Pick up where you left off",
        ctaHref: `/app/campaigns/${campaign.id}`,
        priority: 8,
        isDismissed: false,
        isActioned: false,
        expiresAt: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
        trigger,
      });
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const lastSession = (councilSessions as any[])[0];
  const daysSinceCouncil = lastSession
    ? (Date.now() - new Date(lastSession.createdAt).getTime()) / (24 * 60 * 60 * 1000)
    : 999;

  if (daysSinceCouncil > 14 && !activeTriggers.has("no_recent_council")) {
    nudgesToCreate.push({
      userId,
      type: "insight",
      title: "The Council hasn't met in 2 weeks",
      body: "Regular council sessions sharpen strategy. What decision have you been sitting on? Put it to the council.",
      cta: "Start a session",
      ctaHref: "/app/council",
      priority: 5,
      isDismissed: false,
      isActioned: false,
      expiresAt: null,
      trigger: "no_recent_council",
    });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  for (const session of councilSessions as any[]) {
    const daysSince = (Date.now() - new Date(session.createdAt).getTime()) / (24 * 60 * 60 * 1000);
    const trigger = `council_unactioned_${session.id}`;
    const verdict = (session.synthesisResult as Record<string, unknown> | null)?.verdict as
      | string
      | undefined;

    if (daysSince > 3 && verdict && !activeTriggers.has(trigger)) {
      nudgesToCreate.push({
        userId,
        type: "insight",
        title: "Council verdict waiting to be actioned",
        body: `3 days ago the Council said: "${(verdict as string).slice(0, 120)}${(verdict as string).length > 120 ? "…" : ""}"`,
        cta: "Create a campaign",
        ctaHref: "/app/campaigns",
        priority: 6,
        isDismissed: false,
        isActioned: false,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        trigger,
      });
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const lastRipple = (recentRipples as any[])[0];
  const daysSinceActivity = lastRipple
    ? (Date.now() - new Date(lastRipple.createdAt).getTime()) / (24 * 60 * 60 * 1000)
    : 999;

  if (daysSinceActivity > 3 && !activeTriggers.has("re_engagement")) {
    nudgesToCreate.push({
      userId,
      type: "action",
      title: "RaptorFlow misses you",
      body: `You haven't been active in ${Math.floor(daysSinceActivity)} days. Your campaigns are waiting and the memory system has been idle.`,
      cta: "See what's waiting",
      ctaHref: "/app/dashboard",
      priority: 7,
      isDismissed: false,
      isActioned: false,
      expiresAt: null,
      trigger: "re_engagement",
    });
  }

  const todayKey = new Date().toISOString().split("T")[0];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if ((recentRipples as any[]).length >= 5 && !activeTriggers.has(`ai_insight_${todayKey}`)) {
    try {
      const aiNudge = await generateAINudge(userId, campaigns, recentRipples, councilSessions);
      if (aiNudge) {
        nudgesToCreate.push({ ...aiNudge, trigger: `ai_insight_${todayKey}` } as NudgeData);
      }
    } catch (err) {
      console.error("AI nudge generation failed:", err);
    }
  }

  const created: unknown[] = [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  for (const nudge of nudgesToCreate as any[]) {
    const saved = await prisma.nudge.create({
      data: nudge as Parameters<typeof prisma.nudge.create>[0]["data"],
    });
    created.push(saved);

    broadcast(channels.user(userId), "nudge.created", {
      nudgeId: saved.id,
      title: saved.title,
      type: saved.type,
      priority: saved.priority,
    }).catch(console.error);
  }

  return created;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function generateAINudge(
  userId: string,
  campaigns: any[],
  recentRipples: any[],
  councilSessions: any[],
): Promise<Omit<
  NudgeData,
  "userId" | "trigger" | "isDismissed" | "isActioned" | "expiresAt"
> | null> {
  const campaignNames = campaigns.map((c: any) => c.title).join(", ") || "none";
  const activityTypes = recentRipples.map((r: any) => r.type).join(", ");
  const lastCouncilTopic = councilSessions[0]?.topic ?? "none";

  const { prompt } = await harnessPrompt(
    { userId, mode: "scan", query: "strategic insight pattern detection nudge" },
    `Analyse this user's activity and identify ONE non-obvious strategic insight or action they should take.

Active campaigns: ${campaignNames}
Recent activity types: ${activityTypes}
Last council topic: ${lastCouncilTopic}

Look for patterns like:
- A campaign goal that conflicts with Foundation positioning
- A council verdict that hasn't been acted on
- A Foundation gap that's blocking campaign effectiveness
- An opportunity they haven't explored yet

Return a JSON object with:
- "title": string (short, specific, < 60 chars)
- "body": string (2 sentences — what the pattern is and why it matters)
- "cta": string (action button label)
- "ctaHref": string (one of: /app/foundation, /app/campaigns, /app/council, /app/muse)
- "priority": number (1-10)
- "type": "insight" | "action" | "warning"

If there is no genuine insight worth surfacing, return null.
Return only valid JSON or null.`,
  );

  const response = await convergeFast(prompt, 512);
  if (response.trim() === "null") return null;

  let nudgeData: Record<string, unknown>;
  try {
    const trimmed = response.trim();
    const jsonStr = trimmed.startsWith("```")
      ? trimmed.replace(/^```json\n?/, "").replace(/\n?```$/, "")
      : trimmed;
    nudgeData = JSON.parse(jsonStr);
  } catch {
    return null;
  }

  return {
    type: (nudgeData.type as string) ?? "insight",
    title: (nudgeData.title as string) ?? "Insight detected",
    body: (nudgeData.body as string) ?? "A pattern has been detected in your activity.",
    cta: nudgeData.cta as string | undefined,
    ctaHref: nudgeData.ctaHref as string | undefined,
    priority: (nudgeData.priority as number) ?? 5,
  };
}
