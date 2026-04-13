import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-full text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-[var(--primary)] px-4 py-2 text-[var(--primary-foreground)] hover:opacity-95",
        secondary:
          "bg-white px-4 py-2 text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--muted)]",
        ghost: "px-4 py-2 text-[var(--foreground)] hover:bg-[var(--muted)]",
        outline:
          "border border-[var(--border)] bg-transparent px-4 py-2 text-[var(--foreground)] hover:bg-[var(--muted)]",
        destructive: "bg-red-600 px-4 py-2 text-white hover:bg-red-700",
      },
      size: {
        default: "h-10",
        sm: "h-8 px-3 text-xs",
        lg: "h-12 px-5 text-base",
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
