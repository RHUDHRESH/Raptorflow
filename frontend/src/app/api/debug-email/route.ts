import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
  try {
    console.log('=== EMAIL DEBUG INFO ===');
    console.log('All environment variables:', Object.keys(process.env).filter(key => key.includes('RESEND')));
    console.log('RESEND_API_KEY:', process.env.RESEND_API_KEY ? 'SET' : 'NOT SET');
    console.log('RESEND_FROM_EMAIL:', process.env.RESEND_FROM_EMAIL);
    console.log('NEXT_PUBLIC_APP_URL:', process.env.NEXT_PUBLIC_APP_URL);
    console.log('NODE_ENV:', process.env.NODE_ENV);
    console.log('========================');

    // Test Resend API directly with hardcoded key for debugging
    const testApiKey = 're_De99YTsk_6K4bRLYqUyuDVGSNXs287gdF';

    try {
      const response = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${testApiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: 'onboarding@resend.dev',
          to: 'rhudhresh3697@gmail.com',
          subject: 'Debug Test Email from RaptorFlow',
          html: '<h1>Debug Test</h1><p>This is a debug test email from RaptorFlow to verify email sending is working.</p><p>Requested at: ' + new Date().toISOString() + '</p>'
        })
      });

      const result = await response.json();
      console.log('Resend API Response:', result);

      return NextResponse.json({
        success: true,
        env_vars: {
          resend_api_key: process.env.RESEND_API_KEY ? 'SET' : 'NOT SET',
          resend_from_email: process.env.RESEND_FROM_EMAIL,
          next_public_app_url: process.env.NEXT_PUBLIC_APP_URL,
          node_env: process.env.NODE_ENV,
          all_env_keys: Object.keys(process.env).filter(key => key.includes('RESEND'))
        },
        resend_response: result,
        resend_status: response.status,
        hardcoded_test: 'SUCCESS'
      });
    } catch (error) {
      console.log('Resend API Error:', error);
      return NextResponse.json({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        env_vars: {
          resend_api_key: process.env.RESEND_API_KEY ? 'SET' : 'NOT SET',
          resend_from_email: process.env.RESEND_FROM_EMAIL,
          all_env_keys: Object.keys(process.env).filter(key => key.includes('RESEND'))
        }
      });
    }
  } catch (error) {
    console.error('Debug error:', error);
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
