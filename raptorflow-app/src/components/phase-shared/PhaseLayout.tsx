'use client';

import React, { useRef, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import gsap from 'gsap';

interface PhaseLayoutProps {
  phaseNumber: number;
  phaseTitle: string;
  stepTitle: string;
  stepSubtitle?: string;
  currentStep: number;
  totalSteps: number;
  children: React.ReactNode;
  onBack?: () => void;
  backPath?: string;
  sidebarContent?: React.ReactNode;
}

export function PhaseLayout({
  phaseNumber,
  phaseTitle,
  stepTitle,
  stepSubtitle,
  currentStep,
  totalSteps,
  children,
  onBack,
  backPath,
  sidebarContent,
}: PhaseLayoutProps) {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const leftPanelRef = useRef<HTMLDivElement>(null);
  const rightPanelRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [hasAnimated, setHasAnimated] = useState(false);

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else if (backPath) {
      router.push(backPath);
    }
  };

  // Entry animation
  useEffect(() => {
    if (!containerRef.current || hasAnimated) return;

    const tl = gsap.timeline({ onComplete: () => setHasAnimated(true) });

    gsap.set(leftPanelRef.current, { x: -60, opacity: 0 });
    gsap.set(rightPanelRef.current, { opacity: 0 });
    gsap.set(contentRef.current, { y: 30, opacity: 0 });

    tl.to(leftPanelRef.current, {
      x: 0,
      opacity: 1,
      duration: 0.6,
      ease: 'power3.out',
    })
      .to(
        rightPanelRef.current,
        { opacity: 1, duration: 0.5, ease: 'power2.out' },
        '-=0.3'
      )
      .to(
        contentRef.current,
        { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' },
        '-=0.3'
      );

    return () => {
      tl.kill();
    };
  }, [hasAnimated]);

  // Content transition on step change
  useEffect(() => {
    if (!hasAnimated || !contentRef.current) return;

    gsap.fromTo(
      contentRef.current,
      { opacity: 0, y: 15 },
      { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
    );
  }, [currentStep, hasAnimated]);

  const progress = (currentStep / totalSteps) * 100;

  return (
    <div ref={containerRef} className="flex h-screen overflow-hidden">
      {/* Left Dark Panel */}
      <div
        ref={leftPanelRef}
        className="w-[280px] flex-shrink-0 bg-[#0E1112] text-white flex flex-col"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6 border-b border-white/10">
          <div className="w-6 h-6 bg-white rounded flex-shrink-0" />
          <span className="text-xs font-mono uppercase tracking-[0.2em] text-white/60">
            RaptorFlow
          </span>
        </div>

        {/* Phase Info */}
        <div className="px-6 py-8">
          <span className="text-xs font-mono uppercase tracking-[0.2em] text-white/40 mb-4 block">
            Phase {phaseNumber}
          </span>
          <h2 className="font-serif text-2xl text-white tracking-tight mb-2">
            {phaseTitle}
          </h2>
          <p className="text-sm text-white/50 leading-relaxed">
            Step {currentStep} of {totalSteps}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="px-6 mb-8">
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-white/60 transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Optional Sidebar Content */}
        {sidebarContent && (
          <div className="flex-1 px-6 overflow-y-auto">{sidebarContent}</div>
        )}

        {/* Back Button */}
        <div className="mt-auto px-6 py-6 border-t border-white/10">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-white/50 hover:text-white transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
        </div>
      </div>

      {/* Right Light Panel */}
      <div ref={rightPanelRef} className="flex-1 bg-[#F3F4EE] overflow-y-auto">
        <div className="min-h-full flex flex-col">
          {/* Content Area */}
          <div
            ref={contentRef}
            className="flex-1 flex flex-col max-w-[720px] mx-auto w-full px-12 py-16"
          >
            {/* Step Header */}
            <div className="mb-12">
              <h1 className="font-serif text-4xl text-[#2D3538] tracking-tight leading-tight mb-3">
                {stepTitle}
              </h1>
              {stepSubtitle && (
                <p className="text-lg text-[#5B5F61] leading-relaxed max-w-xl">
                  {stepSubtitle}
                </p>
              )}
            </div>

            {/* Main Content */}
            <div className="flex-1">{children}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
