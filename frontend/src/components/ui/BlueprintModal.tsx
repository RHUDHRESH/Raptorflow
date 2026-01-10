"use client";

import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT MODAL — Technical Dialog
   Features:
   - Paper texture background
   - Registration corner marks
   - Blueprint accent line
   - Figure annotation
   - Ink spread animation on open
   ══════════════════════════════════════════════════════════════════════════════ */

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

    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

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
            {/* Backdrop with blueprint grid */}
            <div
                className="absolute inset-0 bg-[var(--ink)]/80 backdrop-blur-md blueprint-grid"
                onClick={handleBackdropClick}
            />

            {/* Modal */}
            <div
                ref={modalRef}
                className={cn(
                    "relative w-full bg-[var(--paper)] rounded-[var(--radius-lg)]",
                    "border border-[var(--border)] ink-bleed-xl shadow-2xl scale-100",
                    "ink-spread",
                    sizeClasses[size],
                    className
                )}
            >
                {/* Paper texture */}
                <div
                    className="absolute inset-0 pointer-events-none rounded-[var(--radius-lg)] overflow-hidden"
                    style={{
                        backgroundImage: "url('/textures/paper-grain.png')",
                        backgroundRepeat: "repeat",
                        backgroundSize: "256px 256px",
                        opacity: 0.05,
                        mixBlendMode: "multiply",
                    }}
                />

                {/* Registration corner marks */}
                <div className="absolute -top-1 -left-1 w-5 h-5 border-t-2 border-l-2 border-[var(--blueprint)] rounded-tl-[var(--radius-lg)]" />
                <div className="absolute -top-1 -right-1 w-5 h-5 border-t-2 border-r-2 border-[var(--blueprint)] rounded-tr-[var(--radius-lg)]" />
                <div className="absolute -bottom-1 -left-1 w-5 h-5 border-b-2 border-l-2 border-[var(--blueprint)] rounded-bl-[var(--radius-lg)]" />
                <div className="absolute -bottom-1 -right-1 w-5 h-5 border-b-2 border-r-2 border-[var(--blueprint)] rounded-br-[var(--radius-lg)]" />

                {/* Header */}
                {(title || figure || showClose) && (
                    <div className="relative flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
                        <div className="flex items-center gap-4">
                            {figure && (
                                <>
                                    <span className="font-technical text-[var(--blueprint)]">{figure}</span>
                                    <div className="h-4 w-px bg-[var(--blueprint-line)]" />
                                </>
                            )}
                            {title && (
                                <h2 className="font-serif text-xl text-[var(--ink)]">{title}</h2>
                            )}
                            {code && (
                                <span className="font-technical text-[var(--muted)] bg-[var(--canvas)] px-2 py-0.5 rounded-[var(--radius-xs)]">
                                    {code}
                                </span>
                            )}
                        </div>

                        {showClose && (
                            <button
                                onClick={onClose}
                                className="p-2 rounded-[var(--radius-sm)] text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--canvas)] transition-colors"
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
                    <div className="relative px-6 py-4 border-t border-[var(--border)] flex items-center justify-end gap-3">
                        {/* Measurement line */}
                        <div className="absolute left-6 top-0 flex items-center gap-1 -translate-y-1/2">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} className={cn("w-px", i % 4 === 0 ? "h-3 bg-[var(--blueprint)]" : "h-1.5 bg-[var(--blueprint-line)]")} />
                            ))}
                        </div>
                        {footer}
                    </div>
                )}

                {/* Document info */}
                <div className="absolute bottom-2 left-6">
                    <span className="font-technical text-[8px] text-[var(--muted)]">
                        MODAL-PANEL
                    </span>
                </div>
            </div>
        </div>,
        document.body
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   MODAL HELPERS
   ══════════════════════════════════════════════════════════════════════════════ */

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
                    <span className="font-technical text-[var(--muted)]">{title.toUpperCase()}</span>
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    {code && <span className="font-technical text-[var(--blueprint)]">{code}</span>}
                </div>
            )}
            {children}
        </div>
    );
}

export default BlueprintModal;
