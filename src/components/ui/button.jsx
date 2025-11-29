import React from 'react'
import { cn } from '../../utils/cn'

const Button = React.forwardRef(({
    className = '',
    variant = 'default',
    size = 'default',
    disabled = false,
    ...props
}, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neutral-900 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none'

    const variants = {
        default: 'bg-neutral-900 text-white hover:bg-black shadow-sm',
        destructive: 'bg-white text-red-600 border border-red-200 hover:bg-red-50',
        outline: 'border border-neutral-200 bg-white hover:bg-neutral-50 text-neutral-900',
        secondary: 'bg-neutral-100 text-neutral-900 hover:bg-neutral-200',
        ghost: 'hover:bg-neutral-100 hover:text-neutral-900',
        link: 'text-neutral-900 underline-offset-4 hover:underline',
    }

    const sizes = {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3 rounded-md',
        lg: 'h-11 px-8 rounded-md',
        icon: 'h-10 w-10',
    }

    return (
        <button
            ref={ref}
            className={cn(baseStyles, variants[variant], sizes[size], className)}
            disabled={disabled}
            {...props}
        />
    )
})

Button.displayName = 'Button'

export { Button }
