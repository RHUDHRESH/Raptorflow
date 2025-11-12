"use client";

import { useEffect, useState } from "react";

interface TextRotateProps {
  phrases: string[];
  interval?: number;
  className?: string;
}

export function TextRotate({ phrases, interval = 3000, className = "" }: TextRotateProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (phrases.length === 0) return;

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % phrases.length);
    }, interval);

    return () => clearInterval(timer);
  }, [phrases.length, interval]);

  return (
    <span className={className} key={currentIndex}>
      {phrases[currentIndex]}
    </span>
  );
}

