import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Messaging Rules API
 * Generates brand messaging guardrails
 * POST /api/onboarding/messaging-rules
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, company_info, positioning } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend messaging rules engine
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/messaging-rules`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_info, positioning }),
    });

    if (!response.ok) {
      return NextResponse.json(generateDemoRules());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Messaging rules error:', error);
    return NextResponse.json(generateDemoRules());
  }
}

function generateDemoRules() {
  return {
    success: true,
    messaging_rules: {
      rules: [
        { id: 'RUL-TONE-001', category: 'tone', name: 'Avoid Aggressive Language', severity: 'warning', status: 'active' },
        { id: 'RUL-CLAIM-001', category: 'claims', name: 'Avoid Unverified Superlatives', severity: 'warning', status: 'active' },
        { id: 'RUL-COMP-001', category: 'competitors', name: 'No Direct Competitor Bashing', severity: 'warning', status: 'active' },
        { id: 'RUL-LANG-001', category: 'language', name: 'Avoid Jargon Overload', severity: 'suggestion', status: 'active' },
        { id: 'RUL-LEGAL-001', category: 'legal', name: 'Avoid Guarantee Language', severity: 'error', status: 'active' },
      ],
      rule_count: 5,
      categories_covered: ['tone', 'claims', 'competitors', 'language', 'legal'],
      recommendations: [
        'Review all rules with your marketing team',
        'Customize rules based on your brand voice',
        'Run existing content through the checker',
      ],
      summary: 'Generated 5 messaging rules across 5 categories.',
    },
  };
}


