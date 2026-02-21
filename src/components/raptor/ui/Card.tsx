"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

interface CardProps {
  variant?: "default" | "interactive" | "highlight";
  padding?: "sm" | "md" | "lg" | "none";
  isLocked?: boolean;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

interface CardHeaderProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  badge?: { text: string; variant: "success" | "warning" | "info" };
}

interface CardFooterProps {
  children: React.ReactNode;
  align?: "left" | "center" | "right";
}

export function Card({
  variant = "default",
  padding = "md",
  isLocked = false,
  children,
  className = "",
  onClick,
}: CardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (variant !== "interactive" || !cardRef.current) return;
    const card = cardRef.current;

    const handleMouseEnter = () => {
      gsap.to(card, {
        borderColor: "var(--border-2)",
        duration: 0.2,
        ease: "power2.out",
      });
    };

    const handleMouseLeave = () => {
      gsap.to(card, {
        borderColor: "var(--border-1)",
        duration: 0.2,
        ease: "power2.out",
      });
    };

    card.addEventListener("mouseenter", handleMouseEnter);
    card.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      card.removeEventListener("mouseenter", handleMouseEnter);
      card.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, [variant]);

  const baseStyles =
    "bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[14px] relative";

  const paddingStyles = {
    sm: "p-3",
    md: "p-4",
    lg: "p-6",
    none: "",
  };

  const variantStyles = {
    default: "",
    interactive: "cursor-pointer transition-colors",
    highlight: "ring-2 ring-[var(--ink-1)]",
  };

  return (
    <div
      ref={cardRef}
      onClick={onClick}
      className={`
        ${baseStyles}
        ${paddingStyles[padding]}
        ${variantStyles[variant]}
        ${onClick ? "cursor-pointer" : ""}
        ${className}
      `}
    >
      {isLocked && (
        <div className="absolute top-3 right-3 text-[var(--ink-3)]">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        </div>
      )}
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, badge }: CardHeaderProps) {
  const getBadgeStyles = (variant: string) => {
    const styles = {
      success: "bg-[var(--status-success-bg)] text-[var(--status-success)]",
      warning: "bg-[var(--status-warning-bg)] text-[var(--status-warning)]",
      info: "bg-[var(--status-info-bg)] text-[var(--status-info)]",
    };
    return styles[variant as keyof typeof styles] || styles.info;
  };

  return (
    <div className="mb-3">
      <div className="flex items-center gap-2">
        <h3 className="text-[16px] font-semibold text-[var(--ink-1)] font-['DM_Sans',system-ui,sans-serif]">
          {title}
        </h3>
        {badge && (
          <span
            className={`px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide rounded-[10px] ${getBadgeStyles(
              badge.variant
            )}`}
          >
            {badge.text}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="mt-1 text-[14px] text-[var(--ink-3)] font-['DM_Sans',system-ui,sans-serif]">
          {subtitle}
        </p>
      )}
    </div>
  );
}

export function CardFooter({ children, align = "left" }: CardFooterProps) {
  const alignStyles = {
    left: "justify-start",
    center: "justify-center",
    right: "justify-end",
  };

  return (
    <div
      className={`mt-4 pt-3 border-t border-[var(--border-1)] flex items-center gap-2 ${alignStyles[align]}`}
    >
      {children}
    </div>
  );
}

Card.Header = CardHeader;
Card.Footer = CardFooter;
