import { Resend } from 'resend'

/**
 * Resend Email Service Client
 * Centralized email client for the application
 */

const RESEND_API_KEY = process.env.RESEND_API_KEY
const FROM_EMAIL = process.env.RESEND_FROM_EMAIL || 'noreply@raptorflow.in'

if (!RESEND_API_KEY) {
  console.warn('RESEND_API_KEY is not set. Email service will not work.')
}

export const resend = RESEND_API_KEY ? new Resend(RESEND_API_KEY) : null

export interface SendEmailOptions {
  to: string | string[]
  subject: string
  html: string
  text?: string
  from?: string
  reply_to?: string
}

/**
 * Send an email using Resend
 */
export async function sendEmail(options: SendEmailOptions) {
  if (!resend) {
    console.error('Email service not initialized (missing API key)')
    return { success: false, error: 'Email service not initialized' }
  }

  try {
    const { data, error } = await resend.emails.send({
      from: options.from || FROM_EMAIL,
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text,
      reply_to: options.reply_to,
    })

    if (error) {
      console.error('Failed to send email:', error)
      return { success: false, error }
    }

    return { success: true, data }
  } catch (error) {
    console.error('Error sending email:', error)
    return { success: false, error }
  }
}

/**
 * Send a welcome email to a new user
 */
export async function sendWelcomeEmail(email: string, name: string) {
  return sendEmail({
    to: email,
    subject: 'Welcome to RaptorFlow!',
    html: `
      <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h1 style="color: #2D3538;">Welcome to RaptorFlow, ${name}!</h1>
        <p>We're excited to have you on board. RaptorFlow is your all-in-one platform for marketing automation and AI-driven growth.</p>
        <p>Get started by exploring your dashboard:</p>
        <div style="margin: 30px 0;">
          <a href="https://app.raptorflow.in/dashboard" style="background-color: #2D3538; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Go to Dashboard</a>
        </div>
        <p>If you have any questions, feel free to reply to this email.</p>
        <hr style="margin: 30px 0; border: 0; border-top: 1px solid #eee;" />
        <p style="color: #888; font-size: 12px;">© 2026 RaptorFlow. All rights reserved.</p>
      </div>
    `,
  })
}
