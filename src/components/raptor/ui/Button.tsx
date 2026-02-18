"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

interface ButtonProps {
  variant?: "primary" | "secondary" | "tertiary" | "ghost";
  size?: "sm" | "md" | "lg";
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export function Button({
  variant = "primary",
  size = "md",
  leftIcon,
  rightIcon,
  loading = false,
  disabled = false,
  children,
  onClick,
  className = "",
}: ButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!buttonRef.current) return;
    const button = buttonRef.current;

    const handleMouseEnter = () => {
      gsap.to(button, {
        scale: variant === "ghost" ? 1.05 : 1.02,
        duration: 0.2,
        ease: "power2.out",
      });
    };

    const handleMouseLeave = () => {
      gsap.to(button, {
        scale: 1,
        duration: 0.2,
        ease: "power2.out",
      });
    };

    const handleMouseDown = () => {
      gsap.to(button, {
        scale: variant === "ghost" ? 0.95 : 0.98,
        duration: 0.1,
        ease: "power2.out",
      });
    };

    const handleMouseUp = () => {
      gsap.to(button, {
        scale: 1.02,
        duration: 0.1,
        ease: "power2.out",
      });
    };

    button.addEventListener("mouseenter", handleMouseEnter);
    button.addEventListener("mouseleave", handleMouseLeave);
    button.addEventListener("mousedown", handleMouseDown);
    button.addEventListener("mouseup", handleMouseUp);

    return () => {
      button.removeEventListener("mouseenter", handleMouseEnter);
      button.removeEventListener("mouseleave", handleMouseLeave);
      button.removeEventListener("mousedown", handleMouseDown);
      button.removeEventListener("mouseup", handleMouseUp);
    };
  }, [variant]);

  const baseStyles =
    "inline-flex items-center justify-center gap-2 font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#D2CCC0] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F7F5EF]";

  const sizeStyles = {
    sm: "h-[32px] px-3 text-[14px] rounded-[10px]",
    md: "h-[40px] px-4 text-[14px] rounded-[10px]",
    lg: "h-[48px] px-6 text-[14px] rounded-[10px]",
  };

  const variantStyles = {
    primary:
      "bg-[#2A2529] text-[#F3F0E7] hover:bg-[#3D383C] disabled:bg-[#D2CCC0] disabled:text-[#847C82]",
    secondary:
      "bg-transparent border border-[#D2CCC0] text-[#2A2529] hover:bg-[#F3F0E7] hover:border-[#2A2529] disabled:border-[#E3DED3] disabled:text-[#847C82]",
    tertiary:
      "bg-transparent text-[#2A2529] hover:bg-[#F3F0E7] disabled:text-[#847C82]",
    ghost:
      "w-[40px] h-[40px] p-0 bg-transparent text-[#2A2529] hover:bg-[#F3F0E7] rounded-[10px] disabled:text-[#847C82]",
  };

  const isDisabled = disabled || loading;

  return (
    <button
      ref={buttonRef}
      onClick={onClick}
      disabled={isDisabled}
      className={`
        ${baseStyles}
        ${variant === "ghost" ? "" : sizeStyles[size]}
        ${variantStyles[variant]}
        ${isDisabled ? "cursor-not-allowed" : "cursor-pointer"}
        ${className}
      `}
    >
      {loading && (
        <svg
          className="animate-spin h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {!loading && leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
      {variant !== "ghost" && <span>{children}</span>}
      {!loading && rightIcon && variant !== "ghost" && (
        <span className="flex-shrink-0">{rightIcon}</span>
      )}
    </button>
  );
}
