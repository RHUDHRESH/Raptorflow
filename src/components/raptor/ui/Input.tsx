"use client";

import React, { useRef, useEffect, useState } from "react";
import { gsap } from "gsap";

interface InputProps {
  type?: "text" | "email" | "password" | "textarea";
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  error?: string;
}

export function Input({
  type = "text",
  label,
  placeholder,
  value,
  onChange,
  disabled = false,
  error,
}: InputProps) {
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    if (isFocused && !error) {
      gsap.to(containerRef.current, {
        borderColor: "#2A2529",
        duration: 0.2,
        ease: "power2.out",
      });
    } else if (!isFocused && !error) {
      gsap.to(containerRef.current, {
        borderColor: "#D2CCC0",
        duration: 0.2,
        ease: "power2.out",
      });
    }
  }, [isFocused, error]);

  useEffect(() => {
    if (!containerRef.current) return;

    if (error) {
      gsap.to(containerRef.current, {
        borderColor: "#8B3D3D",
        duration: 0.2,
        ease: "power2.out",
      });
    }
  }, [error]);

  const baseInputStyles = `
    w-full bg-transparent text-[16px] text-[#2A2529] 
    font-['DM_Sans',system-ui,sans-serif]
    placeholder:text-[#847C82]
    focus:outline-none
    disabled:cursor-not-allowed disabled:text-[#847C82]
  `;

  const isTextArea = type === "textarea";

  return (
    <div className="w-full">
      {label && (
        <label className="block mb-1.5 text-[14px] font-medium text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
          {label}
        </label>
      )}
      <div
        ref={containerRef}
        className={`
          relative bg-[#F7F5EF] border rounded-[10px]
          ${isTextArea ? "min-h-[120px] py-3" : "h-[44px]"}
          ${error ? "border-[#8B3D3D]" : "border-[#D2CCC0]"}
          ${disabled ? "bg-[#EFEDE6]" : ""}
          focus-within:ring-[3px] focus-within:ring-[#D2CCC0]
          transition-shadow duration-200
        `}
      >
        {isTextArea ? (
          <textarea
            ref={inputRef as React.RefObject<HTMLTextAreaElement>}
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={disabled}
            className={`${baseInputStyles} resize-none px-3 py-0 h-full`}
          />
        ) : (
          <input
            ref={inputRef as React.RefObject<HTMLInputElement>}
            type={type}
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={disabled}
            className={`${baseInputStyles} px-3 h-full`}
          />
        )}
      </div>
      {error && (
        <div className="mt-1.5 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#8B3D3D]" />
          <span className="text-[12px] text-[#8B3D3D] font-['DM_Sans',system-ui,sans-serif]">
            {error}
          </span>
        </div>
      )}
    </div>
  );
}
