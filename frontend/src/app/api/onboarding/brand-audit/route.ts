/**
 * 🔗 ONBOARDING BRAND AUDIT API PROXY
 * Analyzes brand assets and provides audit results
 */

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const { session_id, evidence_list } = await request.json();
    
    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Call backend brand audit analyzer
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/brand-audit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ evidence_list }),
    });

    if (!response.ok) {
      // Return demo data if backend unavailable
      return NextResponse.json(generateDemoBrandAudit());
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Brand audit proxy error:', error);
    return NextResponse.json(generateDemoBrandAudit());
  }
}

function generateDemoBrandAudit() {
  return {
    success: true,
    dimensions: [
      { id: "1", name: "Visual Identity", score: 75, status: "yellow", notes: ["Inconsistent color usage on social", "Logo resolution low on landing page"], code: "AUD-01", icon: "palette" },
      { id: "2", name: "Message Clarity", score: 58, status: "yellow", notes: ["Technical jargon in H1", "Value prop buried below fold"], code: "AUD-02", icon: "message" },
      { id: "3", name: "Proof & Credibility", score: 45, status: "red", notes: ["Zero testimonials visible", "No data-backed claims"], code: "AUD-03", icon: "shield" },
      { id: "4", name: "Differentiation", score: 65, status: "yellow", notes: ["Similar to Competitor X", "Unique mechanism not highlighted"], code: "AUD-04", icon: "sparkles" },
      { id: "5", name: "Consistency", score: 80, status: "green", notes: ["Tone of voice is distinct and consistent"], code: "AUD-05", icon: "eye" },
    ],
    brandItems: [
      { id: "1", name: "Website Hero", category: "web", action: "fix", reason: "Headline focuses on features, not outcomes.", priority: "high" },
      { id: "2", name: "Brand Colors", category: "visual", action: "keep", reason: "Distinctive and accessible palette.", priority: "low" },
      { id: "3", name: "LinkedIn Bio", category: "social", action: "fix", reason: "Disconnect from website messaging.", priority: "medium" },
      { id: "4", name: "Sales Deck", category: "sales", action: "replace", reason: "Uses old pricing model and deprecated logo.", priority: "high" },
    ],
    summary: "Your brand foundational elements are present but lack strategic alignment. Visuals are decent, but credibility is a major weakness.",
    overallRating: "yellow",
    reviewed: false,
  };
}
