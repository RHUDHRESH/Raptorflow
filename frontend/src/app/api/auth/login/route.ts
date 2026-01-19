/**
 * 🔐 LOGIN API ROUTE - Textbook Implementation
 * 
 * This is the most straightforward login API possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Client sends email/password
 * 2. Server validates credentials
 * 3. Server creates JWT token
 * 4. Server sets HttpOnly cookie
 * 5. Server returns success response
 */

import { NextResponse } from 'next/server';
import { loginRoute } from '@/lib/simple-auth';

/**
 * POST /api/auth/login
 * 
 * Handles user login requests
 * 
 * @param request - Request object
 * @returns Response with auth cookie set
 */
export async function POST(request: Request): Promise<Response> {
  return loginRoute(request);
}
