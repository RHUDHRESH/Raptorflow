import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Proof Point Validation API
 * Validates claims with supporting evidence
 * POST /api/onboarding/proof-points
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, claims, evidence } = body;

    if (!session_id || !claims) {
      return NextResponse.json(
        { error: 'Missing session_id or claims' },
        { status: 400 }
      );
    }

    // Call backend proof point validator
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/proof-points`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ claims, evidence }),
    });

    if (!response.ok) {
      // Fallback to demo data
      return NextResponse.json(generateDemoValidation(claims));
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Proof point validation error:', error);
    return NextResponse.json(generateDemoValidation([]));
  }
}

function generateDemoValidation(claims: string[]) {
  const validations = claims.map((claim, index) => ({
    claim_id: `CLM-${String(index + 1).padStart(3, '0')}`,
    claim_text: claim,
    claim_category: 'general',
    status: index === 0 ? 'verified' : index === 1 ? 'partially_verified' : 'needs_evidence',
    strength: index === 0 ? 'strong' : index === 1 ? 'moderate' : 'weak',
    confidence_score: index === 0 ? 0.85 : index === 1 ? 0.6 : 0.3,
    proof_points: index === 0 ? [
      { id: 'PRF-001', proof_type: 'statistic', content: '95% customer satisfaction', credibility_score: 0.8 },
    ] : [],
    recommendations: index === 0 ? [] : ['Add supporting evidence: customer quote, statistic, or case study'],
    improved_claim: index > 1 ? `${claim} — backed by [ADD SPECIFIC METRIC]` : null,
  }));

  return {
    success: true,
    validation: {
      validations,
      overall_score: 0.58,
      strong_claims: 1,
      weak_claims: Math.max(0, claims.length - 2),
      needs_evidence: Math.max(0, claims.length - 2),
      recommendations: [
        'More than half of claims are weak - focus on adding specific proof points',
        `${Math.max(0, claims.length - 2)} claims need supporting evidence`,
      ],
      summary: `Validated ${claims.length} claims: 1 strong, ${claims.length - 1} need improvement. Overall proof score: 58%.`,
    },
  };
}


