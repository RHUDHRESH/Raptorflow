"use client";

import * as React from "react";
import { useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import gsap from "gsap";

/* ══════════════════════════════════════════════════════════════════════════════
   GLASS CARD — Floating glassmorphism card with depth and glow
   ══════════════════════════════════════════════════════════════════════════════ */

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "coral" | "ocean" | "mint" | "violet" | "elevated";
  hover?: "lift" | "glow" | "both" | "none";
  animate?: boolean;
  delay?: number;
}

const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = "default", hover = "both", animate = true, delay = 0, children, ...props }, ref) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const glowRef = useRef<HTMLDivElement>(null);

    // Entrance animation
    useEffect(() => {
      if (!animate || !cardRef.current) return;

      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 24, scale: 0.96 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.6,
          delay: delay,
          ease: "power3.out",
        }
      );
    }, [animate, delay]);

    // Interactive glow effect on mouse move
    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
      if (!glowRef.current || !cardRef.current) return;

      const rect = cardRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      glowRef.current.style.background = `radial-gradient(400px circle at ${x}px ${y}px, var(--rf-coral-glow), transparent 40%)`;
    };

    const handleMouseLeave = () => {
      if (!glowRef.current) return;
      glowRef.current.style.background = "transparent";
    };

    const variantStyles = {
      default: "shadow-glass hover:shadow-glass-hover",
      coral: "shadow-coral",
      ocean: "shadow-ocean",
      mint: "shadow-mint",
      violet: "shadow-violet",
      elevated: "shadow-layered",
    };

    const hoverStyles = {
      lift: "hover-lift",
      glow: "hover-glow",
      both: "hover-lift hover-glow",
      none: "",
    };

    return (
      <div
        ref={(node) => {
          (cardRef as React.MutableRefObject<HTMLDivElement | null>).current = node;
          if (typeof ref === "function") ref(node);
          else if (ref) ref.current = node;
        }}
        className={cn(
          "relative overflow-hidden rounded-[var(--radius)]",
          "bg-[var(--gradient-card)] backdrop-blur-xl",
          "border border-[var(--glass-border)]",
          "transition-all duration-300",
          variantStyles[variant],
          hoverStyles[hover],
          className
        )}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        {...props}
      >
        {/* Interactive glow overlay */}
        <div
          ref={glowRef}
          className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{ mixBlendMode: "overlay" }}
        />

        {/* Shimmer effect on top edge */}
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent" />

        {/* Content */}
        <div className="relative z-10">{children}</div>
      </div>
    );
  }
);

GlassCard.displayName = "GlassCard";

/* ══════════════════════════════════════════════════════════════════════════════
   GLASS CARD HEADER
   ══════════════════════════════════════════════════════════════════════════════ */

interface GlassCardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  gradient?: boolean;
}

const GlassCardHeader = React.forwardRef<HTMLDivElement, GlassCardHeaderProps>(
  ({ className, gradient = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "relative px-6 pt-6 pb-4",
          gradient && "bg-gradient-to-b from-white/5 to-transparent",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GlassCardHeader.displayName = "GlassCardHeader";

/* ══════════════════════════════════════════════════════════════════════════════
   GLASS CARD CONTENT
   ══════════════════════════════════════════════════════════════════════════════ */

const GlassCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn("px-6 pb-6", className)}
      {...props}
    />
  );
});

GlassCardContent.displayName = "GlassCardContent";

/* ══════════════════════════════════════════════════════════════════════════════
   GLASS CARD FOOTER
   ══════════════════════════════════════════════════════════════════════════════ */

const GlassCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        "px-6 py-4 border-t border-[var(--glass-border)]",
        "bg-gradient-to-b from-transparent to-black/[0.02]",
        className
      )}
      {...props}
    />
  );
});

GlassCardFooter.displayName = "GlassCardFooter";

/* ══════════════════════════════════════════════════════════════════════════════
   STAT GLASS CARD — For displaying metrics with visual flair
   ══════════════════════════════════════════════════════════════════════════════ */

interface StatGlassCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: string;
    direction: "up" | "down" | "neutral";
  };
  accentColor?: "coral" | "ocean" | "mint" | "violet";
  index?: number;
}

function StatGlassCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  accentColor = "coral",
  index = 0,
}: StatGlassCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const valueRef = useRef<HTMLSpanElement>(null);

  const accentColors = {
    coral: {
      bg: "bg-gradient-coral",
      glow: "shadow-coral",
      text: "text-[var(--rf-coral)]",
      soft: "bg-[var(--rf-coral)]/10",
    },
    ocean: {
      bg: "bg-gradient-ocean",
      glow: "shadow-ocean",
      text: "text-[var(--rf-ocean)]",
      soft: "bg-[var(--rf-ocean)]/10",
    },
    mint: {
      bg: "bg-gradient-mint",
      glow: "shadow-mint",
      text: "text-[var(--rf-mint)]",
      soft: "bg-[var(--rf-mint)]/10",
    },
    violet: {
      bg: "bg-gradient-violet",
      glow: "shadow-violet",
      text: "text-[var(--rf-violet)]",
      soft: "bg-[var(--rf-violet)]/10",
    },
  };

  const colors = accentColors[accentColor];

  useEffect(() => {
    if (!cardRef.current) return;

    const ctx = gsap.context(() => {
      // Card entrance
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 30, scale: 0.95 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.5,
          delay: index * 0.1,
          ease: "power3.out",
        }
      );

      // Value counter animation
      if (valueRef.current && typeof value === "number") {
        gsap.fromTo(
          valueRef.current,
          { innerText: 0 },
          {
            innerText: value,
            duration: 1.5,
            delay: index * 0.1 + 0.3,
            ease: "power2.out",
            snap: { innerText: 1 },
          }
        );
      }
    }, cardRef);

    return () => ctx.revert();
  }, [index, value]);

  return (
    <div
      ref={cardRef}
      className={cn(
        "group relative overflow-hidden rounded-[var(--radius)] p-5",
        "bg-[var(--gradient-card)] backdrop-blur-xl",
        "border border-[var(--glass-border)]",
        "shadow-glass hover:shadow-glass-hover",
        "transition-all duration-300 hover:-translate-y-1"
      )}
    >
      {/* Accent glow in corner */}
      <div
        className={cn(
          "absolute -top-12 -right-12 h-32 w-32 rounded-full opacity-30 blur-3xl",
          colors.bg
        )}
      />

      {/* Header with icon */}
      <div className="relative flex items-center justify-between mb-3">
        <span className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </span>
        {icon && (
          <div className={cn("flex h-9 w-9 items-center justify-center rounded-xl", colors.soft)}>
            <div className={colors.text}>{icon}</div>
          </div>
        )}
      </div>

      {/* Value */}
      <div className="relative flex items-baseline gap-2">
        <span
          ref={valueRef}
          className="text-[32px] font-bold tracking-tight text-foreground"
        >
          {value}
        </span>
        {trend && (
          <span
            className={cn(
              "flex items-center gap-0.5 text-[13px] font-semibold",
              trend.direction === "up" && "text-[var(--rf-mint)]",
              trend.direction === "down" && "text-[var(--color-destructive)]",
              trend.direction === "neutral" && "text-muted-foreground"
            )}
          >
            {trend.direction === "up" && "↑"}
            {trend.direction === "down" && "↓"}
            {trend.value}
          </span>
        )}
      </div>

      {/* Subtitle */}
      {subtitle && (
        <p className="mt-1 text-[13px] text-muted-foreground">{subtitle}</p>
      )}

      {/* Bottom accent line */}
      <div
        className={cn(
          "absolute bottom-0 left-0 right-0 h-1 opacity-0 transition-opacity group-hover:opacity-100",
          colors.bg
        )}
      />
    </div>
  );
}

export {
  GlassCard,
  GlassCardHeader,
  GlassCardContent,
  GlassCardFooter,
  StatGlassCard,
};
