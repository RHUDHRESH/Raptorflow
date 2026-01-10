"use client";

import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from "react";
import { Check, AlertTriangle, Info, X } from "lucide-react";
import gsap from "gsap";

export type ToastVariant = "success" | "error" | "info" | "blueprint";

export interface ToastMessage {
    id: string;
    title: string;
    description?: string;
    variant: ToastVariant;
}

interface ToastContextType {
    toast: (title: string, options?: { description?: string; variant?: ToastVariant }) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

const ICONS = {
    success: Check,
    error: AlertTriangle,
    info: Info,
    blueprint: Info,
};

const VARIANTS = {
    success: "bg-[var(--success)] text-[var(--paper)] border-[var(--success)]",
    error: "bg-[var(--error)] text-[var(--paper)] border-[var(--error)]",
    info: "bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]",
    blueprint: "bg-[var(--blueprint)] text-[var(--paper)] border-[var(--blueprint)]",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = useState<ToastMessage[]>([]);

    const removeToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    const toast = useCallback((title: string, options: { description?: string; variant?: ToastVariant } = {}) => {
        const id = Math.random().toString(36).substring(7);
        setToasts((prev) => [...prev, { id, title, description: options.description, variant: options.variant || "info" }]);

        const timeout = setTimeout(() => {
            removeToast(id);
        }, 4000);

        return () => clearTimeout(timeout);
    }, [removeToast]);

    return (
        <ToastContext.Provider value={{ toast }}>
            {children}
            <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none">
                {toasts.map((t) => (
                    <ToastItem key={t.id} toast={t} onDismiss={() => removeToast(t.id)} />
                ))}
            </div>
        </ToastContext.Provider>
    );
}

function ToastItem({ toast, onDismiss }: { toast: ToastMessage; onDismiss: () => void }) {
    const ref = useRef<HTMLDivElement>(null);
    const Icon = ICONS[toast.variant];

    useEffect(() => {
        if (!ref.current) return;
        gsap.fromTo(ref.current,
            { opacity: 0, x: 50, scale: 0.95 },
            { opacity: 1, x: 0, scale: 1, duration: 0.4, ease: "power2.out" }
        );
    }, []);

    // Animate out before removing (handled by parent removal mostly, but rigorous impl w/ AnimatePresence ideal. Simplified here for speed.)

    return (
        <div
            ref={ref}
            className={`pointer-events-auto min-w-[320px] max-w-[400px] p-4 rounded-[var(--radius-md)] border shadow-xl ink-bleed-md flex items-start gap-3 ${VARIANTS[toast.variant]}`}
        >
            <div className="mt-0.5 p-0.5 rounded-full border border-[var(--paper)]/30">
                <Icon size={14} strokeWidth={2.5} />
            </div>
            <div className="flex-1">
                <h4 className="font-semibold text-sm leading-none mb-1">{toast.title}</h4>
                {toast.description && <p className="text-xs opacity-90 leading-snug">{toast.description}</p>}
            </div>
            <button onClick={onDismiss} className="text-[var(--paper)]/70 hover:text-[var(--paper)] transition-colors">
                <X size={14} />
            </button>
        </div>
    );
}

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) throw new Error("useToast must be used within ToastProvider");
    return context;
};
