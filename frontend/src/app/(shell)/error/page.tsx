"use client";

import { useEffect } from "react";
import { RefreshCw, AlertTriangle } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

export default function ErrorPage() {
  useEffect(() => {
    // Log the error for debugging but don't show details to user
    console.error("Critical system error occurred");
  }, []);

  const handleRetry = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    window.location.href = "/dashboard";
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center p-8">
      <div className="max-w-md w-full text-center space-y-8">
        {/* Error Icon */}
        <div className="mx-auto w-16 h-16 bg-[var(--error)]/10 rounded-full flex items-center justify-center">
          <AlertTriangle size={32} className="text-[var(--error)]" />
        </div>

        {/* Error Message */}
        <div className="space-y-4">
          <h1 className="font-serif text-3xl text-[var(--ink)]">Error</h1>
          <p className="text-[var(--ink-secondary)] leading-relaxed">
            The system encountered an unexpected structural failure. Our engineers have been dispatched.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <BlueprintButton
            size="lg"
            onClick={handleRetry}
            className="w-full"
          >
            <RefreshCw size={20} />
            Try Again
          </BlueprintButton>

          <BlueprintButton
            variant="ghost"
            size="lg"
            onClick={handleGoHome}
            className="w-full"
          >
            Return to Dashboard
          </BlueprintButton>
        </div>

        {/* Help Text */}
        <p className="text-xs text-[var(--ink-muted)]">
          If this problem persists, please contact support.
        </p>
      </div>
    </div>
  );
}
