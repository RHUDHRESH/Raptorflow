import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

// MFA setup routes - temporarily disabled until otplib is properly configured

export async function POST() {
  try {
    const supabase = await createServerSupabaseClient()

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Check if user is admin
    const { data: user } = await supabase
      .from('users')
      .select('id, role, mfa_enabled')
      .eq('auth_user_id', session.user.id)
      .single()

    if (!user || !['admin', 'super_admin'].includes(user.role)) {
      return NextResponse.json({ error: 'MFA only available for admin users' }, { status: 403 })
    }

    // MFA setup not available - otplib not configured
    return NextResponse.json({
      error: 'MFA setup temporarily unavailable',
      message: 'Contact admin for MFA configuration'
    }, { status: 503 })

  } catch (error) {
    console.error('MFA setup error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PUT() {
  return NextResponse.json({
    error: 'MFA verification temporarily unavailable',
    message: 'Contact admin for MFA configuration'
  }, { status: 503 })
}

export async function DELETE() {
  return NextResponse.json({
    error: 'MFA disable temporarily unavailable',
    message: 'Contact admin for MFA configuration'
  }, { status: 503 })
}
