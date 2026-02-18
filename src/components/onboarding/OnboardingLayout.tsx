"use client";

import { useEffect, useRef, ReactNode } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface OnboardingLayoutProps {
  children: ReactNode;
  currentStep: number;
  totalSteps: number;
  stepTitle: string;
  stepDescription: string;
  onBack?: () => void;
  onNext?: () => void;
  canGoNext: boolean;
  isNextLoading?: boolean;
  nextLabel?: string;
  showBack?: boolean;
}

export function OnboardingLayout({
  children,
  currentStep,
  totalSteps,
  stepTitle,
  stepDescription,
  onBack,
  onNext,
  canGoNext,
  isNextLoading = false,
  nextLabel = "Continue",
  showBack = true,
}: OnboardingLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Entrance animation
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      tl.fromTo(
        ".ob-header",
        { opacity: 0, y: -20 },
        { opacity: 1, y: 0, duration: 0.6 }
      )
        .fromTo(
          ".ob-progress",
          { opacity: 0, scaleX: 0 },
          { opacity: 1, scaleX: 1, duration: 0.5 },
          "-=0.3"
        )
        .fromTo(
          ".ob-step-indicator",
          { opacity: 0, x: -20 },
          { opacity: 1, x: 0, duration: 0.5 },
          "-=0.3"
        )
        .fromTo(
          ".ob-content",
          { opacity: 0, y: 30 },
          { opacity: 1, y: 0, duration: 0.6 },
          "-=0.2"
        )
        .fromTo(
          ".ob-footer",
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.5 },
          "-=0.3"
        );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  // Animate progress bar on step change
  useEffect(() => {
    if (progressRef.current) {
      gsap.to(progressRef.current, {
        width: `${(currentStep / totalSteps) * 100}%`,
        duration: 0.6,
        ease: "power2.out",
      });
    }
  }, [currentStep, totalSteps]);

  // Animate content on mount/change
  useEffect(() => {
    if (contentRef.current) {
      gsap.fromTo(
        contentRef.current,
        { opacity: 0, x: 20 },
        { opacity: 1, x: 0, duration: 0.5, ease: "power2.out" }
      );
    }
  }, [currentStep]);

  const progress = (currentStep / totalSteps) * 100;

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-[var(--bg-canvas)] flex flex-col"
    >
      {/* Header */}
      <header className="ob-header px-6 py-5 border-b border-[var(--border-1)] bg-[var(--bg-surface)]">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CompassLogo size={32} variant="compact" className="text-[var(--rf-charcoal)]" />
            <span className="font-semibold text-[var(--ink-1)] tracking-tight">
              RaptorFlow
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-[var(--ink-3)] rf-mono">
              Step {String(currentStep).padStart(2, "0")} / {String(totalSteps).padStart(2, "0")}
            </span>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="ob-progress w-full h-1 bg-[var(--border-1)]">
        <div
          ref={progressRef}
          className="h-full bg-[var(--rf-charcoal)] origin-left"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Main Content */}
      <main className="flex-1 flex">
        <div className="w-full max-w-3xl mx-auto px-6 py-10 md:py-16">
          {/* Step Header */}
          <div className="ob-step-indicator mb-10">
            <div className="flex items-center gap-2 mb-3">
              <span className="rf-mono text-xs uppercase tracking-[0.15em] text-[var(--ink-3)]">
                Step {currentStep}
              </span>
              <span className="w-8 h-px bg-[var(--border-2)]" />
              <span className="rf-mono text-xs text-[var(--ink-3)]">
                {Math.round(progress)}% complete
              </span>
            </div>
            <h1 className="text-[32px] leading-[40px] font-bold text-[var(--ink-1)] mb-3 tracking-tight">
              {stepTitle}
            </h1>
            <p className="text-base text-[var(--ink-2)] leading-relaxed max-w-xl">
              {stepDescription}
            </p>
          </div>

          {/* Content Area */}
          <div ref={contentRef} className="ob-content">
            {children}
          </div>
        </div>
      </main>

      {/* Footer Navigation */}
      <footer className="ob-footer border-t border-[var(--border-1)] bg-[var(--bg-surface)] px-6 py-5">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <button
            onClick={onBack}
            disabled={!showBack}
            className={`rf-btn-ghost ${!showBack ? "opacity-0 pointer-events-none" : ""}`}
          >
            <svg
              className="w-4 h-4 mr-1.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back
          </button>

          <button
            onClick={onNext}
            disabled={!canGoNext || isNextLoading}
            className="rf-btn-primary min-w-[140px] flex items-center justify-center gap-2"
          >
            {isNextLoading ? (
              <>
                <svg
                  className="animate-spin h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Processing...
              </>
            ) : (
              <>
                {nextLabel}
                <svg
                  className="w-4 h-4 ml-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </>
            )}
          </button>
        </div>
      </footer>
    </div>
  );
}
