import { NextRequest, NextResponse } from "next/server";

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
  return generateFallbackExample(sliders);
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
