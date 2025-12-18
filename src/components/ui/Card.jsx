import * as React from "react"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"

/**
 * RAPTORFLOW UNIFIED CARD SYSTEM
 * Spec: 18px radius, 20px padding, tactile states
 * 
 * Variants:
 * - default: Standard surface, subtle border
 * - elevated: Higher shadow for prominent widgets
 * - interactive: Clickable with hover/press states
 * - muted: De-emphasized background
 * - selected: Active/selected state with accent border
 */

const cardVariants = cva(
  [
    // Base: 18px radius, 1px border, premium layered shadow, consistent transition
    "rounded-[18px] border",
    "shadow-[0_1px_3px_rgba(0,0,0,0.04),0_6px_16px_rgba(0,0,0,0.04)]",
    "transition-all duration-[160ms] ease-[cubic-bezier(0.4,0,0.2,1)]",
  ].join(" "),
  {
    variants: {
      variant: {
        default: [
          "bg-[var(--surface-1)] border-[var(--border-1)]",
        ].join(" "),

        elevated: [
          "bg-[var(--surface-1)] border-[var(--border-1)]",
          "shadow-[0_4px_6px_rgba(0,0,0,0.04),0_10px_24px_rgba(0,0,0,0.06)]",
        ].join(" "),

        interactive: [
          "bg-[var(--surface-1)] border-[var(--border-1)]",
          "cursor-pointer",
          "hover:-translate-y-0.5 hover:shadow-[0_4px_12px_rgba(0,0,0,0.08),0_12px_28px_rgba(0,0,0,0.06)] hover:border-[var(--border-2)]",
          "active:translate-y-px active:shadow-[0_1px_3px_rgba(0,0,0,0.04)]",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        ].join(" "),

        muted: [
          "bg-[var(--surface-2)] border-[var(--border-1)]",
          "shadow-none",
        ].join(" "),

        selected: [
          "bg-[var(--surface-1)] border-[var(--primary)]",
          "ring-2 ring-[var(--primary)]/20",
        ].join(" "),
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const Card = React.forwardRef(({ className, variant, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(cardVariants({ variant }), className)}
    {...props}
  />
))
Card.displayName = "Card"

// CardHeader: 20px padding, 8px gap between title/description
const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col gap-2 p-5", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

// CardTitle: 15px semibold
const CardTitle = React.forwardRef(({ className, as: Comp = "h3", ...props }, ref) => (
  <Comp
    ref={ref}
    className={cn(
      "text-[15px] font-semibold leading-tight text-[var(--text-1)]",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

// CardDescription: 13px muted
const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-[13px] text-[var(--text-3)] leading-relaxed", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

// CardContent: 20px horizontal, 0 top (connects to header)
const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("px-5 pb-5", className)} {...props} />
))
CardContent.displayName = "CardContent"

// CardFooter: 20px padding, flex row, border-top
const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex items-center gap-3 px-5 py-4 border-t border-[var(--border-1)]",
      className
    )}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, cardVariants }
