"use client";

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { BlueprintButton } from './BlueprintButton';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        
        // Log error to monitoring service in production
        if (typeof window !== 'undefined' && (window as any).gtag) {
            (window as any).gtag('event', 'exception', {
                description: error.message,
                fatal: false
            });
        }
    }

    handleReset = () => {
        this.setState({ hasError: false, error: undefined });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-[400px] flex items-center justify-center p-8">
                    <div className="text-center max-w-md">
                        <div className="w-16 h-16 bg-[var(--error-light)] border border-[var(--error)] rounded-full flex items-center justify-center mx-auto mb-4">
                            <AlertTriangle size={24} className="text-[var(--error)]" />
                        </div>
                        
                        <h2 className="font-serif text-xl text-[var(--ink)] mb-2">
                            Something went wrong
                        </h2>
                        
                        <p className="text-sm text-[var(--ink-secondary)] mb-6">
                            {this.state.error?.message || 'An unexpected error occurred. Please try again.'}
                        </p>
                        
                        <BlueprintButton onClick={this.handleReset} className="inline-flex items-center gap-2">
                            <RefreshCw size={16} />
                            Try Again
                        </BlueprintButton>
                        
                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <details className="mt-6 text-left">
                                <summary className="text-xs text-[var(--muted)] cursor-pointer hover:text-[var(--ink)]">
                                    Error Details (Development)
                                </summary>
                                <pre className="mt-2 text-xs text-[var(--error)] bg-[var(--error-light)] p-3 rounded overflow-auto">
                                    {this.state.error.stack}
                                </pre>
                            </details>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
