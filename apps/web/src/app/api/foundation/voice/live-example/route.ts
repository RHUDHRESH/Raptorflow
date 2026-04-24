import { NextRequest, NextResponse } from "next/server";
import { converseStrategist } from "@/lib/bedrock";

export const dynamic = "force-dynamic";

interface LiveExampleRequest {
  sliders: {
    formality: number;
    technicality: number;
    tone: number;
    stance: number;
    register: number;
  };
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const { sliders }: LiveExampleRequest = await req.json();

    if (!sliders) {
      return NextResponse.json({ error: "sliders object is required" }, { status: 400 });
    }

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

  const prompt = `Generate ONE short brand voice example (2-3 sentences, punchy and realistic) based on these voice sliders:

- Formality: ${formality} (${formality > 0.7 ? "highly formal" : formality > 0.4 ? "moderately formal" : "casual"})
- Technicality: ${technicality} (${technicality > 0.7 ? "highly technical" : technicality > 0.4 ? "balanced" : "accessible"})
- Tone: ${tone} (${tone > 0.7 ? "very playful" : tone > 0.4 ? "balanced" : "serious"})
- Stance: ${stance} (${stance > 0.7 ? "highly collaborative" : stance > 0.4 ? "balanced" : "authoritative"})
- Register: ${register} (${register > 0.7 ? "very bold" : register > 0.4 ? "balanced" : "conservative"})

Write it as a real marketing sentence a real brand would use. Be specific and vivid. No meta-commentary.`;

  try {
    return await converseStrategist(prompt, 150);
  } catch {
    return generateFallbackExample(sliders);
  }
}

function generateFallbackExample(sliders: LiveExampleRequest["sliders"]): string {
  const { formality, technicality, tone, stance, register } = sliders;

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

  return "We create solutions that drive real business results for our clients.";
}
