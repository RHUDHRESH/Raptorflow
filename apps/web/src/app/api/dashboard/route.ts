import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

const RUST_API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

export async function GET(request: Request): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const since7d = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
  const since30d = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  const [
    campaignStats,
    councilCount,
    recentNudges,
    todayWin,
    recentRipples,
    intelStats,
    taskStats,
  ] = await Promise.all([
    prisma.campaign.groupBy({
      by: ["status"],
      where: { clerkUserId: userId },
      _count: { id: true },
    }),
    prisma.councilSession.aggregate({
      where: { clerkUserId: userId },
      _count: { id: true },
    }),
    prisma.nudge.findMany({
      where: { userId, isDismissed: false, isActioned: false },
      orderBy: { priority: "desc" },
      take: 3,
    }),
    prisma.dailyWin.findFirst({
      where: {
        userId,
        date: { gte: new Date(new Date().setUTCHours(0, 0, 0, 0)) },
      },
    }),
    prisma.ripple.findMany({
      where: { userId, createdAt: { gte: since7d } },
      orderBy: { createdAt: "desc" },
      take: 20,
    }),
    prisma.intelSignal.aggregate({
      where: { userId, isRead: false, isArchived: false },
      _count: { id: true },
    }),
    prisma.task.findMany({
      where: {
        move: { campaign: { clerkUserId: userId } },
        updatedAt: { gte: since30d },
      },
      select: { status: true },
    }),
  ]);

  let companyName = "your company";
  let foundationFields = 0;
  let positioningScore: number | null = null;
  try {
    const token = (await authObj.getToken({ template: "backend" })) ?? "";
    const res = await fetch(`${RUST_API}/api/v1/foundation`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const body = (await res.json()) as {
        sections?: Record<string, unknown>;
      };
      const ci = (body.sections?.company_info as { name?: string }) ?? {};
      companyName = ci.name ?? companyName;
      const sections = body.sections ?? {};
      foundationFields = Object.entries(sections).filter(
        ([, v]) => v && typeof v === "object" && Object.keys(v as object).length > 0,
      ).length;
    }
  } catch {
    // fallback
  }

  const activeCampaigns = campaignStats.find((s) => s.status === "active")?._count.id ?? 0;
  const totalCampaigns = campaignStats.reduce((sum, s) => sum + s._count.id, 0);
  const completedTasks = taskStats.filter((t: { status: string }) => t.status === "complete").length;
  const totalTasks = taskStats.length;
  const taskCompletionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const activityFeed = recentRipples.map((r) => ({
    id: r.id,
    type: r.type,
    content: r.content,
    createdAt: r.createdAt.toISOString(),
    icon: rippleTypeToIcon(r.type),
    colour: rippleTypeToColour(r.type),
  }));

  return NextResponse.json({
    stats: {
      activeCampaigns,
      totalCampaigns,
      councilSessions: councilCount._count.id,
      taskCompletionRate,
      foundationScore: positioningScore,
      foundationFields,
      intelUnread: intelStats._count.id,
      nudgeCount: recentNudges.length,
    },
    todayWin: todayWin
      ? {
          headline: ((todayWin.briefing as Record<string, unknown>) ?? {}).headline as string,
          momentumScore: ((todayWin.briefing as Record<string, unknown>) ?? {})
            .momentum_score as number,
          focusAreas: todayWin.focusAreas,
        }
      : null,
    nudges: recentNudges,
    activityFeed,
    foundation: {
      companyName,
      fieldsFilledCount: foundationFields,
      positioningScore,
    },
  });
}

function rippleTypeToIcon(type: string): string {
  const icons: Record<string, string> = {
    foundation_save: "🏛️",
    campaign_created: "🚀",
    campaign_evaluated: "📊",
    move_generated: "🎯",
    council_complete: "⚡",
    muse_exchange: "💬",
    task_complete: "✅",
  };
  return icons[type] ?? "•";
}

function rippleTypeToColour(type: string): string {
  const colours: Record<string, string> = {
    foundation_save: "blue",
    campaign_created: "green",
    campaign_evaluated: "purple",
    move_generated: "amber",
    council_complete: "yellow",
    muse_exchange: "grey",
    task_complete: "green",
  };
  return colours[type] ?? "grey";
}
