import { NextResponse } from 'next/server'

export async function POST(request: Request) {
    try {
        console.log('Received PhonePe webhook')

        // Get headers
        const authorization = request.headers.get('authorization')
        const xVerify = request.headers.get('x-verify')

        if (!authorization && !xVerify) {
            console.error('Missing authorization headers')
            return NextResponse.json(
                { error: 'Missing authorization headers' },
                { status: 401 }
            )
        }

        // Get raw body
        const body = await request.text()

        // Forward to backend for validation and processing
        const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

        const backendResponse = await fetch(`${BACKEND_API_URL}/api/payments/v2/webhook`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authorization || xVerify || '',
            },
            body: body
        })

        if (backendResponse.ok) {
            const result = await backendResponse.json()
            console.log('Webhook successfully processed by backend:', result)
            return NextResponse.json(result)
        } else {
            const errorText = await backendResponse.text()
            console.error('Backend webhook processing failed:', errorText)
            return NextResponse.json(
                { error: 'Webhook processing failed' },
                { status: backendResponse.status }
            )
        }

    } catch (err) {
        console.error('Webhook processing error:', err)
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        )
    }
}
