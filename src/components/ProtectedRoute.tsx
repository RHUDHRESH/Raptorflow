import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

/**
 * Protected Route Props
 */
interface ProtectedRouteProps {
    children: React.ReactNode;
    requireOnboarding?: boolean;
}

/**
 * ProtectedRoute Component
 * 
 * Wrapper component that protects routes requiring authentication.
 * 
 * Behavior:
 * - While loading: Shows loading spinner
 * - If unauthenticated: Redirects to /register (with option to login)
 * - If authenticated but onboarding incomplete: Redirects to /onboarding (if required)
 * - If authenticated and onboarding complete: Renders children
 * 
 * @param children - Components to render when authenticated
 * @param requireOnboarding - Whether to check onboarding status (default: true)
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    requireOnboarding = true
}) => {
    const { status, onboardingCompleted } = useAuth();
    const location = useLocation();
    const [isRedirecting, setIsRedirecting] = useState(false);

    // Handle OAuth callback - give it time to process
    useEffect(() => {
        const hash = window.location.hash;
        if (hash && (hash.includes('access_token') || hash.includes('error'))) {
            // Auth state change listener will handle this
            // Just wait a bit before showing anything
            return;
        }
    }, []);

    // Show loading state while checking authentication
    if (status === 'loading') {
        return (
            <div className="flex items-center justify-center min-h-screen bg-white">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-neutral-900 mx-auto mb-4" />
                    <p className="text-neutral-600">Loading...</p>
                </div>
            </div>
        );
    }

    // Redirect to register if not authenticated (prioritize new user signup)
    if (status === 'unauthenticated') {
        if (!isRedirecting) {
            setIsRedirecting(true);
        }

        // Save the location they were trying to access
        return <Navigate to="/register" state={{ from: location }} replace />;
    }

    // Check if user needs to complete onboarding
    // Only redirect to onboarding if:
    // 1. Onboarding is required for this route (requireOnboarding = true)
    // 2. User hasn't completed onboarding
    // 3. User is not already on the onboarding page
    if (
        requireOnboarding &&
        !onboardingCompleted &&
        location.pathname !== '/onboarding'
    ) {
        return <Navigate to="/onboarding" state={{ from: location }} replace />;
    }

    // User is authenticated and has completed onboarding (or onboarding not required)
    // Render the protected content
    return <>{children}</>;
};

export default ProtectedRoute;
