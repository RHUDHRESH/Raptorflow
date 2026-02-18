"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

export function CustomCursor() {
  const dotRef = useRef<HTMLDivElement>(null);
  const outlineRef = useRef<HTMLDivElement>(null);
  const [isPointer, setIsPointer] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only on desktop
    if (window.matchMedia("(pointer: coarse)").matches) return;

    const onMouseMove = (e: MouseEvent) => {
      setIsVisible(true);
      
      gsap.to(dotRef.current, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.1,
        ease: "power2.out",
      });

      gsap.to(outlineRef.current, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.3,
        ease: "power2.out",
      });
    };

    const onMouseEnter = () => setIsVisible(true);
    const onMouseLeave = () => setIsVisible(false);

    // Detect interactive elements
    const onElementHover = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const isInteractive = !!(
        target.tagName === "A" ||
        target.tagName === "BUTTON" ||
        target.closest("a") ||
        target.closest("button") ||
        target.classList.contains("cursor-pointer")
      );

      setIsPointer(isInteractive);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseover", onElementHover);
    document.addEventListener("mouseenter", onMouseEnter);
    document.addEventListener("mouseleave", onMouseLeave);

    return () => {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseover", onElementHover);
      document.removeEventListener("mouseenter", onMouseEnter);
      document.removeEventListener("mouseleave", onMouseLeave);
    };
  }, []);

  // Don't render on mobile
  if (typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches) {
    return null;
  }

  return (
    <>
      {/* Dot */}
      <div
        ref={dotRef}
        className={`fixed top-0 left-0 w-2 h-2 bg-[var(--ink-1)] rounded-full pointer-events-none z-[99999] transition-transform duration-100 ${
          isVisible ? "opacity-100" : "opacity-0"
        } ${isPointer ? "scale-0" : "scale-100"}`}
        style={{ transform: "translate(-50%, -50%)" }}
      />

      {/* Outline */}
      <div
        ref={outlineRef}
        className={`fixed top-0 left-0 pointer-events-none z-[99998] transition-all duration-200 ${
          isVisible ? "opacity-100" : "opacity-0"
        }`}
        style={{
          width: isPointer ? "48px" : "32px",
          height: isPointer ? "48px" : "32px",
          border: isPointer ? "2px solid var(--ink-1)" : "1px solid var(--ink-2)",
          borderRadius: "50%",
          transform: "translate(-50%, -50%)",
          backgroundColor: isPointer ? "rgba(42, 37, 41, 0.05)" : "transparent",
        }}
      />
    </>
  );
}
