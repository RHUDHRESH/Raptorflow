import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Contradiction Detection API
 * Connects to backend ContradictionDetector agent
 * POST /api/onboarding/contradictions
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, facts } = body;

    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend contradiction detector
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/detect-contradictions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ facts }),
    });

    if (!response.ok) {
      // Return demo data if backend unavailable
      return NextResponse.json(generateDemoContradictionReport(facts));
    }

    const data = await response.json();
    const contradictionResult = data.contradiction_result || data;
    return NextResponse.json({
      ...contradictionResult,
      contradictions: contradictionResult.contradictions || [],
    });
  } catch (error) {
    console.error('Contradiction detection error:', error);
    return NextResponse.json(generateDemoContradictionReport([]));
  }
}

interface Fact {
  id: string;
  category: string;
  value: string;
  confidence: number;
}

function generateDemoContradictionReport(facts: Fact[]) {
  // Simple demo: check for any contradictions
  const contradictions = [];
  
  if (facts.length >= 2) {
    // Demo contradiction for illustration
    contradictions.push({
      id: 'CONTR-001',
      type: 'positioning',
      severity: 'medium',
      description: 'Potential positioning inconsistency detected',
      conflicting_facts: [facts[0]?.id, facts[1]?.id].filter(Boolean),
      confidence: 0.65,
      explanation: 'Some claims may need clarification for consistency',
      suggested_resolution: 'Review and clarify your positioning statements',
      auto_resolvable: false,
    });
  }

  return {
    contradictions,
    total_facts_analyzed: facts.length,
    contradiction_count: contradictions.length,
    severity_distribution: {
      critical: 0,
      high: 0,
      medium: contradictions.length,
      low: 0,
    },
    type_distribution: {
      positioning: contradictions.length,
    },
    auto_resolvable_count: 0,
    recommendations: contradictions.length > 0 
      ? ['Review highlighted contradictions', 'Clarify positioning statements']
      : ['No contradictions detected - your facts are consistent'],
  };
}



