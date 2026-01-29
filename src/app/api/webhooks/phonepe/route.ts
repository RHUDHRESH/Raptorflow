import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function POST(request: Request) {
    try {
        console.log('🔐 [PhonePe Webhook] Received webhook')

        // Get headers
        const authorization = request.headers.get('authorization')
        const xVerify = request.headers.get('x-verify')

        if (!authorization && !xVerify) {
            console.error('🔐 [PhonePe Webhook] Missing authorization headers')
            return NextResponse.json(
                { error: 'Missing authorization headers' },
                { status: 401 }
            )
        }

        // Get raw body
        const body = await request.text()
        console.log('🔐 [PhonePe Webhook] Body length:', body.length)

        // Forward to backend for validation and processing
        const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

        const backendResponse = await fetch(`${BACKEND_API_URL}/api/payments/webhook`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authorization || xVerify || '',
            },
            body: body
        })

        if (backendResponse.ok) {
            const result = await backendResponse.json()
            console.log('🔐 [PhonePe Webhook] Successfully processed by backend:', result)

            // Extract payment data from webhook
            try {
                const webhookData = JSON.parse(body)
                const { data } = webhookData

                if (data && data.merchantOrderId) {
                    console.log('🔐 [PhonePe Webhook] Processing payment completion for:', data.merchantOrderId)

                    // Update subscription status in Supabase
                    const supabase = createClient(
                        process.env.NEXT_PUBLIC_SUPABASE_URL!,
                        process.env.SUPABASE_SERVICE_ROLE_KEY!
                    )

                    // Find the payment transaction
                    const { data: transaction, error: txnError } = await supabase
                        .from('payment_transactions')
                        .select('user_id, amount, metadata')
                        .eq('merchant_order_id', data.merchantOrderId)
                        .single()

                    if (txnError) {
                        console.error('🔐 [PhonePe Webhook] Error finding transaction:', txnError)
                    } else if (transaction) {
                        console.log('🔐 [PhonePe Webhook] Found transaction:', transaction)

                        // Update subscription status
                        const { error: subError } = await supabase
                            .from('subscriptions')
                            .upsert({
                                user_id: transaction.user_id,
                                status: 'active',
                                plan: 'premium', // Determine from amount/metadata
                                current_period_start: new Date().toISOString(),
                                current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
                                updated_at: new Date().toISOString(),
                            })

                        if (subError) {
                            console.error('🔐 [PhonePe Webhook] Error updating subscription:', subError)
                        } else {
                            console.log('🔐 [PhonePe Webhook] Subscription activated for user:', transaction.user_id)

                            // Update user's onboarding status
                            await supabase
                                .from('users')
                                .update({
                                    subscription_status: 'active',
                                    updated_at: new Date().toISOString(),
                                })
                                .eq('id', transaction.user_id)
                        }
                    }
                }
            } catch (parseError) {
                console.error('🔐 [PhonePe Webhook] Error parsing webhook data:', parseError)
            }

            return NextResponse.json(result)
        } else {
            const errorText = await backendResponse.text()
            console.error('🔐 [PhonePe Webhook] Backend processing failed:', errorText)
            return NextResponse.json(
                { error: 'Webhook processing failed' },
                { status: backendResponse.status }
            )
        }

    } catch (err) {
        console.error('🔐 [PhonePe Webhook] Processing error:', err)
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        )
    }
}
