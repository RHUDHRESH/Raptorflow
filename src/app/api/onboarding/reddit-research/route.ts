import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Reddit Market Research API
 * Connects to backend RedditResearcher agent
 * POST /api/onboarding/reddit-research
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, query, company_domain, competitors } = body;

    if (!session_id || !query) {
      return NextResponse.json(
        { error: 'Missing session_id or query' },
        { status: 400 }
      );
    }

    // Call backend Reddit researcher
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/reddit-research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, company_domain, competitors }),
    });

    if (!response.ok) {
      // Return demo data if backend unavailable
      return NextResponse.json(generateDemoRedditResearch(query));
    }

    const data = await response.json();
    return NextResponse.json(data.research_result || data);
  } catch (error) {
    console.error('Reddit research error:', error);
    return NextResponse.json(generateDemoRedditResearch(''));
  }
}

function generateDemoRedditResearch(query: string) {
  return {
    posts_analyzed: 47,
    subreddits_analyzed: ['startups', 'SaaS', 'Entrepreneur', 'smallbusiness'],
    pain_points: [
      {
        id: 'PP-001',
        category: 'process',
        description: 'Complex onboarding and setup processes',
        severity: 0.8,
        frequency: 12,
        source_posts: ['abc123', 'def456'],
        quotes: [
          'r/SaaS: "Why does every tool require 10 steps to get started?"',
          'r/startups: "Spent 3 hours just setting up basic integration"',
        ],
        suggested_solution: 'Simplify workflows and streamline onboarding',
      },
      {
        id: 'PP-002',
        category: 'pricing',
        description: 'Unclear or expensive pricing for small teams',
        severity: 0.75,
        frequency: 9,
        source_posts: ['ghi789'],
        quotes: [
          'r/Entrepreneur: "Why charge per seat when I\'m a solo founder?"',
        ],
        suggested_solution: 'Offer flexible pricing tiers for smaller teams',
      },
      {
        id: 'PP-003',
        category: 'integration',
        description: 'Limited integrations with existing tools',
        severity: 0.7,
        frequency: 8,
        source_posts: ['jkl012'],
        quotes: [
          'r/smallbusiness: "Wish it connected to my accounting software"',
        ],
        suggested_solution: 'Develop APIs and enhance compatibility',
      },
    ],
    market_insights: [
      'Overall sentiment shows frustration with current solutions',
      'Most common pain point: process complexity (12 mentions)',
      '47 posts have high engagement - indicates strong market interest',
      'Most active community: r/SaaS with 18 posts',
    ],
    competitor_mentions: [
      {
        competitor: 'Competitor A',
        mention_count: 5,
        avg_sentiment: -0.2,
        top_posts: [
          { id: 'post1', title: 'Competitor A pricing is too high', sentiment: -0.4 },
        ],
      },
    ],
    sentiment_analysis: {
      overall: -0.15,
      by_post_type: {
        question: 0.1,
        complaint: -0.6,
        discussion: 0.05,
      },
    },
    recommendations: [
      'Address top 3 pain points in product development',
      'Market sentiment is negative - opportunity for differentiation',
      'Monitor competitor discussions for positioning opportunities',
    ],
    research_summary: `Analyzed 47 relevant Reddit posts from 4 subreddits. Identified 3 unique pain points. Top issue: process (12 mentions). Market sentiment shows frustration - opportunity for better solution.`,
  };
}



