import { createServerSupabaseClient, getProfileByAuthUserId, upsertProfileForAuthUser, updateProfileRecord } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import crypto from 'crypto'
import { sendPaymentConfirmationEmail } from '@/lib/email'

export async function POST(request: Request) {
  try {
    const { transactionId } = await request.json()

    const supabase = await createServerSupabaseClient()

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get transaction
    const { data: transaction } = await supabase
      .from('payment_transactions')
      .select('*')
      .eq('transaction_id', transactionId)
      .single()

    if (!transaction) {
      return NextResponse.json(
        { error: 'Transaction not found' },
        { status: 404 }
      )
    }

    // Check status with PhonePe via Backend SDK
    const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${BACKEND_API_URL}/api/v1/payments/v2/status/${transactionId}`);
    const data = await response.json();

    if (data.success && data.status === 'COMPLETED') {
      // Update transaction
      await supabase
        .from('payment_transactions')
        .update({
          status: 'completed',
          phonepe_response: data,
          completed_at: new Date().toISOString()
        })
        .eq('transaction_id', transactionId)

    let { profile } = await getProfileByAuthUserId(supabase, session.user.id)

    if (!profile) {
      const created = await upsertProfileForAuthUser(supabase, session.user)
      profile = created.profile
    }

    if (!profile) {
      return NextResponse.json({ error: 'Profile not found' }, { status: 404 })
    }

      // Calculate period end
      const now = new Date()
      const periodEnd = transaction.billing_cycle === 'yearly'
        ? new Date(now.setFullYear(now.getFullYear() + 1))
        : new Date(now.setMonth(now.getMonth() + 1))

      // Activate subscription in subscriptions table
      await supabase
        .from('subscriptions')
        .upsert({
          user_id: profile!.id,
          plan_id: transaction.plan_id,
          billing_cycle: transaction.billing_cycle,
          status: 'active',
          current_period_start: new Date().toISOString(),
          current_period_end: periodEnd.toISOString()
        }, {
          onConflict: 'user_id'
        })

      // Update profile status to pending onboarding
      await updateProfileRecord(
        supabase,
        { authUserId: session.user.id, profileId: profile.id },
        {
          subscription_plan: transaction.plan_id,
          subscription_status: 'active',
          onboarding_status: 'pending',
          updated_at: new Date().toISOString()
        }
      )

      // Send confirmation email via Resend
      try {
        const email = profile.email || session.user.email || ''
        await sendPaymentConfirmationEmail({
          email,
          name: profile.full_name || email.split('@')[0] || 'User',
          planName: transaction.plan_id.toUpperCase(),
          amount: `₹${(transaction.amount / 100).toLocaleString()}`,
          transactionId: transactionId,
          date: new Date().toLocaleDateString()
        });
      } catch (emailError) {
        console.error('Failed to send confirmation email:', emailError);
        // Don't fail the transaction if email fails
      }

      // Log success
      await supabase.from('audit_logs').insert({
        actor_id: profile!.id,
        action: 'payment_completed',
        action_category: 'payment',
        description: `Payment completed for plan: ${transaction.plan_id}`,
        ip_address: request.headers.get('x-forwarded-for') || 'unknown',
        user_agent: request.headers.get('user-agent') || 'unknown',
      })

      return NextResponse.json({ success: true })
    }

    return NextResponse.json({
      success: false,
      error: data.message || 'Payment not completed'
    })

  } catch (err) {
    console.error('Payment verification error:', err)
    return NextResponse.json(
      { error: 'Verification failed' },
      { status: 500 }
    )
  }
}
