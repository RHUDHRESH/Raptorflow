import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 text-sm font-medium transition-all duration-200 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 focus-ring",
  {
    variants: {
      variant: {
        default: "btn-primary",
        secondary: "btn-secondary",
        ghost:
          "px-4 py-2 text-[var(--ink-900)] hover:bg-[var(--paper-150)] rounded-[var(--radius)]",
        outline:
          "border border-[var(--border)] bg-transparent px-4 py-2 text-[var(--ink-900)] hover:bg-[var(--paper-150)] rounded-[var(--radius)]",
        destructive:
          "bg-[var(--destructive)] px-4 py-2 text-white hover:bg-[#B03D33] rounded-[var(--radius)]",
        mono: "btn-mono",
      },
      size: {
        default: "h-10",
        sm: "h-8 px-3 text-xs",
        lg: "h-12 px-5 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    );
  },
);

Button.displayName = "Button";
