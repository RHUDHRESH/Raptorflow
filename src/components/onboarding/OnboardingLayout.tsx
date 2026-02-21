"use client";

import { useEffect, useRef, ReactNode, useState, useCallback } from "react";
import { gsap } from "gsap";
import { ArrowLeft, ArrowRight, CheckCircle2, Sparkles } from "lucide-react";

const PHASES = [
  { label: "Identity", steps: [1, 2, 3, 4, 5] },
  { label: "Customer & Problem", steps: [6, 7, 8, 9] },
  { label: "Strategy", steps: [10, 11, 12, 13] },
  { label: "Brand & Voice", steps: [14, 15, 16] },
  { label: "Market & Proof", steps: [17, 18, 19, 20, 21] },
];

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
  const titleRef = useRef<HTMLHeadingElement>(null);
  const descRef = useRef<HTMLParagraphElement>(null);
  const stepLabelRef = useRef<HTMLDivElement>(null);
  const progressFillRef = useRef<HTMLDivElement>(null);
  const [progressGlow, setProgressGlow] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const progress = (currentStep / totalSteps) * 100;
  const currentPhaseIndex = PHASES.findIndex((p) => p.steps.includes(currentStep));

  // Store previous step for animation direction
  const prevStepRef = useRef(currentStep);

  // Initial entrance animation - elegant stagger
  useEffect(() => {
    // Delay to allow children to render first
    const timer = setTimeout(() => {
      // Double-check elements exist before animating
      const sidebar = containerRef.current?.querySelector(".ob-sidebar");
      const progressContainer = containerRef.current?.querySelector(".ob-progress-container");
      const phaseItems = containerRef.current?.querySelectorAll(".ob-phase-item");
      const contentWrap = containerRef.current?.querySelector(".ob-content-wrap");
      
      // Only animate if core elements exist
      if (!sidebar || !progressContainer || !contentWrap) {
        setIsAnimating(false);
        return;
      }

      const ctx = gsap.context(() => {
        const tl = gsap.timeline({ 
          defaults: { ease: "power3.out" },
          onComplete: () => setIsAnimating(false)
        });

        // Sidebar slides in from left
        tl.fromTo(sidebar, 
          { opacity: 0, x: -30 }, 
          { opacity: 1, x: 0, duration: 0.6 }
        )
        // Progress bar fills
        .fromTo(progressContainer,
          { opacity: 0, y: 10 },
          { opacity: 1, y: 0, duration: 0.4 },
          "-=0.4"
        );
        
        // Phase items stagger (only if exist)
        if (phaseItems && phaseItems.length > 0) {
          tl.fromTo(phaseItems,
            { opacity: 0, x: -15 },
            { opacity: 1, x: 0, duration: 0.35, stagger: 0.08 },
            "-=0.3"
          );
        }
        
        // Content area rises
        tl.fromTo(contentWrap, 
          { opacity: 0, y: 30 }, 
          { opacity: 1, y: 0, duration: 0.5 },
          "-=0.4"
        )
        // Step label fades
        .fromTo(stepLabelRef.current,
          { opacity: 0, y: 10 },
          { opacity: 1, y: 0, duration: 0.35 },
          "-=0.3"
        )
        // Title reveals
        .fromTo(titleRef.current,
          { opacity: 0, y: 15, clipPath: "inset(100% 0 0 0)" },
          { opacity: 1, y: 0, clipPath: "inset(0% 0 0 0)", duration: 0.45 },
          "-=0.25"
        )
        // Description follows
        .fromTo(descRef.current,
          { opacity: 0, y: 10 },
          { opacity: 1, y: 0, duration: 0.35 },
          "-=0.3"
        );
        
        // Content children stagger (only animate if elements exist)
        const animateElements = containerRef.current?.querySelectorAll(".ob-animate-in");
        if (animateElements && animateElements.length > 0) {
          tl.fromTo(animateElements,
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06 },
            "-=0.2"
          );
        }
      }, containerRef);

      return () => ctx.revert();
    }, 100); // Delay to allow children to render

    return () => clearTimeout(timer);
  }, []);

  // Progress bar animation on step change
  useEffect(() => {
    if (progressFillRef.current) {
      gsap.to(progressFillRef.current, {
        width: `${progress}%`,
        duration: 0.7,
        ease: "power2.inOut",
      });
    }
    setProgressGlow(true);
    const t = setTimeout(() => setProgressGlow(false), 900);
    return () => clearTimeout(t);
  }, [currentStep, progress]);

  // Content transition on step change
  useEffect(() => {
    // Skip animation on initial mount
    if (prevStepRef.current === currentStep) {
      prevStepRef.current = currentStep;
      return;
    }
    
    const direction = currentStep > prevStepRef.current ? 1 : -1;
    prevStepRef.current = currentStep;

    if (contentRef.current) {
      const ctx = gsap.context(() => {
        const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

        // Exit animation
        tl.fromTo(contentRef.current,
          { opacity: 0, x: direction * 30 },
          { opacity: 1, x: 0, duration: 0.4 }
        );
        
        // Animate content items with stagger (only if elements exist)
        const contentItems = contentRef.current?.querySelectorAll(".ob-content-item");
        if (contentItems && contentItems.length > 0) {
          tl.fromTo(contentItems,
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.35, stagger: 0.05 },
            "-=0.25"
          );
        }
        
        // Interactive elements pop (only if elements exist)
        const interactiveElements = contentRef.current?.querySelectorAll(".ob-interactive");
        if (interactiveElements && interactiveElements.length > 0) {
          tl.fromTo(interactiveElements,
            { opacity: 0, scale: 0.95 },
            { opacity: 1, scale: 1, duration: 0.3, stagger: 0.04 },
            "-=0.2"
          );
        }
      }, containerRef);

      return () => ctx.revert();
    }
  }, [currentStep]);

  // Title/description update animation
  const isFirstTitleRender = useRef(true);
  useEffect(() => {
    // Skip animation on first render (handled by initial animation)
    if (isFirstTitleRender.current) {
      isFirstTitleRender.current = false;
      return;
    }
    
    const ctx = gsap.context(() => {
      gsap.fromTo([titleRef.current, descRef.current],
        { opacity: 0, y: 8 },
        { opacity: 1, y: 0, duration: 0.35, stagger: 0.08, ease: "power2.out" }
      );
    }, containerRef);
    return () => ctx.revert();
  }, [stepTitle, stepDescription]);

  // Handle navigation with animation
  const handleNext = useCallback(() => {
    if (isAnimating || !canGoNext) return;
    setIsAnimating(true);
    
    const ctx = gsap.context(() => {
      gsap.to(contentRef.current, {
        opacity: 0,
        x: -20,
        duration: 0.2,
        ease: "power2.in",
        onComplete: () => {
          onNext?.();
          setIsAnimating(false);
        }
      });
    }, containerRef);
  }, [canGoNext, isAnimating, onNext]);

  const handleBack = useCallback(() => {
    if (isAnimating) return;
    setIsAnimating(true);

    const ctx = gsap.context(() => {
      gsap.to(contentRef.current, {
        opacity: 0,
        x: 20,
        duration: 0.2,
        ease: "power2.in",
        onComplete: () => {
          onBack?.();
          setIsAnimating(false);
        }
      });
    }, containerRef);
  }, [isAnimating, onBack]);

  return (
    <div ref={containerRef} className="min-h-screen bg-[var(--bg-canvas)] flex font-sans">

      {/* ── Sidebar ── */}
      <aside className="ob-sidebar hidden lg:flex flex-col w-[240px] border-r border-[var(--border-1)] bg-[var(--bg-surface)] flex-shrink-0 sticky top-0 h-screen overflow-y-auto">
        {/* Logo */}
        <div className="ob-logo px-5 py-5 border-b border-[var(--border-1)] flex items-center gap-2.5">
          <div className="relative">
            <svg width="20" height="20" viewBox="0 0 24 24" className="text-[var(--ink-1)] flex-shrink-0">
              <path d="M12 2L18.5 13H5.5L12 2Z" fill="currentColor" />
              <path d="M12 22L18.5 13H5.5L12 22Z" fill="currentColor" opacity="0.4" />
              <circle cx="12" cy="13" r="1.8" fill="var(--bg-surface)" />
            </svg>
            <div className="absolute inset-0 bg-[var(--rf-charcoal)] rounded-full scale-0 opacity-0 animate-ping-slow" 
                 style={{ animationDelay: "1s" }} />
          </div>
          <span className="font-bold text-[14px] text-[var(--ink-1)] tracking-tight">RaptorFlow</span>
        </div>

        {/* Progress bar */}
        <div className="ob-progress-container px-5 pt-5 pb-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono text-[var(--ink-3)] tracking-widest">SETUP PROGRESS</span>
            <span className="text-[11px] font-mono text-[var(--ink-2)] font-semibold">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-[var(--border-1)] rounded-full overflow-hidden">
            <div
              ref={progressFillRef}
              className={`h-full bg-[var(--rf-charcoal)] rounded-full origin-left transition-shadow duration-300 ${progressGlow ? "shadow-[0_0_12px_2px_rgba(42,37,41,0.25)]" : ""}`}
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-1.5 text-[10px] font-mono text-[var(--ink-3)]">Step {currentStep} of {totalSteps}</p>
        </div>

        {/* Phase list */}
        <div className="px-4 pb-6 space-y-0.5 mt-1">
          {PHASES.map((phase, phaseIdx) => {
            const isActive = phaseIdx === currentPhaseIndex;
            const isDone = phaseIdx < currentPhaseIndex;
            return (
              <div key={phase.label} className="ob-phase-item">
                <div className={`flex items-center gap-2.5 px-3 py-2.5 rounded-[var(--radius-sm)] transition-all duration-200 ${isActive ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)]"
                    : isDone ? "text-[var(--status-success)]"
                      : "text-[var(--ink-3)]"
                  }`}>
                  {isDone
                    ? <CheckCircle2 size={14} className="flex-shrink-0" />
                    : <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isActive ? "bg-[var(--rf-ivory)]" : "bg-current opacity-30"}`} />
                  }
                  <span className="text-[12px] font-medium">{phase.label}</span>
                  {isActive && <Sparkles size={12} className="ml-auto opacity-60" />}
                </div>
                {isActive && (
                  <div className="flex items-center gap-1.5 px-3 mt-2 mb-2">
                    {phase.steps.map((s) => (
                      <div key={s} className={`h-1.5 rounded-full transition-all duration-300 ${s === currentStep ? "w-5 bg-[var(--rf-charcoal)]"
                          : s < currentStep ? "w-1.5 bg-[var(--status-success)]"
                            : "w-1.5 bg-[var(--border-2)]"
                        }`} />
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Bottom hint */}
        <div className="mt-auto px-5 py-4 border-t border-[var(--border-1)]">
          <p className="text-[10px] text-[var(--ink-3)] leading-relaxed">
            Your answers build your marketing foundation. You can edit them anytime.
          </p>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <div className="flex-1 flex flex-col min-h-screen">

        {/* Mobile header */}
        <div className="lg:hidden flex items-center justify-between px-5 py-3 border-b border-[var(--border-1)] bg-[var(--bg-surface)]">
          <div className="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24"><path d="M12 2L18.5 13H5.5L12 2Z" fill="currentColor" /><path d="M12 22L18.5 13H5.5L12 22Z" fill="currentColor" opacity="0.4" /></svg>
            <span className="font-bold text-[13px]">RaptorFlow</span>
          </div>
          <span className="text-[11px] font-mono text-[var(--ink-3)]">{currentStep}/{totalSteps}</span>
        </div>

        {/* Mobile progress bar */}
        <div className="lg:hidden h-1.5 bg-[var(--border-1)] w-full">
          <div
            className={`h-full bg-[var(--rf-charcoal)] transition-all duration-500 ease-out ${progressGlow ? "shadow-[0_0_8px_rgba(42,37,41,0.3)]" : ""}`}
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Mobile phase pills */}
        <div className="lg:hidden flex items-center gap-2 px-5 py-3 overflow-x-auto border-b border-[var(--border-1)] bg-[var(--bg-surface)]/60">
          {PHASES.map((phase, phaseIdx) => (
            <span key={phase.label} className={`whitespace-nowrap text-[10px] font-medium px-2.5 py-1 rounded-full transition-all ${phaseIdx === currentPhaseIndex ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)]"
                : phaseIdx < currentPhaseIndex ? "bg-[var(--status-success)]/10 text-[var(--status-success)]"
                  : "text-[var(--ink-3)]"
              }`}>
              {phase.label}
            </span>
          ))}
        </div>

        {/* Content + Footer */}
        <div className="flex-1 flex flex-col ob-content-wrap">
          <main className="flex-1 py-10 lg:py-14 px-6">
            <div className="w-full max-w-[600px] mx-auto">

              {/* Step label */}
              <div ref={stepLabelRef} className="flex items-center gap-2.5 mb-4">
                <span className="text-[10px] font-mono text-[var(--ink-3)] tracking-[0.1em]">
                  STEP {String(currentStep).padStart(2, "0")}
                </span>
                <span className="w-5 h-px bg-[var(--border-2)]" />
                <span className="text-[10px] font-mono text-[var(--ink-3)]">
                  {PHASES[currentPhaseIndex]?.label.toUpperCase()}
                </span>
              </div>

              {/* Title + description */}
              <h1 ref={titleRef} className="text-[28px] md:text-[34px] font-bold text-[var(--ink-1)] tracking-tight leading-tight mb-3">
                {stepTitle}
              </h1>
              <p ref={descRef} className="text-[15px] text-[var(--ink-2)] leading-relaxed mb-8">
                {stepDescription}
              </p>

              {/* Page content */}
              <div ref={contentRef} className="ob-content">
                {children}
              </div>

              {/* Navigation */}
              <div className="mt-10 flex items-center justify-between">
                <button
                  onClick={handleBack}
                  disabled={!showBack || currentStep === 1 || isAnimating}
                  className={`flex items-center gap-1.5 text-[13px] font-medium text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors ${!showBack || currentStep === 1 ? "opacity-0 pointer-events-none" : ""}`}
                >
                  <ArrowLeft size={15} /> Back
                </button>

                <div className="flex items-center gap-4">
                  <span className="hidden sm:block text-[11px] font-mono text-[var(--ink-3)]/60">
                    ↵ Enter
                  </span>
                  <button
                    onClick={handleNext}
                    disabled={!canGoNext || isNextLoading || isAnimating}
                    className={`group px-6 py-2.5 rounded-[var(--radius)] text-[14px] font-semibold transition-all duration-200 flex items-center gap-2 ${canGoNext && !isNextLoading
                        ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] hover:opacity-90 active:scale-[0.98]"
                        : "bg-[var(--border-1)] text-[var(--ink-3)] cursor-not-allowed"
                      }`}
                  >
                    {isNextLoading ? (
                      <><div className="w-4 h-4 border-2 border-[var(--ink-3)] border-t-[var(--rf-ivory)] rounded-full animate-spin" />Processing</>
                    ) : (
                      <>
                        {nextLabel}
                        {nextLabel === "Continue" && <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />}
                        {nextLabel === "Complete Setup" && <CheckCircle2 size={14} className="group-hover:scale-110 transition-transform" />}
                      </>
                    )}
                  </button>
                </div>
              </div>

            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
