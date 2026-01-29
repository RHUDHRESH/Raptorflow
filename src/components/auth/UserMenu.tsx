/**
 * 🔐 USER MENU - Textbook Implementation
 *
 * This is the most straightforward user menu possible.
 * No magic, no complexity, just pure textbook authentication.
 *
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Menu shows user info from context
 * 2. Logout button calls logout function
 * 3. Loading states handled gracefully
 * 4. Error states handled gracefully
 */

'use client';

import { useState } from 'react';
import { useAuth } from './AuthProvider';
import { User, LogOut } from 'lucide-react';

/**
 * User Menu Component - Textbook Simple
 */
export function UserMenu() {
  const { user, logout, isLoading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  /**
   * Handle logout - textbook implementation
   */
  const handleLogout = async () => {
    try {
      await logout();
      setIsOpen(false);
      // Redirect to sign in page
      window.location.href = '/signin';
    } catch (error) {
      console.error('🔐 [Auth] Logout error:', error);
    }
  };

  if (!user) {
    return null; // Don't show menu if not authenticated
  }

  return (
    <div className="relative">
      {/* Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center text-sm rounded-md border border-gray-300 px-3 py-2 text-gray-700 hover:bg-gray-50"
      >
        <User className="h-4 w-4" />
        <span className="ml-2">{user.email}</span>
        <LogOut className="ml-2 h-4 w-4" />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
          <div className="py-1">
            <div className="px-4 py-2 border-b border-gray-100">
              <p className="text-sm font-medium text-gray-900">Signed in as</p>
              <p className="text-sm text-gray-500 truncate">{user.email}</p>
            </div>
            <div className="py-1">
              <button
                onClick={handleLogout}
                disabled={isLoading}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                {isLoading ? (
                  <span className="flex items-center">
                    <div className="animate-spin h-4 w-4 border-b-2 border-gray-300 mr-2"></div>
                    Signing out...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign out
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
