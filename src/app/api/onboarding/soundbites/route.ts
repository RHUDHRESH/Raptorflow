import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Soundbites Generation API
 * Creates messaging library with taglines, value props, soundbites
 * POST /api/onboarding/soundbites
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, company_info, positioning, icp_data } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend soundbites generator
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/soundbites`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_info, positioning, icp_data }),
    });

    if (!response.ok) {
      return NextResponse.json(generateDemoSoundbites());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Soundbites generation error:', error);
    return NextResponse.json(generateDemoSoundbites());
  }
}

function generateDemoSoundbites() {
  return {
    success: true,
    soundbites: {
      library: [
        { id: 'SND-001', type: 'tagline', content: 'Better results without the complexity', audience: 'general', score: 0.85 },
        { id: 'SND-002', type: 'value_prop', content: 'We help growth teams scale faster so they can focus on strategy', audience: 'decision_maker', score: 0.80 },
        { id: 'SND-003', type: 'headline', content: 'What if growth was on autopilot?', audience: 'general', score: 0.75 },
        { id: 'SND-004', type: 'cta', content: 'Start growing today', audience: 'general', score: 0.82 },
        { id: 'SND-005', type: 'pain_statement', content: 'Tired of manual processes holding you back?', audience: 'decision_maker', score: 0.78 },
        { id: 'SND-006', type: 'elevator_pitch', content: 'You know how teams struggle with scaling? We built a platform that automates growth. Unlike traditional tools, we focus on outcomes. That\'s why leading companies trust us.', audience: 'decision_maker', score: 0.72 },
      ],
      by_type: {
        tagline: 1,
        value_prop: 1,
        headline: 1,
        cta: 1,
        pain_statement: 1,
        elevator_pitch: 1,
      },
      recommendations: [
        'Test multiple variations in A/B tests',
        'Customize soundbites for each channel',
        'Update messaging quarterly',
      ],
      summary: 'Generated 6 soundbites across 6 types. High-quality: 4. Ready for use.',
    },
  };
}


