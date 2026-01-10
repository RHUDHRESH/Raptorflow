"use client";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular" | "card";
  animation?: "pulse" | "shimmer" | "wave";
}

export function Skeleton({
  className,
  variant = "rectangular",
  animation = "shimmer"
}: SkeletonProps) {
  const baseStyles = "bg-[var(--warm-200)] relative overflow-hidden";

  const variantStyles = {
    text: "h-4 w-full rounded-lg",
    circular: "rounded-full",
    rectangular: "rounded-[var(--radius)]",
    card: "rounded-3xl min-h-[120px]",
  };

  return (
    <div
      className={cn(
        baseStyles,
        variantStyles[variant],
        className
      )}
    >
      {animation === "shimmer" && (
        <motion.div
          className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent"
          animate={{ x: ["calc(-100%)", "calc(200%)"] }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      )}
      {animation === "pulse" && (
        <motion.div
          className="absolute inset-0 bg-[var(--warm-300)]"
          animate={{ opacity: [0, 0.5, 0] }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      )}
      {animation === "wave" && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
          animate={{
            x: ["-100%", "100%"],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      )}
    </div>
  );
}

// Pre-built skeleton components
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("p-6 space-y-4 rounded-3xl bg-white/60 border border-[var(--warm-200)]", className)}>
      <div className="align-start gap-4">
        <Skeleton variant="circular" className="h-3 w-3 flex-shrink-0 mt-1.5" />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" className="h-5 w-3/4" />
          <Skeleton variant="text" className="h-4 w-full" />
          <Skeleton variant="text" className="h-4 w-2/3" />
        </div>
      </div>
      <div className="align-between pt-4 border-t border-[var(--warm-100)]">
        <div className="align-start gap-4">
          <Skeleton variant="text" className="h-4 w-16" />
          <Skeleton variant="text" className="h-4 w-12" />
        </div>
        <Skeleton variant="rectangular" className="h-8 w-20 rounded-full" />
      </div>
    </div>
  );
}

export function SkeletonStats({ className }: { className?: string }) {
  return (
    <div className={cn("p-5 rounded-[var(--radius)] bg-white/60 border border-[var(--warm-200)]", className)}>
      <div className="align-between mb-4">
        <Skeleton variant="text" className="h-3 w-24" />
        <Skeleton variant="rectangular" className="h-10 w-10 rounded-xl" />
      </div>
      <Skeleton variant="text" className="h-8 w-16 mb-2" />
      <Skeleton variant="text" className="h-4 w-20" />
    </div>
  );
}

export function SkeletonAvatar({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeStyles = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12",
  };

  return <Skeleton variant="circular" className={sizeStyles[size]} />;
}

export function SkeletonList({ count = 3, className }: { count?: number; className?: string }) {
  return (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <SkeletonCard />
        </motion.div>
      ))}
    </div>
  );
}
