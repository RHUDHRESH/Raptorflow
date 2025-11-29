import React from 'react'
import { Loader2, X, Check, ChevronRight, AlertCircle, ArrowLeft } from 'lucide-react'
import { cn } from '../../utils/cn'
import { Link } from 'react-router-dom'

// --- Typography ---
export const LuxeHeading = ({ level = 1, children, className = '', ...props }) => {
    const Tag = `h${level}`
    const sizes = {
        1: "text-4xl lg:text-5xl font-medium tracking-tight",
        2: "text-3xl lg:text-4xl font-medium tracking-tight",
        3: "text-2xl font-medium tracking-tight",
        4: "text-xl font-medium",
        5: "text-lg font-medium",
        6: "text-sm font-bold uppercase tracking-widest"
    }

    return (
        <Tag className={cn("font-display text-neutral-900", sizes[level], className)} {...props}>
            {children}
        </Tag>
    )
}

// --- Page Structure ---
export const PageHeader = ({
    title,
    subtitle,
    backUrl,
    action,
    className = ''
}) => {
    return (
        <div className={cn("flex flex-col gap-6 pb-8 border-b border-neutral-200", className)}>
            <div className="flex items-start justify-between gap-4">
                <div className="space-y-2">
                    {backUrl && (
                        <Link
                            to={backUrl}
                            className="inline-flex items-center text-sm text-neutral-500 hover:text-neutral-900 transition-colors mb-2 group"
                        >
                            <ArrowLeft className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" />
                            Back
                        </Link>
                    )}
                    <LuxeHeading level={1}>{title}</LuxeHeading>
                    {subtitle && (
                        <p className="text-lg text-neutral-500 max-w-3xl text-balance leading-relaxed">
                            {subtitle}
                        </p>
                    )}
                </div>
                {action && (
                    <div className="flex-shrink-0 pt-1">
                        {action}
                    </div>
                )}
            </div>
        </div>
    )
}

export const SectionHeader = ({
    title,
    description,
    action,
    className = ''
}) => {
    return (
        <div className={cn("flex items-end justify-between gap-4 mb-6", className)}>
            <div className="space-y-1">
                <h3 className="text-xl font-display font-medium text-neutral-900">{title}</h3>
                {description && (
                    <p className="text-sm text-neutral-500">{description}</p>
                )}
            </div>
            {action && (
                <div className="flex-shrink-0">
                    {action}
                </div>
            )}
        </div>
    )
}

// --- Buttons ---
export const LuxeButton = ({
    children,
    variant = 'primary',
    size = 'md',
    className = '',
    isLoading = false,
    icon: Icon = null,
    disabled = false,
    ...props
}) => {
    const variants = {
        primary: "bg-neutral-900 text-white hover:bg-black shadow-sm hover:shadow-md",
        secondary: "bg-white text-neutral-900 border border-neutral-200 hover:bg-neutral-50 hover:border-neutral-300 shadow-sm",
        ghost: "bg-transparent text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100",
        danger: "bg-white text-red-600 border border-red-200 hover:bg-red-50 hover:border-red-300"
    }

    const sizes = {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base"
    }

    return (
        <button
            className={cn(
                "inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 rounded-md disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]",
                variants[variant],
                sizes[size],
                className
            )}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            {!isLoading && Icon && <Icon className="w-4 h-4" />}
            {children}
        </button>
    )
}

// --- Cards ---
export const LuxeCard = ({ children, className = '', hover = false, onClick = undefined, delay = 0, ...props }) => {
    return (
        <div
            onClick={onClick}
            className={cn(
                "bg-white border border-neutral-200 rounded-lg shadow-sm p-6",
                (hover || onClick) && "transition-all duration-200 hover:shadow-md hover:border-neutral-300",
                onClick && "cursor-pointer",
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
}

// --- Stats ---
export const LuxeStat = ({ label, value, trend = null, icon: Icon = null, delay = 0 }) => {
    return (
        <LuxeCard className="flex flex-col gap-4" delay={delay}>
            <div className="flex items-center justify-between text-neutral-500">
                <span className="text-sm font-medium">{label}</span>
                {Icon && <Icon className="w-4 h-4" />}
            </div>
            <div className="flex items-end justify-between gap-2">
                <span className="text-3xl font-display font-medium text-neutral-900 tracking-tight">
                    {value}
                </span>
                {trend && (
                    <span className={cn(
                        "text-xs font-medium px-1.5 py-0.5 rounded mb-1",
                        trend > 0 ? "text-neutral-900 bg-neutral-100" : "text-neutral-600 bg-neutral-50"
                    )}>
                        {trend > 0 ? "+" : ""}{trend}%
                    </span>
                )}
            </div>
        </LuxeCard>
    )
}

// --- Badges ---
export const LuxeBadge = ({ children, variant = 'neutral', className = '', icon: Icon = null }) => {
    const variants = {
        neutral: "bg-neutral-100 text-neutral-600 border-transparent",
        dark: "bg-neutral-900 text-white border-transparent",
        success: "bg-white text-green-700 border-green-200",
        warning: "bg-white text-amber-700 border-amber-200",
        error: "bg-white text-red-700 border-red-200",
        info: "bg-white text-blue-700 border-blue-200"
    }

    return (
        <span className={cn(
            "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border",
            variants[variant],
            className
        )}>
            {Icon && <Icon className="w-3 h-3" />}
            {children}
        </span>
    )
}

// --- Inputs ---
export const LuxeInput = ({ label = '', error = '', helperText = '', className = '', id, ...props }) => {
    const inputId = id || React.useId();

    return (
        <div className="space-y-2 w-full">
            {label && (
                <label
                    htmlFor={inputId}
                    className="text-sm font-semibold block"
                    style={{ color: 'var(--ink-strong)' }}
                >
                    {label}
                </label>
            )}
            <div className="relative">
                <input
                    id={inputId}
                    className={cn(
                        "w-full px-4 py-3 rounded-lg bg-white text-base outline-none transition-all",
                        error ? "border-2 border-red-500 focus:border-red-600" : "border focus:border-2",
                        className
                    )}
                    style={{
                        borderColor: error ? undefined : 'var(--border-subtle)',
                        color: 'var(--ink-strong)',
                        fontFamily: 'var(--font-body)'
                    }}
                    onFocus={(e) => {
                        if (!error) {
                            e.target.style.borderColor = 'var(--ink-strong)';
                        }
                    }}
                    onBlur={(e) => {
                        if (!error) {
                            e.target.style.borderColor = 'var(--border-subtle)';
                        }
                    }}
                    {...props}
                />
            </div>
            {helperText && !error && (
                <p className="text-xs" style={{ color: 'var(--ink-soft)' }}>
                    {helperText}
                </p>
            )}
            {error && (
                <p className="text-xs text-red-600 font-medium flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {error}
                </p>
            )}
        </div>
    )
}

// --- Textarea ---
export const LuxeTextarea = ({ label = '', error = '', helperText = '', className = '', id, rows = 4, ...props }) => {
    const inputId = id || React.useId();

    return (
        <div className="space-y-2 w-full">
            {label && (
                <label
                    htmlFor={inputId}
                    className="text-sm font-semibold block"
                    style={{ color: 'var(--ink-strong)' }}
                >
                    {label}
                </label>
            )}
            <div className="relative">
                <textarea
                    id={inputId}
                    rows={rows}
                    className={cn(
                        "w-full px-4 py-3 rounded-lg bg-white text-base outline-none transition-all resize-y leading-relaxed",
                        error ? "border-2 border-red-500 focus:border-red-600" : "border focus:border-2",
                        className
                    )}
                    style={{
                        borderColor: error ? undefined : 'var(--border-subtle)',
                        color: 'var(--ink-strong)',
                        fontFamily: 'var(--font-body)',
                        lineHeight: '1.6'
                    }}
                    onFocus={(e) => {
                        if (!error) {
                            e.target.style.borderColor = 'var(--ink-strong)';
                        }
                    }}
                    onBlur={(e) => {
                        if (!error) {
                            e.target.style.borderColor = 'var(--border-subtle)';
                        }
                    }}
                    {...props}
                />
            </div>
            {helperText && !error && (
                <p className="text-xs" style={{ color: 'var(--ink-soft)' }}>
                    {helperText}
                </p>
            )}
            {error && (
                <p className="text-xs text-red-600 font-medium flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {error}
                </p>
            )}
        </div>
    )
}

// --- Tabs ---
export const LuxeTabs = ({ tabs, activeTab, onChange, className = '' }) => {
    return (
        <div className={cn("flex gap-1 p-1 bg-neutral-100 rounded-lg w-fit", className)}>
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    onClick={() => onChange(tab.id)}
                    className={cn(
                        "px-4 py-2 text-sm font-medium rounded-md transition-all duration-200",
                        activeTab === tab.id
                            ? "bg-white text-neutral-900 shadow-sm"
                            : "text-neutral-500 hover:text-neutral-900 hover:bg-neutral-200/50"
                    )}
                >
                    {tab.label}
                </button>
            ))}
        </div>
    )
}

// --- Modals (Simple CSS version without heavy motion) ---
export const LuxeModal = ({ isOpen, onClose, title, children, size = 'md' }) => {
    const sizes = {
        sm: "max-w-md",
        md: "max-w-2xl",
        lg: "max-w-4xl",
        xl: "max-w-6xl"
    }

    if (!isOpen) return null;

    return (
        <>
            <div
                onClick={onClose}
                className="fixed inset-0 bg-neutral-900/20 backdrop-blur-sm z-50 transition-opacity animate-fade-in"
            />
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                <div
                    className={cn(
                        "w-full bg-white border border-neutral-200 shadow-2xl rounded-lg overflow-hidden pointer-events-auto flex flex-col max-h-[90vh] animate-slide-up",
                        sizes[size]
                    )}
                >
                    <div className="flex items-center justify-between p-6 border-b border-neutral-100 bg-white sticky top-0 z-10">
                        <h3 className="font-display text-xl font-medium text-neutral-900">{title}</h3>
                        <button
                            onClick={onClose}
                            className="p-2 text-neutral-400 hover:text-neutral-900 hover:bg-neutral-100 rounded-md transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                    <div className="p-6 overflow-y-auto">
                        {children}
                    </div>
                </div>
            </div>
        </>
    )
}

// --- Empty States ---
export const LuxeEmptyState = ({
    icon: Icon = null,
    title,
    description,
    action = null,
    className = ''
}) => {
    return (
        <div className={cn(
            "flex flex-col items-center justify-center text-center py-16 px-4 border border-dashed border-neutral-200 rounded-lg bg-neutral-50/50",
            className
        )}>
            {Icon && (
                <div className="mb-4 p-3 bg-white rounded-full shadow-sm border border-neutral-100">
                    <Icon className="w-6 h-6 text-neutral-400" />
                </div>
            )}
            <h3 className="font-display text-lg font-medium text-neutral-900 mb-2">
                {title}
            </h3>
            <p className="text-sm text-neutral-500 max-w-sm mb-6 leading-relaxed text-balance">
                {description}
            </p>
            {action && (
                <div>
                    {action}
                </div>
            )}
        </div>
    )
}

// --- Loading ---
export const LuxeSkeleton = ({ className = '', ...props }) => {
    return (
        <div
            className={cn("animate-pulse bg-neutral-100 rounded", className)}
            {...props}
        />
    )
}
