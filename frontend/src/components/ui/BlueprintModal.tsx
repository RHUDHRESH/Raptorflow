"use client";

import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   BLUEPRINT MODAL ΓÇö Technical Dialog
   Features:
   - Paper texture background
   - Registration corner marks
   - Blueprint accent line
   - Figure annotation
   - Ink spread animation on open
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface BlueprintModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    figure?: string;
    code?: string;
    size?: "sm" | "md" | "lg" | "xl" | "full";
    children: React.ReactNode;
    footer?: React.ReactNode;
    showClose?: boolean;
    className?: string;
}

export function BlueprintModal({
    isOpen,
    onClose,
    title,
    figure,
    code,
    size = "md",
    children,
    footer,
    showClose = true,
    className,
}: BlueprintModalProps) {
    const modalRef = useRef<HTMLDivElement>(null);

    const [mounted, setMounted] = useState(true);

    // Close on escape
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape") onClose();
        };
        if (isOpen) {
            document.addEventListener("keydown", handleEscape);
            document.body.style.overflow = "hidden";
        }
        return () => {
            document.removeEventListener("keydown", handleEscape);
            document.body.style.overflow = "";
        };
    }, [isOpen, onClose]);

    // Close on backdrop click
    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) onClose();
    };

    if (!isOpen || !mounted) return null;

    const sizeClasses = {
        sm: "max-w-sm",
        md: "max-w-lg",
        lg: "max-w-4xl",
        xl: "max-w-6xl",
        full: "max-w-[90vw]",
    };

    return createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop - Solid, minimal transparency */}
            <div
                className="absolute inset-0 bg-ink/98"
                onClick={handleBackdropClick}
            />

            {/* Modal */}
            <div
                ref={modalRef}
                className={cn(
                    "relative w-full bg-[var(--paper)] rounded-lg",
                    "border border-[var(--structure)] shadow-ink-md scale-100",
                    "animate-in fade-in zoom-in-95 duration-200",
                    sizeClasses[size],
                    className
                )}
                style={{ backgroundColor: 'var(--paper)' }} // Force solid background
            >
                {/* Paper texture - REMOVED for solidity
                <div
                    className="absolute inset-0 pointer-events-none rounded-lg overflow-hidden mix-blend-multiply opacity-5"
                    style={{
                        backgroundImage: "url('/textures/paper-grain.png')",
                        backgroundRepeat: "repeat",
                        backgroundSize: "256px 256px",
                    }}
                />
                */}

                {/* Registration corner marks */}
                <div className="absolute -top-1 -left-1 w-5 h-5 border-t-2 border-l-2 border-accent-blue rounded-tl-lg" />
                <div className="absolute -top-1 -right-1 w-5 h-5 border-t-2 border-r-2 border-accent-blue rounded-tr-lg" />
                <div className="absolute -bottom-1 -left-1 w-5 h-5 border-b-2 border-l-2 border-accent-blue rounded-bl-lg" />
                <div className="absolute -bottom-1 -right-1 w-5 h-5 border-b-2 border-r-2 border-accent-blue rounded-br-lg" />

                {/* Header */}
                {(title || figure || showClose) && (
                    <div className="relative flex items-center justify-between px-6 py-4 border-b border-structure/30">
                        <div className="flex items-center gap-4">
                            {figure && (
                                <>
                                    <span className="font-mono text-xs text-accent-blue tracking-widest">{figure}</span>
                                    <div className="h-4 w-px bg-structure" />
                                </>
                            )}
                            {title && (
                                <h2 className="font-serif text-xl text-ink font-bold">{title}</h2>
                            )}
                            {code && (
                                <span className="font-mono text-[10px] text-accent-blue bg-accent-blue/10 px-2 py-0.5 rounded-xs tracking-wider">
                                    {code}
                                </span>
                            )}
                        </div>

                        {showClose && (
                            <button
                                onClick={onClose}
                                className="p-2 rounded-sm text-ink-muted hover:text-ink hover:bg-surface transition-colors"
                            >
                                <X size={18} strokeWidth={1.5} />
                            </button>
                        )}
                    </div>
                )}

                {/* Content */}
                <div className="relative p-6 max-h-[85vh] overflow-y-auto">
                    {children}
                </div>

                {/* Footer */}
                {footer && (
                    <div className="relative px-6 py-4 border-t border-structure/30 flex items-center justify-end gap-3">
                        {/* Measurement line */}
                        <div className="absolute left-6 top-0 flex items-center gap-1 -translate-y-1/2">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} className={cn("w-px", i % 4 === 0 ? "h-3 bg-accent-blue" : "h-1.5 bg-structure")} />
                            ))}
                        </div>
                        {footer}
                    </div>
                )}

                {/* Document info */}
                <div className="absolute bottom-2 left-6">
                    <span className="font-mono text-[8px] tracking-widest text-ink-muted uppercase">
                        MODAL-PANEL
                    </span>
                </div>
            </div>
        </div>,
        document.body
    );
}

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   MODAL HELPERS
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface ModalSectionProps {
    title?: string;
    code?: string;
    children: React.ReactNode;
    className?: string;
}

export function ModalSection({ title, code, children, className }: ModalSectionProps) {
    return (
        <div className={cn("space-y-4", className)}>
            {title && (
                <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px] tracking-widest text-ink/40 uppercase">{title}</span>
                    <div className="h-px flex-1 bg-structure/30" />
                    {code && <span className="font-mono text-[10px] text-accent-blue tracking-wider">{code}</span>}
                </div>
            )}
            {children}
        </div>
    );
}

export default BlueprintModal;
