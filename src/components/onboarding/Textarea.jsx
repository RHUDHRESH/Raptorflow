import React, { useEffect, useRef } from 'react'
import { clsx } from 'clsx'

/**
 * Editorial Textarea Component
 * Matches Input.jsx styling with auto-resize functionality
 */
export default function Textarea({
    label,
    error,
    className = '',
    id,
    rows = 3,
    ...props
}) {
    const textareaRef = useRef(null)
    const textareaId = id || label?.toLowerCase().replace(/\s+/g, '-')

    // Auto-resize textarea based on content
    useEffect(() => {
        const textarea = textareaRef.current
        if (textarea) {
            textarea.style.height = 'auto'
            textarea.style.height = `${textarea.scrollHeight}px`
        }
    }, [props.value])

    return (
        <div className={clsx('space-y-2', className)}>
            {label && (
                <label
                    htmlFor={textareaId}
                    className="block text-[11px] uppercase tracking-[0.22em] text-charcoal/60"
                >
                    {label}
                </label>
            )}
            <textarea
                ref={textareaRef}
                id={textareaId}
                rows={rows}
                className={clsx(
                    'w-full px-4 py-3 rounded-lg border bg-white/40 text-charcoal',
                    'text-sm placeholder:text-charcoal/40',
                    'transition-all duration-200 resize-none',
                    'focus:outline-none focus:ring-1 focus:ring-aubergine focus:border-aubergine',
                    error
                        ? 'border-red-400 focus:ring-red-400 focus:border-red-400'
                        : 'border-line hover:border-charcoal/30'
                )}
                {...props}
            />
            <div className="flex justify-between items-start">
                {error && (
                    <p className="text-xs text-red-500">{error}</p>
                )}
                {props.maxLength && (
                    <p className={clsx(
                        "text-[10px] text-charcoal/40 ml-auto",
                        (props.value?.length || 0) > props.maxLength * 0.9 && "text-orange-500",
                        (props.value?.length || 0) >= props.maxLength && "text-red-500"
                    )}>
                        {props.value?.length || 0}/{props.maxLength}
                    </p>
                )}
            </div>
        </div>
    )
}
