import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'
import { sendPaymentConfirmationEmail } from '@/lib/email'

export async function POST(request: Request) {
    try {
        const body = await request.text();
        const authorization = request.headers.get('authorization');
        const xVerify = request.headers.get('x-verify');

        const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Bridge to FastAPI backend which uses official SDK for validation
        const backendResponse = await fetch(`${BACKEND_API_URL}/api/payments/v2/webhook`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authorization || '',
                'X-VERIFY': xVerify || ''
            },
            body: body
        });

        if (backendResponse.ok) {
            console.log('Webhook successfully processed by backend SDK');
            return NextResponse.json({ success: true });
        }

        // Fallback or handle backend failure
        console.error('Backend SDK failed to process webhook, falling back to basic processing');
        
        // 1. Get Callback Data (Basic fallback)
        const jsonBody = JSON.parse(body);
        const { response } = jsonBody;
        // Decode base64 response if needed, but usually PhonePe sends it directly in some cases
        // This is a simplified fallback
        const data = jsonBody.data || {};
        const code = jsonBody.code || 'PAYMENT_ERROR';
        const merchantTransactionId = data.merchantTransactionId;

        // Use Service Role to bypass RLS for webhooks
        const supabase = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.SUPABASE_SERVICE_ROLE_KEY!,
            {
                auth: {
                    autoRefreshToken: false,
                    persistSession: false
                }
            }
        )

        // 3. Update Payment Record
        const status = code === 'PAYMENT_SUCCESS' ? 'completed' : 'failed'

        const { data: payment } = await supabase
            .from('payment_transactions')
            .update({
                status,
                phonepe_response: jsonBody,
                completed_at: new Date().toISOString()
            })
            .eq('transaction_id', merchantTransactionId)
            .select('*, users(*)')
            .single()

        if (!payment) {
            // If payment not found, legitimate error or replay
            return NextResponse.json({ error: 'Payment record not found' }, { status: 404 })
        }

        // 4. If Success, Activate Subscription & User
        if (status === 'completed') {
            // Activate User
            await supabase
                .from('users')
                .update({ onboarding_status: 'active', is_active: true })
                .eq('id', payment.user_id)

            // Update Subscription
            await supabase
                .from('subscriptions')
                .update({
                    status: 'active',
                    current_period_start: new Date().toISOString(),
                })
                .eq('user_id', payment.user_id)

            // Send confirmation email
            try {
                const user = payment.users;
                await sendPaymentConfirmationEmail({
                    email: user.email,
                    name: user.full_name || user.email.split('@')[0],
                    planName: payment.plan_id.toUpperCase(),
                    amount: `₹${(payment.amount_paise / 100).toLocaleString()}`,
                    transactionId: merchantTransactionId,
                    date: new Date().toLocaleDateString()
                });
            } catch (emailError) {
                console.error('Webhook: Failed to send confirmation email:', emailError);
            }

            // Log Success
            await supabase.from('audit_logs').insert({
                actor_id: payment.user_id,
                action: 'payment_completed',
                action_category: 'billing',
                description: `Payment of ${payment.amount_paise} paise completed via PhonePe Webhook`,
                metadata: { transaction_id: merchantTransactionId }
            })
        } else {
            // Log Failure
            await supabase.from('audit_logs').insert({
                actor_id: payment.user_id,
                action: 'payment_failed',
                action_category: 'billing',
                description: `Payment failed: ${code}`,
                metadata: { provider_ref: data.providerReferenceId }
            })
        }

        return NextResponse.json({ success: true })

    } catch (err) {
        console.error('Webhook Error:', err)
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        )
    }
}
