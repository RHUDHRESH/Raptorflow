import React from 'react'
import { clsx } from 'clsx'

/**
 * Editorial Button Component
 * Variants: primary, secondary, oauth
 */
export default function Button({
    children,
    variant = 'primary',
    className = '',
    type = 'button',
    onClick,
    ...props
}) {
    const baseStyles = 'inline-flex items-center justify-center gap-2 text-xs uppercase tracking-[0.22em] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed'

    const variants = {
        primary: 'px-5 py-3 rounded-full bg-charcoal text-canvas hover:bg-aubergine hover-lift',
        secondary: 'border-b border-charcoal/30 hover:border-aubergine hover:text-aubergine',
        oauth: 'w-full px-5 py-3 rounded-full border border-line bg-white/40 text-charcoal hover:bg-white/60 hover:border-charcoal/30 hover-lift'
    }

    return (
        <button
            type={type}
            onClick={onClick}
            className={clsx(baseStyles, variants[variant], className)}
            {...props}
        >
            {children}
        </button>
    )
}
