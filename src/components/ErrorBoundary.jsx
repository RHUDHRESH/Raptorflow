/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree
 */

import React from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import { analytics } from '../lib/posthog';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to analytics service
    analytics.trackError(error, {
      componentStack: errorInfo?.componentStack,
      errorBoundary: this.props.name || 'ErrorBoundary',
    });
    
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50 p-4">
          <div className="max-w-2xl w-full">
            <div className="runway-card p-12 text-center">
              {/* Error Icon */}
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-red-50 border-2 border-red-200 flex items-center justify-center">
                <AlertCircle className="w-10 h-10 text-red-600" />
              </div>

              {/* Error Title */}
              <h1 className="text-3xl font-bold text-neutral-900 mb-3">
                Oops! Something went wrong
              </h1>
              
              <p className="text-neutral-600 mb-8">
                We encountered an unexpected error. Don't worry, your data is safe.
              </p>

              {/* Error Details (in development) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="mb-8 text-left">
                  <details className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <summary className="cursor-pointer font-medium text-red-900 mb-2">
                      Error Details (Development Only)
                    </summary>
                    <pre className="text-xs text-red-700 overflow-auto max-h-64">
                      {this.state.error.toString()}
                      {'\n\n'}
                      {this.state.errorInfo?.componentStack}
                    </pre>
                  </details>
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.handleReset}
                  className="px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 flex items-center justify-center gap-2 font-medium"
                >
                  <RefreshCw className="w-4 h-4" />
                  Reload Page
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="px-6 py-3 border border-neutral-200 text-neutral-900 rounded-lg hover:bg-neutral-50 flex items-center justify-center gap-2 font-medium"
                >
                  <Home className="w-4 h-4" />
                  Go to Dashboard
                </button>
              </div>

              {/* Support Info */}
              <p className="mt-8 text-sm text-neutral-500">
                If this problem persists, please contact support with the error details above.
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

