"use client";

import React, { useRef, useEffect, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/dist/ScrollTrigger";
import "./the-triptych.css";

// ═══════════════════════════════════════════════════════════════
// THE DIGITAL ODYSSEY
// ═══════════════════════════════════════════════════════════════

export default function TheTriptych() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [activeAct, setActiveAct] = useState(1);
    const [bgImage, setBgImage] = useState<HTMLImageElement | null>(null);

    // Load Asset
    useEffect(() => {
        const img = new Image();
        img.src = "/assets/sci_fi_gyroscope_compass.png";
        img.onload = () => setBgImage(img);
    }, []);

    useEffect(() => {
        if (typeof window === "undefined") return;
        gsap.registerPlugin(ScrollTrigger);

        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let width = window.innerWidth;
        let height = window.innerHeight;

        // STATE
        // Progress 0-3 covering all acts
        const state = {
            progress: 0,
            rotation: 0,
        };

        // PARALLAX STARS (3 Layers for Depth)
        const createStars = (count: number, speed: number) => {
            const arr = [];
            for (let i = 0; i < count; i++) {
                arr.push({
                    x: (Math.random() - 0.5) * width * 2,
                    y: (Math.random() - 0.5) * height * 2,
                    z: Math.random() * width,
                    speedMod: speed
                });
            }
            return arr;
        };

        // Create initial stars, will be repopulated on resize ideally but fine for now
        const starLayers = [
            { id: 'far', stars: createStars(400, 0.5), size: 1, alpha: 0.5 },
            { id: 'mid', stars: createStars(200, 1.0), size: 2, alpha: 0.8 },
            { id: 'near', stars: createStars(50, 2.0), size: 3, alpha: 1.0 }
        ];

        // RESIZE
        const resize = () => {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        };
        window.addEventListener("resize", resize);
        resize();

        // SCROLL
        const scrollAnim = gsap.to(state, {
            progress: 3,
            ease: "none",
            scrollTrigger: {
                trigger: containerRef.current,
                start: "top top",
                end: "bottom bottom",
                scrub: 0.5,
                onUpdate: (self) => {
                    const p = self.progress;
                    // Precise triggers for text state
                    if (p < 0.33) setActiveAct(1);
                    else if (p < 0.66) setActiveAct(2);
                    else setActiveAct(3);
                }
            }
        });

        // RENDER LOOP
        const render = () => {
            // Clear & Void
            ctx.fillStyle = "#050505";
            ctx.fillRect(0, 0, width, height);

            const centerX = width / 2;
            const centerY = height / 2;

            // DRAW STARS (Parallax)
            // Driven by Scroll Progress AND minimal drift
            const warpFactor = Math.max(0, (state.progress - 2.2) * 5); // Act 3 Warp
            const flySpeed = 0.5 + (state.progress * 5) + (warpFactor * 50);

            starLayers.forEach(layer => {
                ctx.fillStyle = "white";
                layer.stars.forEach(star => {
                    // Move Z
                    star.z -= flySpeed * layer.speedMod;
                    if (star.z <= 1) {
                        star.z += width;
                        star.x = (Math.random() - 0.5) * width * 2;
                        star.y = (Math.random() - 0.5) * height * 2;
                    }

                    const k = width / star.z; // Projection
                    const x = centerX + star.x * k;
                    const y = centerY + star.y * k;

                    if (x > 0 && x < width && y > 0 && y < height) {
                        const size = (1 - star.z / width) * layer.size;
                        const alpha = (1 - star.z / width) * layer.alpha;

                        if (warpFactor > 0.1) {
                            // WARP LINES
                            const len = size * warpFactor * 30;
                            // Angle from center
                            const angle = Math.atan2(y - centerY, x - centerX);
                            // Draw line radiating OUT
                            ctx.beginPath();
                            ctx.moveTo(x, y);
                            ctx.lineTo(x + Math.cos(angle) * len, y + Math.sin(angle) * len);
                            ctx.strokeStyle = `rgba(204, 255, 0, ${alpha * 0.8})`;
                            ctx.lineWidth = size * Math.min(1, warpFactor);
                            ctx.stroke();
                        } else {
                            // DOTS
                            ctx.globalAlpha = alpha;
                            ctx.fillRect(x, y, size, size);
                            ctx.globalAlpha = 1.0;
                        }
                    }
                });
            });


            // DRAW ACT 1: THE ARTIFACT
            // Fades out as we move from 0.0 to 1.0
            const act1Alpha = Math.max(0, Math.min(1, 1.2 - state.progress * 1.5));
            if (act1Alpha > 0 && bgImage) {
                state.rotation += 0.0005; // Cinematic slow rotation

                const imgSize = Math.min(width, height) * 0.85;

                ctx.save();
                ctx.translate(centerX, centerY);
                ctx.rotate(state.rotation);
                ctx.globalAlpha = act1Alpha;
                ctx.drawImage(bgImage, -imgSize / 2, -imgSize / 2, imgSize, imgSize);
                ctx.restore();
            }

            // ACT 2: CONSTELLATION GRID
            // A subtle vector grid overlay appearing in Act 2
            const act2Alpha = Math.max(0, Math.min(1, 1 - Math.abs(1.5 - state.progress)));
            if (act2Alpha > 0.1) {
                const gridSize = 150;
                // Move Grid with progress
                const gridY = (state.progress * 200) % gridSize;

                ctx.beginPath();
                ctx.strokeStyle = `rgba(255, 255, 255, ${0.08 * act2Alpha})`;
                ctx.lineWidth = 1;

                // Vertical Lines
                for (let x = 0; x < width; x += gridSize) {
                    ctx.moveTo(x, 0); ctx.lineTo(x, height);
                }
                // Moving horizontal lines
                for (let y = 0; y < height; y += gridSize) {
                    const gy = y + gridY;
                    if (gy < height) {
                        ctx.moveTo(0, gy); ctx.lineTo(width, gy);
                    }
                }
                ctx.stroke();
            }

            requestAnimationFrame(render);
        };
        const raf = requestAnimationFrame(render);

        return () => {
            window.removeEventListener("resize", resize);
            cancelAnimationFrame(raf);
            scrollAnim.kill();
        };
    }, [bgImage]);

    return (
        <section className="triptych-section h-[400vh]">
            <div ref={containerRef} className="absolute top-0 left-0 w-full h-full pointer-events-none" />

            <div className="act-sticky-view">
                <canvas ref={canvasRef} className="act-full-bg-canvas" />

                {/*
                    QUADRANT LAYOUT SYSTEM
                    - Act 1: Bottom Left
                    - Act 2: Top Right
                    - Act 3: Center Center
                */}

                {/* Act 1 */}
                <div className={`act-text-layer md:justify-start md:items-end items-end justify-start ${activeAct === 1 ? 'active' : ''}`}>
                    <div className="act-content-overlay text-left">
                        <div className="module-label-title mb-4">Mechanism 01</div>
                        <h2 className="act-headline-hero">
                            True<br />North.
                        </h2>
                        <p className="act-subtext-hero">
                            The Compass ensures you never drift.<br />
                            Orientation is the precursor to velocity.
                        </p>
                    </div>
                </div>

                {/* Act 2 */}
                <div className={`act-text-layer md:justify-end md:items-start items-start justify-end ${activeAct === 2 ? 'active' : ''}`}>
                    <div className="act-content-overlay text-right">
                        <div className="module-label-title mb-4 ml-auto">Mechanism 02</div>
                        <h2 className="act-headline-hero">
                            Total<br />Vision.
                        </h2>
                        <p className="act-subtext-hero ml-auto">
                            We map the chaos into a coherent grid.<br />
                            Every data point accounted for.
                        </p>
                    </div>
                </div>

                {/* Act 3 */}
                <div className={`act-text-layer justify-center items-center ${activeAct === 3 ? 'active' : ''}`}>
                    <div className="act-content-overlay text-center" style={{ backdropFilter: 'blur(10px)', background: 'radial-gradient(circle, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 70%)' }}>
                        <div className="module-label-title mb-4 mx-auto">Mechanism 03</div>
                        <h2 className="act-headline-hero text-[var(--neon-accent)]">
                            Light<br />Speed.
                        </h2>
                        <p className="act-subtext-hero mx-auto">
                            Execution without friction.<br />
                            Scale at the speed of thought.
                        </p>
                    </div>
                </div>

            </div>
        </section>
    );
}
