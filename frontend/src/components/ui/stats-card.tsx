"use client";

import { ReactNode, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import gsap from "gsap";

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: {
    value: string;
    direction: "up" | "down" | "neutral";
  };
  accent?: "coral" | "ocean" | "sage" | "lavender";
  className?: string;
  index?: number;
}

const accentStyles = {
  coral: {
    iconBg: "bg-[var(--rf-coral-soft)]",
    iconColor: "text-[var(--rf-coral)]",
    trendUp: "text-[var(--rf-sage)]",
  },
  ocean: {
    iconBg: "bg-[var(--rf-ocean-soft)]",
    iconColor: "text-[var(--rf-ocean)]",
    trendUp: "text-[var(--rf-sage)]",
  },
  sage: {
    iconBg: "bg-[var(--rf-sage-soft)]",
    iconColor: "text-[var(--rf-sage)]",
    trendUp: "text-[var(--rf-sage)]",
  },
  lavender: {
    iconBg: "bg-[var(--rf-lavender-soft)]",
    iconColor: "text-[var(--rf-lavender)]",
    trendUp: "text-[var(--rf-sage)]",
  },
};

export function StatsCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  accent = "coral",
  className,
  index = 0,
}: StatsCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const valueRef = useRef<HTMLDivElement>(null);
  const styles = accentStyles[accent];

  useEffect(() => {
    if (!cardRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 24, scale: 0.96 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.5,
          delay: index * 0.08,
          ease: "power3.out",
        }
      );

      if (valueRef.current && typeof value === "number") {
        gsap.fromTo(
          valueRef.current,
          { innerText: 0 },
          {
            innerText: value,
            duration: 1.5,
            delay: index * 0.08 + 0.3,
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
        "group relative overflow-hidden rounded-[var(--radius)] p-5 transition-all duration-300",
        "bg-[var(--gradient-card)] backdrop-blur-xl",
        "border border-[var(--glass-border)]",
        "shadow-glass hover:shadow-glass-hover",
        "hover:-translate-y-1",
        className
      )}
    >
      {/* Subtle ambient glow */}
      <div className={cn(
        "absolute -top-16 -right-16 h-32 w-32 rounded-full blur-3xl opacity-30 transition-opacity group-hover:opacity-50",
        styles.iconBg
      )} />

      {/* Top highlight */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />

      <div className="relative z-10">
        {/* Header with icon */}
        <div className="align-between mb-4">
          <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-[var(--ink-muted)]">
            {title}
          </span>
          {icon && (
            <div className={cn(
              "align-center justify-center rounded-xl transition-all duration-200",
              styles.iconBg,
              "group-hover:scale-110"
            )}>
              <div className={styles.iconColor}>{icon}</div>
            </div>
          )}
        </div>

        {/* Value */}
        <div className="align-baseline gap-2">
          <div
            ref={valueRef}
            className="text-[32px] font-bold tracking-tight text-[var(--ink)]"
          >
            {value}
          </div>
          {trend && (
            <span
              className={cn(
                "flex items-center gap-0.5 text-[13px] font-semibold px-2 py-0.5 rounded-full",
                trend.direction === "up" && `${styles.trendUp} bg-[var(--rf-mint)]/10`,
                trend.direction === "down" && "text-[var(--color-destructive)] bg-[var(--color-destructive)]/10",
                trend.direction === "neutral" && "text-muted-foreground bg-muted"
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
          <p className="mt-1.5 text-[13px] text-muted-foreground">{subtitle}</p>
        )}
      </div>

      {/* Bottom accent line on hover */}
      <div className={cn(
        "absolute bottom-0 left-0 right-0 h-0.5 opacity-0 transition-opacity group-hover:opacity-100",
        accent === "coral" && "bg-gradient-coral",
        accent === "ocean" && "bg-gradient-ocean",
        accent === "sage" && "bg-gradient-sage",
        accent === "lavender" && "bg-gradient-lavender"
      )} />
    </div>
  );
}
