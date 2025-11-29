import React from 'react';
import { motion } from 'framer-motion';

const GradientBackground = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] rounded-full bg-purple-500/20 blur-[120px]"
        animate={{
          x: [0, 50, 0],
          y: [0, 30, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] rounded-full bg-blue-500/20 blur-[120px]"
        animate={{
          x: [0, -30, 0],
          y: [0, -50, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2
        }}
      />
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03]" />
    </div>
  );
};

export default GradientBackground;
