import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Channel Strategy API
 * Connects to backend ChannelRecommender agent
 * POST /api/onboarding/channel-strategy
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, company_info, competitors } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend channel recommender
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/channel-strategy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_info, competitors }),
    });

    if (!response.ok) {
      // Return demo data if backend unavailable
      return NextResponse.json(generateDemoChannelStrategy(company_info));
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Channel strategy error:', error);
    return NextResponse.json(generateDemoChannelStrategy({}));
  }
}

interface CompanyInfo {
  business_model?: string;
}

function generateDemoChannelStrategy(companyInfo: CompanyInfo) {
  const businessModel = companyInfo?.business_model || 'B2B SaaS';

  return {
    strategy: {
      recommendations: [
        {
          id: 'CHAN-001',
          channel: 'content_marketing',
          priority: 'high',
          confidence_score: 0.88,
          estimated_cost: 'Medium',
          time_to_results: '2-4 months',
          required_resources: ['Content writers', 'Subject matter experts', 'Distribution'],
          target_audience_match: 0.88,
          competitive_advantage: 'Educates prospects',
          implementation_steps: [
            'Set up content marketing infrastructure',
            'Define success metrics: Lead generation, Content engagement',
            'Allocate resources: Content writers, Subject matter experts',
            'Create initial content/campaigns',
            'Launch and monitor performance',
          ],
          success_metrics: ['Lead generation', 'Content engagement', 'Thought leadership'],
          rationale: `Recommended for ${businessModel} businesses. Fit score: 88%. Key advantages: Educates prospects, Builds authority.`,
        },
        {
          id: 'CHAN-002',
          channel: 'search_engine',
          priority: 'high',
          confidence_score: 0.85,
          estimated_cost: 'Medium to High',
          time_to_results: '3-6 months',
          required_resources: ['SEO specialist', 'content team', 'technical resources'],
          target_audience_match: 0.85,
          competitive_advantage: 'Sustainable',
          implementation_steps: [
            'Set up search engine infrastructure',
            'Define success metrics: Organic traffic, Keyword rankings',
            'Allocate resources: SEO specialist, content team',
            'Create initial content/campaigns',
            'Launch and monitor performance',
          ],
          success_metrics: ['Organic traffic', 'Keyword rankings', 'Conversion rate'],
          rationale: `Recommended for ${businessModel} businesses. Fit score: 85%. Key advantages: Sustainable, High intent traffic.`,
        },
        {
          id: 'CHAN-003',
          channel: 'email_marketing',
          priority: 'high',
          confidence_score: 0.82,
          estimated_cost: 'Low',
          time_to_results: '1-2 months',
          required_resources: ['Email platform', 'Copywriter', 'List building'],
          target_audience_match: 0.82,
          competitive_advantage: 'High ROI',
          implementation_steps: [
            'Set up email marketing infrastructure',
            'Define success metrics: Open rate, Click-through rate',
            'Allocate resources: Email platform, Copywriter',
            'Create initial content/campaigns',
            'Launch and monitor performance',
          ],
          success_metrics: ['Open rate', 'Click-through rate', 'Conversion rate'],
          rationale: `Recommended for ${businessModel} businesses. Fit score: 82%. Key advantages: High ROI, Direct communication.`,
        },
      ],
      budget_allocation: {
        content_marketing: 35,
        search_engine: 30,
        email_marketing: 20,
        direct_sales: 15,
      },
      timeline: {
        content_marketing: '2-4 months',
        search_engine: '3-6 months',
        email_marketing: '1-2 months',
        direct_sales: '2-4 months',
      },
      resource_requirements: {
        content_marketing: ['Content writers', 'Subject matter experts', 'Distribution'],
        search_engine: ['SEO specialist', 'content team', 'technical resources'],
        email_marketing: ['Email platform', 'Copywriter', 'List building'],
      },
      synergy_opportunities: [
        'Content marketing supports SEO and social media',
        'Email marketing nurtures leads from all channels',
        'Social media amplifies content and PR efforts',
        'Community building enhances retention across channels',
      ],
      risk_assessment: {
        high_priority: 'Resource intensive but high potential',
        medium_priority: 'Balanced risk/reward profile',
        low_priority: 'Lower investment, slower results',
        experimental: 'High uncertainty, learning opportunity',
      },
      expected_roi: {
        content_marketing: 2.5,
        search_engine: 3.5,
        email_marketing: 4.0,
        direct_sales: 5.0,
      },
      implementation_roadmap: [
        {
          channel: 'email_marketing',
          start_month: 1,
          duration_months: 2,
          priority: 'high',
          key_activities: ['Set up email platform', 'Create welcome sequence', 'Build initial list'],
          success_metrics: ['Open rate', 'Click-through rate'],
          estimated_cost: 'Low',
        },
        {
          channel: 'content_marketing',
          start_month: 1,
          duration_months: 3,
          priority: 'high',
          key_activities: ['Define content strategy', 'Create pillar content', 'Set up distribution'],
          success_metrics: ['Lead generation', 'Content engagement'],
          estimated_cost: 'Medium',
        },
        {
          channel: 'search_engine',
          start_month: 2,
          duration_months: 4,
          priority: 'high',
          key_activities: ['Technical SEO audit', 'Keyword research', 'Content optimization'],
          success_metrics: ['Organic traffic', 'Keyword rankings'],
          estimated_cost: 'Medium to High',
        },
      ],
    },
    market_insights: [
      `Business model: ${businessModel}`,
      'Multi-channel approach recommended for diversification',
      'Focus on channels with highest audience match first',
      'Consider budget constraints in prioritization',
    ],
    competitor_channels: [
      {
        competitor: 'Competitor A',
        channels: ['Content Marketing', 'SEO', 'Social Media'],
        estimated_spend: '$50K-$100K monthly',
        strengths: ['Strong content', 'Good SEO', 'Brand recognition'],
      },
    ],
    seasonal_trends: {
      Q1: ['Planning season, B2B budget allocation'],
      Q2: ['Summer slowdown, focus on nurturing'],
      Q3: ['Back to school, B2C ramp up'],
      Q4: ['Holiday season, year-end push'],
    },
    recommendations_summary: 'Generated 3 high-priority channel recommendations. Top recommendation: Content Marketing with 88% confidence.',
    next_steps: [
      'Prioritize Content Marketing for immediate implementation',
      'Allocate budget according to recommended percentages',
      'Hire or train resources for key channels',
      'Set up tracking and analytics for all channels',
      'Create content calendar for content-heavy channels',
    ],
  };
}



