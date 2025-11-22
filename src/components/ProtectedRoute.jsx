import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute component that requires authentication
 * Redirects to login page if user is not authenticated
 * Redirects to onboarding if user hasn't completed onboarding
 */
const ProtectedRoute = ({ children, requireOnboarding = true }) => {
  const { isAuthenticated, loading, onboardingCompleted, subscription } = useAuth();
  const location = useLocation();

  // Check for OAuth callback in URL and wait a bit for auth state to update
  useEffect(() => {
    // If there's an OAuth callback in the URL hash, give it time to process
    if (window.location.hash && (window.location.hash.includes('access_token') || window.location.hash.includes('error'))) {
      // The auth state change listener will handle this
      return;
    }
  }, []);

  // Show loading state while checking authentication (especially important for OAuth callbacks)
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save the location they were trying to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user needs to complete onboarding
  // Only redirect to onboarding if:
  // 1. Onboarding is required for this route (requireOnboarding = true)
  // 2. User hasn't completed onboarding
  // 3. User is not already on the onboarding page
  if (requireOnboarding && !onboardingCompleted && location.pathname !== '/onboarding') {
    return <Navigate to="/onboarding" state={{ from: location }} replace />;
  }

  // User is authenticated and has completed onboarding (or onboarding not required), render the children
  return children;
};

export default ProtectedRoute;
