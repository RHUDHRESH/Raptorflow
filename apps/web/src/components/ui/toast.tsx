"use client";

import * as React from "react";

export type ToastVariant = "default" | "success" | "error" | "warning";

interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
}

interface ToastContextValue {
  toast: (message: string, variant?: ToastVariant) => void;
}

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const toast = React.useCallback((message: string, variant: ToastVariant = "default") => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, message, variant }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={[
              "flex items-center gap-3 rounded-xl border px-4 py-3 shadow-lg text-sm animate-in slide-in-from-right",
              t.variant === "default" && "bg-white border-[var(--border)] text-[var(--foreground)]",
              t.variant === "success" && "bg-green-50 border-green-200 text-green-800",
              t.variant === "error" && "bg-red-50 border-red-200 text-red-800",
              t.variant === "warning" && "bg-amber-50 border-amber-200 text-amber-800",
            ].join(" ")}
          >
            <span>
              {t.variant === "success" && "✓"}
              {t.variant === "error" && "✗"}
              {t.variant === "warning" && "⚠"}
              {t.variant === "default" && "ℹ"}
            </span>
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
