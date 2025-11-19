"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";
import { IMAGES } from "@/lib/images";

export function LiquidMetalBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Liquid metal animation
    let animationId: number;
    let time = 0;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Create flowing liquid metal effect
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, `rgba(139, 124, 249, ${0.1 + Math.sin(time * 0.001) * 0.05})`);
      gradient.addColorStop(0.5, `rgba(52, 211, 153, ${0.05 + Math.cos(time * 0.0015) * 0.03})`);
      gradient.addColorStop(1, `rgba(139, 124, 249, ${0.08 + Math.sin(time * 0.002) * 0.04})`);

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Add flowing waves
      for (let i = 0; i < 3; i++) {
        ctx.beginPath();
        ctx.moveTo(0, canvas.height / 2);
        
        for (let x = 0; x < canvas.width; x += 10) {
          const y =
            canvas.height / 2 +
            Math.sin((x * 0.01 + time * 0.0005 + i * 2) * Math.PI) * 50 +
            Math.cos((x * 0.005 + time * 0.0003) * Math.PI) * 30;
          ctx.lineTo(x, y);
        }
        
        ctx.lineTo(canvas.width, canvas.height);
        ctx.lineTo(0, canvas.height);
        ctx.closePath();
        
        ctx.fillStyle = `rgba(139, 124, 249, ${0.03 + i * 0.01})`;
        ctx.fill();
      }

      time += 16; // ~60fps
      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <div className="fixed inset-0 z-0">
      {/* Background image */}
      <div className="absolute inset-0">
        <Image
          src={IMAGES.heroBackground.src}
          alt={IMAGES.heroBackground.alt}
          fill
          className="object-cover"
          priority
          quality={90}
        />
      </div>
      
      {/* Animated liquid metal overlay */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 mix-blend-soft-light"
      />
      
      {/* Dark overlay for depth */}
      <div className="absolute inset-0 bg-rf-bg/60" />
    </div>
  );
}

