/**
 * 🔐 RESET PASSWORD API
 * Updates user password after validating reset token
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import bcrypt from 'bcryptjs';

// Initialize Supabase client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

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

    // Decode the token to get user ID
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
      .select('id, email, metadata, password_hash')
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

    // Hash the new password
    const saltRounds = 12;
    const newPasswordHash = await bcrypt.hash(password, saltRounds);

    // Update user password and clear reset token
    const { error: updateError } = await supabase
      .from('users')
      .update({
        password_hash: newPasswordHash,
        metadata: {
          ...metadata,
          password_reset_token: null,
          password_reset_expires: null
        },
        updated_at: new Date().toISOString()
      })
      .eq('id', userId);

    if (updateError) {
      console.error('Failed to update password:', updateError);
      return NextResponse.json(
        { error: 'Failed to update password' },
        { status: 500 }
      );
    }

    // Log password reset event (you might want to create an audit log table)
    console.log('Password reset completed for user:', user.email);

    return NextResponse.json({
      success: true,
      message: 'Password has been reset successfully'
    });

  } catch (error) {
    console.error('Reset password error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
