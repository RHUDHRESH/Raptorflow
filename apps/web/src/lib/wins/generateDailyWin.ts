import { prisma } from "@raptorflow/database";
import { broadcast, channels } from "@/lib/pusher/server";
import { harnessPrompt } from "@/lib/harness/buildPrompt";
import { converseStrategist } from "@/lib/bedrock";
import { ingestRipple } from "@/lib/prl/ingest";

const RUST_API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

interface DailyWinResult {
  id: string;
  userId: string;
  date: Date;
  briefing: Record<string, unknown>;
  highlights: string[];
  focusAreas: string[];
  systemActivity: Record<string, unknown>;
  isRead: boolean;
  createdAt: Date;
}

export async function generateDailyWin(
  userId: string,
  date: Date = new Date(),
): Promise<DailyWinResult> {
  const dateKey = new Date(date);
  dateKey.setUTCHours(0, 0, 0, 0);

  const existing = await prisma.dailyWin.findUnique({
    where: { userId_date: { userId, date: dateKey } },
  });
  if (existing) return existing as unknown as DailyWinResult;

  const since = new Date(Date.now() - 24 * 60 * 60 * 1000);

  const [
    recentRipples,
    recentCampaigns,
    recentCouncilSessions,
    completedTasks,
    recentIntelSignals,
  ] = await Promise.all([
    prisma.ripple.findMany({
      where: { userId, createdAt: { gte: since } },
      orderBy: { createdAt: "desc" },
    }),
    prisma.campaign.findMany({
      where: { userId, updatedAt: { gte: since } },
      include: { moves: { include: { tasks: true } } },
    }),
    prisma.councilSession.findMany({
      where: { clerkUserId: userId, createdAt: { gte: since }, status: "complete" },
      include: { positions: true },
    }),
    prisma.task.findMany({
      where: {
        move: { campaign: { clerkUserId: userId } },
        status: "complete",
        updatedAt: { gte: since },
      },
    }),
    prisma.intelSignal.findMany({
      where: { userId, createdAt: { gte: since } },
    }),
  ]);

  const systemActivity = {
    ripplesCreated: recentRipples.length,
    cortexSearchesRun: recentRipples.filter((r) => r.type === "muse_exchange").length,
    intelSignalsGenerated: recentIntelSignals.filter((s) => s.source === "ai_generated").length,
    foundationScansRun: recentRipples.filter(
      (r) => r.type === "foundation_save" && r.content.includes("scan"),
    ).length,
  };

  let companyName = "your company";
  try {
    const token = "";
    const res = await fetch(`${RUST_API}/api/v1/foundation`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const body = (await res.json()) as { sections?: { company_info?: { name?: string } } };
      companyName = (body.sections?.company_info as { name?: string })?.name ?? companyName;
    }
  } catch {
    // fallback to default
  }

  const activitySummary = [
    recentCampaigns.length > 0 &&
      `${recentCampaigns.length} campaign(s) active: ${recentCampaigns.map((c) => c.title).join(", ")}`,
    completedTasks.length > 0 && `${completedTasks.length} task(s) completed`,
    recentCouncilSessions.length > 0 &&
      `${recentCouncilSessions.length} council session(s) completed: ${recentCouncilSessions.map((s) => `"${s.topic}"`).join(", ")}`,
    recentIntelSignals.length > 0 &&
      `${recentIntelSignals.length} new intel signal(s): ${recentIntelSignals.map((s) => s.title).join(", ")}`,
  ]
    .filter(Boolean)
    .join("\n");

  if (!activitySummary) {
    return generateQuietDayWin(userId, dateKey, companyName, systemActivity);
  }

  const taskPrompt = `Generate a daily wins briefing for this founder/marketer.

Activity in the last 24 hours:
${activitySummary}

Council verdicts (if any):
${recentCouncilSessions
  .map(
    (s) =>
      `Topic: "${s.topic}" — Verdict: ${((s.synthesisResult as Record<string, string>) ?? {}).verdict ?? "pending"}`,
  )
  .join("\n")}

Today's date: ${date.toDateString()}

Return a JSON object with:
- "greeting": string (personalised morning greeting using company name, 1 sentence, upbeat but not cringe)
- "headline": string (the single biggest win or progress from yesterday, 1 sentence)
- "highlights": string[] (3-5 specific wins from the activity above — be concrete, reference actual campaign names and tasks)
- "momentum_score": number (1-10, how much productive momentum was built yesterday)
- "focus_areas": string[] (2-3 specific things to focus on TODAY based on active campaigns and open tasks)
- "strategic_pulse": string (1-2 sentences on how the company's strategy is progressing based on Foundation + recent activity)
- "system_note": string (1 sentence describing what RaptorFlow did automatically — memory stored, signals detected, etc.)
- "quote": string (a relevant, non-generic strategic quote that fits the current context — not a cliché)

Be specific. Reference actual campaign names, council topics, and task names.
Return only valid JSON.`;

  const { prompt } = await harnessPrompt(
    { userId, mode: "scan", query: "daily performance review wins achievements" },
    taskPrompt,
  );

  const response = await converseStrategist(prompt, 1024);
  let briefing: Record<string, unknown>;
  try {
    const trimmed = response.trim();
    const jsonStr = trimmed.startsWith("```")
      ? trimmed.replace(/^```json\n?/, "").replace(/\n?```$/, "")
      : trimmed;
    briefing = JSON.parse(jsonStr);
  } catch {
    briefing = {
      greeting: `Good morning, ${companyName}.`,
      headline: "A productive day with meaningful progress across multiple fronts.",
      highlights: activitySummary.split("\n").filter(Boolean).slice(0, 3) as string[],
      momentum_score: 6,
      focus_areas: [
        "Continue building momentum on active campaigns",
        "Review Foundation for strategic gaps",
      ],
      strategic_pulse: "The system is tracking your progress and building strategic memory.",
      system_note: `RaptorFlow processed ${systemActivity.ripplesCreated} memory operations in the background.`,
      quote: "Execution is the bridge between strategy and results.",
    };
  }

  const win = await prisma.dailyWin.create({
    data: {
      userId,
      date: dateKey,
      briefing: briefing as any,
      highlights: (briefing.highlights as string[]) ?? [],
      focusAreas: (briefing.focus_areas as string[]) ?? [],
      systemActivity: systemActivity as any,
    },
  });

  broadcast(channels.user(userId), "daily.win.ready", {
    winId: win.id,
    headline: (briefing.headline as string) ?? "",
    momentumScore: (briefing.momentum_score as number) ?? 5,
  }).catch(console.error);

  ingestRipple({
    userId,
    type: "muse_exchange",
    sourceId: win.id,
    content: `Daily win briefing: ${briefing.headline}. Focus areas: ${((briefing.focus_areas as string[]) ?? []).join(", ")}`,
  }).catch(console.error);

  return win as unknown as DailyWinResult;
}

async function generateQuietDayWin(
  userId: string,
  dateKey: Date,
  companyName: string,
  systemActivity: Record<string, unknown>,
): Promise<DailyWinResult> {
  const briefing = {
    greeting: `Good morning, ${companyName}.`,
    headline: "A quiet day — perfect for strategic thinking.",
    highlights: [
      "No campaigns updated yesterday — today is a good day to review your move ladders.",
    ],
    momentum_score: 3,
    focus_areas: [
      "Run a Foundation quick scan to refresh your strategic positioning",
      "Start a Council session on your biggest current decision",
      "Review your active campaign moves and complete a task",
    ],
    strategic_pulse:
      "The system is ready and waiting. The Foundation is your starting point — the richer it is, the better every AI recommendation becomes.",
    system_note: `RaptorFlow processed ${systemActivity.ripplesCreated} memory operations in the background.`,
    quote: "Strategy without execution is hallucination. — Thomas Edison",
  };

  const win = await prisma.dailyWin.create({
    data: {
      userId,
      date: dateKey,
      briefing: briefing as any,
      highlights: briefing.highlights,
      focusAreas: briefing.focus_areas,
      systemActivity: systemActivity as any,
    },
  });

  return win as unknown as DailyWinResult;
}
