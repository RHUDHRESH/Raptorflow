"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

export function GradientOrbs() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const orbs = containerRef.current.querySelectorAll(".gradient-orb");
    
    orbs.forEach((orb, index) => {
      // Floating animation
      gsap.to(orb, {
        y: "random(-30, 30)",
        x: "random(-20, 20)",
        duration: "random(4, 6)",
        ease: "sine.inOut",
        repeat: -1,
        yoyo: true,
        delay: index * 0.5,
      });

      // Pulsing scale animation
      gsap.to(orb, {
        scale: "random(0.9, 1.1)",
        duration: "random(3, 5)",
        ease: "sine.inOut",
        repeat: -1,
        yoyo: true,
        delay: index * 0.3,
      });
    });

    return () => {
      gsap.killTweensOf(orbs);
    };
  }, []);

  return (
    <div ref={containerRef} className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* Primary Purple Orb - Top Left */}
      <div 
        className="gradient-orb absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full opacity-40"
        style={{
          background: "radial-gradient(circle, rgba(147, 51, 234, 0.6) 0%, rgba(147, 51, 234, 0.2) 40%, transparent 70%)",
          filter: "blur(80px)",
        }}
      />
      
      {/* Secondary Blue Orb - Top Right */}
      <div 
        className="gradient-orb absolute top-20 -right-20 w-[500px] h-[500px] rounded-full opacity-35"
        style={{
          background: "radial-gradient(circle, rgba(59, 130, 246, 0.5) 0%, rgba(59, 130, 246, 0.15) 40%, transparent 70%)",
          filter: "blur(70px)",
        }}
      />
      
      {/* Pink/Magenta Orb - Bottom Left */}
      <div 
        className="gradient-orb absolute bottom-20 -left-20 w-[450px] h-[450px] rounded-full opacity-30"
        style={{
          background: "radial-gradient(circle, rgba(236, 72, 153, 0.5) 0%, rgba(236, 72, 153, 0.1) 40%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />
      
      {/* Cyan Orb - Bottom Right */}
      <div 
        className="gradient-orb absolute -bottom-40 right-1/4 w-[550px] h-[550px] rounded-full opacity-35"
        style={{
          background: "radial-gradient(circle, rgba(6, 182, 212, 0.4) 0%, rgba(6, 182, 212, 0.1) 40%, transparent 70%)",
          filter: "blur(75px)",
        }}
      />
      
      {/* Central Glow */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full opacity-20"
        style={{
          background: "radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, transparent 60%)",
          filter: "blur(100px)",
        }}
      />
    </div>
  );
}
