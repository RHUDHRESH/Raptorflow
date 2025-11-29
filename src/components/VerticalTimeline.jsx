import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const VerticalTimeline = ({ steps }) => {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });

  const scaleY = useTransform(scrollYProgress, [0, 1], [0, 1]);

  return (
    <div ref={containerRef} className="relative max-w-3xl mx-auto pl-8 md:pl-0">
      {/* Vertical Line */}
      <div className="absolute left-4 md:left-1/2 top-0 bottom-0 w-0.5 bg-gray-200 -translate-x-1/2">
        <motion.div 
          style={{ scaleY, transformOrigin: "top" }} 
          className="absolute top-0 left-0 w-full h-full bg-black"
        />
      </div>

      <div className="space-y-12 relative">
        {steps.map((step, index) => (
          <TimelineItem key={index} step={step} index={index} />
        ))}
      </div>
    </div>
  );
};

const TimelineItem = ({ step, index }) => {
  const isEven = index % 2 === 0;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className={`relative flex items-center ${isEven ? 'md:flex-row' : 'md:flex-row-reverse'}`}
    >
      {/* Dot */}
      <div className="absolute left-4 md:left-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-white border-4 border-black z-10" />

      {/* Content */}
      <div className={`ml-12 md:ml-0 md:w-1/2 ${isEven ? 'md:pr-12 md:text-right' : 'md:pl-12 md:text-left'}`}>
        <div className="bg-white p-6 rounded-xl border border-black/5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-baseline gap-2 mb-2 justify-start md:justify-end">
             {isEven ? (
                <>
                  <h3 className="text-xl font-bold font-serif">{step.day}</h3>
                  <span className="text-xs font-mono uppercase tracking-wider text-gray-500">{step.label}</span>
                </>
             ) : (
                <>
                  <h3 className="text-xl font-bold font-serif">{step.day}</h3>
                  <span className="text-xs font-mono uppercase tracking-wider text-gray-500">{step.label}</span>
                </>
             )}
          </div>
          <p className="text-gray-600 text-sm leading-relaxed">{step.desc}</p>
        </div>
      </div>
      
      {/* Spacer for opposite side */}
      <div className="hidden md:block md:w-1/2" />
    </motion.div>
  );
};

export default VerticalTimeline;
