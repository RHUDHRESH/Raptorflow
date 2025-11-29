import React, { useState, useRef, useEffect } from 'react';
import { useInView } from 'framer-motion';

const StatCounter = ({ end, duration = 2, suffix = '', prefix = '' }) => {
  const [count, setCount] = useState(0);
  const nodeRef = useRef(null);
  const isInView = useInView(nodeRef, { once: true, amount: 0.5 });

  useEffect(() => {
    if (!isInView) return;

    let startTime = null;
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);

      // Ease out quart
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeOutQuart * end));

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };
    requestAnimationFrame(animate);
  }, [isInView, end, duration]);

  return (
    <span ref={nodeRef} className="tabular-nums font-mono font-bold text-4xl md:text-5xl tracking-tight text-black">
      {prefix}{count.toLocaleString()}{suffix}
    </span>
  );
};

export default StatCounter;
