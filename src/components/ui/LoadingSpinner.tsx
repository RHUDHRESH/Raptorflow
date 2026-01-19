"use client";

import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
    size?: "sm" | "md" | "lg";
    className?: string;
    text?: string;
}

export function LoadingSpinner({ size = "md", className, text }: LoadingSpinnerProps) {
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
    error?: Error | null;
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
        return errorFallback as React.ReactElement || (
            <div className="text-center py-8">
                <div className="text-[var(--error)] text-sm mb-2">
                    Error: {error.message}
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
        return fallback as React.ReactElement || <LoadingSpinner />;
    }

    return children as React.ReactElement;
}
