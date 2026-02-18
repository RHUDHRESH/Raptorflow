"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface PageChannelPrioritiesProps {
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack?: () => void;
  totalPages?: number;
  currentPage?: number;
}

const CHANNELS = [
  { id: "linkedin", label: "LinkedIn", icon: "💼", description: "B2B professional network" },
  { id: "email", label: "Email", icon: "✉️", description: "Direct outreach & newsletters" },
  { id: "youtube", label: "YouTube", icon: "▶️", description: "Video content & tutorials" },
  { id: "twitter", label: "Twitter/X", icon: "🐦", description: "Social media & engagement" },
  { id: "content", label: "Content/SEO", icon: "📝", description: "Organic search content" },
  { id: "podcast", label: "Podcast", icon: "🎙️", description: "Audio content & interviews" },
  { id: "events", label: "Events", icon: "🎪", description: "Conferences & webinars" },
  { id: "paid-ads", label: "Paid Ads", icon: "📢", description: "PPC & paid acquisition" },
];

export function PageChannelPriorities({
  value,
  onChange,
  onNext,
  onBack,
  totalPages = 21,
  currentPage = 16,
}: PageChannelPrioritiesProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isExiting, setIsExiting] = useState(false);
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    const parsed = value
      .split(/[,;\n]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    setSelectedIds(parsed);
  }, [value]);

  const isValid = selectedIds.length >= 1;

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
        ".channel-card",
        { opacity: 0, y: 40, scale: 0.9 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.6,
          stagger: 0.05,
          ease: "power2.out",
        },
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

  const toggleChannel = (id: string) => {
    let newSelected: string[];
    if (selectedIds.includes(id)) {
      newSelected = selectedIds.filter((item) => item !== id);
    } else {
      newSelected = [...selectedIds, id];
    }
    setSelectedIds(newSelected);
    onChange(newSelected.join(", "));

    const card = document.querySelector(`[data-channel="${id}"]`);
    if (card) {
      gsap.to(card, {
        scale: 0.95,
        duration: 0.1,
        yoyo: true,
        repeat: 1,
      });
    }

    if (newSelected.length >= 1) {
      gsap.to(".btn", {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out",
      });
    } else {
      gsap.to(".btn", {
        opacity: 0.2,
        y: 10,
        duration: 0.4,
      });
    }
  };

  const onHover = (id: string) => {
    setHoveredId(id);
    const card = document.querySelector(`[data-channel="${id}"]`);
    if (card && !selectedIds.includes(id)) {
      gsap.to(card, {
        y: -4,
        boxShadow: "0 20px 60px rgba(42, 37, 41, 0.1)",
        duration: 0.3,
      });
    }
  };

  const onLeave = (id: string) => {
    setHoveredId(null);
    const card = document.querySelector(`[data-channel="${id}"]`);
    if (card && !selectedIds.includes(id)) {
      gsap.to(card, {
        y: 0,
        boxShadow: "0 4px 20px rgba(42, 37, 41, 0.04)",
        duration: 0.3,
      });
    }
  };

  const submit = () => {
    if (!isValid) return;

    setIsExiting(true);
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
        className="grain absolute inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundSize: "256px 256px",
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
              Which channels matter
            </span>
            <span className="hword block text-[clamp(36px,7vw,64px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em] mt-2">
              most<span className="text-[var(--ink-3)]">?</span>
            </span>
          </h1>

          <p className="text-center text-[var(--ink-3)] mb-8 max-w-md">
            Select all that apply to your marketing strategy
          </p>

          <div className="w-full max-w-4xl grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {CHANNELS.map((channel) => {
              const isSelected = selectedIds.includes(channel.id);
              const isHovered = hoveredId === channel.id;

              return (
                <button
                  key={channel.id}
                  data-channel={channel.id}
                  onClick={() => toggleChannel(channel.id)}
                  onMouseEnter={() => onHover(channel.id)}
                  onMouseLeave={() => onLeave(channel.id)}
                  className={`channel-card relative p-6 rounded-[20px] text-left transition-all duration-300 ${
                    isSelected
                      ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)]"
                      : "bg-[var(--bg-raised)] text-[var(--ink-1)] hover:bg-[var(--bg-surface)]"
                  }`}
                  style={{
                    boxShadow: isSelected
                      ? "0 20px 60px rgba(42, 37, 41, 0.2)"
                      : "0 4px 20px rgba(42, 37, 41, 0.04)",
                  }}
                >
                  {isSelected && (
                    <div className="absolute top-4 right-4 w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
                      <svg
                        className="w-3 h-3 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={3}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                  )}

                  <span className="text-3xl mb-3 block">{channel.icon}</span>
                  <span className="block font-semibold text-sm mb-1">
                    {channel.label}
                  </span>
                  <span
                    className={`block text-xs ${
                      isSelected
                        ? "text-[var(--rf-ivory)]/60"
                        : "text-[var(--ink-3)]"
                    }`}
                  >
                    {channel.description}
                  </span>
                </button>
              );
            })}
          </div>
        </main>

        <footer className="nav fixed bottom-0 left-0 right-0 border-t border-[var(--border-1)] bg-[var(--bg-surface)] z-30">
          <div className="max-w-4xl mx-auto px-12 md:px-24 py-6 flex items-center justify-between">
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
              style={{
                opacity: isValid ? 1 : 0.2,
                transform: isValid ? "translateY(0)" : "translateY(10px)",
              }}
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

      <div className="absolute top-8 left-8 w-20 h-20 pointer-events-none opacity-20">
        <div className="absolute top-0 left-0 w-px h-12 bg-gradient-to-b from-[var(--border-2)] to-transparent" />
        <div className="absolute top-0 left-0 h-px w-12 bg-gradient-to-r from-[var(--border-2)] to-transparent" />
      </div>
    </div>
  );
}
