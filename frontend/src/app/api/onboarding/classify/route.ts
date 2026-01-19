import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Evidence Classification API
 * Connects to backend EvidenceClassifier agent
 * POST /api/onboarding/classify
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, evidence, evidence_data } = body;
    const evidencePayload = evidence_data || evidence;

    if (!session_id || !evidencePayload) {
      return NextResponse.json(
        { error: 'Missing session_id or evidence' },
        { status: 400 }
      );
    }

    // Call backend evidence classifier
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/classify-evidence`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(evidencePayload),
    });

    if (!response.ok) {
      // Fallback to local classification if backend unavailable
      const classification = classifyEvidence(evidencePayload);
      return NextResponse.json({ classification, fallback: true });
    }

    const data = await response.json();
    return NextResponse.json({
      classification: data.classification || data,
      success: data.success || true,
    });
  } catch (error) {
    console.error('Evidence classification error:', error);
    // Fallback to local classification
    try {
      const body = await request.clone().json();
      const classification = classifyEvidence(body.evidence_data || body.evidence);
      return NextResponse.json({ classification, fallback: true });
    } catch {
      return NextResponse.json(
        { error: 'Classification failed' },
        { status: 500 }
      );
    }
  }
}

// Local fallback classification
function classifyEvidence(evidence: {
  filename?: string;
  content_type?: string;
  extracted_text?: string;
  url?: string;
}) {
  const filename = (evidence.filename || '').toLowerCase();
  const contentType = evidence.content_type || '';
  const text = (evidence.extracted_text || '').toLowerCase();

  type EvidenceType = 'pitch_deck' | 'product_screenshot' | 'website_content' | 
    'financial_document' | 'legal_document' | 'marketing_material' | 
    'user_testimonial' | 'competitor_analysis' | 'market_research' | 'other';

  let evidenceType: EvidenceType = 'other';
  let confidence = 0.5;
  const keyIndicators: string[] = [];

  // Pitch deck detection
  if (filename.includes('pitch') || filename.includes('deck') || filename.includes('investor')) {
    evidenceType = 'pitch_deck';
    confidence = 0.85;
    keyIndicators.push('Filename indicates pitch deck');
  }
  // Product screenshot detection
  else if (contentType.startsWith('image/') || filename.includes('screenshot') || filename.includes('ui')) {
    evidenceType = 'product_screenshot';
    confidence = 0.8;
    keyIndicators.push('Image file detected');
  }
  // Website content
  else if (evidence.url || filename.includes('html') || contentType.includes('html')) {
    evidenceType = 'website_content';
    confidence = 0.75;
    keyIndicators.push('URL or HTML content detected');
  }
  // Financial document
  else if (filename.includes('financial') || filename.includes('revenue') || filename.includes('p&l')) {
    evidenceType = 'financial_document';
    confidence = 0.8;
    keyIndicators.push('Financial keywords in filename');
  }
  // Legal document
  else if (filename.includes('terms') || filename.includes('policy') || filename.includes('agreement')) {
    evidenceType = 'legal_document';
    confidence = 0.8;
    keyIndicators.push('Legal document keywords detected');
  }
  // Marketing material
  else if (filename.includes('brand') || filename.includes('marketing') || filename.includes('brochure')) {
    evidenceType = 'marketing_material';
    confidence = 0.75;
    keyIndicators.push('Marketing keywords in filename');
  }
  // Testimonial
  else if (filename.includes('testimonial') || filename.includes('review') || filename.includes('feedback')) {
    evidenceType = 'user_testimonial';
    confidence = 0.75;
    keyIndicators.push('Testimonial keywords detected');
  }
  // Competitor analysis
  else if (filename.includes('competitor') || filename.includes('comparison') || filename.includes('analysis')) {
    evidenceType = 'competitor_analysis';
    confidence = 0.75;
    keyIndicators.push('Competitor analysis keywords');
  }
  // Market research
  else if (filename.includes('research') || filename.includes('market') || filename.includes('survey')) {
    evidenceType = 'market_research';
    confidence = 0.7;
    keyIndicators.push('Market research keywords');
  }

  return {
    type: evidenceType,
    confidence,
    reasoning: `Classified as ${evidenceType} with ${(confidence * 100).toFixed(0)}% confidence`,
    key_indicators: keyIndicators,
  };
}


