'use client';

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface Particle {
  x: number;
  y: number;
  id: number;
}

export function MouseTrail() {
  const [particles, setParticles] = useState<Particle[]>([]);
  const particleIdRef = useRef(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const newParticle: Particle = {
        x: e.clientX,
        y: e.clientY,
        id: particleIdRef.current++,
      };

      setParticles((prev) => [...prev.slice(-10), newParticle]);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-[9998] hidden lg:block">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute w-2 h-2 rounded-full bg-foreground/10"
          initial={{
            x: particle.x,
            y: particle.y,
            scale: 1,
            opacity: 0.6,
          }}
          animate={{
            scale: 0,
            opacity: 0,
          }}
          transition={{
            duration: 0.6,
            ease: 'easeOut',
          }}
          style={{
            left: 0,
            top: 0,
            transform: `translate(${particle.x}px, ${particle.y}px)`,
          }}
        />
      ))}
    </div>
  );
}