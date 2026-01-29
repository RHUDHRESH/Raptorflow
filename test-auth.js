import { createClient } from '@supabase/supabase-js'
import { config } from 'dotenv'

// Load environment variables from frontend directory
config({ path: './frontend/.env.local' })

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase environment variables')
  process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseKey)

async function testAuth() {
  try {
    // Get current session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()

    if (sessionError) {
      console.error('Session error:', sessionError)
      return
    }

    if (!session) {
      console.log('No active session - user not logged in')
      return
    }

    console.log('Session found:', {
      userId: session.user.id,
      email: session.user.email,
      fullName: session.user.user_metadata?.full_name || 'NOT SET',
      metadata: session.user.user_metadata
    })

    // Check profiles table
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('full_name, email, role')
      .eq('id', session.user.id)
      .single()

    if (profileError) {
      console.error('Profile error:', profileError)
    } else {
      console.log('Profile data:', profile)
    }

  } catch (error) {
    console.error('Test error:', error)
  }
}

testAuth()
