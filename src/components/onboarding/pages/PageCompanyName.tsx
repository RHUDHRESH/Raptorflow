"use client";

import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface PageCompanyNameProps {
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack?: () => void;
  totalPages?: number;
  currentPage?: number;
}

export function PageCompanyName({
  value,
  onChange,
  onNext,
  onBack,
  totalPages = 21,
  currentPage = 1,
}: PageCompanyNameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const inputWrapRef = useRef<HTMLDivElement>(null);
  const prevValueRef = useRef(value);
  
  // State
  const [isFocused, setIsFocused] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [isValid, setIsValid] = useState(false);
  const [showError, setShowError] = useState(false);
  const [placeholderIdx, setPlaceholderIdx] = useState(0);
  const [isIdle, setIsIdle] = useState(true);
  const [isExiting, setIsExiting] = useState(false);
  const [typingSpeed, setTypingSpeed] = useState(0);
  
  const placeholders = useMemo(() => ["Acme Inc", "Stripe", "Linear", "Notion", "Vercel", "Figma", "Slack", "Shopify"], []);
  
  const idleTimerRef = useRef<NodeJS.Timeout | null>(null);
  const placeholderTimerRef = useRef<NodeJS.Timeout | null>(null);
  const typeTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastTypeRef = useRef<number>(0);

  // Validation
  useEffect(() => {
    const trimmed = value.trim();
    const count = trimmed.length;
    setCharCount(count);
    const valid = count >= 2;
    setIsValid(valid);
    if (valid) setShowError(false);
  }, [value]);

  // Idle detection
  useEffect(() => {
    if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    
    if (value || isFocused || isExiting) {
      setIsIdle(false);
      return;
    }

    idleTimerRef.current = setTimeout(() => {
      setIsIdle(true);
    }, 2000);

    return () => {
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    };
  }, [value, isFocused, isExiting]);

  // Placeholder cycling
  useEffect(() => {
    if (!isIdle || value || isFocused) {
      if (placeholderTimerRef.current) clearInterval(placeholderTimerRef.current);
      return;
    }

    placeholderTimerRef.current = setInterval(() => {
      setPlaceholderIdx(p => (p + 1) % placeholders.length);
      gsap.fromTo(".ghost",
        { opacity: 0, y: 15, filter: "blur(6px)" },
        { opacity: 0.25, y: 0, filter: "blur(0px)", duration: 0.6, ease: "power2.out" }
      );
    }, 3000);

    return () => {
      if (placeholderTimerRef.current) clearInterval(placeholderTimerRef.current);
    };
  }, [isIdle, value, isFocused, placeholders.length]);

  // Master entrance timeline
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        defaults: { ease: "power3.out" },
        delay: 0.1,
        onComplete: () => {
          setTimeout(() => inputRef.current?.focus(), 300);
        }
      });

      // Grain
      tl.fromTo(".grain",
        { opacity: 0 },
        { opacity: 0.03, duration: 2.5, ease: "none" }
      );

      // Compass
      tl.fromTo(".compass",
        { y: -160, opacity: 0, rotation: -40, scale: 0.7 },
        { y: 0, opacity: 1, rotation: 0, scale: 1, duration: 2.2, ease: "back.out(1.02)" },
        "-=2"
      );

      // Step
      tl.fromTo(".step",
        { opacity: 0, x: -50 },
        { opacity: 1, x: 0, duration: 1.2 },
        "-=1.6"
      );

      // Progress
      tl.fromTo(".progress",
        { scaleX: 0 },
        { scaleX: currentPage / totalPages, duration: 3, ease: "power2.inOut" },
        "-=1"
      );

      // Question num
      tl.fromTo(".qnum",
        { opacity: 0, letterSpacing: "1.2em" },
        { opacity: 1, letterSpacing: "0.5em", duration: 2 },
        "-=2.2"
      );

      // Headline words
      tl.fromTo(".hword",
        { opacity: 0, y: 100, rotateX: -60 },
        { opacity: 1, y: 0, rotateX: 0, duration: 1.6, stagger: 0.25, ease: "power3.out" },
        "-=1.6"
      );

      // Input
      tl.fromTo(".inputwrap",
        { opacity: 0, y: 140, scale: 0.85 },
        { opacity: 1, y: 0, scale: 1, duration: 1.8, ease: "power3.out" },
        "-=1.2"
      );

      // Helper
      tl.fromTo(".helper",
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 1.2 },
        "-=1"
      );

      // Nav
      tl.fromTo(".nav",
        { opacity: 0, y: 80 },
        { opacity: 1, y: 0, duration: 1.4 },
        "-=1"
      );

      // Ambient
      gsap.to(".compass", {
        y: "-=12",
        duration: 10,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 3,
      });

      gsap.to(".grain", {
        x: "+=100",
        y: "+=100",
        duration: 50,
        repeat: -1,
        ease: "none",
      });

    }, containerRef);

    return () => ctx.revert();
  }, [currentPage, totalPages]);

  // Focus effects
  useEffect(() => {
    if (!inputWrapRef.current) return;

    if (isFocused) {
      setHasInteracted(true);
      
      gsap.to(inputWrapRef.current, {
        y: -16,
        boxShadow: "0 100px 280px rgba(42, 37, 41, 0.18)",
        duration: 0.8,
        ease: "power2.out",
      });

      gsap.to(".glow", { opacity: 1, duration: 0.7 });
      gsap.to(".line", { scaleX: 1, duration: 0.8, ease: "power2.out" });
      gsap.to(".dim", { opacity: 0.4, duration: 0.7 });
      gsap.to(".compass", { scale: 1.15, duration: 0.6, ease: "power2.out" });

    } else {
      gsap.to(inputWrapRef.current, {
        y: 0,
        boxShadow: "0 14px 56px rgba(42, 37, 41, 0.06)",
        duration: 0.7,
        ease: "power2.out",
      });

      gsap.to(".glow", { opacity: 0, duration: 0.5 });
      gsap.to(".line", { scaleX: value ? 1 : 0, duration: 0.6, ease: "power2.in" });
      gsap.to(".dim", { opacity: 0, duration: 0.5 });
      gsap.to(".compass", { scale: 1, duration: 0.6, ease: "power2.out" });
    }
  }, [isFocused, value]);

  // Valid state
  useEffect(() => {
    if (isValid) {
      gsap.to(".dot", { scale: 1, opacity: 1, duration: 0.7, ease: "back.out(3)" });
      gsap.to(".btn", { opacity: 1, y: 0, duration: 1, ease: "power3.out" });
      gsap.to(".count", { color: "#16a34a", scale: 1.15, duration: 0.5, ease: "back.out(2)" });
    } else {
      gsap.to(".dot", { scale: 0, opacity: 0, duration: 0.4 });
      gsap.to(".btn", { opacity: 0.15, y: 15, duration: 0.6 });
      gsap.to(".count", { color: "var(--ink-3)", scale: 1, duration: 0.4 });
    }
  }, [isValid]);

  // Typing handler
  const onType = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    const now = Date.now();
    
    // Calculate typing speed
    if (lastTypeRef.current) {
      const delta = now - lastTypeRef.current;
      setTypingSpeed(delta);
    }
    lastTypeRef.current = now;
    
    onChange(v);
    setShowError(false);

    // Squash animation
    if (inputWrapRef.current) {
      gsap.fromTo(inputWrapRef.current,
        { scaleY: 0.98 },
        { scaleY: 1, duration: 0.2, ease: "power2.out" }
      );
    }

    // Counter bounce
    gsap.fromTo(".count",
      { y: -12, scale: 1.4 },
      { y: 0, scale: 1, duration: 0.6, ease: "bounce.out" }
    );

    // Line pulse based on speed
    const intensity = typingSpeed < 100 ? 0.6 : 0.3;
    gsap.fromTo(".line",
      { boxShadow: `0 0 ${40 * intensity}px rgba(42,37,41,${intensity})` },
      { boxShadow: "0 0 0 rgba(42,37,41,0)", duration: 0.6 }
    );

    prevValueRef.current = v;
  };

  // Error shake
  const shake = useCallback(() => {
    if (!inputWrapRef.current) return;
    setShowError(true);

    const tl = gsap.timeline({ onComplete: () => {
      setTimeout(() => setShowError(false), 2500);
    }});

    tl.to(inputWrapRef.current, { x: 18, duration: 0.08, ease: "power2.in" })
      .to(inputWrapRef.current, { x: -36, duration: 0.12, yoyo: true, repeat: 3, ease: "power2.inOut" })
      .to(inputWrapRef.current, { x: 0, duration: 1, ease: "elastic.out(1, 0.2)" });

    gsap.fromTo(".line",
      { backgroundColor: "#ef4444", boxShadow: "0 0 50px rgba(239,68,68,0.8)" },
      { backgroundColor: "var(--rf-charcoal)", boxShadow: "0 0 0 rgba(239,68,68,0)", duration: 1.5 }
    );
  }, []);

  // Submit
  const submit = () => {
    if (!isValid) {
      shake();
      inputRef.current?.focus();
      return;
    }

    setIsExiting(true);

    gsap.to(inputWrapRef.current, {
      scale: 0.92,
      duration: 0.25,
      ease: "power2.in",
      onComplete: () => {
        gsap.to(".page", {
          opacity: 0,
          x: -150,
          filter: "blur(12px)",
          duration: 0.8,
          ease: "power3.in",
          onComplete: onNext,
        });
      },
    });
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      submit();
    } else if (e.key === "Escape" && value) {
      onChange("");
      gsap.fromTo(inputWrapRef.current,
        { scale: 0.93 },
        { scale: 1, duration: 0.35, ease: "power2.out" }
      );
    }
  };

  const pct = Math.round((currentPage / totalPages) * 100);

  return (
    <div ref={containerRef} className="min-h-screen w-full bg-[var(--bg-canvas)] relative overflow-hidden">
      <div className="dim absolute inset-0 bg-[var(--rf-charcoal)] opacity-0 pointer-events-none z-10" />

      <div
        className="grain absolute inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundSize: "256px 256px",
        }}
      />

      <div className="page relative z-20 min-h-screen flex flex-col">
        <header className="flex items-center justify-between px-20 md:px-40 py-16">
          <div className="compass">
            <CompassLogo size={56} variant="compact" className="text-[var(--rf-charcoal)]" animate />
          </div>
          
          <div className="step flex items-center gap-6">
            <span className="rf-mono text-[12px] uppercase tracking-[0.4em] text-[var(--ink-3)]">Step</span>
            <div className="flex items-baseline">
              <span className="rf-mono text-3xl font-semibold text-[var(--ink-1)]">{String(currentPage).padStart(2, "0")}</span>
              <span className="text-[var(--ink-3)] mx-3">/</span>
              <span className="rf-mono text-base text-[var(--ink-3)]">{String(totalPages).padStart(2, "0")}</span>
            </div>
          </div>

          <button className="text-[12px] font-medium uppercase tracking-[0.3em] text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors">
            Save & Exit
          </button>
        </header>

        <div className="px-20 md:px-40 mb-36">
          <div className="max-w-2xl mx-auto">
            <div className="relative h-px bg-[var(--border-1)] overflow-hidden">
              <div className="progress absolute inset-y-0 left-0 bg-[var(--rf-charcoal)] origin-left" style={{ transform: "scaleX(0)" }} />
              <div className="absolute inset-y-0 w-40 bg-gradient-to-r from-transparent via-[var(--rf-charcoal)] to-transparent opacity-40"
                style={{ left: `${pct}%`, transform: "translateX(-100%)", animation: "shimmer 5s infinite" }}
              />
            </div>
            <div className="flex justify-between mt-6">
              <span className="rf-mono text-[10px] uppercase tracking-[0.35em] text-[var(--ink-3)]">Start</span>
              <span className="rf-mono text-[10px] uppercase tracking-[0.35em] text-[var(--ink-1)] font-medium">{pct}%</span>
            </div>
          </div>
        </div>

        <main className="flex-1 flex flex-col items-center px-20 md:px-40">
          <div className="qnum mb-20">
            <span className="rf-mono text-[12px] uppercase tracking-[0.7em] text-[var(--ink-3)]">
              Question {String(currentPage).padStart(2, "0")}
            </span>
          </div>

          <h1 className="text-center mb-40" style={{ perspective: "3000px" }}>
            <span className="hword block text-[clamp(60px,12vw,120px)] leading-[0.85] font-bold text-[var(--ink-1)] tracking-[-0.045em]">
              What is your
            </span>
            <span className="hword block text-[clamp(60px,12vw,120px)] leading-[0.85] font-bold text-[var(--ink-1)] tracking-[-0.045em] mt-6">
              company name
              <span className="text-[var(--border-2)]">?</span>
            </span>
          </h1>

          <div className="w-full max-w-4xl relative">
            <div
              ref={inputWrapRef}
              className="inputwrap relative bg-[var(--bg-raised)] rounded-[48px] overflow-hidden"
              style={{ boxShadow: "0 14px 56px rgba(42, 37, 41, 0.06)" }}
            >
              <div className="glow absolute inset-0 opacity-0 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-b from-[rgba(42,37,41,0.1)] to-transparent" />
              </div>

              <div className="relative flex items-center px-16 py-14">
                <input
                  ref={inputRef}
                  type="text"
                  value={value}
                  onChange={onType}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  onKeyDown={onKey}
                  placeholder={isIdle && !value ? placeholders[placeholderIdx] : "Acme Inc"}
                  maxLength={50}
                  className="flex-1 bg-transparent text-[clamp(48px,9vw,88px)] font-semibold text-[var(--ink-1)] placeholder:text-[var(--border-2)] outline-none tracking-tight"
                  style={{ caretColor: "var(--rf-charcoal)" }}
                  autoComplete="organization"
                  spellCheck={false}
                />

                {isIdle && !value && !isFocused && (
                  <span className="ghost absolute left-16 text-[clamp(48px,9vw,88px)] font-semibold text-[var(--border-2)] pointer-events-none opacity-0">
                    {placeholders[placeholderIdx]}
                  </span>
                )}

                <div className="flex items-center gap-10 ml-14">
                  <span className="rf-mono text-[14px] tabular-nums">
                    <span className="count text-[var(--ink-3)] inline-block">{charCount}</span>
                    <span className="text-[var(--border-2)] mx-3">/</span>
                    <span className="text-[var(--border-2)]">50</span>
                  </span>
                  <div className="dot w-5 h-5 rounded-full bg-green-500" style={{ transform: "scale(0)", opacity: 0 }} />
                </div>
              </div>

              <div className="line absolute bottom-0 left-16 right-16 h-[3px] bg-[var(--rf-charcoal)] origin-left" style={{ transform: "scaleX(0)" }} />
            </div>

            <p className="helper text-center mt-16 text-base text-[var(--ink-3)] leading-relaxed max-w-xl mx-auto">
              This is how we&apos;ll refer to your business throughout the platform.
            </p>

            {(showError || (hasInteracted && charCount > 0 && charCount < 2)) && (
              <div className="mt-8 flex items-center justify-center gap-4 text-base text-amber-600">
                <svg className="w-6 h-6 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>Please enter at least 2 characters</span>
              </div>
            )}
          </div>

          <div className="fixed bottom-48 left-1/2 -translate-x-1/2 flex items-center gap-16 text-[12px] text-[var(--ink-3)] uppercase tracking-widest">
            <div className="flex items-center gap-4">
              <kbd className="px-4 py-2.5 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-2)] font-mono text-[12px] shadow-md">Enter</kbd>
              <span>Continue</span>
            </div>
            {value && (
              <div className="flex items-center gap-4">
                <kbd className="px-4 py-2.5 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-2)] font-mono text-[12px] shadow-md">Esc</kbd>
                <span>Clear</span>
              </div>
            )}
          </div>
        </main>

        <footer className="nav fixed bottom-0 left-0 right-0 border-t border-[var(--border-1)] bg-[var(--bg-surface)] z-30">
          <div className="max-w-4xl mx-auto px-20 md:px-40 py-12 flex items-center justify-between">
            <button
              onClick={onBack}
              className={`flex items-center gap-4 text-base font-medium transition-colors ${
                onBack ? "text-[var(--ink-2)] hover:text-[var(--ink-1)]" : "opacity-0 pointer-events-none"
              }`}
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>

            <button
              onClick={submit}
              disabled={!isValid}
              className="btn flex items-center gap-5 px-16 py-8 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[32px] font-semibold text-base tracking-wide hover:bg-[#454045] transition-colors disabled:cursor-not-allowed"
              style={{ opacity: 0.15, transform: "translateY(15px)" }}
            >
              Continue
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </div>
        </footer>
      </div>

      <div className="absolute top-16 left-16 w-32 h-32 pointer-events-none opacity-12">
        <div className="absolute top-0 left-0 w-px h-24 bg-gradient-to-b from-[var(--border-2)] to-transparent" />
        <div className="absolute top-0 left-0 h-px w-24 bg-gradient-to-r from-[var(--border-2)] to-transparent" />
      </div>
      <div className="absolute bottom-48 right-16 w-32 h-32 pointer-events-none opacity-12">
        <div className="absolute bottom-0 right-0 w-px h-24 bg-gradient-to-t from-[var(--border-2)] to-transparent" />
        <div className="absolute bottom-0 right-0 h-px w-24 bg-gradient-to-l from-[var(--border-2)] to-transparent" />
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(500%); }
        }
      `}</style>
    </div>
  );
}
