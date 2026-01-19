import { NextResponse } from 'next/server';
import crypto from 'crypto';
import { validateToken, getToken } from '@/lib/database-token-store';

export async function POST(request: Request) {
  try {
    const { token } = await request.json();

    if (!token) {
      return NextResponse.json(
        { error: 'Token is required' },
        { status: 400 }
      );
    }

    // Validate token using database
    const validation = await validateToken(token);
    
    if (!validation.valid) {
      return NextResponse.json(
        { 
          valid: false, 
          error: 'Invalid or expired reset token' 
        },
        { status: 400 }
      );
    }

    // Token is valid, return token data
    const tokenData = await getToken(token);
    
    return NextResponse.json({
      valid: true,
      email: validation.email,
      expires: tokenData?.expires_at
    });

  } catch (error) {
    console.error('Token validation error:', error);
    return NextResponse.json(
      { 
        valid: false, 
        error: 'Internal server error' 
      },
      { status: 500 }
    );
  }
}
