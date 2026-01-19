import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();
    
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password required' },
        { status: 400 }
      );
    }

    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    // Test login
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      return NextResponse.json({
        success: false,
        error: error.message,
        type: 'auth_error'
      });
    }

    if (!data.session) {
      return NextResponse.json({
        success: false,
        error: 'No session created',
        type: 'session_error'
      });
    }

    return NextResponse.json({
      success: true,
      message: 'Login successful',
      session: {
        access_token: data.session.access_token.substring(0, 20) + '...',
        expires_at: data.session.expires_at,
        user: {
          id: data.user.id,
          email: data.user.email,
          confirmed_at: data.user.confirmed_at
        }
      }
    });

  } catch (error) {
    console.error('Login test error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        type: 'server_error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'POST to test login',
    body: {
      email: 'test@example.com',
      password: 'TestPassword123'
    }
  });
}
