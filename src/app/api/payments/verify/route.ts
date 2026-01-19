import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import crypto from 'crypto'

export async function POST(request: Request) {
  try {
    const { transactionId } = await request.json()

    const supabase = createServerSupabaseClient()

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

      // Get user
      const { data: user } = await supabase
        .from('users')
        .select('id')
        .eq('auth_user_id', session.user.id)
        .single()

      // Activate subscription
      const now = new Date()
      const periodEnd = transaction.billing_cycle === 'yearly'
        ? new Date(now.setFullYear(now.getFullYear() + 1))
        : new Date(now.setMonth(now.getMonth() + 1))

      await supabase
        .from('subscriptions')
        .update({
          status: 'active',
          phonepe_transaction_id: transactionId,
          current_period_start: new Date().toISOString(),
          current_period_end: periodEnd.toISOString()
        })
        .eq('user_id', user!.id)

      // Update user status to active
      await supabase
        .from('users')
        .update({ onboarding_status: 'active' })
        .eq('id', user!.id)

      // Log success
      await supabase.from('audit_logs').insert({
        actor_id: user!.id,
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
