import React from 'react';
import { cn } from "@/lib/utils";

interface PillProps {
    children: React.ReactNode;
    className?: string;
}

export function Pill({ children, className }: PillProps) {
    return (
        <span className={cn("px-2.5 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider", className)}>
            {children}
        </span>
    );
}
