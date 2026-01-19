"use client";

import React from "react";
import { Link } from "lucide-react"; // Fallback if regular link is needed, but we used next/link
import NextLink from "next/link";
import { cn } from "@/lib/utils";

interface ArchButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode;
    href?: string;
    variant?: "primary" | "secondary" | "outline" | "ghost";
    size?: "sm" | "md" | "lg";
    className?: string;
}

export function ArchButton({
    children,
    href,
    variant = "primary",
    size = "md",
    className,
    ...props
}: ArchButtonProps) {

    // Architectural Styles
    // 0px Radius. 1px Border. Mono or Sans.
    const baseStyles = "inline-flex items-center justify-center font-mono uppercase tracking-wider transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-white focus:ring-offset-2 focus:ring-offset-black disabled:opacity-50 disabled:pointer-events-none";

    const variants = {
        primary: "bg-white text-black border border-white hover:bg-transparent hover:text-white",
        secondary: "bg-black text-white border border-white/20 hover:border-white",
        outline: "bg-transparent text-white border border-white hover:bg-white hover:text-black",
        ghost: "bg-transparent text-white/70 hover:text-white hover:bg-white/10 border border-transparent",
    };

    const sizes = {
        sm: "h-8 px-4 text-[10px]",
        md: "h-10 px-6 text-xs",
        lg: "h-14 px-8 text-sm",
    };

    const combinedClassName = cn(baseStyles, variants[variant], sizes[size], className);

    if (href) {
        return (
            <NextLink href={href} className={combinedClassName}>
                {children}
            </NextLink>
        );
    }

    return (
        <button className={combinedClassName} {...props}>
            {children}
        </button>
    );
}
