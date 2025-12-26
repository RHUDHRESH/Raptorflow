import React from 'react';
import { cn } from '@/lib/utils';

export function TypographyH1({ className, children, ...props }: React.ComponentProps<'h1'>) {
    return (
        <h1 className={cn('scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl font-headers', className)} {...props}>
            {children}
        </h1>
    );
}

export function TypographyH2({ className, children, ...props }: React.ComponentProps<'h2'>) {
    return (
        <h2 className={cn('scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight transition-colors first:mt-0 font-headers', className)} {...props}>
            {children}
        </h2>
    );
}

export function TypographyH3({ className, children, ...props }: React.ComponentProps<'h3'>) {
    return (
        <h3 className={cn('scroll-m-20 text-2xl font-semibold tracking-tight font-headers', className)} {...props}>
            {children}
        </h3>
    );
}

export function TypographyH4({ className, children, ...props }: React.ComponentProps<'h4'>) {
    return (
        <h4 className={cn('scroll-m-20 text-xl font-semibold tracking-tight', className)} {...props}>
            {children}
        </h4>
    );
}

export function TypographyP({ className, children, ...props }: React.ComponentProps<'p'>) {
    return (
        <p className={cn('leading-7 [&:not(:first-child)]:mt-6', className)} {...props}>
            {children}
        </p>
    );
}

export function TypographyLarge({ className, children, ...props }: React.ComponentProps<'div'>) {
    return (
        <div className={cn('text-lg font-semibold', className)} {...props}>
            {children}
        </div>
    );
}

export function TypographySmall({ className, children, ...props }: React.ComponentProps<'small'>) {
    return (
        <small className={cn('text-sm font-medium leading-none', className)} {...props}>
            {children}
        </small>
    );
}

export function TypographyMuted({ className, children, ...props }: React.ComponentProps<'p'>) {
    return (
        <p className={cn('text-sm text-muted-foreground', className)} {...props}>
            {children}
        </p>
    );
}

export function TypographyLead({ className, children, ...props }: React.ComponentProps<'p'>) {
    return (
        <p className={cn('text-xl text-muted-foreground', className)} {...props}>
            {children}
        </p>
    );
}
