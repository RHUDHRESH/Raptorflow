import { VertexAI, GenerativeModel } from '@google-cloud/vertexai';
import { env } from '../../config/env';
import { BattlefieldAnalysis } from './analyzeBattlefield';

// Initialize Vertex AI
const project = env.GOOGLE_PROJECT_ID || 'raptorflow-477017';
const location = env.GOOGLE_REGION || 'us-central1';

const vertexAI = new VertexAI({
  project: project,
  location: location,
});

const model: GenerativeModel = vertexAI.getGenerativeModel({
  model: 'gemini-1.5-flash',
  generationConfig: {
    responseMimeType: 'application/json',
    temperature: 0.5,
  },
});

export type Pillar = {
  summary: string;        // 1–2 sentence explanation
  keyInsights: string[];  // 3–5 bullets
  gapsOrRisks: string[];  // 2–4 bullets
};

export type PositioningBlueprint = {
  blueprintId: string;    // uuid
  analysisId: string;
  meta: {
    marketType: 'B2B' | 'B2C' | 'Hybrid';
    offensiveOrDefensive: 'offensive' | 'defensive' | 'mixed';
    category: string;          // chosen category frame
    wordToOwn: string;         // single core word/phrase
    elevatorClaim: string;     // 1–2 sentence positioning claim
    corePromise: string;       // “For [ICP], we ...”
    primaryFocus: 'revenue' | 'pipeline' | 'retention' | 'brand';
    userConfidence: 'spot_on' | 'mostly' | 'not_really';
  };
  pillars: {
    audience: Pillar;
    valueProp: Pillar;
    differentiation: Pillar;
    competition: Pillar;
    discovery: Pillar;
    remarkability: Pillar;
    proof: Pillar;
  };
  risks: string[];         // 3–5 bullets across the whole positioning
  opportunities: string[]; // 3–5 bullets across the whole positioning
  createdAt: string;       // ISO timestamp
};

// Only the part returned by LLM
export type BlueprintLLMResponse = Omit<PositioningBlueprint, 'blueprintId' | 'analysisId' | 'createdAt'>;

export async function generatePositioningBlueprint(
  analysis: BattlefieldAnalysis,
  userConfidence: 'spot_on' | 'mostly' | 'not_really',
  primaryFocus: 'revenue' | 'pipeline' | 'retention' | 'brand'
): Promise<BlueprintLLMResponse> {
  
  const prompt = `
You are a senior marketing strategist combining the thinking of:
Al Ries & Jack Trout (Positioning)
Seth Godin (Remarkability & Tribes)
April Dunford (Positioning frameworks)
Rory Sutherland & Cialdini (behavioral psychology & influence).

INPUT:

A JSON object battlefieldAnalysis with:
summary: ${JSON.stringify(analysis.summary)}
diagnostics: ${JSON.stringify(analysis.diagnostics)}
notes: ${JSON.stringify(analysis.notes)}

A userConfidence flag: ${userConfidence}

A primaryFocus for the next 90 days: ${primaryFocus}

TASK:

Construct a Positioning Blueprint using this 7-pillar model:
audience, valueProp, differentiation, competition, discovery, remarkability, proof.

Decide:

marketType: B2B / B2C / Hybrid

offensiveOrDefensive: offensive / defensive / mixed

category: the market category they should compete in

wordToOwn: a single concept they should own in the mind

elevatorClaim: a 1–2 sentence claim in plain language

corePromise: a clear promise that would matter deeply to their ICP

For each pillar (audience, valueProp, differentiation, competition, discovery, remarkability, proof):

summary: 1–2 sentence explanation, specific to their context.

keyInsights: 3–5 short bullets of what we see.

gapsOrRisks: 2–4 bullets of what could fail or is missing.

Also provide:

risks: 3–5 cross-pillar risks.

opportunities: 3–5 cross-pillar opportunities.

IMPORTANT RULES:

Output MUST be valid JSON only, matching this TypeScript type exactly:
{
  "meta": {
    "marketType": "B2B" | "B2C" | "Hybrid",
    "offensiveOrDefensive": "offensive" | "defensive" | "mixed",
    "category": "string",
    "wordToOwn": "string",
    "elevatorClaim": "string",
    "corePromise": "string",
    "primaryFocus": "${primaryFocus}",
    "userConfidence": "${userConfidence}"
  },
  "pillars": {
    "audience": { "summary": "string", "keyInsights": ["string"], "gapsOrRisks": ["string"] },
    "valueProp": { "summary": "string", "keyInsights": ["string"], "gapsOrRisks": ["string"] },
    "differentiation": { "summary": "string", "keyInsights": ["string"], "gapsOrRisks": ["string"] },
    "competition": { "summary": "string", "keyInsights": ["string"], "gapsOrRisks": ["string"] },
    "discovery": { "summary": "string", "keyInsights": ["string"], "gapsOrRisks": ["string"] },
    "remarkability": { "summary": "string", "keyInsights": ["string"], "gapsOrRisks": ["string"] },
    "proof": { "summary": "string", "keyInsights": ["string"], "gapsOrRisks": ["string"] }
  },
  "risks": ["string"],
  "opportunities": ["string"]
}

Do NOT include commentary, markdown, or backticks.

Keep language concise and concrete. No generic clichés.
`;

  try {
    const result = await model.generateContent(prompt);
    const response = result.response;
    const text = response.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!text) {
      throw new Error('No content generated from LLM');
    }

    // Clean up markdown code blocks if present
    const cleanedText = text.replace(/```json\n?|\n?```/g, '').trim();
    
    const parsed = JSON.parse(cleanedText) as BlueprintLLMResponse;

    // Basic validation
    if (!parsed.pillars || !parsed.meta) {
      throw new Error("Invalid JSON structure returned from LLM");
    }

    return parsed;
  } catch (error) {
    console.error('LLM Blueprint Generation Failed:', error);
    throw new Error('Failed to generate positioning blueprint');
  }
}
