"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface AnimatedCounterProps {
  end: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
}

export function AnimatedCounter({
  end,
  duration = 2,
  prefix = "",
  suffix = "",
  className = "",
}: AnimatedCounterProps) {
  const counterRef = useRef<HTMLSpanElement>(null);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    if (!counterRef.current || hasAnimated) return;

    const ctx = gsap.context(() => {
      ScrollTrigger.create({
        trigger: counterRef.current,
        start: "top 85%",
        onEnter: () => {
          if (hasAnimated) return;
          setHasAnimated(true);

          const obj = { value: 0 };
          gsap.to(obj, {
            value: end,
            duration: duration,
            ease: "power2.out",
            onUpdate: () => {
              if (counterRef.current) {
                counterRef.current.textContent =
                  prefix + Math.round(obj.value).toLocaleString() + suffix;
              }
            },
          });
        },
      });
    });

    return () => ctx.revert();
  }, [end, duration, prefix, suffix, hasAnimated]);

  return (
    <span ref={counterRef} className={className}>
      {prefix}0{suffix}
    </span>
  );
}

export default AnimatedCounter;
