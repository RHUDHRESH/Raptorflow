'use client';

import React, { useEffect, useRef, useState } from 'react';
import { ArrowRight } from 'lucide-react';
import gsap from 'gsap';
import Image from 'next/image';

interface WelcomeScreenProps {
  onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLButtonElement>(null);
  const particlesRef = useRef<HTMLDivElement>(null);
  const [isExiting, setIsExiting] = useState(false);

  // Cinematic entrance animation
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

  // Exit animation
  const handleStart = () => {
    if (isExiting) return;
    setIsExiting(true);

    const tl = gsap.timeline({
      defaults: { ease: 'power3.inOut' },
      onComplete: onStart,
    });

    // Fade everything out dramatically
    tl.to([titleRef.current, subtitleRef.current], {
      opacity: 0,
      y: -30,
      duration: 0.5,
      stagger: 0.1,
    })
      .to(
        ctaRef.current,
        {
          opacity: 0,
          scale: 0.9,
          duration: 0.3,
        },
        '-=0.3'
      )
      .to(
        containerRef.current,
        {
          opacity: 0,
          duration: 0.4,
        },
        '-=0.2'
      );
  };

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 bg-[#0E1112] z-50 flex flex-col items-center justify-center overflow-hidden"
    >
      {/* Ambient particles */}
      <div ref={particlesRef} className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 40 }).map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white/5"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              width: `${2 + Math.random() * 4}px`,
              height: `${2 + Math.random() * 4}px`,
              animation: `subtleFloat ${8 + Math.random() * 12}s ease-in-out infinite`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
      </div>

      {/* Gradient glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[600px] h-[600px] bg-white/[0.02] rounded-full blur-[100px]" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-[600px] text-center px-8">
        {/* Logo mark */}
        <div className="inline-flex items-center gap-3 mb-16 opacity-40">
          <div className="relative w-8 h-8 rounded-sm overflow-hidden">
            <Image
              src="/logo_primary.png"
              alt="RaptorFlow"
              fill
              className="object-contain"
            />
          </div>
        </div>

        {/* Title - Revealed word by word */}
        <h1
          ref={titleRef}
          className="font-serif text-[64px] leading-[1.05] text-white tracking-[-0.03em] mb-8"
        >
          Build Your
          <br />
          <span className="text-white/60">Marketing Foundation</span>
        </h1>

        {/* Subtitle */}
        <p
          ref={subtitleRef}
          className="text-[18px] text-white/50 leading-relaxed mb-16 max-w-[440px] mx-auto"
        >
          10 minutes of focused input will power months of strategic clarity.
        </p>

        {/* CTA */}
        <button
          ref={ctaRef}
          onClick={handleStart}
          disabled={isExiting}
          className="group inline-flex items-center gap-4 bg-white text-[#0E1112] px-12 py-5 rounded-2xl font-medium text-[16px] transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_60px_rgba(255,255,255,0.15)] disabled:opacity-50"
        >
          <span>Begin the Process</span>
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
        </button>

        {/* Keyboard hint */}
        <p className="mt-8 text-[12px] text-white/20 font-mono">
          Press Enter to start
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
            transform: translateY(-20px) translateX(10px);
          }
          50% {
            transform: translateY(-10px) translateX(-5px);
          }
          75% {
            transform: translateY(-25px) translateX(5px);
          }
        }
      `}</style>
    </div>
  );
}
