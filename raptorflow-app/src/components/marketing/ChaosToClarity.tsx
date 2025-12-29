'use client';

import { useEffect, useRef, useState } from 'react';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  targetX?: number;
  targetY?: number;
}

interface TransformationCanvasProps {
  isTransformed: boolean;
}

export function TransformationCanvas({
  isTransformed,
}: TransformationCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);
  const particlesRef = useRef<Particle[]>([]);
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 });

  // Initialize particles
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const updateDimensions = () => {
      const rect = canvas.getBoundingClientRect();
      setDimensions({ width: rect.width, height: rect.height });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);

    // Create particles
    const particleCount = 60;
    particlesRef.current = Array.from({ length: particleCount }, (_, i) => ({
      x: Math.random() * dimensions.width,
      y: Math.random() * dimensions.height,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
      size: Math.random() * 4 + 2,
      opacity: Math.random() * 0.5 + 0.3,
    }));

    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas resolution
    canvas.width = dimensions.width * 2;
    canvas.height = dimensions.height * 2;
    ctx.scale(2, 2);

    // Define organized positions (grid pattern)
    const cols = 6;
    const rows = 5;
    const spacingX = dimensions.width / (cols + 1);
    const spacingY = dimensions.height / (rows + 1);

    const organizedPositions = particlesRef.current.map((_, i) => ({
      x: spacingX * ((i % cols) + 1),
      y: spacingY * ((Math.floor(i / cols) % rows) + 1),
    }));

    const animate = () => {
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);

      // Get computed style for colors
      const style = getComputedStyle(document.documentElement);
      const foregroundColor =
        style.getPropertyValue('--foreground').trim() || '45 45 45';
      const [r, g, b] = foregroundColor.split(' ').map(Number);

      particlesRef.current.forEach((particle, i) => {
        if (isTransformed) {
          // Move towards organized position
          const target = organizedPositions[i];
          const dx = target.x - particle.x;
          const dy = target.y - particle.y;
          particle.x += dx * 0.05;
          particle.y += dy * 0.05;

          // Slow down and stabilize
          particle.vx *= 0.95;
          particle.vy *= 0.95;
        } else {
          // Chaotic movement
          particle.x += particle.vx;
          particle.y += particle.vy;

          // Bounce off edges
          if (particle.x < 0 || particle.x > dimensions.width) {
            particle.vx *= -1;
            particle.x = Math.max(0, Math.min(dimensions.width, particle.x));
          }
          if (particle.y < 0 || particle.y > dimensions.height) {
            particle.vy *= -1;
            particle.y = Math.max(0, Math.min(dimensions.height, particle.y));
          }

          // Random direction changes
          if (Math.random() < 0.02) {
            particle.vx += (Math.random() - 0.5) * 0.5;
            particle.vy += (Math.random() - 0.5) * 0.5;
          }
        }

        // Draw particle
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r || 45}, ${g || 45}, ${b || 45}, ${particle.opacity})`;
        ctx.fill();
      });

      // Draw connections between nearby particles
      const connectionDistance = isTransformed ? spacingX * 1.5 : 80;
      for (let i = 0; i < particlesRef.current.length; i++) {
        for (let j = i + 1; j < particlesRef.current.length; j++) {
          const p1 = particlesRef.current[i];
          const p2 = particlesRef.current[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < connectionDistance) {
            const opacity = isTransformed
              ? 0.15
              : (1 - distance / connectionDistance) * 0.1;

            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(${r || 45}, ${g || 45}, ${b || 45}, ${opacity})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isTransformed, dimensions]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full"
      style={{ width: dimensions.width, height: dimensions.height }}
    />
  );
}

export function ChaosToClarity() {
  const [isTransformed, setIsTransformed] = useState(false);

  return (
    <div className="w-full">
      {/* Canvas Container */}
      <div
        className="relative rounded-2xl overflow-hidden bg-muted/30 border border-border"
        style={{ height: '300px' }}
      >
        <TransformationCanvas isTransformed={isTransformed} />

        {/* Labels */}
        <div className="absolute inset-0 flex items-center justify-between px-8 pointer-events-none">
          <div
            className={`text-center transition-opacity duration-500 ${isTransformed ? 'opacity-30' : 'opacity-100'}`}
          >
            <div className="text-2xl font-display font-medium">Chaos</div>
            <div className="text-sm text-muted-foreground">
              5+ tools, random tactics
            </div>
          </div>
          <div
            className={`text-center transition-opacity duration-500 ${isTransformed ? 'opacity-100' : 'opacity-30'}`}
          >
            <div className="text-2xl font-display font-medium">Clarity</div>
            <div className="text-sm text-muted-foreground">
              1 system, compounding results
            </div>
          </div>
        </div>
      </div>

      {/* Toggle Button */}
      <div className="flex justify-center mt-6">
        <button
          onClick={() => setIsTransformed(!isTransformed)}
          className={`
            px-8 py-4 rounded-xl font-medium text-base transition-all duration-300
            ${
              isTransformed
                ? 'bg-muted text-foreground hover:bg-muted/80'
                : 'bg-foreground text-background hover:bg-foreground/90'
            }
          `}
        >
          {isTransformed ? '← Show the Chaos' : 'Use RaptorFlow →'}
        </button>
      </div>
    </div>
  );
}
