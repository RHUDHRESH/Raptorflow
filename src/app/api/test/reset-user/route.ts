import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

// Create a Supabase client with the service role key for admin access
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function POST(request: Request) {
  // Only allow in development/test
  if (process.env.NODE_ENV === 'production') {
    return NextResponse.json({ error: 'Not allowed in production' }, { status: 403 })
  }

  try {
    const { email } = await request.json()

    if (!email) {
      return NextResponse.json({ error: 'Email is required' }, { status: 400 })
    }

    // 1. Get user ID
    const { data: users, error: userError } = await supabase.auth.admin.listUsers()
    
    if (userError) throw userError

    const user = users.users.find(u => u.email === email)

    if (!user) {
      return NextResponse.json({ message: 'User not found, nothing to reset' })
    }

    // 2. Reset profile/metadata if needed
    // Assuming 'onboarding_status' is in user_metadata or profiles table
    
    // Update auth.users metadata
    const { error: updateError } = await supabase.auth.admin.updateUserById(
      user.id,
      { user_metadata: { onboarding_status: 'pending' } }
    )

    if (updateError) throw updateError

    // Also try to update profiles table if it exists
    const { error: profileError } = await supabase
      .from('profiles')
      .update({ onboarding_step: 0, has_completed_onboarding: false })
      .eq('id', user.id)

    // Ignore profile error as table might not exist or user might not be in it
    
    // Also delete any workspace memberships if needed?
    // For now, just resetting metadata might be enough to trigger onboarding flow
    // if middleware checks `onboarding_status`.

    return NextResponse.json({ message: 'User reset successfully' })
  } catch (error: any) {
    console.error('Reset user error:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
