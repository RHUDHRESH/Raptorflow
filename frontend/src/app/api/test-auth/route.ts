import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function POST(request: Request) {
  try {
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
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
