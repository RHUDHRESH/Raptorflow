'use client';

import { useEffect, useRef } from 'react';
import Link from 'next/link';
import gsap from 'gsap';
import { motion } from 'motion/react';

export function FoundationStudioHero() {
    const containerRef = useRef<HTMLDivElement>(null);
    const titleRef = useRef<HTMLHeadingElement>(null);
    const subtitleRef = useRef<HTMLParagraphElement>(null);
    const ctaContainerRef = useRef<HTMLDivElement>(null);
    const particlesRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        // Set initial states
        gsap.set(titleRef.current, { opacity: 0, y: 40 });
        gsap.set(subtitleRef.current, { opacity: 0, y: 30 });
        gsap.set(ctaContainerRef.current, { opacity: 0, y: 20 });

        // Animate in sequence
        tl.to(titleRef.current, { opacity: 1, y: 0, duration: 1.0 }, 0.3)
            .to(subtitleRef.current, { opacity: 1, y: 0, duration: 0.8 }, 0.6)
            .to(ctaContainerRef.current, { opacity: 1, y: 0, duration: 0.6 }, 0.9);

        return () => { tl.kill(); };
    }, []);

    return (
        <div
            ref={containerRef}
            className="relative h-full flex items-center justify-center"
        >
            {/* Ambient Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {/* Subtle gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-gray-50/50" />

                {/* Floating particles */}
                <div ref={particlesRef} className="absolute inset-0">
                    {Array.from({ length: 25 }).map((_, i) => (
                        <div
                            key={i}
                            className="absolute rounded-full bg-gray-200/30"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                width: `${2 + Math.random() * 3}px`,
                                height: `${2 + Math.random() * 3}px`,
                                animation: `subtleFloat ${10 + Math.random() * 15}s ease-in-out infinite`,
                                animationDelay: `${Math.random() * 8}s`,
                            }}
                        />
                    ))}
                </div>

                {/* Background accent circles */}
                <div className="absolute top-20 right-20 w-96 h-96 bg-gray-100/20 rounded-full blur-3xl" />
                <div className="absolute bottom-20 left-20 w-80 h-80 bg-gray-100/15 rounded-full blur-3xl" />
            </div>

            {/* Main Content */}
            <div className="relative z-10 max-w-4xl mx-auto px-8 text-center">
                {/* Logo/Brand Area */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="mb-12"
                >
                    <div className="inline-flex items-center gap-3 px-4 py-2 bg-gray-100 rounded-full border border-gray-200">
                        <div className="w-4 h-4 bg-gray-900 rounded-sm" />
                        <span className="text-[11px] font-mono uppercase tracking-[0.2em] text-gray-600">
                            RAPTORFLOW
                        </span>
                    </div>
                </motion.div>

                {/* Main Title */}
                <h1
                    ref={titleRef}
                    className="text-6xl lg:text-7xl font-playfair font-normal text-gray-900 leading-[1.05] tracking-[-0.03em] mb-8"
                >
                    Marketing.<br />
                    <span className="text-gray-500">Finally under control.</span>
                </h1>

                {/* Subtitle */}
                <p
                    ref={subtitleRef}
                    className="text-xl text-gray-600 leading-relaxed mb-16 max-w-2xl mx-auto font-light"
                >
                    The Founder Marketing Operating System that converts business chaos into strategic clarity,
                    systematic execution, and measurable growth.
                </p>

                {/* CTA Container */}
                <div
                    ref={ctaContainerRef}
                    className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-16"
                >
                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                        <Link href="/foundation">
                            <button className="group inline-flex items-center gap-3 bg-gray-900 text-white px-8 py-4 rounded-2xl font-inter font-medium text-[16px] transition-all duration-300 hover:bg-gray-800 hover:shadow-[0_8px_30px_rgba(0,0,0,0.12)]">
                                <span>Build Foundation</span>
                                <svg className="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                </svg>
                            </button>
                        </Link>
                    </motion.div>

                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                        <Link href="/muse">
                            <button className="group inline-flex items-center gap-3 bg-white text-gray-900 border border-gray-300 px-8 py-4 rounded-2xl font-inter font-medium text-[16px] transition-all duration-300 hover:border-gray-400 hover:shadow-[0_4px_20px_rgba(0,0,0,0.06)]">
                                <span>Try Studio</span>
                                <svg className="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                </svg>
                            </button>
                        </Link>
                    </motion.div>
                </div>

                {/* Trust Indicators */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1.0, delay: 1.2 }}
                    className="flex items-center justify-center gap-8 text-sm text-gray-400"
                >
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        <span>Live</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <span>500+ Founders</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        <span>2.5s Response</span>
                    </div>
                </motion.div>
            </div>

            {/* Floating animation keyframes */}
            <style jsx>{`
                @keyframes subtleFloat {
                    0%, 100% { transform: translateY(0) translateX(0); }
                    25% { transform: translateY(-12px) translateX(6px); }
                    50% { transform: translateY(-6px) translateX(-3px); }
                    75% { transform: translateY(-18px) translateX(3px); }
                }
            `}</style>
        </div>
    );
}
