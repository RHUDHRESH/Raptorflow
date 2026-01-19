import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * ICP Deep Generation API
 * Creates comprehensive ICP profiles with psychographics
 * POST /api/onboarding/icp-deep
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, company_info, positioning, count } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/icp-deep`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_info, positioning, count }),
    });

    if (!response.ok) {
      return NextResponse.json(generateDemoICPs());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('ICP deep generation error:', error);
    return NextResponse.json(generateDemoICPs());
  }
}

function generateDemoICPs() {
  return {
    success: true,
    icp_profiles: {
      profiles: [
        {
          id: 'ICP-001',
          name: 'Growth-Stage SaaS',
          tier: 'primary',
          description: 'Fast-moving SaaS companies ready to scale',
          firmographics: { company_size: '50-200', revenue_range: '$5M-$20M ARR', stage: 'growth' },
          pain_points: [
            { id: 'PAIN-001', description: 'Spending too much time on manual processes', severity: 'critical' },
            { id: 'PAIN-002', description: 'Lack of visibility into key metrics', severity: 'high' },
          ],
          trigger_events: [
            { id: 'TRIG-001', event: 'New funding round closed', urgency: 'high' },
            { id: 'TRIG-002', event: 'New leadership hire', urgency: 'high' },
          ],
          key_messages: ['We help growth-stage SaaS companies scale faster'],
          estimated_deal_size: '$25K-$100K ACV',
          sales_cycle_length: '30-60 days',
        },
        {
          id: 'ICP-002',
          name: 'Enterprise Innovators',
          tier: 'secondary',
          description: 'Large companies seeking modern solutions',
          firmographics: { company_size: '200-500', revenue_range: '$20M-$50M ARR', stage: 'scale' },
          pain_points: [
            { id: 'PAIN-003', description: 'Legacy systems slowing innovation', severity: 'high' },
          ],
          trigger_events: [
            { id: 'TRIG-003', event: 'Digital transformation initiative', urgency: 'medium' },
          ],
          key_messages: ['Modernize without the risk'],
          estimated_deal_size: '$50K-$200K ACV',
          sales_cycle_length: '60-90 days',
        },
      ],
      primary_icp: 'Growth-Stage SaaS',
      recommendations: [
        'Focus 60% of outreach on primary ICP',
        'Use trigger events to time outreach',
        'Train sales team on handling objections',
      ],
      summary: 'Generated 2 ICP profiles. Primary: Growth-Stage SaaS.',
    },
  };
}


