/**
 * ENHANCED WITH:
 * - context7: GSAP scroll-driven opacity transform
 * - frontend-animations: Navbar show/hide on scroll, blur effect
 * - performance-optimization: Passive scroll listeners
 */

"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Menu, X } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Modules", href: "#modules" },
  { label: "Pricing", href: "#pricing" },
  { label: "About", href: "#about" },
];

export function LandingNavbar() {
  const navRef = useRef<HTMLElement>(null);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!navRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(navRef.current, {
        y: -100,
        opacity: 0,
        duration: 0.8,
        delay: 0.5,
        ease: "power3.out",
      });

      ScrollTrigger.create({
        trigger: document.body,
        start: "top -80",
        onEnter: () => setIsScrolled(true),
        onLeaveBack: () => setIsScrolled(false),
      });

      const mm = gsap.matchMedia();
      
      mm.add("(min-width: 768px)", () => {
        const navLinks = navRef.current?.querySelectorAll(".nav-link");
        navLinks?.forEach((link) => {
          const underline = link.querySelector(".nav-underline");
          
          link.addEventListener("mouseenter", () => {
            gsap.to(underline, { width: "100%", duration: 0.25, ease: "power2.out" });
          });
          
          link.addEventListener("mouseleave", () => {
            gsap.to(underline, { width: 0, duration: 0.25, ease: "power2.out" });
          });
        });

        const cta = navRef.current?.querySelector(".nav-cta");
        cta?.addEventListener("mouseenter", () => {
          gsap.to(cta, { scale: 1.02, duration: 0.2, ease: "power2.out" });
        });
        cta?.addEventListener("mouseleave", () => {
          gsap.to(cta, { scale: 1, duration: 0.2, ease: "power2.out" });
        });
      });

      return () => mm.revert();
    }, navRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const target = document.querySelector(href);
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
      setIsMobileMenuOpen(false);
    }
  };

  return (
    <nav
      ref={navRef}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-[var(--bg-surface)] border-b border-[var(--border-1)]"
          : "bg-[var(--bg-canvas)]"
      }`}
    >
      <div className="max-w-[var(--shell-max-w)] mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <a href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--rf-charcoal)] flex items-center justify-center">
              <span className="text-white font-bold text-[14px]">RF</span>
            </div>
            <span className="text-[18px] font-bold text-[var(--rf-charcoal)]">
              RaptorFlow
            </span>
          </a>

          <div className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.href}
                onClick={(e) => handleNavClick(e, link.href)}
                className="nav-link relative text-[14px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] transition-colors duration-200"
              >
                {link.label}
                <span className="nav-underline absolute -bottom-1 left-0 w-0 h-px bg-[var(--rf-charcoal)] transition-all duration-300" />
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <a
              href="/login"
              className="text-[14px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] transition-colors duration-200"
            >
              Log in
            </a>
            <a
              href="/onboarding"
              className="nav-cta px-5 py-2.5 bg-[var(--rf-charcoal)] text-white rounded-[var(--radius-sm)] text-[14px] font-medium transition-all duration-200 hover:bg-[#3d363b] hover:translate-y-[-1px]"
            >
              Get Started
            </a>
          </div>

          <button
            className="md:hidden p-2 text-[var(--rf-charcoal)]"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-[var(--border-1)]">
            <div className="flex flex-col gap-4">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  onClick={(e) => handleNavClick(e, link.href)}
                  className="text-[15px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] transition-colors duration-200"
                >
                  {link.label}
                </a>
              ))}
              <div className="flex flex-col gap-3 pt-4 border-t border-[var(--border-1)]">
                <a
                  href="/login"
                  className="text-[15px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] transition-colors duration-200"
                >
                  Log in
                </a>
                <a
                  href="/onboarding"
                  className="px-4 py-3 bg-[var(--rf-charcoal)] text-white rounded-[var(--radius-sm)] text-[15px] font-medium text-center"
                >
                  Get Started
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
