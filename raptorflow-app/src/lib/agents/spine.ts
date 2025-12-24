import { StateGraph, Annotation } from "@langchain/langgraph";
import { ChatVertexAI } from "@langchain/google-vertexai";
import { getGemini15Pro, getGemini15Flash } from "../vertexai";
import { FoundationData, DerivedData, DerivedICP, DerivedPositioning, DerivedCompetitive, DerivedSoundbites, DerivedMarket } from "../foundation";
import { Icp } from "@/types/icp-types";

/**
 * Agent Spine State Definition
 */
export const OnboardingStateAnnotation = Annotation.Root({
    foundation: Annotation<FoundationData>(),
    derived: Annotation<DerivedData>({
        reducer: (x, y) => ({ ...x, ...y }),
        default: () => ({}),
    }),
    icps: Annotation<Icp[]>({
        reducer: (x, y) => [...x, ...y],
        default: () => [],
    }),
    moves: Annotation<any[]>({
        reducer: (x, y) => [...x, ...y],
        default: () => [],
    }),
    campaign: Annotation<any>({
        reducer: (x, y) => ({ ...x, ...y }),
        default: () => null,
    }),
    status: Annotation<string[]>({
        reducer: (x, y) => [...x, ...y],
        default: () => [],
    }),
    errors: Annotation<string[]>({
        reducer: (x, y) => [...x, ...y],
        default: () => [],
    }),
});

/**
 * Architect Node: Validates and sanitizes the foundation data.
 * Detects contradictions and refines brand voice.
 */
async function architectNode(state: typeof OnboardingStateAnnotation.State) {
    const model = getGemini15Flash();
    if (!model) return { status: ["Architect: Model unavailable"], errors: ["Missing credentials"] };

    const prompt = `
    You are the Lead Architect for RaptorFlow. Your job is to validate this founder's brand foundation.
    Identify contradictions between their business stage, revenue model, and buyer roles.

    Foundation Data:
    ${JSON.stringify(state.foundation, null, 2)}

    Tasks:
    1. Detect contradictions.
    2. Refine the suggested Brand Voice.
    3. Generate a 'Strategic Pivot' summary if needed.

    Return your analysis as a JSON object with:
    {
      "valid": boolean,
      "contradictions": string[],
      "suggestedVoice": string,
      "summary": string
    }
  `;

    try {
        const response = await model.invoke(prompt);
        const result = JSON.parse(response.content as string);
        return {
            status: ["Architect: Foundation validated"],
            derived: {
                brandVoice: result.suggestedVoice,
                strategicPivot: result.summary
            }
        };
    } catch (e) {
        return {
            status: ["Architect: Validation skipped (parse error)"],
            derived: {}
        };
    }
}

/**
 * Prophet Node: Generates high-fidelity ICPs based on refined foundation.
 */
async function prophetNode(state: typeof OnboardingStateAnnotation.State) {
    const model = getGemini15Pro();
    if (!model) return { errors: ["Prophet: Model unavailable"] };

    const prompt = `
    You are the Prophet for RaptorFlow. Your job is to generate 3 EMERGENT ICPs (Ideal Customer Profiles) based on the provided Foundation Data.

    CRITICAL:
    - Do NOT use generic templates.
    - Deeply analyze the 'Confessions', 'Embarrassing Truths', and 'Pain Rankings'.
    - Use the 'SCARF Drivers' to build psychographic depth.
    - Output MUST be a JSON array of 3 'Icp' objects matching the RaptorFlow schema.

    Foundation Context:
    ${JSON.stringify(state.foundation, null, 2)}

    Desired Schema (Partial for guidance):
    {
      "name": string,
      "priority": "primary" | "secondary",
      "firmographics": { "companyType": [], "geography": [], "salesMotion": [], "budgetComfort": [], "decisionMaker": [] },
      "painMap": { "primaryPains": [], "secondaryPains": [], "triggerEvents": [], "urgencyLevel": "now" | "soon" | "someday" },
      "psycholinguistics": { "mindsetTraits": [], "emotionalTriggers": [], "tonePreference": [], "wordsToUse": [], "wordsToAvoid": [], "proofPreference": [], "ctaStyle": [] },
      "disqualifiers": { "excludedCompanyTypes": [], "excludedGeographies": [], "excludedBehaviors": [] }
    }

    Return ONLY the JSON array.
  `;

    try {
        const response = await model.invoke(prompt);
        const text = response.content as string;
        const jsonMatch = text.match(/\[[\s\S]*\]/);
        if (!jsonMatch) throw new Error("No JSON array found in Prophet response");

        const icps = JSON.parse(jsonMatch[0]);
        return {
            status: ["Prophet: 3 emergent ICPs generated"],
            icps: icps.map((i: any) => ({
                ...i,
                id: crypto.randomUUID(),
                workspaceId: 'default-ws',
                status: 'active',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            }))
        };
    } catch (e: any) {
        console.error("Prophet Error:", e);
        return { errors: [`Prophet failed: ${e.message}`] };
    }
}

/**
 * Strategist Node: Generates the initial 90-day campaign and move backlog.
 */
async function strategistNode(state: typeof OnboardingStateAnnotation.State) {
    const model = getGemini15Pro();
    if (!model) return { errors: ["Strategist: Model unavailable"] };

    const primaryIcp = state.icps.find(i => i.priority === 'primary') || state.icps[0];

    const prompt = `
    You are the Strategist for RaptorFlow. Your job is to generate the first High-Priority Campaign and its initial 3 'Moves' (Battle Plans).

    Basis:
    - Foundation: ${JSON.stringify(state.foundation, null, 2)}
    - Primary ICP: ${JSON.stringify(primaryIcp, null, 2)}

    Output MUST be a JSON object with:
    {
      "campaign": { "name": string, "objective": string, "offer": string, "channels": [] },
      "moves": [
        { "name": string, "goal": string, "channel": string, "duration": 7 | 14, "description": string, "checklist": [{ "label": string, "group": "setup"|"create"|"publish"|"followup" }] }
      ]
    }

    Return ONLY the JSON object.
  `;

    try {
        const response = await model.invoke(prompt);
        const text = response.content as string;
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (!jsonMatch) throw new Error("No JSON object found in Strategist response");

        const result = JSON.parse(jsonMatch[0]);
        const campaignId = crypto.randomUUID();

        return {
            status: ["Strategist: Initial campaign and moves drafted"],
            campaign: {
                ...result.campaign,
                id: campaignId,
                status: 'planned',
                createdAt: new Date().toISOString(),
                moveLength: 14,
                dailyEffort: 30,
                duration: 90
            },
            moves: result.moves.map((m: any) => ({
                ...m,
                id: crypto.randomUUID(),
                campaignId: campaignId,
                status: 'queued',
                createdAt: new Date().toISOString(),
                checklist: m.checklist.map((c: any) => ({ ...c, id: crypto.randomUUID(), completed: false }))
            }))
        };
    } catch (e: any) {
        console.error("Strategist Error:", e);
        return { errors: [`Strategist failed: ${e.message}`] };
    }
}

/**
 * Create the Onboarding Graph
 */
export const createOnboardingGraph = () => {
    const workflow = new StateGraph(OnboardingStateAnnotation)
        .addNode("architect", architectNode)
        .addNode("prophet", prophetNode)
        .addNode("strategist", strategistNode)
        .addEdge("__start__", "architect")
        .addEdge("architect", "prophet")
        .addEdge("prophet", "strategist")
        .addEdge("strategist", "__end__");

    return workflow.compile();
};
