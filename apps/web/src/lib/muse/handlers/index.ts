import { convergeFast, converseStrategist } from "@/lib/bedrock";
import { prisma } from "@raptorflow/database";
import { harnessPrompt } from "@/lib/harness/buildPrompt";
import type { MuseRoute } from "../classifyRoute";

interface HandlerContext {
  userMessage: string;
  conversationHistory: Array<{ role: string; content: string }>;
  clerkUserId: string;
}

function buildHistoryBlock(history: Array<{ role: string; content: string }>): string {
  return history.length
    ? `Conversation history:\n${history.map((m) => `${m.role}: ${m.content}`).join("\n")}\n`
    : "";
}

export async function handleTactical(ctx: HandlerContext): Promise<string> {
  const historyBlock = buildHistoryBlock(ctx.conversationHistory.slice(-6));

  const { prompt } = await harnessPrompt(
    { userId: ctx.clerkUserId, mode: "muse", query: ctx.userMessage },
    `${historyBlock}User: ${ctx.userMessage}\n\nBe concise, specific, and creative. Use the company's brand voice from the Foundation above.`,
  );

  return convergeFast(prompt, 512);
}

export async function handleStrategic(ctx: HandlerContext): Promise<string> {
  const historyBlock = buildHistoryBlock(ctx.conversationHistory.slice(-6));

  const { prompt } = await harnessPrompt(
    { userId: ctx.clerkUserId, mode: "muse", query: ctx.userMessage },
    `${historyBlock}User: ${ctx.userMessage}\n\nGive a direct strategic recommendation. Reference the company's actual situation from Foundation. No generic advice.`,
  );

  return converseStrategist(prompt, 768);
}

export async function handleCampaign(ctx: HandlerContext): Promise<string> {
  const campaigns = await prisma.campaign.findMany({
    where: { clerkUserId: ctx.clerkUserId, status: { in: ["active", "draft", "evaluating"] } },
    select: { id: true, title: true, goal: true, status: true },
    orderBy: { createdAt: "desc" },
    take: 5,
  });

  const campaignList =
    campaigns.length > 0
      ? campaigns
          .map((c) => `- "${c.title}" (${c.status}${c.goal ? `, goal: ${c.goal}` : ""})`)
          .join("\n")
      : "No active campaigns yet.";

  const historyBlock = buildHistoryBlock(ctx.conversationHistory.slice(-6));

  const { prompt } = await harnessPrompt(
    { userId: ctx.clerkUserId, mode: "muse", query: ctx.userMessage },
    `${historyBlock}Active campaigns:\n${campaignList}\n\nUser: ${ctx.userMessage}\n\nFocus on campaign strategy. Reference any active campaigns from the memory context above if relevant.`,
  );

  return converseStrategist(prompt, 768);
}

export async function handleCouncil(
  ctx: HandlerContext,
): Promise<{ response: string; sessionId: string }> {
  const session = await prisma.councilSession.create({
    data: {
      clerkUserId: ctx.clerkUserId,
      topic: ctx.userMessage.slice(0, 80),
      context: ctx.userMessage,
      status: "pending",
    },
  });

  const responseText = `Starting a Council session on this topic to gather multi-perspective input from 12 strategic avatars. The council will deliberate and produce a synthesised verdict with recommendations.\n\n→ View Council Session`;

  return { response: responseText, sessionId: session.id };
}

export async function handleFoundation(ctx: HandlerContext): Promise<string> {
  const historyBlock = buildHistoryBlock(ctx.conversationHistory.slice(-6));

  const { prompt } = await harnessPrompt(
    { userId: ctx.clerkUserId, mode: "muse", query: ctx.userMessage },
    `${historyBlock}User: ${ctx.userMessage}\n\nHelp the user understand what Foundation field to update. Reference their current Foundation data above. Suggest the specific section URL they should edit.`,
  );

  return convergeFast(prompt, 512);
}

export async function routeHandler(
  route: MuseRoute,
  ctx: HandlerContext,
): Promise<{ response: string; sessionId?: string }> {
  switch (route) {
    case "tactical":
      return { response: await handleTactical(ctx) };
    case "strategic":
      return { response: await handleStrategic(ctx) };
    case "campaign":
      return { response: await handleCampaign(ctx) };
    case "council":
      return handleCouncil(ctx);
    case "foundation":
      return { response: await handleFoundation(ctx) };
    default:
      return { response: await handleTactical(ctx) };
  }
}
