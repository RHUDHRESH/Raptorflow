'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class InferenceErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Inference Error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex flex-col items-center justify-center p-12 rounded-[2rem] border border-red-100 bg-red-50/30 dark:bg-red-950/10 dark:border-red-900/20 text-center space-y-6 animate-in fade-in duration-500">
          <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-display font-semibold text-zinc-900 dark:text-zinc-100">
              Intelligence Interrupted
            </h2>
            <p className="text-zinc-500 dark:text-zinc-400 max-w-sm mx-auto">
              Something went wrong while executing the agentic workflow. This is usually a connectivity issue with Vertex AI.
            </p>
          </div>
          <Button
            onClick={this.handleReset}
            className="rounded-full bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 h-12 px-8 font-medium shadow-lg"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Restart Engine
          </Button>
          {this.state.error && (
            <p className="text-[10px] font-mono text-red-400/60 uppercase tracking-widest pt-4">
              Error: {this.state.error.message}
            </p>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
