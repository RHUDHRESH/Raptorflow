'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import gsap from 'gsap';

export function FoundationHero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const particlesRef = useRef<HTMLDivElement>(null);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    // Set initial states
    gsap.set(titleRef.current, { opacity: 0, y: 60 });
    gsap.set(subtitleRef.current, { opacity: 0, y: 40 });
    gsap.set(ctaRef.current, { opacity: 0, y: 30, scale: 0.95 });

    // Animate in sequence
    tl.to(titleRef.current, { opacity: 1, y: 0, duration: 1.2 }, 0.5)
      .to(subtitleRef.current, { opacity: 1, y: 0, duration: 0.8 }, 1.0)
      .to(ctaRef.current, { opacity: 1, y: 0, scale: 1, duration: 0.6 }, 1.3);

    return () => {
      tl.kill();
    };
  }, []);

  const handleCTAClick = () => {
    setIsExiting(true);
    const tl = gsap.timeline({ defaults: { ease: 'power3.inOut' } });

    tl.to([titleRef.current, subtitleRef.current], {
      opacity: 0,
      y: -30,
      duration: 0.5,
      stagger: 0.1,
    }).to(
      ctaRef.current,
      {
        opacity: 0,
        scale: 0.9,
        duration: 0.3,
      },
      '-=0.3'
    );
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full max-w-[800px] text-center"
    >
      {/* Ambient Particles */}
      <div
        ref={particlesRef}
        className="absolute inset-0 pointer-events-none overflow-hidden"
      >
        {Array.from({ length: 30 }).map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-gray-300/20"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              width: `${2 + Math.random() * 3}px`,
              height: `${2 + Math.random() * 3}px`,
              animation: `subtleFloat ${8 + Math.random() * 10}s ease-in-out infinite`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Logo Mark */}
        <div className="inline-flex items-center gap-3 mb-16 opacity-40">
          <div className="w-5 h-5 bg-gray-900 rounded-sm" />
          <span className="text-[10px] font-mono uppercase tracking-[0.3em] text-gray-600">
            RAPTORFLOW
          </span>
        </div>

        {/* Title */}
        <h1
          ref={titleRef}
          className="font-playfair text-[64px] leading-[1.05] text-gray-900 tracking-[-0.03em] mb-8"
        >
          Marketing. Finally
          <br />
          <span className="text-gray-500">under control.</span>
        </h1>

        {/* Subtitle */}
        <p
          ref={subtitleRef}
          className="text-[18px] text-gray-600 leading-relaxed mb-16 max-w-[440px] mx-auto"
        >
          The Founder Marketing Operating System. Convert messy business context
          into clear positioning, a 90-day marketing war plan, weekly execution
          moves, and tracked outcomes.
        </p>

        {/* CTA Buttons */}
        <div
          ref={ctaRef}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8"
        >
          <Link href="/foundation">
            <button
              onClick={handleCTAClick}
              disabled={isExiting}
              className="group inline-flex items-center gap-3 bg-gray-900 text-white px-12 py-5 rounded-2xl font-inter font-medium text-[16px] transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_60px_rgba(0,0,0,0.25)] disabled:opacity-50"
            >
              <span>Build Foundation</span>
              <svg
                className="w-5 h-5 transition-transform group-hover:translate-x-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </button>
          </Link>

          <Link href="/muse">
            <button className="group inline-flex items-center gap-3 bg-white text-gray-900 border border-gray-300 px-8 py-5 rounded-2xl font-inter font-medium text-[16px] transition-all duration-300 hover:border-gray-400 hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)]">
              <span>Try Muse</span>
              <svg
                className="w-5 h-5 transition-transform group-hover:translate-x-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </button>
          </Link>
        </div>

        {/* Keyboard Hint */}
        <p className="text-[12px] text-gray-400 font-mono">
          Press Enter to begin
        </p>
      </div>

      {/* Floating animation keyframes */}
      <style jsx>{`
        @keyframes subtleFloat {
          0%,
          100% {
            transform: translateY(0) translateX(0);
          }
          25% {
            transform: translateY(-15px) translateX(8px);
          }
          50% {
            transform: translateY(-8px) translateX(-4px);
          }
          75% {
            transform: translateY(-20px) translateX(4px);
          }
        }
      `}</style>
    </div>
  );
}
