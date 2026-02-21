"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { useRouter } from "next/navigation";
import { CompassLogo } from "@/components/compass/CompassLogo";

export default function OnboardingSuccessPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        defaults: { ease: "power3.out" },
        delay: 0.2,
      });

      // Grain fade in
      tl.fromTo(".grain", { opacity: 0 }, { opacity: 0.03, duration: 2, ease: "none" });

      // Compass entrance with bounce
      tl.fromTo(
        ".compass",
        { y: -100, opacity: 0, scale: 0.5, rotation: -30 },
        { y: 0, opacity: 1, scale: 1, rotation: 0, duration: 1.5, ease: "back.out(1.7)" },
        "-=1.5"
      );

      // Success icon pop
      tl.fromTo(
        ".success-icon",
        { scale: 0, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.8, ease: "back.out(2)" },
        "-=0.8"
      );

      // Headline words stagger
      tl.fromTo(
        ".hword",
        { opacity: 0, y: 50 },
        { opacity: 1, y: 0, duration: 1, stagger: 0.15 },
        "-=0.5"
      );

      // Subtext fade
      tl.fromTo(".subtext", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8 }, "-=0.5");

      // Feature list stagger
      tl.fromTo(
        ".feature",
        { opacity: 0, x: -30 },
        { opacity: 1, x: 0, duration: 0.6, stagger: 0.1 },
        "-=0.4"
      );

      // CTA button
      tl.fromTo(".cta", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8 }, "-=0.3");

      // Ambient compass floating
      gsap.to(".compass", {
        y: "-=10",
        duration: 6,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      // Confetti effect
      const confettiColors = ["#2a2529", "#16a34a", "#3b82f6", "#f59e0b"];
      for (let i = 0; i < 30; i++) {
        const confetti = document.createElement("div");
        confetti.className = `confetti confetti-${i}`;
        confetti.style.backgroundColor = confettiColors[Math.floor(Math.random() * confettiColors.length)];
        containerRef.current?.appendChild(confetti);

        gsap.fromTo(
          confetti,
          {
            x: "50vw",
            y: "50vh",
            scale: 0,
            rotation: Math.random() * 360,
          },
          {
            x: `${Math.random() * 100}vw`,
            y: `${Math.random() * 100}vh`,
            scale: Math.random() * 0.5 + 0.5,
            rotation: Math.random() * 720 - 360,
            duration: Math.random() * 2 + 1,
            delay: Math.random() * 0.5,
            ease: "power2.out",
            onComplete: () => confetti.remove(),
          }
        );
      }
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const handleGoToDashboard = () => {
    gsap.to(".page", {
      opacity: 0,
      y: -50,
      duration: 0.5,
      ease: "power3.in",
      onComplete: () => router.push("/dashboard"),
    });
  };

  return (
    <div ref={containerRef} className="min-h-screen w-full bg-[var(--bg-canvas)] relative overflow-hidden">
      <style jsx>{`
        .confetti {
          position: fixed;
          width: 10px;
          height: 10px;
          border-radius: 2px;
          pointer-events: none;
          z-index: 5;
        }
      `}</style>

      <div
        className="grain absolute inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundSize: "256px 256px",
        }}
      />

      <div className="page relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-center px-12 py-10">
          <div className="compass">
            <CompassLogo size={48} variant="compact" className="text-[var(--rf-charcoal)]" animate />
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex flex-col items-center justify-center px-6 md:px-12 pb-32">
          {/* Success Icon */}
          <div className="success-icon mb-8">
            <div className="w-24 h-24 rounded-full bg-green-500 flex items-center justify-center shadow-lg">
              <svg
                className="w-12 h-12 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={3}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>

          {/* Headline */}
          <h1 className="text-center mb-6">
            <span className="hword block text-[clamp(40px,8vw,72px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em]">
              Welcome to
            </span>
            <span className="hword block text-[clamp(40px,8vw,72px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em] mt-2">
              RaptorFlow
            </span>
          </h1>

          {/* Subtext */}
          <p className="subtext text-center text-lg md:text-xl text-[var(--ink-2)] max-w-xl mb-12 leading-relaxed">
            Your marketing foundation is ready. We&apos;ve built your business context model
            and configured your AI agents.
          </p>

          {/* Features List */}
          <div className="flex flex-col gap-4 mb-12 w-full max-w-md">
            <div className="feature flex items-center gap-4 p-4 bg-[var(--bg-raised)] rounded-[16px] border border-[var(--border-1)]">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <span className="block font-medium text-[var(--ink-1)]">Business Context Model</span>
                <span className="text-sm text-[var(--ink-3)]">Your unique market position captured</span>
              </div>
            </div>

            <div className="feature flex items-center gap-4 p-4 bg-[var(--bg-raised)] rounded-[16px] border border-[var(--border-1)]">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <span className="block font-medium text-[var(--ink-1)]">AI Agents Activated</span>
                <span className="text-sm text-[var(--ink-3)]">Ready to execute campaigns</span>
              </div>
            </div>

            <div className="feature flex items-center gap-4 p-4 bg-[var(--bg-raised)] rounded-[16px] border border-[var(--border-1)]">
              <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <span className="block font-medium text-[var(--ink-1)]">Analytics Dashboard</span>
                <span className="text-sm text-[var(--ink-3)]">Track your marketing performance</span>
              </div>
            </div>
          </div>

          {/* CTA Button */}
          <button
            onClick={handleGoToDashboard}
            className="cta flex items-center gap-3 px-10 py-5 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[20px] font-semibold text-lg tracking-wide hover:bg-[#3a3338] transition-all hover:scale-105 hover:shadow-xl"
          >
            Go to Dashboard
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>

          <p className="mt-6 text-sm text-[var(--ink-3)]">
            You can update your preferences anytime in Settings
          </p>
        </main>
      </div>
    </div>
  );
}
