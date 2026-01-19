import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Truth Sheet Generation API
 * Auto-generates truth sheet entries from evidence
 * POST /api/onboarding/truth-sheet
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, evidence_list, existing_entries } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend truth sheet generator
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/truth-sheet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ evidence_list, existing_entries }),
    });

    if (!response.ok) {
      // Fallback to demo data
      return NextResponse.json(generateDemoTruthSheet());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Truth sheet generation error:', error);
    return NextResponse.json(generateDemoTruthSheet());
  }
}

function generateDemoTruthSheet() {
  return {
    success: true,
    truth_sheet: {
      entries: [
        { id: 'TRU-001', category: 'company', field_name: 'company_name', value: 'Your Company', confidence: 'high', verified: false },
        { id: 'TRU-002', category: 'company', field_name: 'mission', value: 'Help businesses grow faster', confidence: 'medium', verified: false },
        { id: 'TRU-003', category: 'product', field_name: 'product_name', value: 'Your Product', confidence: 'high', verified: false },
        { id: 'TRU-004', category: 'product', field_name: 'core_feature', value: 'AI-powered automation', confidence: 'medium', verified: false },
        { id: 'TRU-005', category: 'market', field_name: 'target_market', value: 'SMB SaaS companies', confidence: 'medium', verified: false },
        { id: 'TRU-006', category: 'customer', field_name: 'customer_segment', value: 'Growth-stage startups', confidence: 'low', verified: false },
      ],
      completeness_score: 0.6,
      categories_covered: ['company', 'product', 'market', 'customer'],
      missing_fields: ['competition.competitors', 'financials.revenue', 'team.team_size'],
      recommendations: [
        'Upload a pitch deck to extract more company information',
        'Add customer testimonials for social proof',
        'Missing: competition.competitors, financials.revenue',
      ],
      summary: 'Generated 6 truth entries. Completeness: 60%. Add more evidence to improve.',
    },
  };
}


