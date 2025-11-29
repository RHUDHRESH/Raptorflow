import React from 'react';
import { motion } from 'framer-motion';

const TrustStrip = ({ logos }) => {
  // Duplicate logos for seamless loop
  const duplicatedLogos = [...logos, ...logos];

  return (
    <div className="w-full overflow-hidden bg-white py-12 border-b border-black/5">
      <div className="mx-auto max-w-7xl px-6">
        <p className="text-center text-xs font-mono uppercase tracking-widest text-gray-400 mb-8">
          Trusted by 200+ teams across India
        </p>
        
        <div className="relative flex overflow-hidden mask-gradient-x">
          <motion.div
            className="flex gap-16 items-center whitespace-nowrap"
            animate={{
              x: [0, -1000], // Adjust based on width
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            {duplicatedLogos.map((logo, index) => (
              <div key={index} className="h-8 w-auto grayscale opacity-50 hover:opacity-100 hover:grayscale-0 transition-all duration-300">
                {/* Replace with actual Image/Icon component if logo is a URL or Component */}
                {typeof logo === 'string' ? (
                  <img src={logo} alt="Company Logo" className="h-full object-contain" />
                ) : (
                  <div className="text-xl font-bold font-serif">{logo}</div>
                )}
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default TrustStrip;
