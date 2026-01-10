"use client";

import { ReactNode, useRef, useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import gsap from "gsap";

interface DetailRowProps {
  label: string;
  value: ReactNode;
  className?: string;
}

export function DetailRow({ label, value, className }: DetailRowProps) {
  return (
    <div className={cn("flex flex-col gap-1", className)}>
      <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <span className="text-[14px] font-medium text-foreground">{value}</span>
    </div>
  );
}

interface DetailCardProps {
  title: string;
  subtitle?: string;
  status?: {
    label: string;
    variant: "success" | "warning" | "error" | "info" | "pending";
  };
  onClose?: () => void;
  children: ReactNode;
  className?: string;
  animate?: boolean;
}

const statusStyles = {
  success: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  error: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  info: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export function DetailCard({
  title,
  subtitle,
  status,
  onClose,
  children,
  className,
  animate = true,
}: DetailCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!animate || !cardRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 20, scale: 0.98 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.4,
          ease: "power3.out",
        }
      );
    }, cardRef);

    return () => ctx.revert();
  }, [animate]);

  return (
    <div
      ref={cardRef}
      className={cn(
        "relative overflow-hidden rounded-[var(--radius)] border border-border bg-card shadow-modal",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between border-b border-border px-6 py-4">
        <div className="flex items-center gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-[18px] font-semibold text-foreground">{title}</h3>
              {status && (
                <span
                  className={cn(
                    "inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium",
                    statusStyles[status.variant]
                  )}
                >
                  {status.label}
                </span>
              )}
            </div>
            {subtitle && (
              <p className="mt-0.5 text-[13px] text-muted-foreground">{subtitle}</p>
            )}
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-6">{children}</div>
    </div>
  );
}

interface DetailGridProps {
  children: ReactNode;
  columns?: 2 | 3 | 4;
  className?: string;
}

export function DetailGrid({ children, columns = 2, className }: DetailGridProps) {
  return (
    <div
      className={cn(
        "grid gap-x-8 gap-y-4",
        columns === 2 && "grid-cols-2",
        columns === 3 && "grid-cols-3",
        columns === 4 && "grid-cols-4",
        className
      )}
    >
      {children}
    </div>
  );
}

interface DetailSectionProps {
  title?: string;
  children: ReactNode;
  className?: string;
}

export function DetailSection({ title, children, className }: DetailSectionProps) {
  return (
    <div className={cn("space-y-3", className)}>
      {title && (
        <h4 className="text-[13px] font-semibold text-foreground">{title}</h4>
      )}
      {children}
    </div>
  );
}
