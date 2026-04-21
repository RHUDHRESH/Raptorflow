"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingNav() {
  const navRef = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(min-width: 0px)", () => {
        if (!navRef.current) return;

        gsap.fromTo(
          navRef.current,
          {
            backgroundColor: "rgba(247,244,238,0)",
            borderBottomColor: "rgba(19,20,26,0)",
            backdropFilter: "blur(0px)",
          },
          {
            backgroundColor: "rgba(247,244,238,0.94)",
            borderBottomColor: "rgba(19,20,26,0.10)",
            backdropFilter: "blur(16px)",
            ease: "none",
            scrollTrigger: {
              trigger: "body",
              start: "top top",
              end: "80px top",
              scrub: true,
            },
          },
        );
      });

      return () => mm.revert();
    },
    { scope: navRef },
  );

  return (
    <nav
      ref={navRef}
      className="fixed top-0 left-0 right-0 z-50 border-b h-[60px]"
      style={{ backgroundColor: "rgba(247,244,238,0)" }}
    >
      <div className="mx-auto max-w-[1200px] px-6 lg:px-12 h-full flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="text-[#13141A] font-bold text-lg tracking-tight shrink-0">
          RaptorFlow
        </a>

        {/* CTA */}
        <a href="/sign-up" className="btn-primary text-[13px] py-2.5 px-5">
          Start now — ₹5,000/month
        </a>
      </div>
    </nav>
  );
}
