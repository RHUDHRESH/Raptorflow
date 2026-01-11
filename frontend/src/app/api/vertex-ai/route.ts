import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(request: Request) {
  try {
    const { prompt, model = 'gemini-pro', user_id = 'user-bypass' } = await request.json();

    // Bypass subscription check - always allow access
    console.log('AI request received (bypass mode):', { prompt_length: prompt.length, model });

    // Call Vertex AI backend
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8080';
    const response = await fetch(`${backendUrl}/ai/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        model,
        user_id: user_id || 'user-bypass'
      })
    });

    if (!response.ok) {
      throw new Error('AI service unavailable');
    }

    const result = await response.json();

    // Log usage (optional, for analytics)
    try {
      await supabase
        .from('ai_usage_logs')
        .insert({
          user_id: user_id || 'user-bypass',
          model,
          prompt_length: prompt.length,
          response_length: result.content?.length || 0,
          timestamp: new Date().toISOString()
        });
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
