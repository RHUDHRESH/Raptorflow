"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { ArrowRight, Play } from "lucide-react";
import { LottieCompass } from "@/components/effects/LottieCompass";
import { MagneticButton } from "@/components/effects/MagneticButton";
import { WordReveal } from "@/components/effects/TextReveal";
import { RevealOnScroll } from "@/components/effects/RevealOnScroll";
import { FloatingElement } from "@/components/effects/FloatingElements";

export function EnhancedHero() {
  const router = useRouter();
  const heroRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Steam/smoke particle effect
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
        y: canvas.height + 20,
        size: Math.random() * 80 + 40,
        speedX: (Math.random() - 0.5) * 0.3,
        speedY: -Math.random() * 0.8 - 0.3,
        opacity: 0,
        life: 0,
        maxLife: Math.random() * 400 + 200,
      };
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (particles.length < 25) {
        particles.push(createParticle());
      }

      particles = particles.filter((particle) => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        particle.life++;

        const lifeRatio = particle.life / particle.maxLife;

        // Fade in then fade out
        if (lifeRatio < 0.1) {
          particle.opacity = lifeRatio * 10 * 0.15;
        } else if (lifeRatio > 0.7) {
          particle.opacity = (1 - lifeRatio) * 3.3 * 0.15;
        } else {
          particle.opacity = 0.15;
        }

        if (lifeRatio >= 1) return false;

        const gradient = ctx.createRadialGradient(
          particle.x,
          particle.y,
          0,
          particle.x,
          particle.y,
          particle.size
        );
        gradient.addColorStop(0, `rgba(150, 117, 83, ${particle.opacity})`);
        gradient.addColorStop(0.5, `rgba(150, 117, 83, ${particle.opacity * 0.5})`);
        gradient.addColorStop(1, "rgba(150, 117, 83, 0)");

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
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

  // GSAP entrance animations
  useEffect(() => {
    if (!heroRef.current) return;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      tl.fromTo(
        ".hero-badge",
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6 }
      )
        .fromTo(
          ".hero-compass",
          { scale: 0.5, opacity: 0, rotation: -45 },
          { scale: 1, opacity: 1, rotation: 0, duration: 1.2, ease: "elastic.out(1, 0.5)" },
          "-=0.3"
        )
        .fromTo(
          ".hero-title-word",
          { y: 80, opacity: 0, rotateX: -90 },
          { y: 0, opacity: 1, rotateX: 0, duration: 0.8, stagger: 0.1 },
          "-=0.6"
        )
        .fromTo(
          ".hero-subtitle",
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.8 },
          "-=0.4"
        )
        .fromTo(
          ".hero-cta",
          { y: 20, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, stagger: 0.1 },
          "-=0.4"
        )
        .fromTo(
          ".hero-stats",
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6 },
          "-=0.2"
        );
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[var(--bg-primary)] via-[var(--bg-secondary)] to-[var(--bg-primary)]" />

      {/* Animated steam/smoke particles */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{ mixBlendMode: "soft-light" }}
      />

      {/* Subtle radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-[var(--accent)]/5 rounded-full blur-3xl pointer-events-none animate-pulse-subtle" />

      {/* Floating decorative elements */}
      <FloatingElement amplitude={15} duration={4} delay={0} className="absolute top-20 left-[10%] opacity-20">
        <div className="w-2 h-2 rounded-full bg-[var(--accent)]" />
      </FloatingElement>
      <FloatingElement amplitude={20} duration={5} delay={1} className="absolute top-40 right-[15%] opacity-20">
        <div className="w-3 h-3 rounded-full bg-[var(--accent)]" />
      </FloatingElement>
      <FloatingElement amplitude={10} duration={3} delay={2} className="absolute bottom-40 left-[20%] opacity-15">
        <div className="w-2 h-2 rounded-full bg-[var(--accent)]" />
      </FloatingElement>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center pt-20">
        {/* Badge */}
        <div className="hero-badge inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-full mb-8">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm font-medium text-[var(--text-secondary)]">
            Now with Gemini 2.0 AI
          </span>
        </div>

        {/* Animated Compass */}
        <div className="hero-compass flex justify-center mb-8">
          <LottieCompass size={180} autoplay loop />
        </div>

        {/* Headline with character animation */}
        <h1 className="font-display text-5xl md:text-7xl lg:text-8xl font-semibold text-[var(--text-primary)] mb-6 leading-tight" style={{ perspective: "1000px" }}>
          <span className="hero-title-word inline-block overflow-hidden">
            <span className="inline-block">Navigate</span>
          </span>{" "}
          <span className="hero-title-word inline-block overflow-hidden">
            <span className="inline-block">Your</span>
          </span>
          <br />
          <span className="hero-title-word inline-block overflow-hidden text-[var(--accent)]">
            <span className="inline-block">Marketing</span>
          </span>
        </h1>

        {/* Subtitle */}
        <p className="hero-subtitle text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed">
          The artisanal marketing operating system for founders who demand
          precision. From strategy to execution—chart your course to growth.
        </p>

        {/* CTAs with magnetic effect */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <MagneticButton
            strength={0.3}
            onClick={() => router.push("/signup")}
            className="group px-8 py-4 bg-[var(--accent)] text-white font-medium rounded-full hover:bg-[var(--accent-dark)] transition-colors flex items-center gap-2"
          >
            Start Free Trial
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </MagneticButton>
          <MagneticButton
            strength={0.3}
            onClick={() => router.push("#demo")}
            className="group px-8 py-4 border border-[var(--border-strong)] text-[var(--text-primary)] font-medium rounded-full hover:bg-[var(--bg-secondary)] transition-colors flex items-center gap-2"
          >
            <Play size={18} className="text-[var(--accent)]" />
            Watch Demo
          </MagneticButton>
        </div>

        {/* Stats with reveal animation */}
        <RevealOnScroll animation="fadeUp" delay={0.2}>
          <div className="hero-stats grid grid-cols-3 gap-8 max-w-lg mx-auto pt-8 border-t border-[var(--border)]">
            <div className="text-center">
              <div className="font-display text-4xl font-semibold text-[var(--text-primary)]">
                4
              </div>
              <div className="text-sm text-[var(--text-muted)] mt-1">
                Core Pillars
              </div>
            </div>
            <div className="text-center">
              <div className="font-display text-4xl font-semibold text-[var(--text-primary)]">
                AI
              </div>
              <div className="text-sm text-[var(--text-muted)] mt-1">
                Powered
              </div>
            </div>
            <div className="text-center">
              <div className="font-display text-4xl font-semibold text-[var(--text-primary)]">
                ∞
              </div>
              <div className="text-sm text-[var(--text-muted)] mt-1">
                Possibilities
              </div>
            </div>
          </div>
        </RevealOnScroll>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-[var(--text-muted)]">
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

export default EnhancedHero;
