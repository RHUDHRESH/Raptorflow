"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface TextRevealProps {
  children: string;
  className?: string;
  delay?: number;
  stagger?: number;
}

export function TextReveal({
  children,
  className = "",
  delay = 0,
  stagger = 0.02,
}: TextRevealProps) {
  const containerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chars = containerRef.current.querySelectorAll(".char");

    const ctx = gsap.context(() => {
      gsap.fromTo(
        chars,
        {
          y: 100,
          opacity: 0,
          rotateX: -90,
        },
        {
          y: 0,
          opacity: 1,
          rotateX: 0,
          duration: 0.8,
          stagger: stagger,
          ease: "power3.out",
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
          delay: delay,
        }
      );
    });

    return () => ctx.revert();
  }, [children, delay, stagger]);

  const characters = children.split("").map((char, index) => (
    <span
      key={index}
      className="char inline-block"
      style={{
        display: char === " " ? "inline" : "inline-block",
        whiteSpace: char === " " ? "pre" : "normal",
      }}
    >
      {char === " " ? "\u00A0" : char}
    </span>
  ));

  return (
    <span
      ref={containerRef}
      className={`inline-block overflow-hidden ${className}`}
      style={{ perspective: "1000px" }}
    >
      {characters}
    </span>
  );
}

interface WordRevealProps {
  children: string;
  className?: string;
  delay?: number;
}

export function WordReveal({
  children,
  className = "",
  delay = 0,
}: WordRevealProps) {
  const containerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const words = containerRef.current.querySelectorAll(".word");

    const ctx = gsap.context(() => {
      gsap.fromTo(
        words,
        {
          y: 60,
          opacity: 0,
        },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          stagger: 0.1,
          ease: "power3.out",
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
          delay: delay,
        }
      );
    });

    return () => ctx.revert();
  }, [children, delay]);

  const words = children.split(" ").map((word, index) => (
    <span key={index} className="word inline-block overflow-hidden mr-[0.25em]">
      <span className="inline-block">{word}</span>
    </span>
  ));

  return (
    <span ref={containerRef} className={className}>
      {words}
    </span>
  );
}

export default TextReveal;
