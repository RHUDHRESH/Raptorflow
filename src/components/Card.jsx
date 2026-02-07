import React from 'react'
import { clsx } from 'clsx'

/**
 * Editorial Card Component
 * Consistent with landing page card aesthetic
 */
export default function Card({
    children,
    className = '',
    hover = true,
    ...props
}) {
    return (
        <div
            className={clsx(
                'border border-line rounded-2xl p-6 md:p-8 bg-white/40',
                hover && 'hover-lift hover:bg-white/50',
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
}
