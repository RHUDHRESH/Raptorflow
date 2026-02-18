"use client";

import { useEffect, useState } from "react";
import gsap from "gsap";
import { Check, AlertCircle, X } from "lucide-react";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContainerProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Auto dismiss after 4 seconds
    const timer = setTimeout(() => {
      handleDismiss();
    }, 4000);

    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => onDismiss(toast.id), 300);
  };

  const icons = {
    success: <Check size={18} className="text-[var(--status-success)]" />,
    error: <AlertCircle size={18} className="text-[var(--status-error)]" />,
    info: <AlertCircle size={18} className="text-[var(--status-info)]" />,
  };

  const borderColors = {
    success: "border-l-[var(--status-success)]",
    error: "border-l-[var(--status-error)]",
    info: "border-l-[var(--status-info)]",
  };

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-1)] border-l-4 ${borderColors[toast.type]} rounded-[var(--radius-md)] shadow-[var(--shadow-modal)] min-w-[300px] transition-all duration-300 ${
        isExiting ? "translate-x-full opacity-0" : "translate-x-0 opacity-100"
      }`}
    >
      {icons[toast.type]}
      <p className="rf-body-sm flex-1 text-[var(--ink-1)]">{toast.message}</p>
      <button
        onClick={handleDismiss}
        className="p-1 rounded hover:bg-[var(--state-hover)] transition-colors"
      >
        <X size={16} className="text-[var(--ink-3)]" />
      </button>
    </div>
  );
}

// Hook for using toasts
export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: ToastType = "info") => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return { toasts, addToast, dismissToast };
}
