"use client";

import React, { useRef, useEffect, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/dist/ScrollTrigger";
import {
    Target,
    Layers,
    Calendar,
    MessageSquare,
    BarChart3,
    Archive
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import "./six-modules.css";

// Register GSAP plugins
if (typeof window !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
}

// ═══════════════════════════════════════════════════════════════
// MODULE DATA - Enhanced with rich content
// ═══════════════════════════════════════════════════════════════

interface Module {
    id: string;
    name: string;
    tag: string;
    icon: React.ElementType;
    color: string;
    headline: string;
    description: string;
    features: string[];
}

const MODULES: Module[] = [
    {
        id: "foundation",
        name: "Foundation",
        tag: "STRATEGY",
        icon: Target,
        color: "#E08D79",
        headline: "Build your strategic DNA",
        description: "Our 22-step cognitive onboarding extracts your Precision Soundbites, ICP definition, and builds your 90-day war plan in 20 minutes.",
        features: ["ICP Deep Dive", "Brand Positioning", "90-Day Roadmap"],
    },
    {
        id: "cohorts",
        name: "Cohorts",
        tag: "INTELLIGENCE",
        icon: Layers,
        color: "#8CA9B3",
        headline: "Know who converts—and why",
        description: "Segment by behavioral science markers, not demographics. Target with surgical precision and stop wasting budget.",
        features: ["Behavioral Segmentation", "Conversion Scoring", "Audience Insights"],
    },
    {
        id: "moves",
        name: "Moves",
        tag: "EXECUTION",
        icon: Calendar,
        color: "#A6C4B9",
        headline: "Ship every week",
        description: "Ready-to-ship execution packets delivered every Monday. Content drafted. Tasks clear. Just execute.",
        features: ["Weekly Packets", "Task Automation", "Content Queue"],
    },
    {
        id: "muse",
        name: "Muse",
        tag: "CREATION",
        icon: MessageSquare,
        color: "#C4A6B8",
        headline: "Your voice, at scale",
        description: "Generate content that sounds like your specific brand voice, not a generic robot. Scale your ideas without losing authenticity.",
        features: ["Voice Training", "Content Generation", "Multi-Platform"],
    },
    {
        id: "matrix",
        name: "Matrix",
        tag: "ANALYTICS",
        icon: BarChart3,
        color: "#B8C4A6",
        headline: "Signal, not noise",
        description: "The Boardroom View. See what's actually driving pipeline. Cut what isn't. Decide in seconds, not hours.",
        features: ["Pipeline Attribution", "ROI Tracking", "Decision Engine"],
    },
    {
        id: "blackbox",
        name: "Blackbox",
        tag: "MEMORY",
        icon: Archive,
        color: "#A6B8C4",
        headline: "Never lose a learning",
        description: "The Cognitive Spine. Every experiment, every outcome, and every insight preserved forever. Your permanent vault.",
        features: ["Experiment Log", "Pattern Recognition", "Knowledge Base"],
    },
];

// ═══════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════

export default function SixModulesShowcase() {
    const sectionRef = useRef<HTMLElement>(null);
    const headerRef = useRef<HTMLDivElement>(null);
    const cardsRef = useRef<HTMLDivElement>(null);
    const engineRef = useRef<HTMLDivElement>(null);
    const connectionsRef = useRef<SVGSVGElement>(null);

    const [activeModule, setActiveModule] = useState<string | null>(null);
    const [hoveredModule, setHoveredModule] = useState<string | null>(null);

    // GSAP ScrollTrigger Animation
    useEffect(() => {
        if (typeof window === "undefined") return;

        const section = sectionRef.current;
        const header = headerRef.current;
        const cards = cardsRef.current;
        const engine = engineRef.current;
        const connections = connectionsRef.current;

        if (!section || !header || !cards || !engine || !connections) return;

        const ctx = gsap.context(() => {
            // Master timeline with ScrollTrigger
            const tl = gsap.timeline({
                scrollTrigger: {
                    trigger: section,
                    start: "top 75%",
                    end: "top 20%",
                    toggleActions: "play none none reverse",
                }
            });

            // 1. Header fade in
            tl.from(header, {
                y: 60,
                opacity: 0,
                duration: 0.8,
                ease: "power3.out"
            });

            // 2. Cards stagger in
            tl.from(".module-card", {
                y: 80,
                opacity: 0,
                scale: 0.92,
                stagger: {
                    each: 0.12,
                    from: "center"
                },
                duration: 0.7,
                ease: "back.out(1.2)"
            }, "-=0.4");

            // 3. Central engine appears
            tl.from(engine, {
                scale: 0,
                opacity: 0,
                rotation: -90,
                duration: 1,
                ease: "elastic.out(1, 0.6)"
            }, "-=0.5");

            // 4. Draw neural connections
            const paths = connections.querySelectorAll(".neural-path");
            paths.forEach((path) => {
                const pathElement = path as SVGPathElement;
                const length = pathElement.getTotalLength();
                gsap.set(pathElement, {
                    strokeDasharray: length,
                    strokeDashoffset: length
                });
            });

            tl.to(".neural-path", {
                strokeDashoffset: 0,
                duration: 1.2,
                stagger: 0.08,
                ease: "power2.inOut"
            }, "-=0.8");

            // Continuous engine rotation
            gsap.to(".engine-core", {
                rotation: 360,
                duration: 20,
                repeat: -1,
                ease: "none"
            });

            // Pulsing rings
            gsap.to(".engine-ring", {
                scale: 1.15,
                opacity: 0.2,
                duration: 2,
                repeat: -1,
                yoyo: true,
                ease: "power1.inOut",
                stagger: 0.4
            });

        }, section);

        return () => ctx.revert();
    }, []);

    // Get active module data
    const activeModuleData = activeModule
        ? MODULES.find(m => m.id === activeModule)
        : null;

    return (
        <section
            ref={sectionRef}
            id="system"
            className="six-modules-section"
        >
            <div className="six-modules-container">

                {/* Section Header */}
                <div ref={headerRef} className="six-modules-header">
                    <span className="six-modules-eyebrow">The Technical Spine</span>
                    <h2 className="six-modules-title">
                        Six modules.
                        <br />
                        <span className="six-modules-title-muted">One unified engine.</span>
                    </h2>
                    <p className="six-modules-subtitle">
                        Everything you need to go from business context to market domination.
                        No more tool-switching. Marketing, finally under control.
                    </p>
                </div>

                {/* Main Grid Area */}
                <div className="six-modules-grid-wrapper">

                    {/* Neural Connections SVG */}
                    <svg
                        ref={connectionsRef}
                        className="neural-connections-svg"
                        preserveAspectRatio="xMidYMid slice"
                    >
                        <defs>
                            <linearGradient id="neuralGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="rgba(224, 141, 121, 0.6)" />
                                <stop offset="50%" stopColor="rgba(140, 169, 179, 0.4)" />
                                <stop offset="100%" stopColor="rgba(166, 196, 185, 0.6)" />
                            </linearGradient>
                            <filter id="neuralGlow">
                                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                                <feMerge>
                                    <feMergeNode in="coloredBlur" />
                                    <feMergeNode in="SourceGraphic" />
                                </feMerge>
                            </filter>
                        </defs>

                        {/* Connection paths from each card to center */}
                        <path className="neural-path" d="M 15% 25% Q 35% 40%, 50% 50%" />
                        <path className="neural-path" d="M 85% 25% Q 65% 40%, 50% 50%" />
                        <path className="neural-path" d="M 15% 75% Q 35% 60%, 50% 50%" />
                        <path className="neural-path" d="M 85% 75% Q 65% 60%, 50% 50%" />
                        <path className="neural-path" d="M 50% 10% Q 50% 30%, 50% 50%" />
                        <path className="neural-path" d="M 50% 90% Q 50% 70%, 50% 50%" />
                    </svg>

                    {/* Central Engine */}
                    <div ref={engineRef} className="central-engine">
                        <div className="engine-ring engine-ring-1" />
                        <div className="engine-ring engine-ring-2" />
                        <div className="engine-ring engine-ring-3" />
                        <div className="engine-core">
                            <div className="engine-hexagon">
                                <svg viewBox="0 0 100 100" className="hexagon-svg">
                                    <polygon
                                        points="50,3 93,25 93,75 50,97 7,75 7,25"
                                        fill="none"
                                        stroke="url(#neuralGradient)"
                                        strokeWidth="2"
                                    />
                                    <polygon
                                        points="50,20 75,35 75,65 50,80 25,65 25,35"
                                        fill="rgba(224, 141, 121, 0.1)"
                                        stroke="rgba(224, 141, 121, 0.4)"
                                        strokeWidth="1"
                                    />
                                </svg>
                                <span className="engine-label">ENGINE</span>
                            </div>
                        </div>
                    </div>

                    {/* Module Cards Grid */}
                    <div ref={cardsRef} className="module-cards-grid">
                        {MODULES.map((module) => {
                            const Icon = module.icon;
                            const isHovered = hoveredModule === module.id;
                            const isActive = activeModule === module.id;

                            return (
                                <motion.div
                                    key={module.id}
                                    className={`module-card ${isActive ? 'active' : ''} ${isHovered ? 'hovered' : ''}`}
                                    style={{ '--module-color': module.color } as React.CSSProperties}
                                    onMouseEnter={() => setHoveredModule(module.id)}
                                    onMouseLeave={() => setHoveredModule(null)}
                                    onClick={() => setActiveModule(isActive ? null : module.id)}
                                    whileHover={{ y: -8 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    {/* Card Glow Effect */}
                                    <div className="module-card-glow" />

                                    {/* Card Content */}
                                    <div className="module-card-inner">
                                        {/* Tag Badge */}
                                        <span className="module-tag">{module.tag}</span>

                                        {/* Icon + Title */}
                                        <div className="module-header">
                                            <div className="module-icon-wrapper">
                                                <Icon className="module-icon" />
                                            </div>
                                            <h3 className="module-name">{module.name}</h3>
                                        </div>

                                        {/* Headline */}
                                        <p className="module-headline">{module.headline}</p>

                                        {/* Features */}
                                        <div className="module-features">
                                            {module.features.map((feature, i) => (
                                                <span key={i} className="module-feature">{feature}</span>
                                            ))}
                                        </div>

                                        {/* Expand indicator */}
                                        <div className="module-expand-hint">
                                            {isActive ? "Click to collapse" : "Click for details"}
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>
                </div>

                {/* Expanded Detail Panel */}
                <AnimatePresence>
                    {activeModuleData && (
                        <motion.div
                            className="module-detail-panel"
                            initial={{ opacity: 0, y: 30, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 20, scale: 0.98 }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        >
                            <div className="module-detail-inner">
                                <div className="module-detail-header">
                                    <div
                                        className="module-detail-icon"
                                        style={{ background: activeModuleData.color }}
                                    >
                                        {React.createElement(activeModuleData.icon, {
                                            className: "detail-icon"
                                        })}
                                    </div>
                                    <div>
                                        <span className="module-detail-tag">{activeModuleData.tag}</span>
                                        <h4 className="module-detail-name">{activeModuleData.name}</h4>
                                    </div>
                                </div>
                                <p className="module-detail-description">
                                    {activeModuleData.description}
                                </p>
                                <div className="module-detail-features">
                                    {activeModuleData.features.map((feature, i) => (
                                        <div key={i} className="detail-feature">
                                            <span className="detail-feature-bullet">→</span>
                                            {feature}
                                        </div>
                                    ))}
                                </div>
                                <button
                                    className="module-detail-close"
                                    onClick={() => setActiveModule(null)}
                                >
                                    Close
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Status Bar */}
                <motion.div
                    className="modules-status-bar"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.5 }}
                >
                    <span className="status-dot" />
                    <span className="status-text">
                        {MODULES.length} modules unified today
                    </span>
                </motion.div>
            </div>
        </section>
    );
}
