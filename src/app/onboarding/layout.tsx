import { redirect } from 'next/navigation'
import { createServerSupabaseClient, getProfileByAuthUserId, getRedirectPath } from '@/lib/auth-server'

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
  let supabase;
  try {
    supabase = await createServerSupabaseClient()
  } catch (error) {
    console.error('Failed to create Supabase client in onboarding layout:', error)
    // Redirect to sign in if we can't initialize auth
    redirect('/signin')
  }

  // Get session
  let session;
  try {
    const { data } = await supabase.auth.getSession()
    session = data?.session
  } catch (error) {
    console.error('Failed to get session in onboarding layout:', error)
    // Redirect to sign in if we can't get session
    redirect('/signin')
  }

  // DEV BYPASS: If no session, mock a user for UI viewing purposes
  let user;

  if (!session) {
    console.log("No session found in OnboardingLayout. Using DEV BYPASS mock user.");
    user = {
      onboarding_status: 'pending_workspace',
      role: 'user'
    };
  } else {
    // Get user status from DB
    try {
      const { profile } = await getProfileByAuthUserId(supabase, session.user.id)
      user = profile;
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      // Use default user if DB query fails
      user = { onboarding_status: 'pending_workspace', role: 'user' };
    }
  }

  // Fallback if DB fetch failed even with session
  if (!user && session) {
    // Handle case where user exists in Auth but not in public.profiles table yet
    user = { onboarding_status: 'pending_workspace', role: 'user' };
  }

  if (!user) {
    redirect('/signin')
  }

  // Check if user is banned (role-based check)
  if (user.role === 'banned') {
    redirect('/account/banned')
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
