import React from 'react'
import { clsx } from 'clsx'

/**
 * ChipGroup Component
 * Supports single-select (radio) or multi-select (checkbox) chips
 */
export default function ChipGroup({
    options,
    value,
    onChange,
    multiple = false,
    className = '',
    label
}) {
    const handleClick = (optionValue) => {
        if (multiple) {
            // Multi-select: toggle value in array
            const newValue = value?.includes(optionValue)
                ? value.filter(v => v !== optionValue)
                : [...(value || []), optionValue]
            onChange(newValue)
        } else {
            // Single-select: set value directly
            onChange(optionValue)
        }
    }

    const isSelected = (optionValue) => {
        if (multiple) {
            return value?.includes(optionValue)
        }
        return value === optionValue
    }

    return (
        <div className={clsx('space-y-2', className)}>
            {label && (
                <label className="block text-[11px] uppercase tracking-[0.22em] text-charcoal/60">
                    {label}
                </label>
            )}
            <div className="flex flex-wrap gap-2">
                {options.map((option) => {
                    const optionValue = typeof option === 'string' ? option : option.value
                    const optionLabel = typeof option === 'string' ? option : option.label
                    const selected = isSelected(optionValue)

                    return (
                        <button
                            key={optionValue}
                            type="button"
                            onClick={() => handleClick(optionValue)}
                            className={clsx(
                                'px-4 py-2 rounded-full text-xs uppercase tracking-[0.18em]',
                                'border transition-all duration-300',
                                'hover:scale-105',
                                selected
                                    ? 'bg-charcoal text-canvas border-charcoal'
                                    : 'bg-white/40 text-charcoal border-line hover:border-charcoal/30'
                            )}
                        >
                            {optionLabel}
                        </button>
                    )
                })}
            </div>
        </div>
    )
}
