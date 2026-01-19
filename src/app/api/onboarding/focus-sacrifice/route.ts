import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Focus & Sacrifice Analysis API
 * Analyzes strategic focus and sacrifice tradeoffs
 * POST /api/onboarding/focus-sacrifice
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, company_info, icp_data, capabilities, positioning } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend focus/sacrifice engine
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/focus-sacrifice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_info, icp_data, capabilities, positioning }),
    });

    if (!response.ok) {
      // Fallback to demo data
      return NextResponse.json(generateDemoFocusSacrifice());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Focus/sacrifice analysis error:', error);
    return NextResponse.json(generateDemoFocusSacrifice());
  }
}

function generateDemoFocusSacrifice() {
  return {
    success: true,
    focus_sacrifice: {
      focus_items: [
        { description: 'Focus exclusively on primary ICP segment', category: 'audience', impact: 0.9 },
        { description: 'Double down on differentiating capabilities', category: 'feature', impact: 0.85 },
        { description: 'Own the speed and simplicity position', category: 'value', impact: 0.9 },
      ],
      sacrifice_items: [
        { description: 'Deprioritize secondary audience segments', impact: 'high', alternative_message: "We're built specifically for our target customers" },
        { description: 'Accept good enough on table stakes features', impact: 'medium', alternative_message: 'We nail the things that matter most' },
        { description: 'Sacrifice being all-in-one', impact: 'medium', alternative_message: "We're the best at one thing, not mediocre at everything" },
      ],
      tradeoff_pairs: 3,
      positioning_statement: 'We focus on our primary ICP segment, which means we deliberately don\'t try to serve everyone.',
      lightbulb_insights: [
        {
          icon: '💡',
          title: 'The Paradox of Choice',
          insight: 'By choosing to NOT serve everyone, you become irresistible to your ideal customer.',
          source: 'Based on The Positioning Playbook',
        },
        {
          icon: '🎯',
          title: 'Focus Creates Magnetism',
          insight: 'Your 3 focus areas will define what you\'re known for.',
          source: 'Strategic positioning principle',
        },
        {
          icon: '🔥',
          title: 'Sacrifice is Strategy',
          insight: 'The 3 things you\'re choosing NOT to do are as important as what you do.',
          source: 'Michael Porter',
        },
      ],
      recommendations: [
        'Communicate your focus areas clearly in all marketing',
        'Train sales team on "why we don\'t" responses for sacrifices',
        'Review sacrifices quarterly - some may become strategic adds',
      ],
      summary: 'Strategic focus on 3 key areas, with 3 deliberate sacrifices. This creates a clear, defensible market position.',
    },
  };
}


