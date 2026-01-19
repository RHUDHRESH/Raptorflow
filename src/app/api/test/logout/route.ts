import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function POST(request: Request) {
  try {
    const { access_token } = await request.json();
    
    if (!access_token) {
      return NextResponse.json(
        { error: 'Access token required' },
        { status: 400 }
      );
    }

    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    // Set the session and then sign out
    const { error } = await supabase.auth.setSession({
      access_token,
      refresh_token: ''
    });

    if (error) {
      return NextResponse.json({
        success: false,
        error: 'Invalid session',
        details: error.message
      });
    }

    // Sign out
    const { error: signOutError } = await supabase.auth.signOut();

    if (signOutError) {
      return NextResponse.json({
        success: false,
        error: 'Sign out failed',
        details: signOutError.message
      });
    }

    return NextResponse.json({
      success: true,
      message: 'Logout successful'
    });

  } catch (error) {
    console.error('Logout test error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'POST to test logout',
    body: {
      access_token: 'eyJhbGciOiJIUzI1NiIs...'
    }
  });
}
