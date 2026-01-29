import { NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase/server';
import { getToken, deleteToken } from '@/lib/database-token-store';

export async function POST(request: Request) {
  try {
    const { token, newPassword } = await request.json();

    if (!token || !newPassword) {
      return NextResponse.json(
        { error: 'Token and new password are required' },
        { status: 400 }
      );
    }

    // Validate new password
    if (newPassword.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters long' },
        { status: 400 }
      );
    }

    // Get token data
    const tokenData = await getToken(token);
    if (!tokenData) {
      return NextResponse.json(
        { error: 'Invalid or expired reset token' },
        { status: 400 }
      );
    }

    // Check if token has expired
    const expiresAt = new Date(tokenData.expires_at).getTime();
    if (Date.now() > expiresAt) {
      await deleteToken(token);
      return NextResponse.json(
        { error: 'Reset token has expired' },
        { status: 400 }
      );
    }

    // Get Supabase client with service role for admin operations
    const supabase = await createServerSupabaseClient();

    // Find user by email
    const { data: { users }, error: userError } = await supabase.auth.admin.listUsers();

    if (userError) {
      console.error('Error listing users:', userError);
      return NextResponse.json(
        { error: 'Failed to process password reset' },
        { status: 500 }
      );
    }

    const user = users.find(u => u.email === tokenData.email);

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Production password update with proper error handling
    try {
      // Use admin.updateUserById for password reset
      const { error: updateError } = await supabase.auth.admin.updateUserById(
        user.id,
        { password: newPassword }
      );

      if (updateError) {
        throw new Error(`Password update failed: ${updateError.message}`);
      }

      // Mark token as used
      await deleteToken(token);

      return NextResponse.json({
        success: true,
        message: 'Password reset successfully!',
        user: {
          id: user.id,
          email: user.email
        }
      });

    } catch (updateError) {
      console.error('Password update failed:', updateError);

      // For development/testing - simulate success
      if (process.env.NODE_ENV === 'development') {
        await deleteToken(token);

        return NextResponse.json({
          success: true,
          message: 'Password reset simulated in development mode',
          note: 'Password not actually changed. In production, ensure SUPABASE_SERVICE_ROLE_KEY has proper permissions.',
          debug: {
            error: updateError instanceof Error ? updateError.message : 'Unknown error',
            userId: user.id,
            email: user.email
          }
        });
      }

      return NextResponse.json(
        {
          error: 'Failed to update password. Please contact support.',
          details: process.env.NODE_ENV === 'development' ? updateError : undefined
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('Reset password error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
