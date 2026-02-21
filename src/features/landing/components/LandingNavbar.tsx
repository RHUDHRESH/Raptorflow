"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Menu, X } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const NAV_LINKS = [
  { label: "Platform", href: "#modules" },
  { label: "How It Works", href: "#control" },
  { label: "Pricing", href: "#pricing" },
  { label: "For Who", href: "#personas" },
];

export function LandingNavbar() {
  const navRef = useRef<HTMLElement>(null);
  const pillRef = useRef<HTMLDivElement>(null);
  const linkRefs = useRef<(HTMLAnchorElement | null)[]>([]);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isReducedMotion, activeSection } = useLandingStore();

  useEffect(() => {
    if (!navRef.current) return;

    const ctx = gsap.context(() => {
      if (!isReducedMotion) {
        gsap.from(navRef.current, {
          y: -80,
          opacity: 0,
          duration: 0.9,
          delay: 0.2,
          ease: "power3.out",
        });
      }

      ScrollTrigger.create({
        trigger: document.body,
        start: "top -60",
        onEnter: () => setIsScrolled(true),
        onLeaveBack: () => setIsScrolled(false),
      });
    }, navRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  useEffect(() => {
    if (isReducedMotion || !pillRef.current) return;

    const mm = gsap.matchMedia();
    mm.add("(min-width: 768px)", () => {
      const activeIdx = NAV_LINKS.findIndex((l) => l.href === `#${activeSection}`);
      const activeLink = linkRefs.current[activeIdx];

      if (activeLink && pillRef.current) {
        const navEl = navRef.current;
        const navRect = navEl?.getBoundingClientRect();
        const linkRect = activeLink.getBoundingClientRect();
        const offsetLeft = navRect ? linkRect.left - navRect.left : 0;

        gsap.to(pillRef.current, {
          x: offsetLeft,
          width: linkRect.width,
          opacity: 1,
          duration: 0.35,
          ease: "power2.out",
        });
      } else if (pillRef.current) {
        gsap.to(pillRef.current, { opacity: 0, duration: 0.2 });
      }

      return () => {};
    });

    return () => mm.revert();
  }, [activeSection, isReducedMotion]);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const target = document.querySelector(href);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      setIsMobileMenuOpen(false);
    }
  };

  return (
    <nav
      ref={navRef}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-[var(--bg-surface)] border-b border-[var(--border-1)]"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-[var(--shell-max-w)] mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <a href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--rf-charcoal)] flex items-center justify-center flex-shrink-0">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 12L8 4L13 12" stroke="var(--rf-ivory)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M5.5 9H10.5" stroke="var(--rf-ivory)" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            </div>
            <span className="text-[17px] font-bold text-[var(--rf-charcoal)] tracking-tight">
              RaptorFlow
            </span>
          </a>

          <div className="hidden md:flex items-center relative">
            <div
              ref={pillRef}
              className="absolute top-0 h-full bg-[var(--rf-charcoal)] rounded-[var(--radius-sm)] pointer-events-none opacity-0"
              style={{ width: 0 }}
            />
            {NAV_LINKS.map((link, i) => {
              const isActive = activeSection && link.href === `#${activeSection}`;
              return (
                <a
                  key={link.label}
                  ref={(el) => { linkRefs.current[i] = el; }}
                  href={link.href}
                  onClick={(e) => handleNavClick(e, link.href)}
                  className={`relative z-10 px-4 py-2 text-[14px] font-medium transition-colors duration-200 rounded-[var(--radius-sm)] ${
                    isActive
                      ? "text-[var(--rf-ivory)]"
                      : "text-[var(--ink-2)] hover:text-[var(--ink-1)]"
                  }`}
                >
                  {link.label}
                </a>
              );
            })}
          </div>

          <div className="hidden md:flex items-center gap-3">
            <a
              href="/login"
              className="text-[14px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] transition-colors duration-200"
            >
              Log in
            </a>
            <a
              href="/onboarding"
              className="px-5 py-2.5 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[var(--radius-sm)] text-[14px] font-semibold transition-all duration-200 hover:bg-[#3d363b] hover:translate-y-[-1px]"
            >
              Get Access
            </a>
          </div>

          <button
            className="md:hidden p-2 text-[var(--rf-charcoal)]"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>

        {isMobileMenuOpen && (
          <div className="md:hidden py-5 border-t border-[var(--border-1)]">
            <div className="flex flex-col gap-1">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  onClick={(e) => handleNavClick(e, link.href)}
                  className="px-3 py-3 text-[15px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] hover:bg-[var(--bg-surface)] rounded-[var(--radius-sm)] transition-colors duration-200"
                >
                  {link.label}
                </a>
              ))}
              <div className="flex flex-col gap-3 pt-4 mt-2 border-t border-[var(--border-1)]">
                <a
                  href="/login"
                  className="px-3 py-3 text-[15px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] transition-colors duration-200"
                >
                  Log in
                </a>
                <a
                  href="/onboarding"
                  className="px-4 py-3 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[var(--radius-sm)] text-[15px] font-semibold text-center"
                >
                  Get Access
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
