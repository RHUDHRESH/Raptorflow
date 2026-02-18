"use client";

import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface PageCompanyWebsiteProps {
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack?: () => void;
  totalPages?: number;
  currentPage?: number;
}

export function PageCompanyWebsite({
  value,
  onChange,
  onNext,
  onBack,
  totalPages = 21,
  currentPage = 2,
}: PageCompanyWebsiteProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const inputWrapRef = useRef<HTMLDivElement>(null);
  const protocolRef = useRef<HTMLSpanElement>(null);
  
  const [isFocused, setIsFocused] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [isValid, setIsValid] = useState(false);
  const [isPotentiallyValid, setIsPotentiallyValid] = useState(false);
  const [showError, setShowError] = useState(false);
  const [isIdle, setIsIdle] = useState(true);
  const [isExiting, setIsExiting] = useState(false);
  const [typingSpeed, setTypingSpeed] = useState(0);
  const [focusedProtocol, setFocusedProtocol] = useState(false);
  
  const idleTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastTypeRef = useRef<number>(0);

  // URL validation
  useEffect(() => {
    const trimmed = value.trim();
    const count = trimmed.length;
    setCharCount(count);
    
    // Check for valid URL patterns
    const hasProtocol = /^https?:\/\//.test(trimmed);
    const hasDomain = /[a-zA-Z0-9][-\w]*\.[a-zA-Z]{2,}/.test(trimmed);
    const looksLikeUrl = hasProtocol || (trimmed.includes('.') && !trimmed.includes(' '));
    
    setIsPotentiallyValid(looksLikeUrl && count > 3);
    setIsValid((hasProtocol || hasDomain) && count > 3);
    
    if ((hasProtocol || hasDomain) && count > 3) {
      setShowError(false);
    }
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
    }, 2500);

    return () => {
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    };
  }, [value, isFocused, isExiting]);

  // Master entrance timeline - distinct from page 1
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        defaults: { ease: "power3.out" },
        delay: 0.1,
        onComplete: () => {
          setTimeout(() => inputRef.current?.focus(), 200);
        }
      });

      // Grain
      tl.fromTo(".grain",
        { opacity: 0 },
        { opacity: 0.03, duration: 2, ease: "none" }
      );

      // Compass - slight bounce settling
      tl.fromTo(".compass",
        { y: -80, opacity: 0 },
        { y: 0, opacity: 1, duration: 1.2 },
        "-=1.8"
      );

      // Step - slide from right this time (variation)
      tl.fromTo(".step",
        { opacity: 0, x: 30 },
        { opacity: 1, x: 0, duration: 0.9 },
        "-=0.8"
      );

      // Progress continues from page 1
      tl.fromTo(".progress",
        { scaleX: (currentPage - 1) / totalPages },
        { scaleX: currentPage / totalPages, duration: 2.5, ease: "power2.inOut" },
        "-=0.6"
      );

      // Question number
      tl.fromTo(".qnum",
        { opacity: 0, y: -20 },
        { opacity: 1, y: 0, duration: 0.8 },
        "-=2"
      );

      // Headline - different animation (slide from sides)
      tl.fromTo(".h-line-1",
        { opacity: 0, x: -80 },
        { opacity: 1, x: 0, duration: 1.2, ease: "power3.out" },
        "-=1.6"
      );
      
      tl.fromTo(".h-line-2",
        { opacity: 0, x: 80 },
        { opacity: 1, x: 0, duration: 1.2, ease: "power3.out" },
        "-=1"
      );

      // Input rises with rotation
      tl.fromTo(".input-wrap",
        { opacity: 0, y: 100, rotateX: 15 },
        { opacity: 1, y: 0, rotateX: 0, duration: 1.4, ease: "power3.out" },
        "-=0.8"
      );

      // Protocol badge drops in
      tl.fromTo(".protocol",
        { opacity: 0, y: -20, scale: 0.8 },
        { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(2)" },
        "-=0.8"
      );

      // Helper
      tl.fromTo(".helper",
        { opacity: 0 },
        { opacity: 1, duration: 0.8 },
        "-=0.6"
      );

      // Nav
      tl.fromTo(".nav",
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 1 },
        "-=0.6"
      );

      // Ambient
      gsap.to(".compass", {
        y: "-=8",
        duration: 8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      gsap.to(".grain", {
        x: "+=80",
        y: "+=80",
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
        y: -12,
        boxShadow: "0 60px 180px rgba(42, 37, 41, 0.14)",
        duration: 0.6,
        ease: "power2.out",
      });

      gsap.to(".glow", { opacity: 1, duration: 0.5 });
      gsap.to(".underline", { scaleX: 1, duration: 0.6, ease: "power2.out" });
      gsap.to(".dim", { opacity: 0.35, duration: 0.5 });
      
      // Protocol shifts to show focus
      gsap.to(".protocol", {
        x: -5,
        color: "var(--ink-1)",
        duration: 0.3,
      });

    } else {
      gsap.to(inputWrapRef.current, {
        y: 0,
        boxShadow: "0 12px 48px rgba(42, 37, 41, 0.04)",
        duration: 0.5,
        ease: "power2.out",
      });

      gsap.to(".glow", { opacity: 0, duration: 0.4 });
      gsap.to(".underline", { scaleX: value ? 1 : 0, duration: 0.5, ease: "power2.in" });
      gsap.to(".dim", { opacity: 0, duration: 0.4 });
      
      gsap.to(".protocol", {
        x: 0,
        color: "var(--ink-3)",
        duration: 0.3,
      });
    }
  }, [isFocused, value]);

  // Valid state
  useEffect(() => {
    if (isValid) {
      gsap.to(".valid-dot", { scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2)" });
      gsap.to(".btn", { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" });
      gsap.to(".count", { color: "#16a34a", duration: 0.4 });
      
      // Success pulse on input
      gsap.fromTo(".input-wrap",
        { boxShadow: "0 60px 180px rgba(42, 37, 41, 0.14), 0 0 0 2px rgba(34, 197, 94, 0.2)" },
        { boxShadow: "0 60px 180px rgba(42, 37, 41, 0.14)", duration: 0.8 }
      );
    } else {
      gsap.to(".valid-dot", { scale: 0, opacity: 0, duration: 0.3 });
      gsap.to(".btn", { opacity: 0.2, y: 10, duration: 0.4 });
      gsap.to(".count", { color: "var(--ink-3)", duration: 0.3 });
    }
  }, [isValid]);

  // Protocol suggestion animation
  useEffect(() => {
    if (value && !value.startsWith('http') && value.includes('.')) {
      gsap.to(".protocol-suggestion", {
        opacity: 1,
        y: 0,
        duration: 0.4,
        ease: "power2.out",
      });
    } else {
      gsap.to(".protocol-suggestion", {
        opacity: 0,
        y: 10,
        duration: 0.3,
      });
    }
  }, [value]);

  // Typing handler
  const onType = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    const now = Date.now();
    
    if (lastTypeRef.current) {
      setTypingSpeed(now - lastTypeRef.current);
    }
    lastTypeRef.current = now;
    
    // Auto-prepend https:// if user starts typing domain
    if (!v.startsWith('http') && v.includes('.') && v.length > 3 && !hasInteracted) {
      // Let them type, but show suggestion
    }
    
    onChange(v);
    setShowError(false);

    if (inputWrapRef.current) {
      gsap.fromTo(inputWrapRef.current,
        { scaleY: 0.985 },
        { scaleY: 1, duration: 0.15, ease: "power2.out" }
      );
    }

    gsap.fromTo(".count",
      { y: -8, scale: 1.2 },
      { y: 0, scale: 1, duration: 0.4, ease: "bounce.out" }
    );

    const intensity = typingSpeed < 100 ? 0.5 : 0.25;
    gsap.fromTo(".underline",
      { boxShadow: `0 0 ${30 * intensity}px rgba(42,37,41,${intensity})` },
      { boxShadow: "0 0 0 rgba(42,37,41,0)", duration: 0.5 }
    );
  };

  // Auto-format URL on blur
  const handleBlur = () => {
    setIsFocused(false);
    
    if (value && !value.startsWith('http') && value.includes('.')) {
      // Auto-prepend https://
      const formatted = `https://${value}`;
      onChange(formatted);
      
      // Visual feedback for auto-format
      gsap.fromTo(".input-wrap",
        { backgroundColor: "rgba(34, 197, 94, 0.05)" },
        { backgroundColor: "var(--bg-raised)", duration: 0.6 }
      );
    }
  };

  // Error shake
  const shake = useCallback(() => {
    if (!inputWrapRef.current) return;
    setShowError(true);

    const tl = gsap.timeline({ onComplete: () => {
      setTimeout(() => setShowError(false), 2000);
    }});

    tl.to(inputWrapRef.current, { x: 12, duration: 0.07, ease: "power2.in" })
      .to(inputWrapRef.current, { x: -24, duration: 0.1, yoyo: true, repeat: 3, ease: "power2.inOut" })
      .to(inputWrapRef.current, { x: 0, duration: 0.7, ease: "elastic.out(1, 0.3)" });

    gsap.fromTo(".underline",
      { backgroundColor: "#ef4444", boxShadow: "0 0 40px rgba(239,68,68,0.6)" },
      { backgroundColor: "var(--rf-charcoal)", boxShadow: "0 0 0 rgba(239,68,68,0)", duration: 1.2 }
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
      scale: 0.95,
      duration: 0.2,
      ease: "power2.in",
      onComplete: () => {
        gsap.to(".page", {
          opacity: 0,
          x: -100,
          duration: 0.5,
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
        { scale: 0.96 },
        { scale: 1, duration: 0.25, ease: "power2.out" }
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
        <header className="flex items-center justify-between px-12 md:px-24 py-10">
          <div className="compass">
            <CompassLogo size={40} variant="compact" className="text-[var(--rf-charcoal)]" animate />
          </div>
          
          <div className="step flex items-center gap-4">
            <span className="rf-mono text-[10px] uppercase tracking-[0.3em] text-[var(--ink-3)]">Step</span>
            <div className="flex items-baseline">
              <span className="rf-mono text-xl font-semibold text-[var(--ink-1)]">{String(currentPage).padStart(2, "0")}</span>
              <span className="text-[var(--ink-3)] mx-1.5">/</span>
              <span className="rf-mono text-sm text-[var(--ink-3)]">{String(totalPages).padStart(2, "0")}</span>
            </div>
          </div>

          <button className="text-[10px] font-medium uppercase tracking-[0.2em] text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors">
            Save & Exit
          </button>
        </header>

        <div className="px-12 md:px-24 mb-16">
          <div className="max-w-lg mx-auto">
            <div className="relative h-px bg-[var(--border-1)] overflow-hidden">
              <div className="progress absolute inset-y-0 left-0 bg-[var(--rf-charcoal)] origin-left" style={{ transform: "scaleX(0)" }} />
              <div className="absolute inset-y-0 w-24 bg-gradient-to-r from-transparent via-[var(--rf-charcoal)] to-transparent opacity-20"
                style={{ left: `${pct}%`, transform: "translateX(-100%)", animation: "shimmer 3s infinite" }}
              />
            </div>
            <div className="flex justify-between mt-3">
              <span className="rf-mono text-[9px] uppercase tracking-[0.2em] text-[var(--ink-3)]">Start</span>
              <span className="rf-mono text-[9px] uppercase tracking-[0.2em] text-[var(--ink-1)] font-medium">{pct}%</span>
            </div>
          </div>
        </div>

        <main className="flex-1 flex flex-col items-center px-12 md:px-24">
          <div className="qnum mb-10">
            <span className="rf-mono text-[10px] uppercase tracking-[0.5em] text-[var(--ink-3)]">
              Question {String(currentPage).padStart(2, "0")}
            </span>
          </div>

          <h1 className="text-center mb-20" style={{ perspective: "2000px" }}>
            <span className="h-line-1 block text-[clamp(40px,9vw,80px)] leading-[0.95] font-bold text-[var(--ink-1)] tracking-[-0.03em]">
              What&apos;s your company
            </span>
            <span className="h-line-2 block text-[clamp(40px,9vw,80px)] leading-[0.95] font-bold text-[var(--ink-1)] tracking-[-0.03em] mt-3">
              website
              <span className="text-[var(--ink-3)]">?</span>
            </span>
          </h1>

          <div className="w-full max-w-3xl relative">
            {/* Protocol suggestion popup */}
            <div 
              className="protocol-suggestion absolute -top-12 left-16 opacity-0 pointer-events-none"
              style={{ transform: "translateY(10px)" }}
            >
              <span className="text-xs text-[var(--ink-3)] bg-[var(--bg-surface)] px-3 py-1.5 rounded-full border border-[var(--border-1)]">
                We&apos;ll add https:// for you
              </span>
            </div>

            <div
              ref={inputWrapRef}
              className="input-wrap relative bg-[var(--bg-raised)] rounded-[28px] overflow-hidden"
              style={{ boxShadow: "0 10px 40px rgba(42, 37, 41, 0.04)" }}
            >
              <div className="glow absolute inset-0 opacity-0 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-b from-[rgba(42,37,41,0.06)] to-transparent" />
              </div>

              <div className="relative flex items-center px-10 py-8">
                {/* Protocol indicator */}
                <span 
                  ref={protocolRef}
                  className="protocol text-[var(--ink-3)] text-[clamp(20px,3vw,32px)] font-medium mr-2 select-none"
                >
                  {value.startsWith('http') ? '' : 'https://'}
                </span>

                <input
                  ref={inputRef}
                  type="text"
                  value={value}
                  onChange={onType}
                  onFocus={() => setIsFocused(true)}
                  onBlur={handleBlur}
                  onKeyDown={onKey}
                  placeholder="acme.com"
                  maxLength={100}
                  className="flex-1 bg-transparent text-[clamp(24px,4vw,48px)] font-semibold text-[var(--ink-1)] placeholder:text-[var(--border-2)] outline-none tracking-tight"
                  style={{ caretColor: "var(--rf-charcoal)" }}
                  autoComplete="url"
                  spellCheck={false}
                />

                <div className="flex items-center gap-5 ml-6">
                  <span className="rf-mono text-[11px] tabular-nums">
                    <span className="count text-[var(--ink-3)]">{charCount}</span>
                    <span className="text-[var(--border-2)] mx-1">/</span>
                    <span className="text-[var(--border-2)]">100</span>
                  </span>
                  <div className="valid-dot w-3 h-3 rounded-full bg-green-500" style={{ transform: "scale(0)", opacity: 0 }} />
                </div>
              </div>

              <div className="underline absolute bottom-0 left-10 right-10 h-[2px] bg-[var(--rf-charcoal)] origin-left" style={{ transform: "scaleX(0)" }} />
            </div>

            <p className="helper text-center mt-8 text-sm text-[var(--ink-3)] leading-relaxed max-w-md mx-auto">
              Optional — helps us understand your brand and verify your business. We&apos;ll automatically add https:// if needed.
            </p>

            {(showError || (hasInteracted && charCount > 0 && charCount < 4)) && (
              <div className="mt-5 flex items-center justify-center gap-2 text-xs text-amber-600">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>Please enter a valid URL (e.g., acme.com)</span>
              </div>
            )}
          </div>

          <div className="fixed bottom-28 left-1/2 -translate-x-1/2 flex items-center gap-10 text-[10px] text-[var(--ink-3)] uppercase tracking-wider">
            <div className="flex items-center gap-2">
              <kbd className="px-2.5 py-1.5 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-2)] font-mono text-[10px]">Enter</kbd>
              <span>Continue</span>
            </div>
            {value && (
              <div className="flex items-center gap-2">
                <kbd className="px-2.5 py-1.5 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-2)] font-mono text-[10px]">Esc</kbd>
                <span>Clear</span>
              </div>
            )}
          </div>
        </main>

        <footer className="nav fixed bottom-0 left-0 right-0 border-t border-[var(--border-1)] bg-[var(--bg-surface)] z-30">
          <div className="max-w-3xl mx-auto px-12 md:px-24 py-6 flex items-center justify-between">
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-sm font-medium text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>

            <button
              onClick={submit}
              disabled={!isValid}
              className="btn flex items-center gap-3 px-8 py-4 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[16px] font-semibold text-sm tracking-wide hover:bg-[#3a3338] transition-colors disabled:cursor-not-allowed"
              style={{ opacity: 0.2, transform: "translateY(10px)" }}
            >
              Continue
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </div>
        </footer>
      </div>

      <div className="absolute top-8 left-8 w-20 h-20 pointer-events-none opacity-20">
        <div className="absolute top-0 left-0 w-px h-12 bg-gradient-to-b from-[var(--border-2)] to-transparent" />
        <div className="absolute top-0 left-0 h-px w-12 bg-gradient-to-r from-[var(--border-2)] to-transparent" />
      </div>
      <div className="absolute bottom-24 right-8 w-20 h-20 pointer-events-none opacity-20">
        <div className="absolute bottom-0 right-0 w-px h-12 bg-gradient-to-t from-[var(--border-2)] to-transparent" />
        <div className="absolute bottom-0 right-0 h-px w-12 bg-gradient-to-l from-[var(--border-2)] to-transparent" />
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
      `}</style>
    </div>
  );
}
