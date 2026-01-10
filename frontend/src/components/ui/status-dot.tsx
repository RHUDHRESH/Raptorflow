"use client";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";

export type StatusType = "done" | "in-progress" | "blocked" | "attention" | "idea" | "planned" | "pending";

interface StatusDotProps {
  status: StatusType;
  size?: "sm" | "md" | "lg";
  pulse?: boolean;
  className?: string;
}

const statusConfig: Record<StatusType, { color: string; glow: string; label: string }> = {
  "done": {
    color: "bg-[var(--rf-sage)]",
    glow: "shadow-[0_0_8px_var(--rf-sage-glow)]",
    label: "Done"
  },
  "in-progress": {
    color: "bg-[var(--rf-ocean)]",
    glow: "shadow-[0_0_8px_var(--rf-ocean-glow)]",
    label: "In Progress"
  },
  "blocked": {
    color: "bg-[var(--rf-coral)]",
    glow: "shadow-[0_0_8px_var(--rf-coral-glow)]",
    label: "Blocked"
  },
  "attention": {
    color: "bg-[var(--rf-peach)]",
    glow: "shadow-[0_0_8px_rgba(253,186,116,0.4)]",
    label: "Attention"
  },
  "idea": {
    color: "bg-[var(--rf-lavender)]",
    glow: "shadow-[0_0_8px_var(--rf-lavender-glow)]",
    label: "Idea"
  },
  "planned": {
    color: "bg-[var(--warm-400)]",
    glow: "shadow-[0_0_6px_rgba(212,208,202,0.5)]",
    label: "Planned"
  },
  "pending": {
    color: "bg-[var(--rf-peach)]",
    glow: "shadow-[0_0_8px_rgba(253,186,116,0.4)]",
    label: "Pending"
  },
};

const sizeConfig = {
  sm: "h-2 w-2",
  md: "h-2.5 w-2.5",
  lg: "h-3 w-3",
};

export function StatusDot({
  status,
  size = "md",
  pulse = false,
  className
}: StatusDotProps) {
  const config = statusConfig[status];

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{
        type: "spring",
        stiffness: 500,
        damping: 25,
        delay: 0.1
      }}
      className={cn(
        "relative rounded-full",
        sizeConfig[size],
        config.color,
        pulse && "animate-status-pulse",
        className
      )}
    >
      {/* Glow ring */}
      <motion.div
        className={cn(
          "absolute inset-0 rounded-full",
          config.color,
          config.glow,
          "opacity-60"
        )}
        animate={pulse ? {
          scale: [1, 1.5, 1],
          opacity: [0.6, 0, 0.6],
        } : {}}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </motion.div>
  );
}

// Tooltip wrapper for status dot with label
interface StatusDotWithLabelProps extends StatusDotProps {
  showLabel?: boolean;
}

export function StatusDotWithLabel({
  status,
  size = "md",
  pulse = false,
  showLabel = false,
  className
}: StatusDotWithLabelProps) {
  const config = statusConfig[status];

  return (
    <div className={cn("align-center gap-sm", className)}>
      <StatusDot status={status} size={size} pulse={pulse} />
      {showLabel && (
        <motion.span
          initial={{ opacity: 0, x: -4 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15, duration: 0.2 }}
          className="text-[12px] font-medium text-[var(--warm-600)] capitalize"
        >
          {config.label}
        </motion.span>
      )}
    </div>
  );
}

export { statusConfig };
