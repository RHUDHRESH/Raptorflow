"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Search, Check, ChevronDown, X, Building } from "lucide-react";

interface PageIndustryProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const ALL_INDUSTRIES = [
  "SaaS / Software", "Fintech", "E-commerce / Retail", "Healthcare / MedTech",
  "Education / EdTech", "Agency / Consulting", "Marketing Technology",
  "Pharmaceutical", "Legal / LegalTech", "Real Estate / PropTech",
  "Logistics / Supply Chain", "Manufacturing", "Cybersecurity",
  "Artificial Intelligence / ML", "Deep Tech / Hardware", "Robotics / Automation",
  "CleanTech / Sustainability", "FoodTech / AgriTech", "Travel / Hospitality",
  "Media / Content", "Gaming / Entertainment", "Non-profit / Social Impact",
  "Government / Public Sector", "HR / Recruiting / HRTech",
  "Insurance / InsurTech", "Construction / PropTech", "Retail Analytics",
  "Telecommunications", "Automotive / Mobility", "Aerospace / Defence", "Other",
];

export function PageIndustry({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageIndustryProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const customRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState(value === "Other" ? "" : value);
  const [isOpen, setIsOpen] = useState(false);
  const [customValue, setCustomValue] = useState("");
  const [showCustom, setShowCustom] = useState(value === "Other");

  // Focus on mount
  useEffect(() => {
    const t = setTimeout(() => inputRef.current?.focus(), 400);
    return () => clearTimeout(t);
  }, []);

  // Focus custom input when Other is shown
  useEffect(() => {
    if (showCustom) setTimeout(() => customRef.current?.focus(), 100);
  }, [showCustom]);

  // Entrance animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".ob-content-item",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  // Filter list
  const filtered = query.trim()
    ? ALL_INDUSTRIES.filter(i => i.toLowerCase().includes(query.toLowerCase()))
    : ALL_INDUSTRIES;

  const handleSelect = useCallback((industry: string) => {
    if (industry === "Other") {
      onChange("Other");
      setShowCustom(true);
      setIsOpen(false);
      setQuery("Other");
    } else {
      onChange(industry);
      setQuery(industry);
      setShowCustom(false);
      setIsOpen(false);
      inputRef.current?.blur();
      // Selection made - user must click Continue or press Enter to advance
    }
  }, [onChange]);

  const handleClear = () => {
    onChange("");
    setQuery("");
    setShowCustom(false);
    setCustomValue("");
    setIsOpen(true);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomValue(e.target.value);
    onChange(e.target.value ? `Other: ${e.target.value}` : "Other");
  };

  // Keyboard navigation
  const [activeIdx, setActiveIdx] = useState(-1);
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") { 
      e.preventDefault(); 
      setActiveIdx(i => Math.min(i + 1, filtered.length - 1)); 
    }
    if (e.key === "ArrowUp") { 
      e.preventDefault(); 
      setActiveIdx(i => Math.max(i - 1, 0)); 
    }
    if (e.key === "Enter") {
      e.preventDefault();
      if (activeIdx >= 0 && filtered[activeIdx]) handleSelect(filtered[activeIdx]);
      else if (value) {
        gsap.to(wrapperRef.current, {
          scale: 0.98,
          duration: 0.1,
          yoyo: true,
          repeat: 1,
          onComplete: () => onNext()
        });
      }
    }
    if (e.key === "Escape") setIsOpen(false);
  };

  // Scroll active item into view
  useEffect(() => {
    if (activeIdx >= 0 && dropdownRef.current) {
      const el = dropdownRef.current.querySelector(`[data-idx="${activeIdx}"]`) as HTMLElement;
      el?.scrollIntoView({ block: "nearest" });
    }
  }, [activeIdx]);

  // Dropdown open animation
  useEffect(() => {
    if (dropdownRef.current) {
      if (isOpen) {
        gsap.fromTo(dropdownRef.current,
          { opacity: 0, y: -10, scaleY: 0.95 },
          { opacity: 1, y: 0, scaleY: 1, duration: 0.2, ease: "power2.out" }
        );
        // Animate items
        gsap.fromTo(".dropdown-item",
          { opacity: 0, x: -10 },
          { opacity: 1, x: 0, duration: 0.15, stagger: 0.02, delay: 0.1 }
        );
      }
    }
  }, [isOpen]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="What industry are you in?"
      stepDescription="Start typing — we'll find it."
      onBack={onBack}
      onNext={onNext}
      canGoNext={!!value && value !== "Other"}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-content-item ob-animate-in relative">
        {/* Search input */}
        <div className={`flex items-center gap-2.5 px-4 py-3.5 rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isOpen ? "border-[var(--rf-charcoal)] ring-2 ring-[var(--rf-charcoal)]/10" : "border-[var(--border-2)]"}`}>
          <Search size={16} className="text-[var(--ink-3)] flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => { setQuery(e.target.value); setIsOpen(true); setActiveIdx(-1); }}
            onFocus={() => setIsOpen(true)}
            onBlur={() => setTimeout(() => setIsOpen(false), 150)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. Pharmaceutical, SaaS, Legal..."
            className="flex-1 bg-transparent border-none outline-none text-[15px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/50"
          />
          {value && (
            <button onClick={handleClear} className="flex-shrink-0 text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors p-1 hover:bg-[var(--border-1)] rounded-full">
              <X size={14} />
            </button>
          )}
          {!value && <ChevronDown size={14} className={`flex-shrink-0 text-[var(--ink-3)] transition-transform ${isOpen ? "rotate-180" : ""}`} />}
        </div>

        {/* Selected badge */}
        {value && !isOpen && !showCustom && (
          <div className="mt-3 flex items-center gap-2">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] w-fit">
              <Building size={14} />
              <span className="text-[13px] font-medium">{value}</span>
              <Check size={12} className="opacity-60" />
            </div>
          </div>
        )}

        {/* Dropdown */}
        {isOpen && (
          <div
            ref={dropdownRef}
            className="absolute top-full mt-1 left-0 right-0 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-md)] overflow-auto shadow-xl z-20 origin-top"
            style={{ maxHeight: "280px" }}
          >
            {filtered.length === 0 ? (
              <div className="px-4 py-4 text-[13px] text-[var(--ink-3)]">
                No match — select "Other" to enter custom
              </div>
            ) : (
              filtered.map((industry, i) => (
                <button
                  key={industry}
                  data-idx={i}
                  onMouseDown={() => handleSelect(industry)}
                  onMouseEnter={() => setActiveIdx(i)}
                  className={`dropdown-item w-full text-left px-4 py-3 text-[13px] flex items-center justify-between transition-colors ${i === activeIdx ? "bg-[var(--bg-raised)] text-[var(--ink-1)]" : "text-[var(--ink-2)] hover:bg-[var(--bg-raised)]"
                    } ${industry === value ? "font-semibold" : ""}`}
                >
                  {industry}
                  {industry === value && <Check size={14} className="text-[var(--rf-charcoal)]" />}
                </button>
              ))
            )}
          </div>
        )}
      </div>

      {/* Custom input */}
      {showCustom && (
        <div className="ob-content-item ob-animate-in mt-4">
          <label className="text-[11px] font-mono text-[var(--ink-3)] mb-2 block tracking-wide">SPECIFY YOUR INDUSTRY</label>
          <input
            ref={customRef}
            type="text"
            value={customValue}
            onChange={handleCustomChange}
            onKeyDown={e => { if (e.key === "Enter" && customValue.trim()) onNext(); }}
            placeholder="e.g. Pharmaceutical Logistics, B2B Wholesale..."
            className="w-full px-4 py-3 rounded-[var(--radius-md)] border border-[var(--border-2)] bg-[var(--bg-surface)] text-[15px] text-[var(--ink-1)] outline-none focus:border-[var(--rf-charcoal)] focus:ring-2 focus:ring-[var(--rf-charcoal)]/10 transition-all"
          />
          {customValue.trim() && (
            <p className="mt-2 text-[12px] text-[var(--status-success)] font-medium flex items-center gap-1">
              <Check size={12} /> Got it — press Enter or Continue
            </p>
          )}
        </div>
      )}

      {/* Quick picks */}
      {!value && (
        <div className="ob-content-item ob-animate-in mt-6">
          <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3 tracking-wide">POPULAR</p>
          <div className="flex flex-wrap gap-2">
            {["SaaS / Software", "Fintech", "E-commerce / Retail", "Agency / Consulting"].map(industry => (
              <button
                key={industry}
                onClick={() => handleSelect(industry)}
                className="px-3 py-1.5 text-[12px] rounded-full border border-[var(--border-2)] text-[var(--ink-2)] hover:border-[var(--rf-charcoal)] hover:text-[var(--ink-1)] transition-all"
              >
                {industry}
              </button>
            ))}
          </div>
        </div>
      )}
    </OnboardingLayout>
  );
}
