"use client";

import * as React from "react";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { navLinks } from "@/lib/landing-copy";
import { referralSignupHref } from "@/lib/referrals";
import { usePrefersReducedMotion } from "./landing-gsap-provider";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingNav() {
  const navRef = useRef<HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion || !navRef.current) return;

      // Nav background appears on scroll
      gsap.fromTo(
        navRef.current,
        {
          backgroundColor: "rgba(251,248,242,0)",
          borderBottomColor: "rgba(229,222,212,0)",
          backdropFilter: "blur(0px)",
        },
        {
          backgroundColor: "rgba(251,248,242,0.92)",
          borderBottomColor: "rgba(229,222,212,0.7)",
          backdropFilter: "blur(14px)",
          ease: "none",
          scrollTrigger: {
            trigger: "body",
            start: "top top",
            end: "80px top",
            scrub: true,
          },
        }
      );
    },
    { scope: navRef }
  );

  return (
    <nav
      ref={navRef}
      className="fixed top-0 left-0 right-0 z-50 border-b border-transparent"
      style={{ backgroundColor: "rgba(251,248,242,0)" }}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 lg:px-8 h-16">
        {/* Wordmark */}
        <a href="/" className="text-[#2A2622] font-semibold text-lg tracking-tight shrink-0 font-[family-name:var(--font-display)]">
          RaptorFlow
        </a>

        {/* Center links — desktop only */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors duration-200 font-mono uppercase tracking-widest"
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* Right CTAs */}
        <div className="flex items-center gap-3 shrink-0">
          <a
            href="/sign-in"
            className="hidden md:inline-flex text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors duration-200 px-4 py-2"
          >
            Sign in
          </a>
          <a
            href={referralSignupHref("LOKI")}
            className="inline-flex items-center gap-2 bg-[#D97757] text-white text-sm font-semibold px-5 py-2 hover:bg-[#C46A4D] transition-colors duration-200"
          >
            Start now
          </a>
        </div>
      </div>
    </nav>
  );
}
