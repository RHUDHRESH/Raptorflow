/**
 * 🔗 ONBOARDING VAULT EVIDENCE API PROXY
 * Retrieves evidence items from vault for processing
 */

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const { session_id } = await request.json();
    
    if (!session_id) {
      return NextResponse.json(
        { error: 'Missing session_id' },
        { status: 400 }
      );
    }

    // Forward to backend
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/vault`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: 'Backend vault fetch failed', details: error },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Vault evidence proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
