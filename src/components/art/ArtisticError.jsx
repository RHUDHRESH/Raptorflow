import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const ArtisticError = ({ error, resetErrorBoundary, code = 500 }) => {
    return (
        <div className="min-h-screen bg-white text-black flex flex-col items-center justify-center p-8 relative overflow-hidden selection:bg-black selection:text-white">
            {/* Decorative Line */}
            <motion.div
                initial={{ height: 0 }}
                animate={{ height: '100px' }}
                transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                className="w-px bg-black mb-12"
            />

            <div className="max-w-2xl w-full text-center z-10">
                {/* Error Code - Elegant Serif */}
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="font-serif text-xl italic text-gray-500 mb-6"
                >
                    Error {code}
                </motion.p>

                {/* Main Heading - Fashion Editorial Style */}
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="font-serif text-6xl md:text-8xl font-light tracking-tight mb-8 leading-[0.9]"
                >
                    {code === 404 ? "Lost in the Void" : "Temporary Disruption"}
                </motion.h1>

                {/* Message - Clean Sans */}
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="font-sans text-sm md:text-base text-gray-600 max-w-md mx-auto leading-relaxed mb-16 tracking-wide uppercase"
                >
                    {error?.message || "An unexpected error has occurred. Our systems are recalibrating."}
                </motion.p>

                {/* Actions - Minimal Buttons */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-8"
                >
                    <button
                        onClick={resetErrorBoundary}
                        className="group relative px-8 py-3 overflow-hidden"
                    >
                        <span className="relative z-10 font-sans text-xs font-bold uppercase tracking-[0.2em] transition-colors group-hover:text-white">
                            Reload System
                        </span>
                        <div className="absolute inset-0 bg-black transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left ease-out" />
                        <div className="absolute bottom-0 left-0 w-full h-px bg-black group-hover:hidden" />
                    </button>

                    <Link
                        to="/"
                        className="group relative px-8 py-3 overflow-hidden"
                    >
                        <span className="relative z-10 font-sans text-xs font-bold uppercase tracking-[0.2em] transition-colors group-hover:text-white">
                            Return Home
                        </span>
                        <div className="absolute inset-0 bg-black transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left ease-out" />
                        <div className="absolute bottom-0 left-0 w-full h-px bg-black group-hover:hidden" />
                    </Link>
                </motion.div>
            </div>

            {/* Footer - Minimal Signature */}
            <div className="absolute bottom-8 text-center">
                <p className="font-serif italic text-xs text-gray-400">RaptorFlow Strategy Engine</p>
            </div>
        </div>
    );
};

export default ArtisticError;
