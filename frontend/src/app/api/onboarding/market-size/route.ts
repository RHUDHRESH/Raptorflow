import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Market Size Calculator API
 * Calculates TAM/SAM/SOM with beautiful visualization data
 * POST /api/onboarding/market-size
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, company_info } = body;

    if (!session_id || !company_info) {
      return NextResponse.json(
        { error: 'Missing session_id or company_info' },
        { status: 400 }
      );
    }

    // Call backend market size calculator
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/market-size`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(company_info),
    });

    if (!response.ok) {
      // Fallback to local calculation if backend unavailable
      const marketSize = calculateMarketSizeFallback(company_info);
      return NextResponse.json(marketSize);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Market size calculation error:', error);
    // Fallback to local calculation
    try {
      const body = await request.clone().json();
      const marketSize = calculateMarketSizeFallback(body.company_info);
      return NextResponse.json(marketSize);
    } catch {
      return NextResponse.json(
        { error: 'Market size calculation failed' },
        { status: 500 }
      );
    }
  }
}

// Local fallback calculation
function calculateMarketSizeFallback(companyInfo: {
  industry?: string;
  target_market?: string;
  market_scope?: string;
}) {
  const industry = (companyInfo.industry || 'saas').toLowerCase();
  
  // Industry benchmarks (simplified)
  const benchmarks: Record<string, { tam: number; samPct: number; somPct: number; growth: number }> = {
    saas: { tam: 50_000_000_000, samPct: 0.15, somPct: 0.02, growth: 0.12 },
    fintech: { tam: 100_000_000_000, samPct: 0.10, somPct: 0.01, growth: 0.15 },
    martech: { tam: 30_000_000_000, samPct: 0.20, somPct: 0.03, growth: 0.10 },
    default: { tam: 20_000_000_000, samPct: 0.15, somPct: 0.02, growth: 0.10 },
  };
  
  const benchmark = benchmarks[industry] || benchmarks.default;
  
  const tam = benchmark.tam;
  const sam = tam * benchmark.samPct;
  const som = sam * benchmark.somPct;
  
  const formatCurrency = (value: number): string => {
    if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
    return `$${value.toLocaleString()}`;
  };

  return {
    success: true,
    market_size: {
      tam: {
        value: tam,
        formatted: formatCurrency(tam),
        description: 'Total market demand for the entire product category',
        confidence: 0.6,
        growth_rate: benchmark.growth,
      },
      sam: {
        value: sam,
        formatted: formatCurrency(sam),
        percentage_of_tam: benchmark.samPct * 100,
        description: 'Market segment you can realistically target',
        confidence: 0.7,
      },
      som: {
        value: som,
        formatted: formatCurrency(som),
        percentage_of_tam: (som / tam) * 100,
        description: 'Realistic market share achievable in 1-3 years',
        confidence: 0.8,
      },
      summary: `The ${industry} market represents a ${formatCurrency(tam)} opportunity. Target capturing ${formatCurrency(som)} in 1-3 years.`,
      recommendations: [
        `Market growing at ${(benchmark.growth * 100).toFixed(0)}% annually`,
        `Focus on ${formatCurrency(som)} achievable market before expanding`,
      ],
      visualization: {
        type: 'concentric',
        circles: [
          { tier: 'TAM', label: 'Total Addressable Market', formatted: formatCurrency(tam), radius: 100, color: '#E8F4F8' },
          { tier: 'SAM', label: 'Serviceable Addressable Market', formatted: formatCurrency(sam), radius: 65, color: '#B8D4E3' },
          { tier: 'SOM', label: 'Serviceable Obtainable Market', formatted: formatCurrency(som), radius: 30, color: '#4A90A4' },
        ],
      },
    },
  };
}


