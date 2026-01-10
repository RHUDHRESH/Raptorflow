"use client";

import React, { useEffect, useRef } from "react";
import { X } from "lucide-react";
import gsap from "gsap";

interface BlueprintDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    code?: string;
    children: React.ReactNode;
    width?: "md" | "lg" | "xl" | "full";
}

const WIDTHS = {
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    full: "max-w-full",
};

export function BlueprintDrawer({ isOpen, onClose, title, code = "PNL-01", children, width = "md" }: BlueprintDrawerProps) {
    const drawerRef = useRef<HTMLDivElement>(null);
    const overlayRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
            gsap.to(overlayRef.current, { opacity: 1, duration: 0.3, display: "block" });
            gsap.fromTo(drawerRef.current, { x: "100%" }, { x: "0%", duration: 0.4, ease: "power3.out", display: "flex" });
        } else {
            document.body.style.overflow = "";
            gsap.to(overlayRef.current, { opacity: 0, duration: 0.3, onComplete: () => { if (overlayRef.current) overlayRef.current.style.display = "none"; } });
            gsap.to(drawerRef.current, { x: "100%", duration: 0.3, ease: "power2.in", onComplete: () => { if (drawerRef.current) drawerRef.current.style.display = "none"; } });
        }
    }, [isOpen]);

    // Handle ESC key
    useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === "Escape" && isOpen) onClose();
        };
        window.addEventListener("keydown", handleEsc);
        return () => window.removeEventListener("keydown", handleEsc);
    }, [isOpen, onClose]);

    return (
        <>
            {/* Overlay */}
            <div
                ref={overlayRef}
                onClick={onClose}
                className="fixed inset-0 bg-[var(--ink)]/20 backdrop-blur-sm z-40 hidden opacity-0 transition-opacity"
            />

            {/* Drawer */}
            <div
                ref={drawerRef}
                className={`fixed inset-y-0 right-0 z-50 w-full ${WIDTHS[width]} bg-[var(--paper)] border-l border-[var(--border)] shadow-2xl flex flex-col hidden transform translate-x-full`}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-[var(--border-subtle)]">
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <span className="font-technical text-[var(--blueprint)] tracking-wider">FIG. {code}</span>
                            <div className="h-px w-8 bg-[var(--blueprint-line)]" />
                        </div>
                        <h2 className="text-xl font-editorial text-[var(--ink)]">{title}</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 -mr-2 text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--canvas)] rounded-[var(--radius-sm)] transition-colors"
                    >
                        <X size={20} strokeWidth={1.5} />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
                    {children}
                </div>

                {/* Decorative Handle */}
                <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-full h-24 w-6 flex items-center justify-center pointer-events-none">
                    <div className="h-12 w-1 bg-[var(--border)] rounded-full" />
                </div>
            </div>
        </>
    );
}
