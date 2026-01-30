'use client';

import { useEffect } from 'react';
import { isAuthenticated } from '../lib/auth-helpers';
import SystemIntegrationDashboard from '../components/SystemIntegrationDashboard';

export default function Home() {
  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      window.location.href = '/login';
    }
  }, []);

  // Show loading while checking auth
  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800">Checking authentication...</h2>
        </div>
      </div>
    );
  }

  return (
    <main>
      <SystemIntegrationDashboard />
    </main>
  );
}
      window.location.href = '/login';
    }
  }, []);

  // Show loading while checking auth
  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800">Checking authentication...</h2>
        </div>
      </div>
    );
  }

  return (
    <main>
      <SystemIntegrationDashboard />
    </main>
  );
}
