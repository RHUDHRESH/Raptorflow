import { redirect } from 'next/navigation'
import { createServerSupabaseClient, getRedirectPath } from '@/lib/auth-server'

const ONBOARDING_STEPS = [
  { id: 'workspace', label: 'Create Workspace', status: 'pending_workspace' },
  { id: 'storage', label: 'Setup Storage', status: 'pending_storage' },
  { id: 'plan', label: 'Choose Plan', status: 'pending_plan_selection' },
  { id: 'payment', label: 'Payment', status: 'pending_payment' },
]

export default async function OnboardingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const supabase = createServerSupabaseClient()

  // Get session
  const { data: { session } } = await supabase.auth.getSession()

  // DEV BYPASS: If no session, mock a user for UI viewing purposes
  let user;

  if (!session) {
    console.log("No session found in OnboardingLayout. Using DEV BYPASS mock user.");
    user = {
      onboarding_status: 'pending_workspace',
      is_banned: false,
      is_active: true // Set to false to test inactive redirect, but true to see onboarding
    };
  } else {
    // Get user status from DB
    const { data: dbUser } = await supabase
      .from('users')
      .select('onboarding_status, is_banned, is_active')
      .eq('auth_user_id', session.user.id)
      .single()

    user = dbUser;
  }

  // Fallback if DB fetch failed even with session
  if (!user && session) {
    // Handle case where user exists in Auth but not in public.users table yet
    user = { onboarding_status: 'pending_workspace', is_banned: false, is_active: true };
  }

  if (!user) {
    redirect('/login')
  }

  // Check if user is banned
  if (user.is_banned) {
    redirect('/account/banned')
  }

  // Check if user is inactive
  if (!user.is_active) {
    redirect('/account/inactive')
  }

  // If already active, go to dashboard
  if (user.onboarding_status === 'active') {
    redirect('/dashboard')
  }

  // If user is not in onboarding flow, redirect to appropriate step
  // In bypass mode, we just let them stay on the requested URL or default to step 1 via page.tsx
  // if (!ONBOARDING_STEPS.some(step => step.status === user.onboarding_status)) {
  //   const redirectPath = getRedirectPath(user.onboarding_status)
  //   redirect(redirectPath)
  // }

  const currentStepIndex = ONBOARDING_STEPS.findIndex(
    step => step.status === user.onboarding_status
  )

  return (
    <div className="min-h-screen bg-background">
      {/* 
        LEGACY LAYOUT CLEARED 
        The internal OnboardingShell now handles the full UI, Sidebar, and Progress.
        We simply render the children full-width here.
      */}
      <div className="w-full h-full">
        {children}
      </div>
    </div>
  )
}
