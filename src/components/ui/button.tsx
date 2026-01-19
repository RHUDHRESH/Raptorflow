import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ink disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 active:scale-[0.99]",
  {
    variants: {
      variant: {
        default:
          "bg-[var(--ink)] text-[var(--paper)] hover:bg-[var(--ink)]/90 border border-transparent shadow-sm",
        destructive:
          "bg-[var(--error)] text-[var(--paper)] hover:bg-[var(--error)]/90 shadow-sm",
        outline:
          "border border-[var(--border)] bg-transparent text-[var(--ink)] hover:bg-[var(--surface)] hover:text-[var(--ink)] hover:border-[var(--ink)]",
        secondary:
          "bg-[var(--surface)] text-[var(--ink)] border border-[var(--border-subtle)] hover:bg-[var(--surface-hover)] shadow-sm",
        ghost:
          "hover:bg-[var(--surface)] text-[var(--ink)] hover:text-[var(--ink)]",
        link: "text-[var(--ink)] underline-offset-4 hover:underline",
        // Blueprint variant - Kept for backward compat but styled as Quiet Luxury Secondary
        blueprint:
          "bg-[var(--blueprint-light)] text-[var(--blueprint)] border border-[var(--blueprint-line)] hover:bg-[var(--blueprint-line)]",
      },
      size: {
        default: "h-11 px-6 py-2", // Slightly taller for premium feel
        sm: "h-9 rounded-md px-4 text-xs",
        lg: "h-12 rounded-lg px-8 text-base",
        icon: "h-11 w-11",
        "icon-sm": "h-9 w-9 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
