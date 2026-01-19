/**
 * API Route: /api/onboarding/classify
 * Forwards evidence classification requests to the backend AI service
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { session_id, evidence_data } = body;

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Call the backend classify-evidence endpoint
        const response = await fetch(`${apiUrl}/api/v1/onboarding/${session_id}/classify-evidence`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(request.headers.get('Authorization') && {
                    'Authorization': request.headers.get('Authorization')!
                })
            },
            body: JSON.stringify(evidence_data),
        });

        if (!response.ok) {
            console.error(`Backend classification failed: ${response.status} ${response.statusText}`);
            // Fallback to simple heuristics if backend fails
            return NextResponse.json({
                classification: await getFallbackClassification(evidence_data),
                fallback: true,
                error: `Backend error: ${response.statusText}`
            });
        }

        const result = await response.json();

        return NextResponse.json({
            classification: result.classification || result,
            success: result.success || true
        });

    } catch (error) {
        console.error('Classification API error:', error);
        // Return fallback classification on error
        return NextResponse.json({
            classification: { category: 'other', confidence: 0.3 },
            fallback: true,
            error: error instanceof Error ? error.message : 'Unknown error'
        });
    }
}

async function getFallbackClassification(data: any): Promise<{ category: string; confidence: number }> {
    const fileName = (data.name || data.file_name || '').toLowerCase();

    if (fileName.includes('manifesto') || fileName.includes('brand')) {
        return { category: 'manifesto', confidence: 0.6 };
    } else if (fileName.includes('screenshot') || fileName.includes('ui') || fileName.includes('design')) {
        return { category: 'product_screenshots', confidence: 0.6 };
    } else if (fileName.includes('deck') || fileName.includes('pitch') || fileName.includes('sales')) {
        return { category: 'sales_deck', confidence: 0.6 };
    } else if (fileName.includes('stat') || fileName.includes('proof') || fileName.includes('test')) {
        return { category: 'testimonials', confidence: 0.5 };
    } else if (fileName.includes('comp') || fileName.includes('market')) {
        return { category: 'competitors', confidence: 0.5 };
    }

    return { category: 'other', confidence: 0.3 };
}
