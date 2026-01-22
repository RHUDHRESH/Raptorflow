"use client";

import { useEffect, useRef, useCallback } from "react";
import gsap from "gsap";

// --- Types ---
interface ConfettiPiece {
    x: number;
    y: number;
    rotation: number;
    scale: number;
    color: string;
    velocity: { x: number; y: number };
}

// --- Confetti Colors ---
const COLORS = [
    "#D7C9AE", // Accent tan
    "#4A7C59", // Success green
    "#a67c52", // Darker tan
    "#5B5F61", // Muted
    "#2D3538", // Ink
];

// --- Celebration Hook ---
export function useCelebration() {
    const containerRef = useRef<HTMLDivElement | null>(null);

    const triggerConfetti = useCallback((origin?: { x: number; y: number }) => {
        if (!containerRef.current) {
            // Create container if it doesn't exist
            const div = document.createElement("div");
            div.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:9999;overflow:hidden";
            document.body.appendChild(div);
            containerRef.current = div;
        }

        const container = containerRef.current;
        const centerX = origin?.x ?? window.innerWidth / 2;
        const centerY = origin?.y ?? window.innerHeight / 2;

        // Create confetti pieces
        for (let i = 0; i < 50; i++) {
            const piece = document.createElement("div");
            const color = COLORS[Math.floor(Math.random() * COLORS.length)];
            const size = 8 + Math.random() * 8;
            const isCircle = Math.random() > 0.5;

            piece.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${isCircle ? size : size * 0.6}px;
        background: ${color};
        border-radius: ${isCircle ? "50%" : "2px"};
        left: ${centerX}px;
        top: ${centerY}px;
        transform-origin: center;
      `;

            container.appendChild(piece);

            // Animate
            const angle = (Math.random() * 360) * (Math.PI / 180);
            const velocity = 300 + Math.random() * 400;
            const targetX = Math.cos(angle) * velocity;
            const targetY = Math.sin(angle) * velocity - 200; // Bias upward

            gsap.to(piece, {
                x: targetX,
                y: targetY + 400, // Fall with gravity
                rotation: Math.random() * 720 - 360,
                scale: 0,
                opacity: 0,
                duration: 1.5 + Math.random() * 0.5,
                ease: "power2.out",
                onComplete: () => piece.remove(),
            });
        }

        // Cleanup container after animation
        setTimeout(() => {
            if (container.children.length === 0) {
                container.remove();
                containerRef.current = null;
            }
        }, 2500);
    }, []);

    const triggerSuccess = useCallback((element?: HTMLElement) => {
        if (!element) return;

        // Pulse animation
        gsap.fromTo(
            element,
            { scale: 1 },
            {
                scale: 1.05,
                duration: 0.15,
                ease: "power2.out",
                yoyo: true,
                repeat: 1
            }
        );

        // Add glow effect
        gsap.fromTo(
            element,
            { boxShadow: "0 0 0 rgba(74, 124, 89, 0)" },
            {
                boxShadow: "0 0 30px rgba(74, 124, 89, 0.4)",
                duration: 0.3,
                yoyo: true,
                repeat: 1
            }
        );
    }, []);

    const triggerPhaseComplete = useCallback((phaseName: string) => {
        // Create overlay
        const overlay = document.createElement("div");
        overlay.style.cssText = `
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9998;
      pointer-events: none;
    `;

        const content = document.createElement("div");
        content.innerHTML = `
      <div style="
        background: white;
        padding: 32px 48px;
        border-radius: 20px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        text-align: center;
      ">
        <div style="
          width: 64px;
          height: 64px;
          background: linear-gradient(135deg, #4A7C59, #5a9c6d);
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 16px;
        ">
          <svg width="32" height="32" fill="white" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
          </svg>
        </div>
        <h2 style="font-family: serif; font-size: 24px; color: #2D3538; margin-bottom: 8px;">
          Phase Complete!
        </h2>
        <p style="font-size: 14px; color: #5B5F61;">
          ${phaseName} finished
        </p>
      </div>
    `;

        overlay.appendChild(content);
        document.body.appendChild(overlay);

        // Animate in with subtle ease
        gsap.fromTo(
            content.firstChild,
            { opacity: 0, y: 12 },
            { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }
        );

        // Animate out after delay
        setTimeout(() => {
            gsap.to(content.firstChild, {
                opacity: 0,
                scale: 0.9,
                y: -20,
                duration: 0.3,
                ease: "power2.in",
                onComplete: () => overlay.remove(),
            });
        }, 2000);
    }, [triggerConfetti]);

    const triggerStepComplete = useCallback((element?: HTMLElement) => {
        if (element) {
            // Quick success pulse
            gsap.fromTo(
                element,
                { backgroundColor: "rgba(74, 124, 89, 0)" },
                {
                    backgroundColor: "rgba(74, 124, 89, 0.1)",
                    duration: 0.3,
                    yoyo: true,
                    repeat: 1
                }
            );
        }
    }, []);

    return {
        triggerConfetti,
        triggerSuccess,
        triggerPhaseComplete,
        triggerStepComplete,
    };
}

// --- Celebration Provider Component ---
export function CelebrationProvider({ children }: { children: React.ReactNode }) {
    return <>{children}</>;
}
