/**
 * 🔐 LOGOUT API ROUTE - Textbook Implementation
 * 
 * This is the most straightforward logout API possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Client requests logout
 * 2. Server clears auth cookie
 * 3. Server returns success response
 */

import { NextResponse } from 'next/server';
import { logoutRoute } from '@/lib/simple-auth';

/**
 * POST /api/auth/logout
 * 
 * Handles user logout requests
 * 
 * @returns Response with auth cookie cleared
 */
export async function POST(): Promise<Response> {
  return logoutRoute();
}
