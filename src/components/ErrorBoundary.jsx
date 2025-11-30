/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree
 */

import React from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
// import { analytics } from '../lib/posthog';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to analytics service (if available)
    try {
      // analytics.trackError(error, {
      //   componentStack: errorInfo?.componentStack,
      //   errorBoundary: this.props.name || 'ErrorBoundary',
      // });
      console.error('Error caught by boundary:', error, errorInfo);
    } catch (e) {
      console.error('Failed to track error:', e);
    }

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
        <React.Suspense fallback={<div className="min-h-screen bg-black" />}>
          <Error500
            error={this.state.error}
            resetErrorBoundary={this.handleReset}
          />
        </React.Suspense>
      );
    }

    return this.props.children;
  }
}

const Error500 = React.lazy(() => import('../pages/Error500'));

export default ErrorBoundary;

