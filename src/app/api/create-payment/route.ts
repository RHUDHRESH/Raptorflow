import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

// Backend API URL - calls to Python backend with PhonePe SDK v2.1.7
const BACKEND_API_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: Request) {
    try {
        const { planId, billingCycle } = await request.json()
        const supabase = createServerSupabaseClient()

        // 1. Get Session
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

        // 2. Get User from public.users
        const { data: user, error: userError } = await supabase
            .from('users')
            .select('id, email, full_name')
            .eq('auth_user_id', session.user.id)
            .single()

        if (userError || !user) {
            console.error('User lookup error:', userError)
            return NextResponse.json({ error: 'User not found' }, { status: 404 })
        }

        // 3. Get Plan
        const { data: plan } = await supabase
            .from('plans')
            .select('*')
            .eq('id', planId)
            .single()

        if (!plan) return NextResponse.json({ error: 'Plan not found' }, { status: 404 })

        // 4. Calculate Amount in PAISE
        const amount = billingCycle === 'yearly' ? plan.price_yearly_paise : plan.price_monthly_paise

        // 5. Generate order ID
        const merchantOrderId = `ORD${Date.now()}${Math.random().toString(36).substr(2, 6).toUpperCase()}`

        // 6. Create Pending Payment Record
        const { data: payment, error: paymentError } = await supabase
            .from('payments')
            .insert({
                user_id: user.id,
                amount_paise: amount,
                currency: 'INR',
                status: 'pending',
                merchant_transaction_id: merchantOrderId,
                payment_instrument_type: 'PAY_PAGE',
                metadata: {
                    plan_id: planId,
                    plan_name: plan.name,
                    billing_cycle: billingCycle
                }
            })
            .select()
            .single()

        if (paymentError) {
            console.error('Payment record creation error:', paymentError)
            throw paymentError
        }

        // 7. Call NEW v2 Backend API (uses official PhonePe SDK)
        console.log(`[Payment] Calling backend: ${BACKEND_API_URL}/api/v1/payments/v2/initiate`)

        const backendResponse = await fetch(`${BACKEND_API_URL}/api/v1/payments/v2/initiate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: amount,
                merchant_order_id: merchantOrderId,
                redirect_url: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/onboarding/payment?status=callback&orderId=${merchantOrderId}`,
                customer_email: user.email,
                customer_name: user.full_name || '',
                user_id: user.id,
                metadata: {
                    plan_id: planId,
                    billing_cycle: billingCycle,
                    payment_db_id: payment.id
                }
            })
        })

        const backendData = await backendResponse.json()
        console.log('[Payment] Backend response:', backendData)

        if (backendData.success && backendData.checkout_url) {
            // Update payment with PhonePe order ID
            await supabase
                .from('payments')
                .update({
                    provider_transaction_id: backendData.transaction_id
                })
                .eq('id', payment.id)

            console.log(`[Payment] SUCCESS - Redirecting to: ${backendData.checkout_url}`)

            return NextResponse.json({
                url: backendData.checkout_url,
                transactionId: merchantOrderId,
                orderId: backendData.transaction_id
            })
        } else {
            console.error('[Payment] PhonePe SDK Failed:', backendData)

            // Update payment status to failed
            await supabase
                .from('payments')
                .update({ status: 'failed', error_message: backendData.error })
                .eq('id', payment.id)

            return NextResponse.json({
                error: backendData.error || 'Payment initialization failed'
            }, { status: 400 })
        }

    } catch (err) {
        console.error('[Payment] Create payment error:', err)
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        )
    }
}
