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
            <details className="mb-8 max-w-2xl w-full bg-white/70 border border-black/10 rounded p-4 text-sm">
                <summary className="cursor-pointer font-medium">Error details</summary>
                <div className="mt-3 space-y-2">
                    <div>
                        <div className="text-xs uppercase tracking-wide text-[#5B5F61]">Message</div>
                        <div className="font-mono whitespace-pre-wrap">{error?.message || "(no message)"}</div>
                    </div>
                    {error?.digest && (
                        <div>
                            <div className="text-xs uppercase tracking-wide text-[#5B5F61]">Digest</div>
                            <div className="font-mono">{error.digest}</div>
                        </div>
                    )}
                    {error?.stack && (
                        <div>
                            <div className="text-xs uppercase tracking-wide text-[#5B5F61]">Stack</div>
                            <pre className="overflow-auto font-mono text-xs whitespace-pre-wrap">{error.stack}</pre>
                        </div>
                    )}
                </div>
            </details>
            <button
                onClick={() => reset()}
                className="px-6 py-3 bg-[#2D3538] text-white rounded hover:bg-[#1a1f21] transition-colors"
            >
                Try again
            </button>
        </div>
    )
}
