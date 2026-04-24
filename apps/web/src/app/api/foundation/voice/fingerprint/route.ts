import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

export const dynamic = "force-dynamic";

interface FingerprintRequest {
  sliders: {
    formality: number;
    technicality: number;
    tone: number;
    stance: number;
    register: number;
  };
  descriptors: string[];
  writingSamples: Array<{
    prompt: string;
    output: string;
  }>;
}

interface FingerprintResponse {
  fingerprint: number[];
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const { sliders, descriptors, writingSamples }: FingerprintRequest = await req.json();

    if (!sliders || !descriptors || !writingSamples) {
      return NextResponse.json(
        { error: "sliders, descriptors, and writingSamples are required" },
        { status: 400 },
      );
    }

    // Generate voice fingerprint
    const fingerprint = await generateVoiceFingerprint(sliders, descriptors, writingSamples);

    return NextResponse.json({ fingerprint });
  } catch (error) {
    console.error("Voice fingerprint error:", error);
    return NextResponse.json(
      {
        error: "Failed to generate voice fingerprint",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

async function generateVoiceFingerprint(
  sliders: FingerprintRequest["sliders"],
  descriptors: string[],
  writingSamples: FingerprintRequest["writingSamples"],
): Promise<number[]> {
  // Step 1: Generate voice description from sliders
  const voiceDescription = await generateVoiceDescription(sliders, descriptors);

  // Step 2: Get embeddings for description and writing samples
  const embeddings = await getEmbeddings([
    voiceDescription,
    ...writingSamples.map((sample) => sample.output),
  ]);

  if (embeddings.length < 4) {
    throw new Error("Failed to generate sufficient embeddings");
  }

  // Step 3: Compute weighted average
  // 0.4 × description_embedding + 0.2 × sample1 + 0.2 × sample2 + 0.2 × sample3
  const weights = [0.4, 0.2, 0.2, 0.2];
  const fingerprint: number[] = [];

  // Assume embeddings are 64-dimensional (this is a simplification)
  const dimensions = Math.min(64, embeddings[0].length);

  for (let i = 0; i < dimensions; i++) {
    let weightedSum = 0;
    for (let j = 0; j < weights.length; j++) {
      weightedSum += weights[j] * (embeddings[j][i] || 0);
    }
    fingerprint.push(weightedSum);
  }

  return fingerprint;
}

async function generateVoiceDescription(
  sliders: FingerprintRequest["sliders"],
  descriptors: string[],
): Promise<string> {
  const { formality, technicality, tone, stance, register } = sliders;

  const prompt = `Write a 200-word description of a brand voice based on these characteristics:

Sliders (0-1 scale):
- Formality: ${formality} (${formality > 0.7 ? "highly formal" : formality > 0.4 ? "moderately formal" : "casual"})
- Technicality: ${technicality} (${technicality > 0.7 ? "highly technical" : technicality > 0.4 ? "balanced" : "accessible"})
- Tone: ${tone} (${tone > 0.7 ? "very playful" : tone > 0.4 ? "balanced" : "serious"})
- Stance: ${stance} (${stance > 0.7 ? "highly collaborative" : stance > 0.4 ? "balanced" : "authoritative"})
- Register: ${register} (${register > 0.7 ? "very bold" : register > 0.4 ? "balanced" : "conservative"})

Descriptors: ${descriptors.join(", ")}

Write a cohesive description that captures how this brand would communicate across different contexts. Focus on language patterns, attitude, and relationship with the audience.`;

  return `This brand voice combines ${descriptors.join(" and ")} communication with ${formality > 0.5 ? "formal" : "casual"} language patterns, ${technicality > 0.5 ? "technical" : "accessible"} explanations, and a ${tone > 0.5 ? "playful" : "serious"} tone.`;
}

async function getEmbeddings(texts: string[]): Promise<number[][]> {
  // This is a simplified implementation
  // In a real system, this would call an embedding API
  // For now, we'll generate pseudo-random embeddings based on text hash

  const embeddings: number[][] = [];

  for (const text of texts) {
    const hash = crypto.createHash("sha256").update(text).digest("hex");
    const embedding: number[] = [];

    // Convert hash to 64 float values between -1 and 1
    for (let i = 0; i < 64; i++) {
      const chunk = hash.substring(i * 2, i * 2 + 2);
      const value = parseInt(chunk, 16) / 255.0; // 0-1
      embedding.push((value - 0.5) * 2); // -1 to 1
    }

    embeddings.push(embedding);
  }

  return embeddings;
}
