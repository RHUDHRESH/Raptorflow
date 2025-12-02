import React from 'react'
import { clsx } from 'clsx'

/**
 * Editorial Input Component
 * Supports text, email, password types with label and error states
 */
export default function Input({
    label,
    type = 'text',
    error,
    className = '',
    id,
    ...props
}) {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
        <div className={clsx('space-y-2', className)}>
            {label && (
                <label
                    htmlFor={inputId}
                    className="block text-[11px] uppercase tracking-[0.22em] text-charcoal/60"
                >
                    {label}
                </label>
            )}
            <input
                id={inputId}
                type={type}
                className={clsx(
                    'w-full px-4 py-3 rounded-lg border bg-white/40 text-charcoal',
                    'text-sm placeholder:text-charcoal/40',
                    'transition-all duration-200',
                    'focus:outline-none focus:ring-1 focus:ring-aubergine focus:border-aubergine',
                    error
                        ? 'border-red-400 focus:ring-red-400 focus:border-red-400'
                        : 'border-line hover:border-charcoal/30'
                )}
                {...props}
            />
            {error && (
                <p className="text-xs text-red-500">{error}</p>
            )}
        </div>
    )
}
