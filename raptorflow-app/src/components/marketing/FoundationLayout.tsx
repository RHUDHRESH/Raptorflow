'use client';

import { ReactNode, useEffect, useRef } from 'react';
import gsap from 'gsap';

interface FoundationLayoutProps {
  children: ReactNode;
}

export function FoundationLayout({ children }: FoundationLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const leftPanelRef = useRef<HTMLDivElement>(null);
  const rightPanelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    // Set initial states
    gsap.set(leftPanelRef.current, { x: -100, opacity: 0 });
    gsap.set(rightPanelRef.current, { x: 100, opacity: 0 });

    // Animate in
    tl.to(leftPanelRef.current, { x: 0, opacity: 1, duration: 1.2 }, 0).to(
      rightPanelRef.current,
      { x: 0, opacity: 1, duration: 1.2 },
      0.2
    );

    return () => {
      tl.kill();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-[#0E1112] flex overflow-hidden"
    >
      {/* Left Panel - Context/Navigation */}
      <div
        ref={leftPanelRef}
        className="w-[400px] bg-[#1A1D1E] flex flex-col p-12 relative z-10 flex-shrink-0"
      >
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-100 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/3" />
        </div>

        {/* Logo Area */}
        <div className="relative z-10 mb-16 flex items-center gap-3">
          <div className="w-6 h-6 bg-white rounded-sm flex-shrink-0" />
          <span className="text-white font-inter font-bold text-[16px] tracking-[-0.02em]">
            RAPTORFLOW
          </span>
        </div>

        {/* Section Info */}
        <div className="relative z-10 flex-1">
          <div className="mb-4">
            <span className="text-[11px] font-inter font-semibold text-white/50 uppercase tracking-[0.15em]">
              Chapter 1
            </span>
          </div>
          <h2 className="font-playfair text-[40px] font-normal text-white leading-[1.1] mb-4">
            Marketing Foundation
          </h2>
          <p className="font-inter text-[14px] text-white/70 leading-[1.6] max-w-[280px]">
            Transform business chaos into strategic clarity with precision
            positioning and systematic growth.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="relative z-10 mt-auto space-y-3">
          {['Foundation', 'Positioning', 'Execution', 'Analytics'].map(
            (step, index) => (
              <div key={step} className="flex items-center gap-3 opacity-40">
                <div className="w-[6px] h-[6px] bg-white rounded-full" />
                <span className="font-inter text-[12px] font-medium text-white">
                  {step}
                </span>
              </div>
            )
          )}
        </div>
      </div>

      {/* Right Panel - Content Canvas */}
      <div
        ref={rightPanelRef}
        className="flex-1 bg-[#F8F9F7] relative overflow-y-auto"
      >
        {/* Top Navigation */}
        <div className="absolute top-8 right-8 z-20">
          <button className="w-10 h-10 bg-white border border-gray-200 rounded-xl flex items-center justify-center text-gray-600 hover:border-gray-300 hover:text-gray-900 hover:transform hover:-translate-y-0.5 transition-all duration-200">
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content Area */}
        <div className="relative z-10 flex-1 flex items-center justify-center min-h-screen p-20">
          {children}
        </div>

        {/* Background Gradient */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-to-br from-white/10 to-transparent rounded-full blur-[120px]" />
        </div>
      </div>
    </div>
  );
}
