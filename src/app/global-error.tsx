'use client'

import * as Sentry from '@sentry/nextjs'
import { useEffect } from 'react'

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        Sentry.captureException(error)
    }, [error])

    return (
        <html>
            <body className="flex min-h-screen flex-col items-center justify-center bg-[#F3F4EE] text-[#2D3538] font-sans">
                <h2 className="text-3xl font-serif font-bold mb-4">Critical System Error</h2>
                <p className="mb-8 text-[#5B5F61]">A critical error occurred preventing the app from loading.</p>
                <button
                    onClick={() => reset()}
                    className="px-6 py-3 bg-[#2D3538] text-white rounded hover:bg-[#1a1f21] transition-colors"
                >
                    Try again
                </button>
            </body>
        </html>
    )
}
