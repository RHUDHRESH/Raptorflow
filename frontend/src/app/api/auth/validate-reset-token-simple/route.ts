/**
 * 🔐 SIMPLE RESET TOKEN VALIDATION API
 * Works with the simple forgot password flow
 */

import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function POST(request: NextRequest) {
  try {
    const { token } = await request.json();

    if (!token) {
      return NextResponse.json(
        { error: 'Reset token is required' },
        { status: 400 }
      );
    }

    // Decode the token to get email and timestamp
    let decodedToken: string;
    try {
      decodedToken = Buffer.from(token, 'base64').toString();
    } catch (error) {
      return NextResponse.json(
        { error: 'Invalid reset token format' },
        { status: 400 }
      );
    }

    const [email, timestamp] = decodedToken.split(':');

    if (!email || !timestamp) {
      return NextResponse.json(
        { error: 'Invalid reset token format' },
        { status: 400 }
      );
    }

    // Check if token is expired (1 hour = 3600000 ms)
    const tokenTime = parseInt(timestamp);
    const now = Date.now();
    if (now - tokenTime > 3600000) {
      return NextResponse.json(
        { error: 'Reset token has expired' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email in token' },
        { status: 400 }
      );
    }

    console.log('✅ Reset token validated for:', email);
    console.log('Token created:', new Date(tokenTime).toISOString());
    console.log('Token expires:', new Date(tokenTime + 3600000).toISOString());

    return NextResponse.json({
      success: true,
      message: 'Reset token is valid',
      user: {
        email: email
      }
    });

  } catch (error) {
    console.error('Validate reset token error:', error);
    return NextResponse.json(
      { error: 'Internal server error: ' + (error instanceof Error ? error.message : 'Unknown error') },
      { status: 500 }
    );
  }
}
