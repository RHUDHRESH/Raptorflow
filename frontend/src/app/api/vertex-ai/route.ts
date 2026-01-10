import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(request: Request) {
  try {
    const { prompt, model = 'gemini-pro', user_id } = await request.json();

    // Check if user has active subscription
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('subscription_plan, subscription_status')
      .eq('id', user_id)
      .single();

    if (!profile || profile.subscription_status !== 'active') {
      return NextResponse.json(
        { error: 'Active subscription required for AI features' },
        { status: 403 }
      );
    }

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
        user_id
      })
    });

    if (!response.ok) {
      throw new Error('AI service unavailable');
    }

    const result = await response.json();

    // Log usage to Supabase (or BigQuery in production)
    await supabase
      .from('ai_usage_logs')
      .insert({
        user_id,
        model,
        prompt_length: prompt.length,
        response_length: result.content?.length || 0,
        timestamp: new Date().toISOString()
      });

    return NextResponse.json(result);

  } catch (error: any) {
    console.error('Vertex AI error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
