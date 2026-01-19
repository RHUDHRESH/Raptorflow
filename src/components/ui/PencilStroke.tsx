"use client";

import React, { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PENCIL STROKE — SVG Path Animation Component
   A reusable component that draws a pencil/ink stroke around any shape
   ══════════════════════════════════════════════════════════════════════════════ */

interface PencilStrokeProps {
    // Shape
    shape?: "rect" | "circle" | "line";
    width: number;
    height: number;

    // Animation
    animate?: boolean;
    delay?: number;
    duration?: number;

    // Style
    color?: string;
    strokeWidth?: number;
    cornerRadius?: number;

    // State
    active?: boolean;

    className?: string;
}

export function PencilStroke({
    shape = "rect",
    width,
    height,
    animate = true,
    delay = 0,
    duration = 0.6,
    color = "var(--blueprint)",
    strokeWidth = 1.5,
    cornerRadius = 4,
    active = true,
    className,
}: PencilStrokeProps) {
    const pathRef = useRef<SVGRectElement | SVGCircleElement | SVGLineElement>(null);
    const [pathLength, setPathLength] = useState(0);

    useEffect(() => {
        if (pathRef.current && "getTotalLength" in pathRef.current) {
            setPathLength((pathRef.current as SVGGeometryElement).getTotalLength());
        } else {
            // Calculate for rect manually
            setPathLength(2 * (width + height));
        }
    }, [width, height]);

    const animationStyle = animate ? {
        strokeDasharray: pathLength,
        strokeDashoffset: active ? 0 : pathLength,
        transition: `stroke-dashoffset ${duration}s cubic-bezier(0.4, 0, 0.2, 1) ${delay}s`,
    } : {};

    return (
        <svg
            className={cn("absolute inset-0 pointer-events-none overflow-visible", className)}
            width={width}
            height={height}
            style={{ left: -1, top: -1 }}
        >
            {shape === "rect" && (
                <rect
                    ref={pathRef as React.RefObject<SVGRectElement>}
                    x={strokeWidth / 2}
                    y={strokeWidth / 2}
                    width={width - strokeWidth}
                    height={height - strokeWidth}
                    rx={cornerRadius}
                    ry={cornerRadius}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    style={animationStyle}
                />
            )}

            {shape === "circle" && (
                <circle
                    ref={pathRef as React.RefObject<SVGCircleElement>}
                    cx={width / 2}
                    cy={height / 2}
                    r={(Math.min(width, height) - strokeWidth) / 2}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    style={animationStyle}
                />
            )}

            {shape === "line" && (
                <line
                    ref={pathRef as React.RefObject<SVGLineElement>}
                    x1={0}
                    y1={height / 2}
                    x2={width}
                    y2={height / 2}
                    stroke={color}
                    strokeWidth={strokeWidth}
                    style={animationStyle}
                />
            )}
        </svg>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   PENCIL UNDERLINE — Animated underline for text
   ══════════════════════════════════════════════════════════════════════════════ */

interface PencilUnderlineProps {
    width?: number | string;
    color?: string;
    strokeWidth?: number;
    delay?: number;
    active?: boolean;
    className?: string;
}

export function PencilUnderline({
    width = "100%",
    color = "var(--blueprint)",
    strokeWidth = 2,
    delay = 0,
    active = true,
    className,
}: PencilUnderlineProps) {
    return (
        <svg
            className={cn("pointer-events-none", className)}
            width={width}
            height={strokeWidth + 2}
            style={{ display: "block" }}
        >
            <line
                x1={0}
                y1={strokeWidth / 2 + 1}
                x2="100%"
                y2={strokeWidth / 2 + 1}
                stroke={color}
                strokeWidth={strokeWidth}
                strokeLinecap="round"
                style={{
                    strokeDasharray: 1000,
                    strokeDashoffset: active ? 0 : 1000,
                    transition: `stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${delay}s`,
                }}
            />
        </svg>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   PENCIL BORDER — Wrapper that adds pencil stroke to children
   ══════════════════════════════════════════════════════════════════════════════ */

interface PencilBorderProps {
    children: React.ReactNode;
    active?: boolean;
    color?: string;
    className?: string;
}

export function PencilBorder({
    children,
    active = false,
    color = "var(--blueprint)",
    className,
}: PencilBorderProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    useEffect(() => {
        if (!containerRef.current) return;

        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                const { width, height } = entry.contentRect;
                setDimensions({ width: width + 2, height: height + 2 });
            }
        });

        observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);

    return (
        <div ref={containerRef} className={cn("relative", className)}>
            {dimensions.width > 0 && (
                <PencilStroke
                    width={dimensions.width}
                    height={dimensions.height}
                    active={active}
                    color={color}
                />
            )}
            {children}
        </div>
    );
}

export default PencilStroke;
