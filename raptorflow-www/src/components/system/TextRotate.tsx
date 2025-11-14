"use client";

import { useEffect, useState } from "react";

interface TextRotateProps {
  phrases: string[];
  interval?: number;
  className?: string;
}

export function TextRotate({ phrases, interval = 3000, className = "" }: TextRotateProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (phrases.length === 0) return;

    const timer = setInterval(() => {
      setIsVisible(false);
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % phrases.length);
        setIsVisible(true);
      }, 300); // Half of transition duration
    }, interval);

    return () => clearInterval(timer);
  }, [phrases.length, interval]);

  return (
    <span
      className={`transition-opacity duration-300 ${isVisible ? "opacity-100" : "opacity-0"} ${className}`}
    >
      {phrases[currentIndex]}
    </span>
  );
}

