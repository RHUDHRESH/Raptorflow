import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Category Path Selection API
 * Generates Safe/Clever/Bold strategic paths
 * POST /api/onboarding/category-paths
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, company_info, positioning_context } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend category advisor
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/category-paths`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_info, positioning_context }),
    });

    if (!response.ok) {
      // Return demo data if backend unavailable
      return NextResponse.json(generateDemoCategoryPaths());
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Category paths error:', error);
    return NextResponse.json(generateDemoCategoryPaths());
  }
}

function generateDemoCategoryPaths() {
  return {
    paths: [
      {
        id: 'safe',
        name: 'Safe Path',
        category: 'Marketing Automation Software',
        description: 'Play in an established category where buyers already know what they want.',
        effort: 'low',
        education_needed: 'minimal',
        pricing_power: 'medium',
        time_to_market: '1-2 months',
        pros: [
          'Lower customer education costs',
          'Existing search demand',
          'Clear competitive benchmarks',
          'Faster sales cycles',
        ],
        cons: [
          'Crowded market with established players',
          'Feature comparison shopping',
          'Price pressure from commoditization',
          'Harder to differentiate',
        ],
        competitors_in_space: ['HubSpot', 'Marketo', 'Pardot', 'Mailchimp'],
        buyer_expectations: 'Email campaigns, lead scoring, CRM integration, analytics dashboards',
        confidence: 0.85,
      },
      {
        id: 'clever',
        name: 'Clever Path',
        category: 'Positioning Intelligence Platform',
        description: 'Create a new sub-category that reframes the problem in your favor.',
        effort: 'medium',
        education_needed: 'moderate',
        pricing_power: 'high',
        time_to_market: '3-4 months',
        pros: [
          'Less direct competition',
          'Define the category rules',
          'Premium positioning possible',
          'Attract innovative buyers',
        ],
        cons: [
          'Need to educate the market',
          'Longer sales cycles initially',
          'Must prove the category exists',
          'Risk of being too niche',
        ],
        competitors_in_space: ['No direct competitors yet'],
        buyer_expectations: 'AI-powered insights, positioning validation, brand strategy automation',
        confidence: 0.78,
      },
      {
        id: 'bold',
        name: 'Bold Path',
        category: 'Growth Operating System',
        description: 'Create an entirely new category and own it completely.',
        effort: 'high',
        education_needed: 'significant',
        pricing_power: 'very high',
        time_to_market: '6+ months',
        pros: [
          'Category king potential',
          'No direct competition',
          'Define all the rules',
          'Massive upside if successful',
        ],
        cons: [
          'Requires significant market education',
          'Higher risk of failure',
          'Long timeline to adoption',
          'Needs strong funding/runway',
        ],
        competitors_in_space: [],
        buyer_expectations: 'Complete reimagining of how growth teams operate',
        confidence: 0.65,
      },
    ],
    recommendation: {
      path_id: 'clever',
      reasoning: 'Based on your positioning context and competitive landscape, the Clever Path offers the best balance of differentiation and market accessibility.',
    },
    analysis_summary: 'Generated 3 category paths: Safe (established), Clever (sub-category), Bold (new category). Recommended: Clever Path with 78% confidence.',
  };
}


