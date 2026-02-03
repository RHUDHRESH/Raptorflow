"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

export function AnimatedCompass() {
  const compassRef = useRef<HTMLDivElement>(null);
  const needleRef = useRef<HTMLDivElement>(null);
  const ring1Ref = useRef<HTMLDivElement>(null);
  const ring2Ref = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (!compassRef.current) return;

    const ctx = gsap.context(() => {
      // Continuous needle animation - seeking north with slight wobble
      gsap.to(needleRef.current, {
        rotation: "+=5",
        duration: 2,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });

      // Outer ring slow rotation
      gsap.to(ring1Ref.current, {
        rotation: 360,
        duration: 60,
        ease: "none",
        repeat: -1,
      });

      // Inner ring counter-rotation
      gsap.to(ring2Ref.current, {
        rotation: -360,
        duration: 45,
        ease: "none",
        repeat: -1,
      });

      // Floating animation for entire compass
      gsap.to(compassRef.current, {
        y: "-=15",
        duration: 3,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });

      // Glow pulse
      gsap.to(".compass-glow", {
        opacity: 0.6,
        scale: 1.1,
        duration: 2,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });
    }, compassRef);

    return () => ctx.revert();
  }, []);

  // Mouse interaction
  useEffect(() => {
    if (!compassRef.current || !needleRef.current) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = compassRef.current!.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
      const degrees = angle * (180 / Math.PI) + 90;

      gsap.to(needleRef.current, {
        rotation: degrees,
        duration: 0.5,
        ease: "power2.out",
      });
    };

    if (isHovered) {
      window.addEventListener("mousemove", handleMouseMove);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [isHovered]);

  return (
    <div
      ref={compassRef}
      className="relative w-[350px] h-[350px] md:w-[450px] md:h-[450px] lg:w-[500px] lg:h-[500px]"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Glow effect */}
      <div className="compass-glow absolute inset-0 rounded-full bg-gradient-to-r from-purple-500/30 to-blue-500/30 blur-3xl opacity-40" />

      {/* Outer decorative ring */}
      <div
        ref={ring1Ref}
        className="absolute inset-0 rounded-full border border-purple-500/20"
        style={{
          background: "conic-gradient(from 0deg, transparent, rgba(147, 51, 234, 0.1), transparent, rgba(59, 130, 246, 0.1), transparent)",
        }}
      >
        {/* Degree markers */}
        {Array.from({ length: 24 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-px bg-white/20 origin-bottom"
            style={{
              height: "50%",
              left: "50%",
              transform: `translateX(-50%) rotate(${i * 15}deg)`,
              transformOrigin: "50% 100%",
            }}
          />
        ))}
      </div>

      {/* Middle ring with ticks */}
      <div
        ref={ring2Ref}
        className="absolute inset-8 rounded-full border border-white/10 bg-gradient-to-br from-white/5 to-transparent backdrop-blur-sm"
      >
        {/* Cardinal direction markers */}
        {["N", "E", "S", "W"].map((dir, i) => (
          <span
            key={dir}
            className={`absolute text-sm font-bold ${
              dir === "N" ? "text-purple-400" : "text-white/40"
            }`}
            style={{
              top: dir === "S" ? "auto" : dir === "N" ? "12px" : "50%",
              bottom: dir === "S" ? "12px" : "auto",
              left: dir === "E" ? "auto" : dir === "W" ? "16px" : "50%",
              right: dir === "E" ? "16px" : "auto",
              transform: dir === "N" || dir === "S" ? "translateX(-50%)" : "translateY(-50%)",
            }}
          >
            {dir}
          </span>
        ))}
      </div>

      {/* Inner face */}
      <div className="absolute inset-16 rounded-full bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/10 backdrop-blur-md flex items-center justify-center">
        {/* Decorative circles */}
        <div className="absolute inset-4 rounded-full border border-white/5" />
        <div className="absolute inset-8 rounded-full border border-white/5" />
        
        {/* Center pivot */}
        <div className="absolute w-6 h-6 rounded-full bg-gradient-to-br from-purple-400 to-blue-400 shadow-lg shadow-purple-500/50 z-20">
          <div className="absolute inset-1 rounded-full bg-white/20" />
        </div>
      </div>

      {/* The Needle */}
      <div
        ref={needleRef}
        className="absolute inset-0 flex items-center justify-center pointer-events-none z-10"
        style={{ transformOrigin: "center center" }}
      >
        {/* North half */}
        <div
          className="absolute top-[15%] left-1/2 -translate-x-1/2 w-4 h-[35%] bg-gradient-to-t from-purple-600 to-purple-400 rounded-full shadow-lg shadow-purple-500/30"
          style={{ clipPath: "polygon(50% 0%, 0% 100%, 100% 100%)" }}
        />
        {/* South half */}
        <div
          className="absolute bottom-[15%] left-1/2 -translate-x-1/2 w-4 h-[35%] bg-gradient-to-b from-white/80 to-white/40 rounded-full"
          style={{ clipPath: "polygon(50% 100%, 0% 0%, 100% 0%)" }}
        />
        
        {/* Needle shine effect */}
        <div className="absolute top-[20%] left-1/2 -translate-x-1/2 w-1 h-[25%] bg-gradient-to-t from-transparent via-white/30 to-transparent" />
      </div>

      {/* Glass reflection overlay */}
      <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-transparent via-white/5 to-transparent pointer-events-none" />

      {/* Hover hint */}
      <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-white/30 text-xs opacity-0 hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
        Hover to guide the needle
      </div>
    </div>
  );
}
