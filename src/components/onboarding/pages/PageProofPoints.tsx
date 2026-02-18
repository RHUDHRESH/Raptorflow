"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface PageProofPointsProps {
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack?: () => void;
  totalPages?: number;
  currentPage?: number;
}

const EXAMPLES = [
  "99.9% uptime SLA",
  "500+ enterprise customers",
  "Featured in TechCrunch",
  "SOC 2 certified",
  "4.8/5 G2 rating",
  "$10M ARR",
];

export function PageProofPoints({
  value,
  onChange,
  onNext,
  onBack,
  totalPages = 21,
  currentPage = 19,
}: PageProofPointsProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [items, setItems] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState("");

  useEffect(() => {
    const parsed = value
      .split(/[,;\n]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    setItems(parsed);
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
        ".input-area",
        { opacity: 0, y: 80 },
        { opacity: 1, y: 0, duration: 1.2 },
        "-=0.6"
      );
      tl.fromTo(
        ".examples",
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
    gsap.to(".btn", { opacity: 1, y: 0, duration: 0.5 });
  }, []);

  const addItem = (text: string) => {
    const trimmed = text.trim();
    if (trimmed && !items.includes(trimmed)) {
      const newItems = [...items, trimmed];
      setItems(newItems);
      onChange(newItems.join(", "));
      setInputValue("");
    }
  };

  const removeItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
    onChange(newItems.join(", "));
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addItem(inputValue);
    }
    if (e.key === "Backspace" && !inputValue && items.length > 0) {
      removeItem(items.length - 1);
    }
  };

  const submit = () => {
    gsap.to(".page", {
      opacity: 0,
      x: -100,
      duration: 0.5,
      ease: "power3.in",
      onComplete: onNext,
    });
  };

  const pct = Math.round((currentPage / totalPages) * 100);

  return (
    <div
      ref={containerRef}
      className="min-h-screen w-full bg-[var(--bg-canvas)] relative overflow-hidden"
    >
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
          <h1 className="text-center mb-4">
            <span className="hword block text-[clamp(36px,7vw,64px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em]">
              Proof points
            </span>
          </h1>
          <p className="text-center text-[var(--ink-3)] mb-12 max-w-md">
            Optional — metrics, traction, testimonials that build credibility
          </p>
          <div className="w-full max-w-3xl relative">
            <div
              className="input-area bg-[var(--bg-raised)] rounded-[24px] p-6 min-h-[140px]"
              style={{ boxShadow: "0 10px 40px rgba(42, 37, 41, 0.04)" }}
            >
              <div className="flex flex-wrap gap-2 mb-3">
                {items.map((item, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-full text-sm"
                  >
                    {item}
                    <button
                      onClick={() => removeItem(i)}
                      className="hover:opacity-70"
                    >
                      <svg
                        className="w-3 h-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={3}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </span>
                ))}
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={onKeyDown}
                  placeholder={
                    items.length === 0 ? "Type and press Enter..." : "Add more..."
                  }
                  className="flex-1 min-w-[200px] bg-transparent outline-none text-lg text-[var(--ink-1)] placeholder:text-[var(--border-2)] py-2"
                />
              </div>
            </div>
            <div className="examples mt-6">
              <p className="text-sm text-[var(--ink-3)] mb-3">Examples:</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    onClick={() => addItem(ex)}
                    className="px-3 py-1.5 rounded-full bg-[var(--bg-surface)] border border-[var(--border-2)] text-xs text-[var(--ink-2)] hover:bg-[var(--border-1)] hover:text-[var(--ink-1)] transition-colors"
                  >
                    + {ex}
                  </button>
                ))}
              </div>
            </div>
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
              className="btn flex items-center gap-3 px-8 py-4 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[16px] font-semibold text-sm tracking-wide hover:bg-[#3a3338] transition-colors"
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
