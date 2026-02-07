'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';

interface TypingTextProps {
    messages: string[];
    className?: string;
    speed?: number;
    deleteSpeed?: number;
    pauseDuration?: number;
}

export function TypingText({
    messages,
    className = '',
    speed = 100,
    deleteSpeed = 50,
    pauseDuration = 2000
}: TypingTextProps) {
    const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
    const [currentText, setCurrentText] = useState('');
    const [isDeleting, setIsDeleting] = useState(false);
    const [isPaused, setIsPaused] = useState(false);

    useEffect(() => {
        const currentMessage = messages[currentMessageIndex];

        if (isPaused) {
            const pauseTimeout = setTimeout(() => {
                setIsPaused(false);
                setIsDeleting(true);
            }, pauseDuration);
            return () => clearTimeout(pauseTimeout);
        }

        if (isDeleting) {
            if (currentText.length > 0) {
                const deleteTimeout = setTimeout(() => {
                    setCurrentText(currentText.slice(0, -1));
                }, deleteSpeed);
                return () => clearTimeout(deleteTimeout);
            } else {
                setIsDeleting(false);
                setCurrentMessageIndex((prev) => (prev + 1) % messages.length);
            }
        } else {
            if (currentText.length < currentMessage.length) {
                const typeTimeout = setTimeout(() => {
                    setCurrentText(currentMessage.slice(0, currentText.length + 1));
                }, speed);
                return () => clearTimeout(typeTimeout);
            } else {
                setIsPaused(true);
            }
        }
    }, [currentText, isDeleting, isPaused, currentMessageIndex, messages, speed, deleteSpeed, pauseDuration]);

    return (
        <motion.span
            className={className}
            key={currentText}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.1 }}
        >
            {currentText}
            <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="inline-block ml-1"
            >
                |
            </motion.span>
        </motion.span>
    );
}
