"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import gsap from "gsap";

/* ══════════════════════════════════════════════════════════════════════════════
   DRAGGABLE ITEM — Shared component for drag interactions
   Used by: PerceptualMap bubbles, PositioningGrid cards
   ══════════════════════════════════════════════════════════════════════════════ */

interface DraggableItemProps {
    id: string;
    initialX: number; // Percentage 0-100
    initialY: number; // Percentage 0-100
    onPositionChange?: (id: string, x: number, y: number) => void;
    onClick?: () => void;
    children: React.ReactNode;
    className?: string;
    disabled?: boolean;
    constrainToParent?: boolean;
}

export function DraggableItem({
    id,
    initialX,
    initialY,
    onPositionChange,
    onClick,
    children,
    className = "",
    disabled = false,
    constrainToParent = true,
}: DraggableItemProps) {
    const itemRef = useRef<HTMLDivElement>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [position, setPosition] = useState({ x: initialX, y: initialY });
    const dragStart = useRef({ x: 0, y: 0, posX: 0, posY: 0 });

    // Update position when initialX/Y changes
    useEffect(() => {
        setPosition({ x: initialX, y: initialY });
    }, [initialX, initialY]);

    const handleMouseDown = useCallback((e: React.MouseEvent) => {
        if (disabled) return;
        e.preventDefault();
        e.stopPropagation();

        setIsDragging(true);
        dragStart.current = {
            x: e.clientX,
            y: e.clientY,
            posX: position.x,
            posY: position.y,
        };

        // Add shadow effect
        if (itemRef.current) {
            gsap.to(itemRef.current, { scale: 1.05, boxShadow: "0 10px 30px rgba(0,0,0,0.2)", duration: 0.15 });
        }
    }, [disabled, position]);

    const handleMouseMove = useCallback((e: MouseEvent) => {
        if (!isDragging || !itemRef.current?.parentElement) return;

        const parent = itemRef.current.parentElement;
        const parentRect = parent.getBoundingClientRect();

        const deltaX = e.clientX - dragStart.current.x;
        const deltaY = e.clientY - dragStart.current.y;

        // Convert pixel delta to percentage
        const deltaXPercent = (deltaX / parentRect.width) * 100;
        const deltaYPercent = (deltaY / parentRect.height) * 100;

        let newX = dragStart.current.posX + deltaXPercent;
        let newY = dragStart.current.posY + deltaYPercent;

        // Constrain to parent bounds
        if (constrainToParent) {
            newX = Math.max(0, Math.min(100, newX));
            newY = Math.max(0, Math.min(100, newY));
        }

        setPosition({ x: newX, y: newY });
    }, [isDragging, constrainToParent]);

    const handleMouseUp = useCallback(() => {
        if (!isDragging) return;

        setIsDragging(false);
        onPositionChange?.(id, position.x, position.y);

        // Remove shadow effect
        if (itemRef.current) {
            gsap.to(itemRef.current, { scale: 1, boxShadow: "0 2px 8px rgba(0,0,0,0.1)", duration: 0.15 });
        }
    }, [isDragging, id, position, onPositionChange]);

    const handleClick = useCallback((e: React.MouseEvent) => {
        if (!isDragging) {
            onClick?.();
        }
    }, [isDragging, onClick]);

    // Global mouse events for drag
    useEffect(() => {
        if (isDragging) {
            window.addEventListener("mousemove", handleMouseMove);
            window.addEventListener("mouseup", handleMouseUp);
        }
        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseup", handleMouseUp);
        };
    }, [isDragging, handleMouseMove, handleMouseUp]);

    return (
        <div
            ref={itemRef}
            onMouseDown={handleMouseDown}
            onClick={handleClick}
            style={{
                position: "absolute",
                left: `${position.x}%`,
                top: `${position.y}%`,
                transform: "translate(-50%, -50%)",
                cursor: disabled ? "default" : isDragging ? "grabbing" : "grab",
                zIndex: isDragging ? 100 : 1,
                userSelect: "none",
            }}
            className={`transition-shadow ${className}`}
        >
            {children}
        </div>
    );
}
