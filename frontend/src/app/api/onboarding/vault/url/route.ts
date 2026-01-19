/**
 * 🔗 ONBOARDING VAULT URL API PROXY
 * Proxies URL submissions to backend vault endpoint
 */

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const { session_id, url, title } = await request.json();
    
    if (!session_id || !url) {
      return NextResponse.json(
        { error: 'Missing session_id or url' },
        { status: 400 }
      );
    }

    // Forward to backend
    const response = await fetch(`${API_URL}/api/v1/onboarding/${session_id}/vault/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, title }),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: 'Backend URL submission failed', details: error },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Vault URL proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
