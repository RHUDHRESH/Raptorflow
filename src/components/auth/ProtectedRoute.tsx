/**
 * 🔐 PROTECTED ROUTE COMPONENT - Textbook Implementation
 *
 * This is the most straightforward protected route component possible.
 * No magic, no complexity, just pure textbook authentication.
 *
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Component renders → Checks if authenticated
 * 2. Not authenticated → Show login prompt
 * 3. Authenticated → Show protected content
 * 4. User data available from context
 */

'use client';

import { useAuth } from './AuthProvider';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * Protected Route Component - Textbook Simple
 */
export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Authentication Required
          </h1>
          <p className="text-gray-600 mb-4">
            Please sign in to access this page.
          </p>
          <button
            onClick={() => window.location.href = '/signin'}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Go to Sign In
          </button>
        </div>
      </div>
    );
  }

  // Show protected content if authenticated
  return <>{children}</>;
}
