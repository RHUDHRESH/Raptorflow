import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { ValidationError, createDatabaseError } from '@/lib/security/error-handler';
import { validateUuid, sanitizeInput } from '@/lib/security/input-validation';

export async function POST(request: Request) {
  try {
    const { token } = await request.json();
    
    // Validate input
    if (!token || typeof token !== 'string') {
      throw new ValidationError('Token is required');
    }
    
    const sanitizedToken = sanitizeInput(token);
    
    if (!validateUuid(sanitizedToken)) {
      throw new ValidationError('Invalid token format');
    }
    
    // Initialize Supabase client
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
    
    // Find verification token
    const { data: tokenData, error: tokenError } = await supabase
      .from('email_verification_tokens')
      .select('*')
      .eq('token', sanitizedToken)
      .eq('used', false)
      .single();
    
    if (tokenError || !tokenData) {
      throw new ValidationError('Invalid or expired verification token');
    }
    
    // Check if token has expired
    const now = new Date();
    const expiresAt = new Date(tokenData.expires_at);
    
    if (now > expiresAt) {
      throw new ValidationError('Verification token has expired');
    }
    
    // Mark token as used
    const { error: updateError } = await supabase
      .from('email_verification_tokens')
      .update({ used: true, used_at: now.toISOString() })
      .eq('token', sanitizedToken);
    
    if (updateError) {
      throw createDatabaseError('mark token as used', updateError);
    }
    
    // Update user email verification status
    const { error: userUpdateError } = await supabase.auth.admin.updateUserById(
      tokenData.user_id,
      { email_confirm: true }
    );
    
    if (userUpdateError) {
      throw createDatabaseError('update user email verification', userUpdateError);
    }
    
    // Update user profile
    const { error: profileUpdateError } = await supabase
      .from('profiles')
      .update({ email_verified: true })
      .eq('id', tokenData.user_id);
    
    if (profileUpdateError) {
      throw createDatabaseError('update profile email verification', profileUpdateError);
    }
    
    return NextResponse.json({
      message: 'Email verified successfully',
      verified: true
    });
    
  } catch (error) {
    console.error('Email verification error:', error);
    
    if (error instanceof ValidationError) {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to verify email' },
      { status: 500 }
    );
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const token = searchParams.get('token');
    
    if (!token) {
      throw new ValidationError('Token is required');
    }
    
    const sanitizedToken = sanitizeInput(token);
    
    if (!validateUuid(sanitizedToken)) {
      throw new ValidationError('Invalid token format');
    }
    
    // Initialize Supabase client
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
    
    // Check if token is valid
    const { data: tokenData, error: tokenError } = await supabase
      .from('email_verification_tokens')
      .select('expires_at, used')
      .eq('token', sanitizedToken)
      .single();
    
    if (tokenError || !tokenData) {
      return NextResponse.json(
        { valid: false, error: 'Invalid token' },
        { status: 400 }
      );
    }
    
    // Check if token is already used
    if (tokenData.used) {
      return NextResponse.json(
        { valid: false, error: 'Token already used' },
        { status: 400 }
      );
    }
    
    // Check if token has expired
    const now = new Date();
    const expiresAt = new Date(tokenData.expires_at);
    
    if (now > expiresAt) {
      return NextResponse.json(
        { valid: false, error: 'Token expired' },
        { status: 400 }
      );
    }
    
    return NextResponse.json({
      valid: true,
      expiresAt: tokenData.expires_at
    });
    
  } catch (error) {
    console.error('Token validation error:', error);
    
    if (error instanceof ValidationError) {
      return NextResponse.json(
        { valid: false, error: error.message },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { valid: false, error: 'Failed to validate token' },
      { status: 500 }
    );
  }
}
