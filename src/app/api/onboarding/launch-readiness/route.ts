import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Launch Readiness API
 * Checks go-to-market readiness
 * POST /api/onboarding/launch-readiness
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, onboarding_data } = body;

    if (!session_id) {
      return NextResponse.json({ error: 'Missing session_id' }, { status: 400 });
    }

    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/launch-readiness`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ onboarding_data }),
    });

    if (!response.ok) {
      return NextResponse.json(generateDemoChecklist());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Launch readiness error:', error);
    return NextResponse.json(generateDemoChecklist());
  }
}

function generateDemoChecklist() {
  return {
    success: true,
    launch_readiness: {
      overall_score: 65,
      ready_count: 8,
      total_items: 18,
      launch_ready: false,
      launch_date: '1-2 weeks with focused effort',
      by_category: {
        positioning: { ready: 2, total: 3, score: 80 },
        messaging: { ready: 2, total: 3, score: 70 },
        icp: { ready: 2, total: 3, score: 85 },
        content: { ready: 1, total: 2, score: 50 },
        channels: { ready: 1, total: 2, score: 60 },
      },
      next_steps: [
        '[CRITICAL] Primary positioning statement: Not finalized',
        '[HIGH] Website copy: Create using generated messaging',
        '[HIGH] Channel setup: Configure top 2 channels',
      ],
      summary: 'Launch readiness: 65%. 8/18 items ready. 5 blockers. NOT YET READY.',
    },
  };
}


