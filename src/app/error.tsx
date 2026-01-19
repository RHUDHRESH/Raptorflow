'use client'

import { useEffect } from 'react'

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error(error)
    }, [error])

    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-[#F3F4EE] text-[#2D3538] font-sans">
            <h2 className="text-3xl font-serif font-bold mb-4">Something went wrong!</h2>
            <p className="mb-8 text-[#5B5F61]">The system encountered an unexpected error.</p>
            <button
                onClick={() => reset()}
                className="px-6 py-3 bg-[#2D3538] text-white rounded hover:bg-[#1a1f21] transition-colors"
            >
                Try again
            </button>
        </div>
    )
}
