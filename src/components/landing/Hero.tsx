"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { ArrowRight, Play } from "lucide-react";
import { CompassLogo } from "@/components/compass/CompassLogo";

export function Hero() {
  const router = useRouter();
  const heroRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Animated particle background (coffee steam/smoke effect)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let particles: Array<{
      x: number;
      y: number;
      size: number;
      speedX: number;
      speedY: number;
      opacity: number;
      life: number;
      maxLife: number;
    }> = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const createParticle = () => {
      return {
        x: Math.random() * canvas.width,
        y: canvas.height + 10,
        size: Math.random() * 3 + 1,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: -Math.random() * 1 - 0.5,
        opacity: Math.random() * 0.3 + 0.1,
        life: 0,
        maxLife: Math.random() * 200 + 100,
      };
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Add new particles
      if (particles.length < 50) {
        particles.push(createParticle());
      }

      // Update and draw particles
      particles = particles.filter((particle) => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        particle.life++;

        const lifeRatio = particle.life / particle.maxLife;
        const currentOpacity = particle.opacity * (1 - lifeRatio);

        if (lifeRatio >= 1) return false;

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(150, 117, 83, ${currentOpacity})`;
        ctx.fill();

        return true;
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    resize();
    window.addEventListener("resize", resize);
    animate();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  // GSAP animations
  useEffect(() => {
    if (!contentRef.current) return;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      tl.fromTo(
        ".hero-compass",
        { scale: 0.8, opacity: 0 },
        { scale: 1, opacity: 1, duration: 1.2 }
      )
        .fromTo(
          ".hero-title",
          { y: 40, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.8 },
          "-=0.6"
        )
        .fromTo(
          ".hero-subtitle",
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.8 },
          "-=0.5"
        )
        .fromTo(
          ".hero-cta",
          { y: 20, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, stagger: 0.1 },
          "-=0.4"
        )
        .fromTo(
          ".hero-scroll",
          { opacity: 0 },
          { opacity: 1, duration: 0.6 },
          "-=0.2"
        );
    }, contentRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[var(--bg-primary)] via-[var(--bg-secondary)] to-[var(--bg-primary)]" />

      {/* Animated particle canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{ mixBlendMode: "multiply" }}
      />

      {/* Subtle radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[var(--accent)]/5 rounded-full blur-3xl pointer-events-none" />

      {/* Content */}
      <div
        ref={contentRef}
        className="relative z-10 max-w-5xl mx-auto px-6 text-center pt-20"
      >
        {/* Compass Logo */}
        <div className="hero-compass flex justify-center mb-8">
          <CompassLogo size={140} variant="default" animate={true} />
        </div>

        {/* Headline */}
        <h1 className="hero-title font-display text-5xl md:text-7xl lg:text-8xl font-semibold text-[var(--text-primary)] mb-6 leading-tight">
          Navigate Your
          <br />
          <span className="text-[var(--accent)]">Marketing</span>
        </h1>

        {/* Subtitle */}
        <p className="hero-subtitle text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed">
          The artisanal marketing operating system for founders who demand
          precision. From strategy to execution—chart your course to growth.
        </p>

        {/* CTAs */}
        <div className="hero-cta flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <button
            onClick={() => router.push("/signup")}
            className="group magnetic-button px-8 py-4 bg-[var(--accent)] text-white font-medium rounded-full hover:bg-[var(--accent-dark)] transition-all flex items-center gap-2"
          >
            Start Free Trial
            <ArrowRight
              size={18}
              className="group-hover:translate-x-1 transition-transform"
            />
          </button>
          <button
            onClick={() => router.push("#demo")}
            className="group magnetic-button px-8 py-4 border border-[var(--border-strong)] text-[var(--text-primary)] font-medium rounded-full hover:bg-[var(--bg-secondary)] transition-all flex items-center gap-2"
          >
            <Play size={18} className="text-[var(--accent)]" />
            Watch Demo
          </button>
        </div>

        {/* Social proof / stats */}
        <div className="hero-cta grid grid-cols-3 gap-8 max-w-lg mx-auto pt-8 border-t border-[var(--border)]">
          <div className="text-center">
            <div className="font-display text-3xl font-semibold text-[var(--text-primary)]">
              4
            </div>
            <div className="text-sm text-[var(--text-muted)] mt-1">
              Core Pillars
            </div>
          </div>
          <div className="text-center">
            <div className="font-display text-3xl font-semibold text-[var(--text-primary)]">
              AI
            </div>
            <div className="text-sm text-[var(--text-muted)] mt-1">
              Powered
            </div>
          </div>
          <div className="text-center">
            <div className="font-display text-3xl font-semibold text-[var(--text-primary)]">
              ∞
            </div>
            <div className="text-sm text-[var(--text-muted)] mt-1">
              Possibilities
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="hero-scroll absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-[var(--text-muted)]">
          <span className="text-xs font-medium tracking-widest uppercase">
            Scroll
          </span>
          <div className="w-6 h-10 border-2 border-[var(--border-strong)] rounded-full flex justify-center pt-2">
            <div className="w-1.5 h-1.5 bg-[var(--accent)] rounded-full animate-bounce" />
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
