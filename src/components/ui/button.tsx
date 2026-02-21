import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius-sm)] text-sm font-semibold transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-outer)] focus-visible:border-[var(--focus-inner)] disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 active:translate-y-[0px] cursor-pointer select-none font-sans",
  {
    variants: {
      variant: {
        default:
          "bg-[var(--btn-primary-bg)] text-[var(--btn-primary-fg)] hover:bg-[#3d363b] hover:translate-y-[-1px]",
        destructive:
          "bg-[var(--status-error)] text-[var(--rf-ivory)] hover:bg-[#7a3535]",
        outline:
          "bg-transparent border border-[var(--border-2)] text-[var(--ink-1)] hover:bg-[var(--bg-surface)] hover:border-[var(--ink-2)] active:bg-[var(--border-1)]",
        secondary:
          "bg-[var(--bg-surface)] text-[var(--ink-1)] border border-[var(--border-1)] hover:border-[var(--border-2)]",
        ghost:
          "bg-transparent text-[var(--ink-2)] font-medium hover:text-[var(--ink-1)] hover:bg-[#F3F0E7]",
        link: "text-[var(--ink-1)] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-11 px-6 py-2", // Premium feel height
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
