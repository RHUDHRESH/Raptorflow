import { NavigateFunction } from 'react-router-dom';
import { routes } from '../lib/routes';

interface AuthRedirectParams {
  user: any;
  onboardingCompleted: boolean;
  subscription: any;
  navigate: NavigateFunction;
  source?: string;
}

export const ONBOARDING_ROUTE = routes.onboardingNew;

export const redirectAfterAuth = ({
  user,
  onboardingCompleted,
  subscription,
  navigate,
  source
}: AuthRedirectParams) => {
  console.log('[redirectAfterAuth]', {
    source,
    onboardingCompleted,
    hasSubscription: !!subscription
  });

  // 1. Not onboarded -> Onboarding
  if (!onboardingCompleted) {
    console.log('[RedirectHelper] User not onboarded -> Redirecting to', ONBOARDING_ROUTE);
    navigate(ONBOARDING_ROUTE, { replace: true });
    return;
  }

  // 2. Onboarded but needs payment?
  // Check if subscription is missing or not active (and not free plan if that's allowed)
  // If the requirement is "If payment gating is enabled: Go to pricing/payment onboarding (if required)"
  // logic from Register.jsx was:
  // !subscription || subscription.plan === 'free' || (subscription.status !== 'active' && subscription.status !== 'trialing')
  // But let's strictly follow the new spec:
  // "If onboardingCompleted is true but subscription/payment is required and not active: Redirect to pricing/payment onboarding (if used)."
  
  // We'll keep the existing logic for pricing check for now, but make it clear.
  const isSubscriptionActive = subscription && 
    (subscription.status === 'active' || subscription.status === 'trialing') &&
    subscription.plan !== 'free'; // Assuming free plan users might need to upgrade? Or is free plan allowed?
    
  // Based on Register.jsx, it seemed to force pricing if not active/trialing/paid. 
  // But let's stick to the prompt: "If payment gating is enabled...".
  // I'll assume we route to onboardingPricing if valid subscription is missing.
  if (!isSubscriptionActive) {
     // Check if we should enforce payment. For now, let's assume yes if that was previous behavior.
     // But the prompt says "Optional: Pricing/Payment onboarding if that exists, but that comes *after* onboarding".
     // Since we are here (onboardingCompleted = true), we can check payment.
     console.log('[RedirectHelper] Payment required -> Redirecting to', routes.onboardingPricing);
     navigate(routes.onboardingPricing, { replace: true });
     return;
  }

  // 3. All good -> Dashboard
  console.log('[RedirectHelper] All checks passed -> Redirecting to', routes.dashboard);
  navigate(routes.dashboard, { replace: true });
};
