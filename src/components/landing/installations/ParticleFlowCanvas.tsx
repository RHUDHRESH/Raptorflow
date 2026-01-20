"use client";

import React, { useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";

interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    radius: number;
    color: string;
    baseX: number;
    baseY: number;
    density: number;
}

const PARTICLE_COLORS = [
    "rgba(224, 141, 121, 0.6)", // --rf-coral
    "rgba(140, 169, 179, 0.5)", // --rf-ocean
    "rgba(166, 196, 185, 0.5)", // --rf-mint
    "rgba(157, 146, 176, 0.4)", // --rf-violet
    "rgba(156, 175, 152, 0.4)", // --rf-sage
];

export default function ParticleFlowCanvas() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const particlesRef = useRef<Particle[]>([]);
    const mouseRef = useRef({ x: -1000, y: -1000 });
    const animationRef = useRef<number>();

    const initParticles = useCallback((canvas: HTMLCanvasElement) => {
        const particles: Particle[] = [];
        const particleCount = Math.min(80, Math.floor((canvas.width * canvas.height) / 15000));

        for (let i = 0; i < particleCount; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;
            particles.push({
                x,
                y,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                radius: Math.random() * 3 + 1.5,
                color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
                baseX: x,
                baseY: y,
                density: Math.random() * 30 + 10,
            });
        }
        particlesRef.current = particles;
    }, []);

    const animate = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const mouse = mouseRef.current;
        const particles = particlesRef.current;

        // Draw connection lines between nearby particles
        ctx.strokeStyle = "rgba(200, 198, 192, 0.08)";
        ctx.lineWidth = 0.5;
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    ctx.globalAlpha = (1 - distance / 120) * 0.3;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[j].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }

        ctx.globalAlpha = 1;

        // Update and draw particles
        particles.forEach((particle) => {
            // Mouse interaction - gentle attraction
            const dx = mouse.x - particle.x;
            const dy = mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 200 && distance > 0) {
                const force = (200 - distance) / 200;
                const dirX = dx / distance;
                const dirY = dy / distance;
                particle.vx += dirX * force * 0.02;
                particle.vy += dirY * force * 0.02;
            }

            // Gentle sinusoidal drift
            const time = Date.now() * 0.001;
            particle.vx += Math.sin(time + particle.baseX * 0.01) * 0.005;
            particle.vy += Math.cos(time + particle.baseY * 0.01) * 0.005;

            // Apply velocity with damping
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.vx *= 0.98;
            particle.vy *= 0.98;

            // Soft boundary bounce
            if (particle.x < 0 || particle.x > canvas.width) {
                particle.vx *= -0.8;
                particle.x = Math.max(0, Math.min(canvas.width, particle.x));
            }
            if (particle.y < 0 || particle.y > canvas.height) {
                particle.vy *= -0.8;
                particle.y = Math.max(0, Math.min(canvas.height, particle.y));
            }

            // Draw particle with glow
            const gradient = ctx.createRadialGradient(
                particle.x,
                particle.y,
                0,
                particle.x,
                particle.y,
                particle.radius * 3
            );
            gradient.addColorStop(0, particle.color);
            gradient.addColorStop(1, "transparent");

            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius * 3, 0, Math.PI * 2);
            ctx.fillStyle = gradient;
            ctx.fill();

            // Solid core
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            ctx.fillStyle = particle.color;
            ctx.fill();
        });

        animationRef.current = requestAnimationFrame(animate);
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const handleResize = () => {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            initParticles(canvas);
        };

        const handleMouseMove = (e: MouseEvent) => {
            const rect = canvas.getBoundingClientRect();
            mouseRef.current = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top,
            };
        };

        const handleMouseLeave = () => {
            mouseRef.current = { x: -1000, y: -1000 };
        };

        handleResize();
        window.addEventListener("resize", handleResize);
        canvas.addEventListener("mousemove", handleMouseMove);
        canvas.addEventListener("mouseleave", handleMouseLeave);

        animationRef.current = requestAnimationFrame(animate);

        return () => {
            window.removeEventListener("resize", handleResize);
            canvas.removeEventListener("mousemove", handleMouseMove);
            canvas.removeEventListener("mouseleave", handleMouseLeave);
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [animate, initParticles]);

    return (
        <motion.canvas
            ref={canvasRef}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5 }}
            className="absolute inset-0 w-full h-full pointer-events-auto"
            style={{ zIndex: 0 }}
        />
    );
}
