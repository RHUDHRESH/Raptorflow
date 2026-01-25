import { NextResponse } from 'next/server';
import { Resend } from 'resend';
import crypto from 'crypto';
import { storeToken } from '@/lib/database-token-store';

// Initialize Resend
const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      );
    }

    // Generate secure reset token
    const token = crypto.randomBytes(32).toString('hex');
    const expires = Date.now() + (60 * 60 * 1000); // 1 hour

    // Store token
    await storeToken(token, email, expires);

    // Create reset link
    const resetLink = `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3001'}/auth/reset-password?token=${token}`;

    // Email configuration
    const primaryEmail = 'rhudhresh3697@gmail.com'; // Verified email
    const targetEmail = email; // User's requested email

    // Professional email template
    const emailHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Your RaptorFlow Password</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { text-align: center; padding: 20px 0; border-bottom: 1px solid #eee; }
          .logo { font-size: 24px; font-weight: bold; color: #2563eb; }
          .content { padding: 30px 0; }
          .button { display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; }
          .footer { text-align: center; padding: 20px 0; border-top: 1px solid #eee; font-size: 14px; color: #666; }
          .note { background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 20px 0; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <div class="logo">🦅 RaptorFlow</div>
          </div>
          
          <div class="content">
            <h2>Reset Your Password</h2>
            <p>We received a request to reset the password for your RaptorFlow account.</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="${resetLink}" class="button">Reset Password</a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; background: #f4f4f4; padding: 10px; border-radius: 4px;">
              ${resetLink}
            </p>
            
            ${targetEmail !== primaryEmail ? `
            <div class="note">
              <strong>Note:</strong> This password reset was requested for ${targetEmail}. 
              For delivery, this email was routed to ${primaryEmail}.
            </div>
            ` : ''}
            
            <p style="color: #666; font-size: 14px;">
              This link will expire in 1 hour for security reasons.
            </p>
          </div>
          
          <div class="footer">
            <p>© 2026 RaptorFlow. All rights reserved.</p>
            <p>If you didn't request this password reset, you can safely ignore this email.</p>
          </div>
        </div>
      </body>
      </html>
    `;

    // Send email
    const { data, error } = await resend.emails.send({
      from: 'onboarding@resend.dev',
      to: primaryEmail, // Send to verified email
      subject: 'Reset Your RaptorFlow Password',
      html: emailHtml,
    });

    if (error) {
      console.error('Email send error:', error);
      return NextResponse.json(
        { error: 'Failed to send reset email' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'Reset link sent! Please check your email.',
      data,
      token, // Include token for testing
      resetLink // Include link for testing
    });

  } catch (error) {
    console.error('Forgot password error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
