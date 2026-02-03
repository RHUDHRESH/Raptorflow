"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

interface FloatingElementsProps {
  children: React.ReactNode;
  className?: string;
  amplitude?: number;
  duration?: number;
  delay?: number;
}

export function FloatingElement({
  children,
  className = "",
  amplitude = 20,
  duration = 3,
  delay = 0,
}: FloatingElementsProps) {
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!elementRef.current) return;

    const ctx = gsap.context(() => {
      gsap.to(elementRef.current, {
        y: -amplitude,
        duration: duration,
        ease: "sine.inOut",
        repeat: -1,
        yoyo: true,
        delay: delay,
      });
    });

    return () => ctx.revert();
  }, [amplitude, duration, delay]);

  return (
    <div ref={elementRef} className={className}>
      {children}
    </div>
  );
}

// Rotating element
interface RotatingElementProps {
  children: React.ReactNode;
  className?: string;
  duration?: number;
  reverse?: boolean;
}

export function RotatingElement({
  children,
  className = "",
  duration = 20,
  reverse = false,
}: RotatingElementProps) {
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!elementRef.current) return;

    const ctx = gsap.context(() => {
      gsap.to(elementRef.current, {
        rotation: reverse ? -360 : 360,
        duration: duration,
        ease: "none",
        repeat: -1,
      });
    });

    return () => ctx.revert();
  }, [duration, reverse]);

  return (
    <div ref={elementRef} className={className}>
      {children}
    </div>
  );
}

export default FloatingElement;
