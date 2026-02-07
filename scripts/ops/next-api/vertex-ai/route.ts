import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    return null;
  }

  return createClient(url, key);
}

export async function POST(request: Request) {
  try {
    const { prompt, model = 'gemini-pro', user_id = 'user-bypass', max_tokens, temperature } = await request.json();

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      );
    }

    // Bypass subscription check - always allow access
    console.log('AI request received (bypass mode):', { prompt_length: prompt.length, model });

    // Call Vertex AI backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';
    const authHeader = request.headers.get('authorization') || request.headers.get('Authorization');

    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }

    const response = await fetch(`${backendUrl}/api/v1/ai/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify({
        prompt,
        model,
        max_tokens,
        temperature,
        user_id: user_id || 'user-bypass',
      })
    });

    if (!response.ok) {
      throw new Error('AI service unavailable');
    }

    const result = await response.json();

    // Log usage (optional, for analytics)
    try {
      const supabase = getSupabase();
      if (supabase) {
        await supabase
          .from('ai_usage_logs')
          .insert({
            user_id: user_id || 'user-bypass',
            model,
            prompt_length: prompt.length,
            response_length: result.content?.length || 0,
            timestamp: new Date().toISOString()
          });
      }
    } catch (logError) {
      // Ignore logging errors
      console.log('Logging error (non-critical):', logError);
    }

    return NextResponse.json(result);

  } catch (error: any) {
    console.error('Vertex AI error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
