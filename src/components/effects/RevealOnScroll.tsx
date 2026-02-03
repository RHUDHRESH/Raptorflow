"use client";

import { useEffect, useRef, ReactNode } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

type AnimationType = "fadeUp" | "fadeDown" | "fadeLeft" | "fadeRight" | "scale" | "rotate";

interface RevealOnScrollProps {
  children: ReactNode;
  className?: string;
  animation?: AnimationType;
  duration?: number;
  delay?: number;
  distance?: number;
  once?: boolean;
}

export function RevealOnScroll({
  children,
  className = "",
  animation = "fadeUp",
  duration = 0.8,
  delay = 0,
  distance = 50,
  once = true,
}: RevealOnScrollProps) {
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!elementRef.current) return;

    const animations: Record<AnimationType, gsap.TweenVars> = {
      fadeUp: { y: distance, opacity: 0 },
      fadeDown: { y: -distance, opacity: 0 },
      fadeLeft: { x: distance, opacity: 0 },
      fadeRight: { x: -distance, opacity: 0 },
      scale: { scale: 0.8, opacity: 0 },
      rotate: { rotation: -15, opacity: 0, scale: 0.9 },
    };

    const ctx = gsap.context(() => {
      gsap.fromTo(
        elementRef.current,
        animations[animation],
        {
          x: 0,
          y: 0,
          scale: 1,
          rotation: 0,
          opacity: 1,
          duration: duration,
          ease: "power3.out",
          delay: delay,
          scrollTrigger: {
            trigger: elementRef.current,
            start: "top 85%",
            toggleActions: once ? "play none none none" : "play reverse play reverse",
          },
        }
      );
    });

    return () => ctx.revert();
  }, [animation, duration, delay, distance, once]);

  return (
    <div ref={elementRef} className={className}>
      {children}
    </div>
  );
}

export default RevealOnScroll;
