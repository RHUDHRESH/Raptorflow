import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Positioning Statement Generation API
 * Creates strategic positioning statements
 * POST /api/onboarding/positioning
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

    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/positioning`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_info, positioning, icp_data }),
    });

    if (!response.ok) {
      return NextResponse.json(generateDemoPositioning());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Positioning generation error:', error);
    return NextResponse.json(generateDemoPositioning());
  }
}

function generateDemoPositioning() {
  return {
    success: true,
    positioning: {
      statements: [
        {
          id: 'POS-001',
          type: 'full',
          framework: 'classic',
          statement: 'For growth-focused teams who need to scale efficiently, our product is the outcome-driven solution that delivers measurable results. Unlike traditional tools, we focus on outcomes over features.',
          score: 0.85,
        },
        {
          id: 'POS-002',
          type: 'elevator',
          framework: 'benefit_focused',
          statement: 'We help growth teams achieve their goals by focusing on what matters. Unlike alternatives, we measure what counts.',
          score: 0.80,
        },
        {
          id: 'POS-003',
          type: 'tagline',
          framework: 'benefit_focused',
          statement: 'Better results without the complexity.',
          score: 0.78,
        },
      ],
      primary_statement: 'For growth-focused teams who need to scale efficiently, our product is the outcome-driven solution that delivers measurable results.',
      primary_framework: 'classic',
      only_we_claims: [
        'Only we focus on outcomes over features',
        "We're the only solution that measures what matters",
        'No one else takes this outcome-first approach',
      ],
      matrix: {
        axes: ['Price/Value', 'Ease of Use', 'Feature Depth', 'Support Quality'],
        your_position: { 'Price/Value': 8, 'Ease of Use': 9, 'Feature Depth': 7, 'Support Quality': 9 },
        white_space: 'High value + ease of use combination',
      },
      recommendations: [
        'Lead with classic framework in sales conversations',
        'Test tagline variations in A/B tests',
        "Use 'Only We' claims sparingly",
      ],
      summary: 'Generated 3 positioning statements across 5 frameworks. Top framework: classic. Score: 85%.',
    },
  };
}


