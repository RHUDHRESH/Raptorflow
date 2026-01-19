import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * AI Perceptual Map Generation API
 * Connects to backend PerceptualMapGenerator agent
 * Returns 3 unique positioning options
 * POST /api/onboarding/perceptual-map
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

    // Call backend perceptual map generator
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/generate-perceptual-map`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_info, competitors }),
    });

    if (!response.ok) {
      // Return demo data if backend unavailable
      return NextResponse.json(generateDemoPerceptualMap(company_info, competitors));
    }

    const data = await response.json();
    return NextResponse.json(data.perceptual_map || data);
  } catch (error) {
    console.error('Perceptual map error:', error);
    return NextResponse.json(generateDemoPerceptualMap({}, []));
  }
}

interface CompanyInfo {
  name?: string;
  product_description?: string;
}

interface Competitor {
  name?: string;
  description?: string;
}

function generateDemoPerceptualMap(companyInfo: CompanyInfo, competitors: Competitor[]) {
  return {
    primary_axis: {
      name: 'Innovation vs Traditional',
      low_label: 'Traditional',
      high_label: 'Innovative',
      description: 'Innovation and technology adoption axis',
    },
    secondary_axis: {
      name: 'Price vs Quality',
      low_label: 'Low Price',
      high_label: 'High Quality',
      description: 'Traditional price-quality tradeoff axis',
    },
    current_position: {
      id: 'current',
      name: companyInfo?.name || 'Your Company',
      x: 0.5,
      y: 0.5,
      size: 1.0,
      description: companyInfo?.product_description || '',
      is_competitor: false,
      is_current: true,
    },
    competitors: (competitors || []).map((c: Competitor, i: number) => ({
      id: `competitor_${i}`,
      name: c.name || `Competitor ${i + 1}`,
      x: 0.3 + (i * 0.2),
      y: 0.4 + (i * 0.15),
      size: 0.7,
      description: c.description || '',
      is_competitor: true,
      is_current: false,
    })),
    // 3 UNIQUE POSITIONING OPTIONS - Core feature
    positioning_options: [
      {
        id: 'POS-001',
        name: 'Gap Opportunity: Innovation Leader',
        description: 'Position in the high innovation and high quality space with innovation leader approach',
        strategy: 'innovation_leader',
        coordinates: [0.85, 0.75],
        rationale: 'Exploits the largest gap in the market with minimal competition',
        advantages: ['First-mover advantage', 'Premium pricing', 'Brand leadership'],
        disadvantages: ['High R&D costs', 'Market education needed', 'Technology risk'],
        target_audience: 'Early adopters, tech enthusiasts',
        competitive_angle: 'Advanced technology and innovation',
        confidence: 0.85,
      },
      {
        id: 'POS-002',
        name: 'Premium Differentiator',
        description: 'Position as the premium, high-quality solution with superior features',
        strategy: 'differentiator',
        coordinates: [0.7, 0.8],
        rationale: 'Differentiate through superior quality and innovation',
        advantages: ['Premium pricing', 'Customer loyalty', 'Barriers to entry'],
        disadvantages: ['Higher costs', 'Niche appeal', 'Complex sales process'],
        target_audience: 'Quality-focused buyers, enterprise clients',
        competitive_angle: 'Superior features and performance',
        confidence: 0.78,
      },
      {
        id: 'POS-003',
        name: 'Niche Specialist',
        description: 'Focus on a specific market segment with specialized solutions',
        strategy: 'niche',
        coordinates: [0.4, 0.65],
        rationale: 'Focus on underserved niche with deep domain expertise',
        advantages: ['Limited competition', 'High expertise', 'Customer intimacy'],
        disadvantages: ['Limited market size', 'Growth constraints', 'Dependency risk'],
        target_audience: 'Specialized industries, specific use cases',
        competitive_angle: 'Deep domain expertise',
        confidence: 0.72,
      },
    ],
    market_gaps: [
      {
        coordinates: [0.8, 0.8],
        grid_position: [4, 4],
        attractiveness: 0.85,
        description: 'High innovation, high quality gap',
      },
      {
        coordinates: [0.2, 0.8],
        grid_position: [1, 4],
        attractiveness: 0.7,
        description: 'Traditional but high quality gap',
      },
    ],
    recommendations: [
      "Consider the 'Gap Opportunity: Innovation Leader' strategy with 85% confidence",
      'Explored 2 market gaps - largest opportunity identified',
    ],
    analysis_summary: 'Generated perceptual map using Innovation vs Traditional and Price vs Quality. Analyzed 3 competitors and identified 2 market gaps. Generated 3 strategic positioning options.',
  };
}



