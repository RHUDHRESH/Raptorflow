"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

export function CursorFollower() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const cursorDotRef = useRef<HTMLDivElement>(null);
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const cursor = cursorRef.current;
    const cursorDot = cursorDotRef.current;
    if (!cursor || !cursorDot) return;

    const onMouseMove = (e: MouseEvent) => {
      gsap.to(cursor, {
        x: e.clientX - 20,
        y: e.clientY - 20,
        duration: 0.5,
        ease: "power3.out",
      });
      gsap.to(cursorDot, {
        x: e.clientX - 4,
        y: e.clientY - 4,
        duration: 0.1,
      });
    };

    const onMouseEnterLink = () => setIsHovering(true);
    const onMouseLeaveLink = () => setIsHovering(false);

    window.addEventListener("mousemove", onMouseMove);

    // Add hover detection for interactive elements
    const interactiveElements = document.querySelectorAll(
      "a, button, [data-cursor-hover]"
    );
    interactiveElements.forEach((el) => {
      el.addEventListener("mouseenter", onMouseEnterLink);
      el.addEventListener("mouseleave", onMouseLeaveLink);
    });

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      interactiveElements.forEach((el) => {
        el.removeEventListener("mouseenter", onMouseEnterLink);
        el.removeEventListener("mouseleave", onMouseLeaveLink);
      });
    };
  }, []);

  // Don't show on touch devices
  if (typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches) {
    return null;
  }

  return (
    <>
      <div
        ref={cursorRef}
        className={`pointer-events-none fixed z-[9999] h-10 w-10 rounded-full border transition-all duration-300 mix-blend-difference hidden lg:block
          ${isHovering ? "scale-150 border-barley bg-barley/20" : "border-rock/50"}
        `}
        style={{ left: 0, top: 0 }}
      />
      <div
        ref={cursorDotRef}
        className="pointer-events-none fixed z-[9999] h-2 w-2 rounded-full bg-barley hidden lg:block"
        style={{ left: 0, top: 0 }}
      />
    </>
  );
}
