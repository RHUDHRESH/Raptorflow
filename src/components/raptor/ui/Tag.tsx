"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

interface TagProps {
  active?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export function Tag({ active = false, children, onClick }: TagProps) {
  const tagRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!tagRef.current || !onClick) return;
    const tag = tagRef.current;

    const handleMouseEnter = () => {
      gsap.to(tag, {
        scale: 1.02,
        duration: 0.15,
        ease: "power2.out",
      });
    };

    const handleMouseLeave = () => {
      gsap.to(tag, {
        scale: 1,
        duration: 0.15,
        ease: "power2.out",
      });
    };

    tag.addEventListener("mouseenter", handleMouseEnter);
    tag.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      tag.removeEventListener("mouseenter", handleMouseEnter);
      tag.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, [onClick]);

  const baseStyles =
    "inline-flex items-center h-[28px] px-3 text-[13px] font-medium rounded-[10px] border transition-colors duration-200 font-['DM_Sans',system-ui,sans-serif]";

  const activeStyles = active
    ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)]"
    : "bg-[var(--bg-canvas)] text-[var(--ink-1)] border-[var(--border-2)] hover:bg-[var(--state-hover)] hover:border-[var(--rf-charcoal)]";

  if (onClick) {
    return (
      <button
        ref={tagRef}
        onClick={onClick}
        className={`${baseStyles} ${activeStyles} cursor-pointer`}
      >
        {children}
      </button>
    );
  }

  return (
    <span className={`${baseStyles} ${activeStyles}`}>
      {children}
    </span>
  );
}
