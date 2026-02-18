"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface PageKeyDifferentiatorProps {
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack?: () => void;
  totalPages?: number;
  currentPage?: number;
}

const MIN_CHARS = 20;
const MAX_CHARS = 500;

export function PageKeyDifferentiator({
  value,
  onChange,
  onNext,
  onBack,
  totalPages = 21,
  currentPage = 12,
}: PageKeyDifferentiatorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  const [isFocused, setIsFocused] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [isValid, setIsValid] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const count = value.length;
    setCharCount(count);
    setIsValid(count >= MIN_CHARS && count <= MAX_CHARS);
    setProgress(Math.min((count / MIN_CHARS) * 100, 100));
  }, [value]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        defaults: { ease: "power3.out" },
        delay: 0.1,
      });
      tl.fromTo(
        ".grain",
        { opacity: 0 },
        { opacity: 0.03, duration: 2, ease: "none" }
      );
      tl.fromTo(
        ".compass",
        { y: -60, opacity: 0 },
        { y: 0, opacity: 1, duration: 1 },
        "-=1.6"
      );
      tl.fromTo(
        ".step",
        { opacity: 0, x: 20 },
        { opacity: 1, x: 0, duration: 0.8 },
        "-=0.6"
      );
      tl.fromTo(
        ".progress",
        { scaleX: (currentPage - 1) / totalPages },
        {
          scaleX: currentPage / totalPages,
          duration: 2,
          ease: "power2.inOut",
        },
        "-=0.4"
      );
      tl.fromTo(
        ".qnum",
        { opacity: 0 },
        { opacity: 1, duration: 0.6 },
        "-=1.6"
      );
      tl.fromTo(
        ".hword",
        { opacity: 0, y: 50 },
        { opacity: 1, y: 0, duration: 1, stagger: 0.1 },
        "-=1.2"
      );
      tl.fromTo(
        ".textarea-wrap",
        { opacity: 0, y: 80 },
        { opacity: 1, y: 0, duration: 1.2 },
        "-=0.6"
      );
      tl.fromTo(
        ".helper",
        { opacity: 0 },
        { opacity: 1, duration: 0.8 },
        "-=0.6"
      );
      tl.fromTo(
        ".nav",
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.8 },
        "-=0.4"
      );
      gsap.to(".compass", {
        y: "-=6",
        duration: 8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
    }, containerRef);

    return () => ctx.revert();
  }, [currentPage, totalPages]);

  useEffect(() => {
    if (!wrapRef.current) return;

    if (isFocused) {
      gsap.to(wrapRef.current, {
        y: -8,
        boxShadow: "0 60px 160px rgba(42, 37, 41, 0.12)",
        duration: 0.5,
      });
      gsap.to(".dim", { opacity: 0.3, duration: 0.5 });
    } else {
      gsap.to(wrapRef.current, {
        y: 0,
        boxShadow: "0 10px 40px rgba(42, 37, 41, 0.04)",
        duration: 0.4,
      });
      gsap.to(".dim", { opacity: 0, duration: 0.4 });
    }
  }, [isFocused]);

  useEffect(() => {
    if (isValid) {
      gsap.to(".btn", { opacity: 1, y: 0, duration: 0.5 });
      gsap.to(".counter", { color: "#16a34a", duration: 0.3 });
    } else {
      gsap.to(".btn", { opacity: 0.2, y: 10, duration: 0.4 });
      gsap.to(".counter", {
        color: charCount > MAX_CHARS ? "#ef4444" : "var(--ink-3)",
        duration: 0.3,
      });
    }
  }, [isValid, charCount]);

  const onType = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const v = e.target.value;
    if (v.length <= MAX_CHARS) {
      onChange(v);

      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
        textareaRef.current.style.height =
          textareaRef.current.scrollHeight + "px";
      }

      gsap.fromTo(
        ".counter",
        { scale: 1.2 },
        { scale: 1, duration: 0.3 }
      );
    }
  };

  const shake = useCallback(() => {
    if (!wrapRef.current) return;

    gsap.to(wrapRef.current, { x: 10, duration: 0.08, yoyo: true, repeat: 5 });
    gsap.to(".underline", {
      backgroundColor: "#ef4444",
      duration: 0.3,
      yoyo: true,
      repeat: 1,
    });
  }, []);

  const submit = () => {
    if (!isValid) {
      shake();
      return;
    }
    gsap.to(".page", {
      opacity: 0,
      x: -100,
      duration: 0.5,
      ease: "power3.in",
      onComplete: onNext,
    });
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && e.metaKey) submit();
  };

  const pct = Math.round((currentPage / totalPages) * 100);

  return (
    <div
      ref={containerRef}
      className="min-h-screen w-full bg-[var(--bg-canvas)] relative overflow-hidden"
    >
      <div className="dim absolute inset-0 bg-[var(--rf-charcoal)] opacity-0 pointer-events-none z-10" />
      <div
        className="grain absolute inset-0 pointer-events-none z-0 opacity-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundSize: "256px",
        }}
      />

      <div className="page relative z-20 min-h-screen flex flex-col pb-32">
        <header className="flex items-center justify-between px-12 md:px-24 py-10">
          <div className="compass">
            <CompassLogo
              size={40}
              variant="compact"
              className="text-[var(--rf-charcoal)]"
              animate
            />
          </div>
          <div className="step flex items-center gap-4">
            <span className="rf-mono text-[10px] uppercase tracking-[0.3em] text-[var(--ink-3)]">
              Step
            </span>
            <div className="flex items-baseline">
              <span className="rf-mono text-xl font-semibold text-[var(--ink-1)]">
                {String(currentPage).padStart(2, "0")}
              </span>
              <span className="text-[var(--ink-3)] mx-1.5">/</span>
              <span className="rf-mono text-sm text-[var(--ink-3)]">
                {String(totalPages).padStart(2, "0")}
              </span>
            </div>
          </div>
          <button className="text-[10px] font-medium uppercase tracking-[0.2em] text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors">
            Save & Exit
          </button>
        </header>

        <div className="px-12 md:px-24 mb-12">
          <div className="max-w-lg mx-auto">
            <div className="relative h-px bg-[var(--border-1)] overflow-hidden">
              <div
                className="progress absolute inset-y-0 left-0 bg-[var(--rf-charcoal)] origin-left"
                style={{ transform: "scaleX(0)" }}
              />
            </div>
            <div className="flex justify-between mt-3">
              <span className="rf-mono text-[9px] uppercase tracking-[0.2em] text-[var(--ink-3)]">
                Start
              </span>
              <span className="rf-mono text-[9px] uppercase tracking-[0.2em] text-[var(--ink-1)] font-medium">
                {pct}%
              </span>
            </div>
          </div>
        </div>

        <main className="flex-1 flex flex-col items-center px-12 md:px-24">
          <div className="qnum mb-8">
            <span className="rf-mono text-[10px] uppercase tracking-[0.5em] text-[var(--ink-3)]">
              Question {String(currentPage).padStart(2, "0")}
            </span>
          </div>

          <h1 className="text-center mb-12">
            <span className="hword block text-[clamp(36px,7vw,64px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em]">
              What makes you
            </span>
            <span className="hword block text-[clamp(36px,7vw,64px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em] mt-2">
              different<span className="text-[var(--ink-3)]">?</span>
            </span>
          </h1>

          <div className="w-full max-w-3xl relative">
            <div
              ref={wrapRef}
              className="textarea-wrap relative bg-[var(--bg-raised)] rounded-[24px] overflow-hidden"
              style={{ boxShadow: "0 10px 40px rgba(42, 37, 41, 0.04)" }}
            >
              <textarea
                ref={textareaRef}
                value={value}
                onChange={onType}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                onKeyDown={onKey}
                placeholder="Describe your unique advantages, proprietary technology, or what sets you apart from competitors. Why should customers choose you?"
                rows={5}
                className="w-full bg-transparent text-xl text-[var(--ink-1)] placeholder:text-[var(--border-2)] outline-none p-10 resize-none leading-relaxed"
                style={{ caretColor: "var(--rf-charcoal)", minHeight: "200px" }}
              />

              <div className="absolute bottom-0 left-0 right-0 h-1 bg-[var(--border-1)]">
                <div
                  className="h-full bg-[var(--rf-charcoal)] transition-all duration-300"
                  style={{
                    width: `${progress}%`,
                    backgroundColor: isValid ? "#16a34a" : undefined,
                  }}
                />
              </div>
            </div>

            <div className="flex items-center justify-between mt-6">
              <p className="helper text-sm text-[var(--ink-3)]">
                Minimum {MIN_CHARS} characters for best results
              </p>
              <span className="counter rf-mono text-sm text-[var(--ink-3)]">
                {charCount} / {MAX_CHARS}
              </span>
            </div>

            {charCount > 0 && charCount < MIN_CHARS && (
              <p className="mt-4 text-xs text-amber-600">
                {MIN_CHARS - charCount} more characters needed
              </p>
            )}
            {charCount > MAX_CHARS && (
              <p className="mt-4 text-xs text-red-600">
                Maximum {MAX_CHARS} characters exceeded
              </p>
            )}
          </div>
        </main>

        <footer className="nav fixed bottom-0 left-0 right-0 border-t border-[var(--border-1)] bg-[var(--bg-surface)] z-30">
          <div className="max-w-3xl mx-auto px-12 md:px-24 py-6 flex items-center justify-between">
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-sm font-medium text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
            >
              <svg
                className="w-4 h-4"
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
              onClick={submit}
              disabled={!isValid}
              className="btn flex items-center gap-3 px-8 py-4 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[16px] font-semibold text-sm tracking-wide hover:bg-[#3a3338] transition-colors disabled:cursor-not-allowed"
              style={{ opacity: 0.2, transform: "translateY(10px)" }}
            >
              Continue
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
