import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius)] text-sm font-semibold transition-all duration-300 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none active:scale-[0.97]",
  {
    variants: {
      variant: {
        default:
          "bg-[var(--rf-coral)] text-white shadow-[0_2px_8px_rgba(249,112,102,0.25)] hover:shadow-[0_4px_16px_rgba(249,112,102,0.35)] hover:-translate-y-0.5 hover:bg-[#f85f55] focus-visible:ring-2 focus-visible:ring-[var(--rf-coral)]/40",
        destructive:
          "bg-[var(--rf-coral)] text-white hover:bg-[#e85a50] shadow-[0_2px_8px_rgba(249,112,102,0.2)] focus-visible:ring-2 focus-visible:ring-[var(--rf-coral)]/30",
        outline:
          "border border-[var(--warm-300)] bg-white/60 backdrop-blur-sm hover:bg-white hover:border-[var(--warm-400)] focus-visible:ring-2 focus-visible:ring-[var(--rf-coral)]/20",
        secondary:
          "bg-[var(--warm-100)] text-[var(--warm-700)] hover:bg-[var(--warm-200)] focus-visible:ring-2 focus-visible:ring-[var(--warm-400)]/30",
        ghost:
          "hover:bg-[var(--warm-100)] text-[var(--warm-600)] hover:text-[var(--warm-800)] focus-visible:ring-2 focus-visible:ring-[var(--warm-300)]/30",
        link: "text-[var(--rf-coral)] underline-offset-4 hover:underline focus-visible:ring-0",
        soft:
          "bg-[var(--rf-coral-soft)] text-[var(--rf-coral)] hover:bg-[var(--rf-coral)]/15 focus-visible:ring-2 focus-visible:ring-[var(--rf-coral)]/20",
      },
      size: {
        default: "h-11 px-6 py-2.5 has-[>svg]:px-5",
        sm: "h-9 rounded-xl gap-1.5 px-4 has-[>svg]:px-3 text-[13px]",
        lg: "h-12 rounded-[var(--radius)] px-8 has-[>svg]:px-6 text-[15px]",
        icon: "size-11 rounded-[var(--radius)]",
        "icon-sm": "size-9 rounded-xl",
        "icon-lg": "size-12 rounded-[var(--radius)]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
