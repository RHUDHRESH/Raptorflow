"use client";

import React from "react";
import { motion } from "framer-motion";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular" | "card";
  width?: string | number;
  height?: string | number;
  lines?: number;
}

/**
 * Premium skeleton loading component with subtle shimmer animation.
 * Used to show loading states while async content is being fetched.
 */
export function Skeleton({
  className = "",
  variant = "rectangular",
  width,
  height,
  lines = 1
}: SkeletonProps) {
  const baseClasses = "bg-[var(--border)] animate-pulse rounded";

  const variantClasses = {
    text: "h-4 rounded",
    circular: "rounded-full",
    rectangular: "rounded-lg",
    card: "rounded-2xl"
  };

  const style: React.CSSProperties = {
    width: width || (variant === "circular" ? height : "100%"),
    height: height || (variant === "text" ? "1rem" : variant === "circular" ? width : "auto"),
  };

  if (variant === "text" && lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0.5 }}
            animate={{ opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.1 }}
            className={`${baseClasses} ${variantClasses.text}`}
            style={{ width: i === lines - 1 ? "60%" : "100%" }}
          />
        ))}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0.5 }}
      animate={{ opacity: [0.5, 0.8, 0.5] }}
      transition={{ duration: 1.5, repeat: Infinity }}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
    />
  );
}

/**
 * Skeleton for a full card with header, content, and footer.
 */
export function CardSkeleton({ className = "" }: { className?: string }) {
  return (
    <div className={`p-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <Skeleton variant="text" width="40%" />
        <Skeleton variant="circular" width={32} height={32} />
      </div>
      <Skeleton variant="text" lines={3} />
      <div className="flex gap-2 pt-2">
        <Skeleton variant="rectangular" width={80} height={32} />
        <Skeleton variant="rectangular" width={80} height={32} />
      </div>
    </div>
  );
}

/**
 * Skeleton for a stats/metric card.
 */
export function MetricSkeleton({ className = "" }: { className?: string }) {
  return (
    <div className={`p-4 rounded-xl border border-[var(--border)] bg-[var(--surface)] space-y-2 ${className}`}>
      <Skeleton variant="text" width="50%" height={12} />
      <Skeleton variant="text" width="70%" height={28} />
      <Skeleton variant="text" width="40%" height={12} />
    </div>
  );
}

/**
 * Skeleton for a table row.
 */
export function TableRowSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <div className="flex items-center gap-4 py-3 border-b border-[var(--border)]">
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          width={i === 0 ? "30%" : `${Math.floor(70 / (columns - 1))}%`}
        />
      ))}
    </div>
  );
}
