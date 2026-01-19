/**
 * 🔐 SIMPLE FORGOT PASSWORD API (TESTING VERSION)
 * Basic version for testing without database dependencies
 */

import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json(
        { error: 'Email address is required' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email address' },
        { status: 400 }
      );
    }

    // Generate a simple reset token for testing
    const resetToken = Buffer.from(`${email}:${Date.now()}:${Math.random().toString(36)}`).toString('base64');

    // Create reset link
    const resetLink = `${process.env.NEXT_PUBLIC_APP_URL}/reset-password?token=${resetToken}`;

    // Log the reset link for development
    console.log('=== PASSWORD RESET EMAIL ===');
    console.log('To:', email);
    console.log('Reset Link:', resetLink);
    console.log('========================');

    // Try to send email using Resend API (if configured)
    let emailSent = false;
    if (process.env.RESEND_API_KEY && process.env.RESEND_API_KEY !== 're_your_actual_resend_api_key_here') {
      try {
        const response = await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: process.env.RESEND_FROM_EMAIL || 'noreply@raptorflow.in',
            to: email,
            subject: 'Reset Your RaptorFlow Password',
            html: `
              <!DOCTYPE html>
              <html>
              <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Reset Your RaptorFlow Password</title>
                <style>
                  body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                  }
                  .header {
                    background: #000;
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                  }
                  .content {
                    background: white;
                    padding: 40px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                    border-radius: 0 0 8px 8px;
                  }
                  .logo {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                  }
                  .title {
                    font-size: 28px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    color: #1f2937;
                  }
                  .reset-button {
                    display: inline-block;
                    background: #000;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                  }
                  .reset-button:hover {
                    background: #1f2937;
                  }
                  .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                    text-align: center;
                  }
                  .security-note {
                    background: #fef3c7;
                    border: 1px solid #f59e0b;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                    font-size: 14px;
                    color: #92400e;
                  }
                </style>
              </head>
              <body>
                <div class="header">
                  <div class="logo">🦅 RaptorFlow</div>
                  <div>Marketing Operating System</div>
                </div>
                
                <div class="content">
                  <h1 class="title">Reset Your Password</h1>
                  
                  <p>Hello,</p>
                  
                  <p>We received a request to reset the password for your RaptorFlow account associated with this email address.</p>
                  
                  <p>Click the button below to reset your password:</p>
                  
                  <a href="${resetLink}" class="reset-button">Reset Password</a>
                  
                  <p>Or copy and paste this link into your browser:</p>
                  <p style="word-break: break-all; background: #f3f4f6; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px;">
                    ${resetLink}
                  </p>
                  
                  <div class="security-note">
                    <strong>Security Notice:</strong><br>
                    This link will expire in 1 hour for your security. If you didn't request this password reset, please ignore this email or contact support if you have concerns.
                  </div>
                  
                  <p>If you have any questions, please don't hesitate to contact our support team.</p>
                  
                  <p>Best regards,<br>The RaptorFlow Team</p>
                </div>
                
                <div class="footer">
                  <p>This email was sent to ${email}</p>
                  <p>© 2026 RaptorFlow. All rights reserved.</p>
                </div>
              </body>
              </html>
            `
          })
        });

        if (response.ok) {
          emailSent = true;
          console.log('✅ Email sent via Resend API to:', email);
        } else {
          const errorText = await response.text();
          console.log('❌ Resend API error:', errorText);
        }
      } catch (resendError) {
        console.log('❌ Resend API error:', resendError);
      }
    }

    return NextResponse.json({
      success: true,
      message: emailSent ? 'Password reset link sent to your email address' : 'Password reset link generated (check console for development)',
      resetLink: resetLink,
      emailSent: emailSent
    });

  } catch (error) {
    console.error('Forgot password error:', error);
    return NextResponse.json(
      { error: 'Internal server error: ' + (error instanceof Error ? error.message : 'Unknown error') },
      { status: 500 }
    );
  }
}
