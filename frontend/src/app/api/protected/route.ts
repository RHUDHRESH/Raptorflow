/**
 * 🔐 PROTECTED API ROUTE - Textbook Implementation
 * 
 * This is the most straightforward protected API route possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. API request comes in → Middleware checks auth
 * 2. No auth token → Returns 401 error
 * 3. Auth token valid → Returns protected data
 * 4. User data available from JWT
 */

import { NextResponse } from 'next/server';
import { withAuth } from '@/lib/simple-auth';

/**
 * Protected API handler - textbook implementation
 * 
 * @returns Response with protected data
 */
async function protectedHandler() {
  // This is a protected endpoint
  // Only authenticated users can access it
  
  // In a real app, you would:
  // 1. Get user ID from JWT
  // 2. Fetch user-specific data from database
  // 3. Return the data
  
  // For now, we'll return mock data
  const protectedData = {
    message: 'This is protected data',
    timestamp: new Date().toISOString(),
    user: 'Authenticated user'
  };
  
  return NextResponse.json(protectedData);
}

/**
 * GET /api/protected/route
 * 
 * Protected API route that requires authentication
 * 
 * @returns Response with protected data or error
 */
export async function GET() {
  return withAuth(protectedHandler)();
}
