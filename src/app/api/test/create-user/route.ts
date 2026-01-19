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
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );

    // Create user using service role
    const { data, error } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true, // Auto-confirm for testing
      user_metadata: {
        is_active: true,
        role: 'user'
      }
    });

    if (error) {
      if (error.message.includes('already registered')) {
        // User exists, just return success
        return NextResponse.json({
          success: true,
          message: 'User already exists',
          email
        });
      }
      throw error;
    }

    // Create profile record
    if (data.user) {
      const { error: profileError } = await supabase
        .from('profiles')
        .upsert({
          id: data.user.id,
          email: data.user.email,
          is_active: true,
          role: 'user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });

      if (profileError) {
        console.error('Profile creation error:', profileError);
      }
    }

    return NextResponse.json({
      success: true,
      message: 'Test user created successfully',
      user: {
        id: data.user?.id,
        email: data.user?.email,
        confirmed_at: data.user?.confirmed_at
      }
    });

  } catch (error) {
    console.error('Create user error:', error);
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Unknown error',
        details: 'Failed to create test user'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'POST to create test user',
    body: {
      email: 'test@example.com',
      password: 'TestPassword123'
    }
  });
}
