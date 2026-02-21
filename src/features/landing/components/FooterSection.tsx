"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const FOOTER_COLUMNS = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "#modules" },
      { label: "Modules", href: "#modules" },
      { label: "Pricing", href: "#pricing" },
      { label: "Changelog", href: "#" },
      { label: "Roadmap", href: "#" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "#" },
      { label: "Blog", href: "#" },
      { label: "Careers", href: "#" },
      { label: "Contact", href: "#" },
      { label: "Press", href: "#" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Docs", href: "#" },
      { label: "Help Center", href: "#" },
      { label: "Community", href: "#" },
      { label: "Templates", href: "#" },
      { label: "API", href: "#" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy", href: "#" },
      { label: "Terms", href: "#" },
      { label: "Security", href: "#" },
      { label: "Cookie Policy", href: "#" },
    ],
  },
];

export function FooterSection() {
  const footerRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!footerRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(".footer-col", {
        scrollTrigger: {
          trigger: footerRef.current,
          start: "top 90%",
          toggleActions: "play none none none",
        },
        y: 30,
        opacity: 0,
        duration: 0.6,
        stagger: 0.06,
        ease: "power2.out",
      });

      gsap.from(".footer-bottom", {
        scrollTrigger: {
          trigger: ".footer-bottom",
          start: "top 95%",
          toggleActions: "play none none none",
        },
        opacity: 0,
        duration: 0.5,
        delay: 0.3,
        ease: "power2.out",
      });
    }, footerRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <footer ref={footerRef} className="bg-[var(--rf-charcoal)] pt-24 pb-10 px-6">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-10 mb-16">
          <div className="footer-col col-span-2 md:col-span-1">
            <a href="/" className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-white/10 flex items-center justify-center flex-shrink-0">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M3 12L8 4L13 12" stroke="var(--rf-ivory)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M5.5 9H10.5" stroke="var(--rf-ivory)" strokeWidth="1.4" strokeLinecap="round" />
                </svg>
              </div>
              <span className="text-[16px] font-bold text-[var(--rf-ivory)] tracking-tight">
                RaptorFlow
              </span>
            </a>
            <p className="text-[13px] font-semibold text-white/60 mb-3 leading-snug">
              The Marketing OS for Operators.
            </p>
            <p className="text-[12px] text-white/35 leading-relaxed mb-6">
              One cockpit for every marketing move. Built for operators who need precision and speed.
            </p>
            <div className="flex items-center gap-4">
              {[
                {
                  label: "Twitter",
                  href: "#",
                  icon: (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                    </svg>
                  ),
                },
                {
                  label: "LinkedIn",
                  href: "#",
                  icon: (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                    </svg>
                  ),
                },
                {
                  label: "GitHub",
                  href: "#",
                  icon: (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                    </svg>
                  ),
                },
              ].map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  aria-label={social.label}
                  className="text-white/35 hover:text-white/80 transition-colors duration-200"
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>

          {FOOTER_COLUMNS.map((col) => (
            <div key={col.title} className="footer-col">
              <h4 className="rf-label text-white/30 mb-5">{col.title}</h4>
              <ul className="space-y-3">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-[13px] text-white/50 hover:text-white/90 transition-colors duration-200"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="footer-bottom border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="rf-mono-xs text-white/25">
            © 2026 RaptorFlow, Inc. All rights reserved.
          </p>
          <p className="text-[12px] text-white/15 tracking-[0.05em]">
            The Marketing OS for Operators
          </p>
        </div>
      </div>
    </footer>
  );
}
