/**
 * 🔐 CURRENT USER API ROUTE - Textbook Implementation
 * 
 * This is the most straightforward user info API possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Client requests current user info
 * 2. Server checks auth cookie
 * 3. Server verifies JWT token
 * 4. Server returns user data if valid
 */

import { NextResponse } from 'next/server';
import { getCurrentUserRoute } from '@/lib/simple-auth';

/**
 * GET /api/auth/me
 * 
 * Returns current user information
 * 
 * @returns Response with user data or error
 */
export async function GET(): Promise<Response> {
  return getCurrentUserRoute();
}
