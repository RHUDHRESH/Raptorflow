import { NextRequest, NextResponse } from "next/server";
import { apiFetch } from "@/lib/api";

export const dynamic = "force-dynamic";

interface LiveExampleRequest {
  sliders: {
    formality: number; // 0-1: Casual ↔ Formal
    technicality: number; // 0-1: Accessible ↔ Technical
    tone: number; // 0-1: Serious ↔ Playful
    stance: number; // 0-1: Authoritative ↔ Collaborative
    register: number; // 0-1: Conservative ↔ Bold
  };
}

interface LiveExampleResponse {
  example: string;
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const { sliders }: LiveExampleRequest = await req.json();

    if (!sliders) {
      return NextResponse.json({ error: "sliders object is required" }, { status: 400 });
    }

    // Generate AI example based on slider positions
    const example = await generateVoiceExample(sliders);

    return NextResponse.json({ example });
  } catch (error) {
    console.error("Live voice example error:", error);
    return NextResponse.json(
      {
        error: "Failed to generate voice example",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

async function generateVoiceExample(sliders: LiveExampleRequest["sliders"]): Promise<string> {
  const { formality, technicality, tone, stance, register } = sliders;

  // Map sliders to descriptive terms
  const formalityLevel = formality > 0.7 ? "formal" : formality > 0.4 ? "neutral" : "casual";
  const technicalityLevel =
    technicality > 0.7 ? "technical" : technicality > 0.4 ? "balanced" : "accessible";
  const toneLevel = tone > 0.7 ? "playful" : tone > 0.4 ? "balanced" : "serious";
  const stanceLevel = stance > 0.7 ? "collaborative" : stance > 0.4 ? "balanced" : "authoritative";
  const registerLevel = register > 0.7 ? "bold" : register > 0.4 ? "balanced" : "conservative";

  // Create prompt for AI
  const prompt = `Generate a single sentence that demonstrates a brand voice with these characteristics:
- Formality: ${formalityLevel} (${(formality * 100).toFixed(0)}%)
- Technicality: ${technicalityLevel} (${(technicality * 100).toFixed(0)}%)
- Tone: ${toneLevel} (${(tone * 100).toFixed(0)}%)
- Stance: ${stanceLevel} (${(stance * 100).toFixed(0)}%)
- Register: ${registerLevel} (${(register * 100).toFixed(0)}%)

The sentence should be about a software company helping businesses grow. Make it sound natural and authentic to the voice profile. Return only the sentence, no explanation.`;

  try {
    // Call AI API (using the existing chat endpoint with flash-lite model)
    const aiResponse = await apiFetch<{ choices: { message: { content: string } }[] }>(
      "/api/ai/chat",
      {
        method: "POST",
        body: {
          messages: [{ role: "user", content: prompt }],
          model: "mixtral-8x7b-32768", // Use fast model for live examples
          max_tokens: 100,
          temperature: 0.7,
        },
        auth: true,
      },
    );

    const example = aiResponse.choices?.[0]?.message?.content?.trim();
    return example || "We help businesses grow through innovative solutions.";
  } catch (error) {
    console.error("AI call failed:", error);
    // Fallback examples based on slider positions
    return generateFallbackExample(sliders);
  }
}

function generateFallbackExample(sliders: LiveExampleRequest["sliders"]): string {
  const { formality, technicality, tone, stance, register } = sliders;

  // Simple fallback logic based on extreme slider positions
  if (formality > 0.8 && technicality > 0.8) {
    return "Our proprietary algorithms leverage machine learning architectures to optimize conversion pathways at enterprise scale.";
  }

  if (formality < 0.3 && technicality < 0.3 && tone > 0.6) {
    return "We help startups get their first 100 customers without the bullshit.";
  }

  if (stance > 0.7 && register < 0.4) {
    return "Together, we'll build something amazing that serves your customers perfectly.";
  }

  if (tone < 0.4 && register > 0.7) {
    return "We're not afraid to challenge the status quo and redefine what's possible.";
  }

  // Default balanced example
  return "We create solutions that drive real business results for our clients.";
}
