"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg";
}

export function Modal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
  size = "md",
}: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!overlayRef.current || !contentRef.current) return;

    if (isOpen) {
      // Prevent body scroll
      document.body.style.overflow = "hidden";

      // Animate in
      gsap.fromTo(
        overlayRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.2, ease: "power2.out" }
      );

      gsap.fromTo(
        contentRef.current,
        { opacity: 0, scale: 0.95, y: 20 },
        { opacity: 1, scale: 1, y: 0, duration: 0.3, ease: "power2.out", delay: 0.1 }
      );
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  const handleClose = () => {
    if (!overlayRef.current || !contentRef.current) return;

    // Animate out
    gsap.to(contentRef.current, {
      opacity: 0,
      scale: 0.95,
      y: 20,
      duration: 0.2,
      ease: "power2.in",
    });

    gsap.to(overlayRef.current, {
      opacity: 0,
      duration: 0.2,
      ease: "power2.in",
      delay: 0.1,
      onComplete: onClose,
    });
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === overlayRef.current) {
      handleClose();
    }
  };

  const maxWidthStyles = {
    sm: "max-w-[400px]",
    md: "max-w-[560px]",
    lg: "max-w-[720px]",
  };

  if (!isOpen) return null;

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: "rgba(42, 37, 41, 0.4)" }}
    >
      <div
        ref={contentRef}
        className={`
          w-full ${maxWidthStyles[size]}
          bg-[var(--bg-raised)] border border-[var(--border-1)] rounded-[14px]
          shadow-[0_8px_32px_rgba(42,37,41,0.08)]
          overflow-hidden
        `}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 pb-0">
          <div>
            <h2 className="text-[20px] font-semibold text-[var(--ink-1)] font-['DM_Sans',system-ui,sans-serif]">
              {title}
            </h2>
            {subtitle && (
              <p className="mt-1 text-[14px] text-[var(--ink-3)] font-['DM_Sans',system-ui,sans-serif]">
                {subtitle}
              </p>
            )}
          </div>
          <button
            onClick={handleClose}
            className="p-2 -mr-2 -mt-2 text-[var(--ink-3)] hover:text-[var(--ink-1)] hover:bg-[var(--state-hover)] rounded-[10px] transition-colors"
            aria-label="Close modal"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-[var(--border-1)] bg-[var(--bg-surface)]">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "default" | "danger";
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default",
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-[14px] font-medium text-[var(--ink-2)] hover:text-[var(--ink-1)] hover:bg-[var(--bg-canvas)] rounded-[10px] transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`px-4 py-2 text-[14px] font-medium rounded-[10px] transition-colors ${variant === "danger"
                ? "bg-[#8B3D3D] text-white hover:bg-[#6B2D2D]"
                : "bg-[var(--ink-1)] text-white hover:bg-[#3D383C]"
              }`}
          >
            {confirmText}
          </button>
        </div>
      }
    >
      <p className="text-[14px] text-[var(--ink-2)] font-['DM_Sans',system-ui,sans-serif]">
        {description}
      </p>
    </Modal>
  );
}
