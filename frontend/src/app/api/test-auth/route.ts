import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

// Lazy client creation to avoid build-time errors
function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error('Missing Supabase configuration');
  }

  return createClient(url, key);
}

export async function POST(request: Request) {
  try {
    const supabase = getSupabase();
    const { email, password, fullName } = await request.json()

    // Test signup
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName }
      }
    })

    if (signUpError) {
      console.error('Signup error:', signUpError);
      return NextResponse.json({
        error: signUpError.message,
        details: signUpError,
        code: signUpError.code
      }, { status: 400 })
    }

    // Check if profile was created
    if (signUpData.user) {
      const { data: profile } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', signUpData.user.id)
        .single()

      return NextResponse.json({
        success: true,
        user: signUpData.user,
        profile: profile,
        message: 'User created successfully'
      })
    }

    return NextResponse.json({ success: false, message: 'Failed to create user' })

  } catch (error: any) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 500 })
  }
}
