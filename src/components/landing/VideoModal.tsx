"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cancel01Icon } from "hugeicons-react";

interface VideoModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function VideoModal({ isOpen, onClose }: VideoModalProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        transition={{ type: "spring", damping: 25, stiffness: 300 }}
                        onClick={(e) => e.stopPropagation()}
                        className="relative w-full max-w-4xl aspect-video bg-[var(--ink)] rounded-2xl overflow-hidden shadow-2xl"
                    >
                        {/* Close Button */}
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                        >
                            {React.createElement(Cancel01Icon as any, { className: "w-5 h-5 text-white" })}
                        </button>

                        {/* Video Placeholder - Replace with actual video embed */}
                        <div className="w-full h-full flex flex-col items-center justify-center text-white">
                            <div className="w-20 h-20 rounded-full bg-[var(--accent)]/20 flex items-center justify-center mb-6">
                                <div className="w-0 h-0 border-t-[12px] border-t-transparent border-l-[20px] border-l-white border-b-[12px] border-b-transparent ml-1" />
                            </div>
                            <h3 className="text-2xl font-editorial mb-2">Product Demo Coming Soon</h3>
                            <p className="text-white/60 text-sm">
                                A 2-minute walkthrough of the RaptorFlow system.
                            </p>

                            {/* Placeholder Video Embed Area */}
                            {/* When you have a video, replace the above with:
                            <iframe 
                                className="w-full h-full"
                                src="https://www.youtube.com/embed/YOUR_VIDEO_ID?autoplay=1"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                            />
                            */}
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
