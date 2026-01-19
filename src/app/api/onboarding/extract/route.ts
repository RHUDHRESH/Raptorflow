/**
 * API Route: /api/onboarding/extract
 * Forwards extraction requests to the backend AI service
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { session_id, evidence_list } = body;

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Call the backend extract-facts endpoint
        const response = await fetch(`${apiUrl}/api/v1/onboarding/${session_id}/extract-facts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Forward auth header if present
                ...(request.headers.get('Authorization') && {
                    'Authorization': request.headers.get('Authorization')!
                })
            },
            body: JSON.stringify(evidence_list),
        });

        if (!response.ok) {
            console.error(`Backend extraction failed: ${response.status} ${response.statusText}`);
            // Return empty facts so frontend can handle gracefully
            return NextResponse.json({
                facts: [],
                error: `Backend error: ${response.statusText}`
            });
        }

        const result = await response.json();

        // Map backend response to frontend expected format
        return NextResponse.json({
            facts: result.extraction_result?.facts || result.facts || [],
            success: result.success || true
        });

    } catch (error) {
        console.error('Extraction API error:', error);
        return NextResponse.json({
            facts: [],
            error: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}
