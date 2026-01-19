/**
 * 🔐 VALIDATE RESET TOKEN API
 * Validates password reset token and checks if it's still valid
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function POST(request: NextRequest) {
  // Initialize Supabase client inside handler to avoid build-time errors
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
  try {
    const { token } = await request.json();

    if (!token) {
      return NextResponse.json(
        { error: 'Reset token is required' },
        { status: 400 }
      );
    }

    // Decode the token to get user ID and timestamp
    let decodedToken: string;
    try {
      decodedToken = Buffer.from(token, 'base64').toString();
    } catch (error) {
      return NextResponse.json(
        { error: 'Invalid reset token format' },
        { status: 400 }
      );
    }

    const [userId, timestamp] = decodedToken.split(':');

    if (!userId || !timestamp) {
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

    // Get user and check stored reset token
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('id, email, metadata')
      .eq('id', userId)
      .single();

    if (userError || !user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Check if reset token matches and hasn't expired
    const metadata = user.metadata || {};
    const storedTokenHash = metadata.password_reset_token;
    const resetExpires = metadata.password_reset_expires;

    if (!storedTokenHash || !resetExpires) {
      return NextResponse.json(
        { error: 'No valid reset request found' },
        { status: 400 }
      );
    }

    // Check if stored token has expired
    const expiresTime = new Date(resetExpires).getTime();
    if (now > expiresTime) {
      return NextResponse.json(
        { error: 'Reset token has expired' },
        { status: 400 }
      );
    }

    // Verify token hash matches
    const tokenHash = Buffer.from(token).toString('hex');
    if (tokenHash !== storedTokenHash) {
      return NextResponse.json(
        { error: 'Invalid reset token' },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'Reset token is valid',
      user: {
        id: user.id,
        email: user.email
      }
    });

  } catch (error) {
    console.error('Validate reset token error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
