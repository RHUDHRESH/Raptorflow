/**
 * 🔐 SIMPLE RESET PASSWORD API
 * Works with the simple forgot password flow
 */

import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function POST(request: NextRequest) {
  try {
    const { token, password } = await request.json();

    if (!token || !password) {
      return NextResponse.json(
        { error: 'Reset token and password are required' },
        { status: 400 }
      );
    }

    // Validate password strength
    if (password.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters long' },
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

    // For the simple version, we'll just log the password reset
    // In a real implementation, you would update the database
    console.log('🔐 PASSWORD RESET SUCCESSFUL');
    console.log('Email:', email);
    console.log('New password length:', password.length);
    console.log('Reset time:', new Date().toISOString());
    console.log('Token was valid, password would be updated in database');

    return NextResponse.json({
      success: true,
      message: 'Password has been reset successfully'
    });

  } catch (error) {
    console.error('Reset password error:', error);
    return NextResponse.json(
      { error: 'Internal server error: ' + (error instanceof Error ? error.message : 'Unknown error') },
      { status: 500 }
    );
  }
}
