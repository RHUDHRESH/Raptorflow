import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className,
  onClick,
  disabled = false,
  type = 'button'
}: ButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center rounded-[var(--radius)] font-medium transition-all focus:outline-none focus:ring-2 focus:ring-[var(--blueprint)] focus:ring-offset-2';

  const variantClasses = {
    primary: 'bg-[var(--ink)] text-white hover:bg-[var(--ink)]/90',
    secondary: 'bg-[var(--surface)] border border-[var(--border)] text-[var(--ink)] hover:bg-[var(--surface)]/80',
    outline: 'border border-[var(--border)] text-[var(--ink)] hover:bg-[var(--surface)]',
    ghost: 'text-[var(--ink)] hover:bg-[var(--surface)]'
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  return (
    <button
      type={type}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
