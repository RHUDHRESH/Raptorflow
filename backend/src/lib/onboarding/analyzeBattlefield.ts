import { VertexAI, GenerativeModel } from '@google-cloud/vertexai';
import { env } from '../../config/env';

// Initialize Vertex AI
// Ensure GOOGLE_PROJECT_ID is set.
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
    temperature: 0.4,
  },
});

export interface BattlefieldAnalysisInput {
  description: string;
  websiteUrl?: string | null;
  geography?: string | null;
  industry?: string | null;
}

export type BattlefieldAnalysis = {
  analysisId: string; // UUID
  summary: {
    companyType: string;
    productOrService: string;
    primaryAudience: string;
    mainPainPoints: string[];
    currentApproach: string;
    desiredOutcome: string;
  };
  diagnostics: {
    positioningUniqueness: number; // 0-1
    icpClarity: number;            // 0-1
    marketingMaturity: number;     // 0-1
  };
  notes: {
    positioningRisks: string[];
    obviousOpportunities: string[];
    statusQuoCompetitor: string;
  };
  rawModelText?: string;
  createdAt: string;
};

// Only the part returned by LLM
export type LLMResponse = Omit<BattlefieldAnalysis, 'analysisId' | 'createdAt' | 'rawModelText'>;

export async function analyzeBattlefield(input: BattlefieldAnalysisInput): Promise<LLMResponse> {
  const prompt = `
You are a senior B2B/B2C marketing strategist.
The user has described their business and context in free text.
Your job is to EXTRACT and INFER a structured "battlefield analysis" that will be visualized in onboarding.

Read the user's description and the optional metadata (website URL, geography, industry).

Business Input:
- Description: ${input.description}
- Website: ${input.websiteUrl || 'N/A'}
- Geography: ${input.geography || 'Global'}
- Industry: ${input.industry || 'General'}

Infer:

companyType

productOrService

primaryAudience

mainPainPoints (list)

currentApproach to marketing/sales

desiredOutcome

Score diagnostics from 0 to 1:

positioningUniqueness: how differentiated and specific does the positioning sound?

icpClarity: how clearly defined is the ideal customer profile?

marketingMaturity: how evolved do their current marketing efforts sound?

Identify:

positioningRisks: 2–4 short bullets.

obviousOpportunities: 2–4 short bullets.

statusQuoCompetitor: their most likely real competitor (often "doing nothing" or "manual spreadsheets").

IMPORTANT:

Return ONLY JSON matching this exact TypeScript type:

{
  "summary": {
    "companyType": "string",
    "productOrService": "string",
    "primaryAudience": "string",
    "mainPainPoints": ["string"],
    "currentApproach": "string",
    "desiredOutcome": "string"
  },
  "diagnostics": {
    "positioningUniqueness": number,
    "icpClarity": number,
    "marketingMaturity": number
  },
  "notes": {
    "positioningRisks": ["string"],
    "obviousOpportunities": ["string"],
    "statusQuoCompetitor": "string"
  }
}

Do NOT wrap it in backticks or prose.

Make short, concrete phrases. No fluff.
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
    
    const parsed = JSON.parse(cleanedText) as LLMResponse;
    
    // Validate structure rudimentarily
    if (!parsed.summary || !parsed.diagnostics || !parsed.notes) {
        throw new Error("Invalid JSON structure returned from LLM");
    }

    return parsed;
  } catch (error) {
    console.error('LLM Analysis Failed:', error);
    throw new Error('Failed to analyze business data');
  }
}

// TODO: Add unit tests for analyzeBattlefield
