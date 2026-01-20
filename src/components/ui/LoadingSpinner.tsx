"use client";

import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { BlueprintLoader } from "./BlueprintLoader";

interface LoadingSpinnerProps {
    size?: "sm" | "md" | "lg";
    className?: string;
    text?: string;
    variant?: "classic" | "blueprint";
}

/**
 * Standardized Loading Spinner for RaptorFlow.
 * Uses BlueprintLoader for technical branding by default.
 */
export function LoadingSpinner({ 
    size = "md", 
    className, 
    text,
    variant = "blueprint" 
}: LoadingSpinnerProps) {
    if (variant === "blueprint") {
        return (
            <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
                <BlueprintLoader size={size} />
                {text && (
                    <span className="font-technical text-[10px] text-[var(--blueprint)] uppercase tracking-wider">
                        {text}
                    </span>
                )}
            </div>
        );
    }

    const sizeClasses = {
        sm: "w-4 h-4",
        md: "w-6 h-6", 
        lg: "w-8 h-8"
    };

    return (
        <div className={cn("flex items-center justify-center gap-2", className)}>
            <Loader2 className={cn("animate-spin text-[var(--blueprint)]", sizeClasses[size])} />
            {text && (
                <span className="text-sm text-[var(--ink-secondary)]">{text}</span>
            )}
        </div>
    );
}

interface LoadingStateProps {
    isLoading: boolean;
    error?: Error | { message: string } | null;
    children: React.ReactNode;
    fallback?: React.ReactNode;
    errorFallback?: React.ReactNode;
}

export function LoadingState({ 
    isLoading, 
    error, 
    children, 
    fallback, 
    errorFallback 
}: LoadingStateProps): React.ReactElement {
    if (error) {
        const message = 'message' in error ? error.message : String(error);
        return (errorFallback as React.ReactElement) || (
            <div className="text-center py-8">
                <div className="text-[var(--error)] text-sm mb-2">
                    Error: {message}
                </div>
                <button 
                    onClick={() => window.location.reload()}
                    className="text-xs text-[var(--blueprint)] hover:underline"
                >
                    Retry
                </button>
            </div>
        );
    }

    if (isLoading) {
        return (fallback as React.ReactElement) || <LoadingSpinner />;
    }

    return <>{children}</> as React.ReactElement;
}