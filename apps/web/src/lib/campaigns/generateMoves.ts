import { prisma } from "@raptorflow/database";
import { converseStrategist } from "@/lib/bedrock";
import { harnessPrompt } from "@/lib/harness/buildPrompt";

interface MoveInput {
  title: string;
  description: string;
  channel: string;
  priority: number;
  tasks: string[];
}

function parseMoves(text: string): MoveInput[] {
  const trimmed = text.trim();
  const jsonStr = trimmed.startsWith("```")
    ? trimmed.replace(/^```json\n?/, "").replace(/\n?```$/, "")
    : trimmed;
  const parsed = JSON.parse(jsonStr);
  return Array.isArray(parsed) ? parsed : [];
}

export async function generateMoves(campaignId: string, token: string): Promise<unknown[]> {
  const campaign = await prisma.campaign.findUnique({ where: { id: campaignId } });
  if (!campaign) throw new Error(`Campaign ${campaignId} not found`);

  if (!campaign.evaluationResult) {
    throw new Error(
      "Campaign must be evaluated before generating moves — call evaluateBrief first",
    );
  }

  const evaluationResult = campaign.evaluationResult as Record<string, unknown>;

  const taskPrompt = `Generate a move ladder for this campaign.

IMPORTANT: Each move's channel MUST be one of: email, social, seo, paid, content, events.

Return ONLY a valid JSON array (no markdown) where each item has:
{
  "title": "<short action title, e.g. 'Launch email re-engagement sequence'>",
  "description": "<2-3 sentences — what to do and why it matters>",
  "channel": "<email|social|seo|paid|content|events>",
  "priority": <1 = do first, 2 = next, etc.>,
  "tasks": ["<specific sub-task 1>", "<sub-task 2>", "<sub-task 3>", "<sub-task 4>"]
}

Campaign:
Title: ${campaign.title}
Brief: ${campaign.brief}
Goal: ${campaign.goal ?? "not specified"}
Evaluation score: ${(evaluationResult.score as number) ?? "?"}/10
Recommended channels: ${((evaluationResult.recommended_channels as string[]) ?? []).join(", ")}

Order by priority — highest leverage, lowest effort first. Return only the JSON array.`;

  const { prompt, meta } = await harnessPrompt(
    {
      userId: campaign.clerkUserId,
      mode: "evaluation",
      query: `${campaign.title} move ladder execution plan`,
      token,
    },
    taskPrompt,
  );
  console.log(`Harness [evaluation] meta:`, meta);

  const response = await converseStrategist(prompt, 2048);
  const moveInputs = parseMoves(response);

  if (moveInputs.length === 0) {
    throw new Error("Failed to generate moves — model returned invalid response");
  }

  await prisma.move.deleteMany({ where: { campaignId } });

  const createdMoves = await Promise.all(
    moveInputs.map((m) =>
      prisma.move.create({
        data: {
          campaignId,
          title: m.title,
          description: m.description,
          channel: m.channel,
          priority: m.priority,
          status: "pending",
          tasks: {
            create: m.tasks.map((t) => ({
              title: t,
              status: "pending",
            })),
          },
        },
        include: { tasks: { orderBy: { createdAt: "asc" } } },
      }),
    ),
  );

  return createdMoves.map((m) => ({
    id: m.id,
    title: m.title,
    description: m.description,
    channel: m.channel,
    priority: m.priority,
    status: m.status,
    tasks: m.tasks.map((t) => ({
      id: t.id,
      title: t.title,
      description: t.description,
      status: t.status,
      due_date: t.dueDate?.toISOString() ?? null,
    })),
  }));
}
