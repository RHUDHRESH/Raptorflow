import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  // In a real implementation, we would fetch from Supabase
  // const { id } = params;
  // const { data, error } = await supabase.from('rationales').select('*').eq('move_id', id).single();

  // Simulate delay
  await new Promise((resolve) => setTimeout(resolve, 800));

  // Mock Response mimicking the structure returned by getMoveRationale
  const mockRationale = {
    type: 'move',
    strategicDecree:
      "The Council has aligned on a high-velocity distribution strategy. The primary driver is a detected 15% WoW increase in 'founder burnout' signals across Twitter/X, creating a perfect window for our 'Systematized Relief' narrative.",
    confidence: 0.92,
    risks: [
      'Tone may be perceived as too aggressive if not balanced with empathy.',
      "Visual assets must strictly follow the new 'Quiet Luxury' guidelines to avoid looking like a generic info-product.",
    ],
    debateTranscript: [
      {
        role: 'The Skeptic',
        argument:
          "Are we sure this isn't just noise? The signal volume is low.",
      },
      {
        role: 'The Strategist',
        argument:
          "It's low volume but high intent. The influencers driving this conversation match our clean ICP perfectly.",
      },
      {
        role: 'The Data Quant',
        argument:
          "Corroborating data from Search Console shows a spike in 'marketing delegation' queries.",
      },
    ],
    rejectedPaths: [
      {
        path: 'Direct Sales Pitch',
        reason: 'Too early in the awareness cycle; would burn credibility.',
      },
      {
        path: 'Long-form Education',
        reason:
          'Attention spans are compressed right now; quick hits will perform better.',
      },
    ],
  };

  return NextResponse.json(mockRationale);
}
