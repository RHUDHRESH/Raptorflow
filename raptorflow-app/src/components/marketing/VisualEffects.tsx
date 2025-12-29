'use client';

import { useEffect, useRef, ReactNode } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register plugin
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

// ============================================================================
// MORPH SVG PATH - Animated morphing SVG paths
// ============================================================================

interface MorphPathProps {
  paths: string[];
  className?: string;
  duration?: number;
  strokeColor?: string;
  fillColor?: string;
}

export function MorphPath({
  paths,
  className = '',
  duration = 2,
  strokeColor = 'currentColor',
  fillColor = 'none',
}: MorphPathProps) {
  const pathRef = useRef<SVGPathElement>(null);

  useEffect(() => {
    const path = pathRef.current;
    if (!path || paths.length < 2) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    const tl = gsap.timeline({ repeat: -1, yoyo: true });

    paths.slice(1).forEach((targetPath) => {
      tl.to(path, {
        attr: { d: targetPath },
        duration,
        ease: 'power2.inOut',
      });
    });

    return () => {
      tl.kill();
    };
  }, [paths, duration]);

  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      preserveAspectRatio="xMidYMid meet"
    >
      <path
        ref={pathRef}
        d={paths[0]}
        stroke={strokeColor}
        fill={fillColor}
        strokeWidth="0.5"
      />
    </svg>
  );
}

// ============================================================================
// DRAW SVG - SVG path drawing animation
// ============================================================================

interface DrawSVGProps {
  children: ReactNode;
  className?: string;
  duration?: number;
  delay?: number;
}

export function DrawSVG({
  children,
  className = '',
  duration = 2,
  delay = 0,
}: DrawSVGProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    const paths = svg.querySelectorAll(
      'path, line, polyline, polygon, circle, ellipse, rect'
    );

    paths.forEach((path) => {
      const length = (path as SVGGeometryElement).getTotalLength?.() || 1000;
      gsap.set(path, {
        strokeDasharray: length,
        strokeDashoffset: length,
      });
    });

    gsap.to(paths, {
      strokeDashoffset: 0,
      duration,
      delay,
      stagger: 0.2,
      ease: 'power2.inOut',
      scrollTrigger: {
        trigger: svg,
        start: 'top 80%',
      },
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => {
        if (trigger.trigger === svg) {
          trigger.kill();
        }
      });
    };
  }, [duration, delay]);

  return (
    <svg ref={svgRef} className={className}>
      {children}
    </svg>
  );
}

// ============================================================================
// ANIMATED GRADIENT - Moving gradient background
// ============================================================================

interface AnimatedGradientProps {
  className?: string;
  colors?: string[];
  speed?: number;
}

export function AnimatedGradient({
  className = '',
  colors = [
    'hsl(var(--background))',
    'hsl(var(--muted))',
    'hsl(var(--background))',
  ],
  speed = 5,
}: AnimatedGradientProps) {
  const gradientRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = gradientRef.current;
    if (!element) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    gsap.to(element, {
      backgroundPosition: '200% center',
      duration: speed,
      ease: 'none',
      repeat: -1,
    });
  }, [speed]);

  return (
    <div
      ref={gradientRef}
      className={className}
      style={{
        background: `linear-gradient(90deg, ${colors.join(', ')})`,
        backgroundSize: '200% 100%',
      }}
    />
  );
}

// ============================================================================
// PARTICLE FIELD - Animated particles with mouse interaction
// ============================================================================

interface ParticleFieldProps {
  className?: string;
  particleCount?: number;
  connectionDistance?: number;
  mouseInteraction?: boolean;
}

export function ParticleField({
  className = '',
  particleCount = 50,
  connectionDistance = 100,
  mouseInteraction = true,
}: ParticleFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    let animationId: number;
    let mouseX = 0;
    let mouseY = 0;
    let isMouseInCanvas = false;

    // Resize handler
    const resize = () => {
      canvas.width = canvas.offsetWidth * 2;
      canvas.height = canvas.offsetHeight * 2;
      ctx.scale(2, 2);
    };
    resize();
    window.addEventListener('resize', resize);

    // Particles
    interface Particle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
    }

    const particles: Particle[] = Array.from({ length: particleCount }, () => ({
      x: Math.random() * canvas.offsetWidth,
      y: Math.random() * canvas.offsetHeight,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 2 + 1,
    }));

    // Mouse events
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    };
    const handleMouseEnter = () => {
      isMouseInCanvas = true;
    };
    const handleMouseLeave = () => {
      isMouseInCanvas = false;
    };

    if (mouseInteraction) {
      canvas.addEventListener('mousemove', handleMouseMove);
      canvas.addEventListener('mouseenter', handleMouseEnter);
      canvas.addEventListener('mouseleave', handleMouseLeave);
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

      // Get computed color
      const style = getComputedStyle(document.documentElement);
      const fgColor =
        style.getPropertyValue('--foreground').trim() || '45 45 45';
      const [r, g, b] = fgColor.split(' ').map(Number);

      particles.forEach((particle, i) => {
        // Mouse repulsion
        if (mouseInteraction && isMouseInCanvas) {
          const dx = particle.x - mouseX;
          const dy = particle.y - mouseY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 100) {
            const force = (100 - dist) / 100;
            particle.vx += (dx / dist) * force * 0.5;
            particle.vy += (dy / dist) * force * 0.5;
          }
        }

        // Move
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Dampen
        particle.vx *= 0.99;
        particle.vy *= 0.99;

        // Bounce
        if (particle.x < 0 || particle.x > canvas.offsetWidth)
          particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.offsetHeight)
          particle.vy *= -1;

        // Draw particle
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r || 45}, ${g || 45}, ${b || 45}, 0.4)`;
        ctx.fill();

        // Draw connections
        for (let j = i + 1; j < particles.length; j++) {
          const other = particles[j];
          const dx = particle.x - other.x;
          const dy = particle.y - other.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionDistance) {
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(other.x, other.y);
            ctx.strokeStyle = `rgba(${r || 45}, ${g || 45}, ${b || 45}, ${(1 - dist / connectionDistance) * 0.15})`;
            ctx.stroke();
          }
        }
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
      if (mouseInteraction) {
        canvas.removeEventListener('mousemove', handleMouseMove);
        canvas.removeEventListener('mouseenter', handleMouseEnter);
        canvas.removeEventListener('mouseleave', handleMouseLeave);
      }
    };
  }, [particleCount, connectionDistance, mouseInteraction]);

  return <canvas ref={canvasRef} className={`w-full h-full ${className}`} />;
}

// ============================================================================
// WAVE ANIMATION - Animated wave SVG
// ============================================================================

interface WaveProps {
  className?: string;
  color?: string;
  amplitude?: number;
  frequency?: number;
}

export function Wave({
  className = '',
  color = 'currentColor',
  amplitude = 20,
  frequency = 0.02,
}: WaveProps) {
  const pathRef = useRef<SVGPathElement>(null);

  useEffect(() => {
    const path = pathRef.current;
    if (!path) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    let frame = 0;

    const animate = () => {
      const points: string[] = [];
      const width = 1000;
      const height = 100;

      for (let x = 0; x <= width; x += 10) {
        const y =
          height / 2 + Math.sin(x * frequency + frame * 0.02) * amplitude;
        points.push(`${x},${y}`);
      }

      path.setAttribute(
        'd',
        `M0,${height} L${points.join(' L')} L${width},${height} Z`
      );
      frame++;
      requestAnimationFrame(animate);
    };

    const animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [amplitude, frequency]);

  return (
    <svg
      viewBox="0 0 1000 100"
      preserveAspectRatio="none"
      className={className}
    >
      <path ref={pathRef} fill={color} opacity="0.1" />
    </svg>
  );
}

// ============================================================================
// BLOB ANIMATION - Morphing blob shape
// ============================================================================

interface BlobProps {
  className?: string;
  color?: string;
  size?: number;
}

export function Blob({
  className = '',
  color = 'currentColor',
  size = 400,
}: BlobProps) {
  const pathRef = useRef<SVGPathElement>(null);

  useEffect(() => {
    const path = pathRef.current;
    if (!path) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    const generateBlobPath = (time: number) => {
      const points = 6;
      const center = 50;
      const baseRadius = 35;

      let d = '';
      for (let i = 0; i <= points; i++) {
        const angle = (i / points) * Math.PI * 2;
        const wobble = Math.sin(angle * 3 + time * 0.002) * 5;
        const radius = baseRadius + wobble;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius;

        if (i === 0) {
          d = `M ${x} ${y}`;
        } else {
          d += ` Q ${center + Math.cos(angle - 0.3) * (radius + 5)} ${center + Math.sin(angle - 0.3) * (radius + 5)}, ${x} ${y}`;
        }
      }
      d += ' Z';
      return d;
    };

    let animationId: number;
    let time = 0;

    const animate = () => {
      path.setAttribute('d', generateBlobPath(time));
      time += 16;
      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      style={{ width: size, height: size }}
    >
      <path ref={pathRef} fill={color} opacity="0.1" />
    </svg>
  );
}
