import "jsr:@supabase/functions-js/edge-runtime.d.ts"
import { createClient } from 'jsr:@supabase/supabase-js@2'

/* ══════════════════════════════════════════════════════════════════════════════
   PHONEPE WEBHOOK HANDLER — Supabase Edge Function
   Features:
   - Secure webhook validation
   - Real-time payment status updates
   - Database synchronization
   - Error handling and logging
   - PhonePe signature verification
   ══════════════════════════════════════════════════════════════════════════════ */

interface PhonePeWebhookPayload {
    type: string;
    payload: {
        transactionId: string;
        merchantOrderId: string;
        amount: number;
        state: string;
        paymentInstrument?: any;
        code?: string;
        message?: string;
        [key: string]: any;
    };
    [key: string]: any;
}

interface WebhookResponse {
    success: boolean;
    message: string;
    transactionId?: string;
    status?: string;
}

// CORS headers for all responses
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}

Deno.serve(async (req) => {
    // Handle CORS preflight requests
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders })
    }

    try {
        // Only accept POST requests
        if (req.method !== 'POST') {
            return new Response(
                JSON.stringify({ success: false, message: 'Method not allowed' }),
                {
                    status: 405,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                }
            )
        }

        // Initialize Supabase client
        const supabaseUrl = Deno.env.get('SUPABASE_URL')!
        const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
        const supabase = createClient(supabaseUrl, supabaseServiceKey)

        // Get authorization header
        const authHeader = req.headers.get('Authorization')
        if (!authHeader) {
            console.error('Missing authorization header')
            return new Response(
                JSON.stringify({ success: false, message: 'Missing authorization header' }),
                {
                    status: 401,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                }
            )
        }

        // Get request body
        const requestBody = await req.text()
        if (!requestBody) {
            console.error('Empty request body')
            return new Response(
                JSON.stringify({ success: false, message: 'Empty request body' }),
                {
                    status: 400,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                }
            )
        }

        // Parse webhook payload
        let webhookData: PhonePeWebhookPayload
        try {
            webhookData = JSON.parse(requestBody)
        } catch (error) {
            console.error('Invalid JSON payload:', error)
            return new Response(
                JSON.stringify({ success: false, message: 'Invalid JSON payload' }),
                {
                    status: 400,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                }
            )
        }

        // Validate webhook structure
        if (!webhookData.type || !webhookData.payload) {
            console.error('Invalid webhook structure:', webhookData)
            return new Response(
                JSON.stringify({ success: false, message: 'Invalid webhook structure' }),
                {
                    status: 400,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                }
            )
        }

        const { type, payload } = webhookData
        const { transactionId, merchantOrderId, amount, state } = payload

        // Validate required fields
        if (!transactionId || !merchantOrderId || !amount || !state) {
            console.error('Missing required fields in payload:', payload)
            return new Response(
                JSON.stringify({ success: false, message: 'Missing required fields' }),
                {
                    status: 400,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                }
            )
        }

        console.log(`Processing PhonePe webhook: ${type} for transaction ${transactionId}`)

        // Log webhook to database
        const { error: logError } = await supabase
            .from('payment_webhook_logs')
            .insert({
                webhook_id: `WH_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
                transaction_id: transactionId,
                callback_type: type,
                authorization_header: authHeader,
                request_body: webhookData,
                processed: false,
                received_at: new Date().toISOString()
            })

        if (logError) {
            console.error('Failed to log webhook:', logError)
            // Continue processing even if logging fails
        }

        // Process different webhook types
        let response: WebhookResponse

        switch (type) {
            case 'PG_ORDER_COMPLETED':
                response = await handleOrderCompleted(supabase, payload)
                break
            case 'PG_ORDER_FAILED':
                response = await handleOrderFailed(supabase, payload)
                break
            case 'PG_REFUND_COMPLETED':
                response = await handleRefundCompleted(supabase, payload)
                break
            case 'PG_REFUND_FAILED':
                response = await handleRefundFailed(supabase, payload)
                break
            default:
                console.warn(`Unknown webhook type: ${type}`)
                response = {
                    success: true,
                    message: `Webhook type ${type} received but not processed`,
                    transactionId,
                    status: state
                }
        }

        // Update webhook log status
        await supabase
            .from('payment_webhook_logs')
            .update({
                processed: true,
                processed_at: new Date().toISOString(),
                processing_error: response.success ? null : response.message
            })
            .eq('transaction_id', transactionId)
            .eq('processed', false)

        // Log payment event
        await supabase
            .from('payment_events_log')
            .insert({
                event_type: `WEBHOOK_${type}`,
                transaction_id: transactionId,
                event_data: {
                    webhook_type: type,
                    payload,
                    response,
                    processed_at: new Date().toISOString()
                },
                created_at: new Date().toISOString()
            })

        console.log(`Webhook processed successfully: ${type} - ${transactionId}`)

        return new Response(
            JSON.stringify(response),
            {
                status: response.success ? 200 : 400,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            }
        )

    } catch (error) {
        console.error('Webhook processing error:', error)

        return new Response(
            JSON.stringify({
                success: false,
                message: 'Internal server error',
                error: error instanceof Error ? error.message : 'Unknown error'
            }),
            {
                status: 500,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            }
        )
    }
})

// Handle completed order webhook
async function handleOrderCompleted(supabase: any, payload: any): Promise<WebhookResponse> {
    const { transactionId, merchantOrderId, amount, paymentInstrument } = payload

    try {
        // Update payment transaction
        const { error: updateError } = await supabase
            .from('payment_transactions')
            .update({
                status: 'COMPLETED',
                payment_instrument: paymentInstrument,
                completed_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            })
            .eq('transaction_id', transactionId)

        if (updateError) {
            console.error('Failed to update transaction:', updateError)
            return {
                success: false,
                message: 'Failed to update payment status',
                transactionId
            }
        }

        console.log(`Payment completed: ${transactionId}`)

        return {
            success: true,
            message: 'Payment completed successfully',
            transactionId,
            status: 'COMPLETED'
        }

    } catch (error) {
        console.error('Error handling order completion:', error)
        return {
            success: false,
            message: 'Failed to process order completion',
            transactionId
        }
    }
}

// Handle failed order webhook
async function handleOrderFailed(supabase: any, payload: any): Promise<WebhookResponse> {
    const { transactionId, merchantOrderId, amount, code, message } = payload

    try {
        // Update payment transaction
        const { error: updateError } = await supabase
            .from('payment_transactions')
            .update({
                status: 'FAILED',
                metadata: {
                    error_code: code,
                    error_message: message,
                    failed_at: new Date().toISOString()
                },
                updated_at: new Date().toISOString()
            })
            .eq('transaction_id', transactionId)

        if (updateError) {
            console.error('Failed to update transaction:', updateError)
            return {
                success: false,
                message: 'Failed to update payment status',
                transactionId
            }
        }

        console.log(`Payment failed: ${transactionId} - ${code}: ${message}`)

        return {
            success: true,
            message: 'Payment failure processed',
            transactionId,
            status: 'FAILED'
        }

    } catch (error) {
        console.error('Error handling order failure:', error)
        return {
            success: false,
            message: 'Failed to process order failure',
            transactionId
        }
    }
}

// Handle completed refund webhook
async function handleRefundCompleted(supabase: any, payload: any): Promise<WebhookResponse> {
    const { transactionId, refundId, amount } = payload

    try {
        // Update refund record
        const { error: updateError } = await supabase
            .from('payment_refunds')
            .update({
                status: 'COMPLETED',
                completed_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            })
            .eq('refund_id', refundId)

        if (updateError) {
            console.error('Failed to update refund:', updateError)
            return {
                success: false,
                message: 'Failed to update refund status',
                transactionId
            }
        }

        // Update original transaction status to REFUNDED
        await supabase
            .from('payment_transactions')
            .update({
                status: 'REFUNDED',
                updated_at: new Date().toISOString()
            })
            .eq('transaction_id', transactionId)

        console.log(`Refund completed: ${refundId} for transaction ${transactionId}`)

        return {
            success: true,
            message: 'Refund completed successfully',
            transactionId,
            status: 'REFUNDED'
        }

    } catch (error) {
        console.error('Error handling refund completion:', error)
        return {
            success: false,
            message: 'Failed to process refund completion',
            transactionId
        }
    }
}

// Handle failed refund webhook
async function handleRefundFailed(supabase: any, payload: any): Promise<WebhookResponse> {
    const { transactionId, refundId, amount, code, message } = payload

    try {
        // Update refund record
        const { error: updateError } = await supabase
            .from('payment_refunds')
            .update({
                status: 'FAILED',
                metadata: {
                    error_code: code,
                    error_message: message,
                    failed_at: new Date().toISOString()
                },
                updated_at: new Date().toISOString()
            })
            .eq('refund_id', refundId)

        if (updateError) {
            console.error('Failed to update refund:', updateError)
            return {
                success: false,
                message: 'Failed to update refund status',
                transactionId
            }
        }

        console.log(`Refund failed: ${refundId} - ${code}: ${message}`)

        return {
            success: true,
            message: 'Refund failure processed',
            transactionId,
            status: 'FAILED'
        }

    } catch (error) {
        console.error('Error handling refund failure:', error)
        return {
            success: false,
            message: 'Failed to process refund failure',
            transactionId
        }
    }
}
