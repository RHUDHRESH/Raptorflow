"use client";

import React, { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(useGSAP);
}

interface GsapBridgeProps {
  children: React.ReactNode;
  className?: string;
  animation?: (tl: gsap.core.Timeline, container: React.MutableRefObject<HTMLDivElement | null>) => void;
  stagger?: boolean;
}

export function GsapBridge({ children, className, animation, stagger = false }: GsapBridgeProps) {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const tl = gsap.timeline();
      
      if (animation && container.current) {
        animation(tl, container);
      } else if (stagger && container.current) {
        // Default stagger reveals for any element with .gsap-reveal inside
        tl.fromTo(
          ".gsap-reveal",
          { y: 30, opacity: 0, visibility: "hidden" },
          { 
            y: 0, 
            opacity: 1, 
            visibility: "visible", 
            duration: 0.8, 
            ease: "power3.out", 
            stagger: 0.1 
          }
        );
      }
    },
    { scope: container }
  );

  return (
    <div ref={container} className={className}>
      {children}
    </div>
  );
}
