/**
 * ENHANCED WITH:
 * - context7: GSAP link hover animations
 * - frontend-animations: Subtle link underline reveals
 * - performance-optimization: Lightweight animations
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const FOOTER_LINKS = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "Pricing", href: "#pricing" },
      { label: "Integrations", href: "#integrations" },
      { label: "Changelog", href: "#changelog" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "#about" },
      { label: "Blog", href: "#blog" },
      { label: "Careers", href: "#careers" },
      { label: "Contact", href: "#contact" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Documentation", href: "#docs" },
      { label: "Help Center", href: "#help" },
      { label: "Community", href: "#community" },
      { label: "Templates", href: "#templates" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy", href: "#privacy" },
      { label: "Terms", href: "#terms" },
      { label: "Security", href: "#security" },
    ],
  },
];

export function FooterSection() {
  const footerRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!footerRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Footer entrance
      gsap.from(".footer-content", {
        scrollTrigger: {
          trigger: footerRef.current,
          start: "top 90%",
          toggleActions: "play none none none",
        },
        y: 30,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out",
      });

      // Link hover underline animation
      const links = footerRef.current?.querySelectorAll(".footer-link");
      links?.forEach((link) => {
        const underline = link.querySelector(".link-underline");
        
        link.addEventListener("mouseenter", () => {
          gsap.to(underline, {
            scaleX: 1,
            duration: 0.25,
            ease: "power2.out",
          });
        });
        
        link.addEventListener("mouseleave", () => {
          gsap.to(underline, {
            scaleX: 0,
            duration: 0.25,
            ease: "power2.out",
          });
        });
      });
    }, footerRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <footer ref={footerRef} className="py-16 px-6 bg-[var(--bg-surface)] border-t border-[var(--border-1)]">
      <div className="footer-content max-w-[var(--shell-max-w)] mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 mb-12">
          {/* Logo and tagline */}
          <div className="col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--rf-charcoal)] flex items-center justify-center">
                <span className="text-white font-bold text-[14px]">RF</span>
              </div>
              <span className="text-[18px] font-bold text-[var(--rf-charcoal)]">
                RaptorFlow
              </span>
            </div>
            <p className="text-[14px] text-[var(--ink-2)] leading-relaxed max-w-xs">
              Marketing OS for operators who move with precision.
            </p>
          </div>

          {/* Link columns */}
          {FOOTER_LINKS.map((column) => (
            <div key={column.title}>
              <h4 className="text-[12px] font-semibold text-[var(--rf-charcoal)] tracking-wider uppercase mb-4">
                {column.title}
              </h4>
              <ul className="space-y-3">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="footer-link relative inline-block text-[14px] text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] transition-colors duration-200"
                    >
                      {link.label}
                      <span className="link-underline absolute bottom-0 left-0 w-full h-px bg-[var(--rf-charcoal)] origin-left scale-x-0" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-[var(--border-1)] flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[13px] text-[var(--ink-3)]">
            © 2025 RaptorFlow. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <a href="#twitter" className="footer-link relative text-[13px] text-[var(--ink-3)] hover:text-[var(--rf-charcoal)] transition-colors duration-200">
              Twitter
              <span className="link-underline absolute bottom-0 left-0 w-full h-px bg-[var(--rf-charcoal)] origin-left scale-x-0" />
            </a>
            <a href="#linkedin" className="footer-link relative text-[13px] text-[var(--ink-3)] hover:text-[var(--rf-charcoal)] transition-colors duration-200">
              LinkedIn
              <span className="link-underline absolute bottom-0 left-0 w-full h-px bg-[var(--rf-charcoal)] origin-left scale-x-0" />
            </a>
            <a href="#github" className="footer-link relative text-[13px] text-[var(--ink-3)] hover:text-[var(--rf-charcoal)] transition-colors duration-200">
              GitHub
              <span className="link-underline absolute bottom-0 left-0 w-full h-px bg-[var(--rf-charcoal)] origin-left scale-x-0" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
