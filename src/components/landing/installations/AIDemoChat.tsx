"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

interface Message {
    role: "user" | "ai";
    content: string;
}

const AI_RESPONSES: Record<string, string> = {
    // Greetings
    "hi": "Hey there! 👋 I'm Muse, RaptorFlow's AI. How can I help you today?",
    "hello": "Hello! Welcome to RaptorFlow. What would you like to know?",
    "hey": "Hey! 🚀 Ready to transform your marketing? Ask me anything!",

    // Product questions
    "what is raptorflow": "RaptorFlow is the first operating system for founder-led marketing. We connect strategy, content, and execution in one unified workflow. No more tool sprawl!",
    "how does it work": "It's simple: 1️⃣ Set up your Foundation (ICP, positioning, voice) in 20 mins. 2️⃣ Receive weekly Moves (ready-to-ship content). 3️⃣ Track everything in the Matrix. Want to see a demo?",
    "what are moves": "Moves are your weekly content packets! Each Monday, you get LinkedIn posts, tweets, and emails—all aligned to your strategy and written in your voice. Ready to ship.",

    // Pricing
    "pricing": "We have 3 plans: Ascent (₹5,000/mo), Glide (₹7,000/mo - most popular!), and Soar (₹10,000/mo for teams). Which sounds right for you?",
    "how much": "Starting at ₹5,000/month for Ascent. Our most popular plan, Glide, is ₹7,000/month with unlimited Moves and advanced AI features.",

    // Features
    "muse": "I'm Muse! 🧠 I learn your voice, your style, and generate content that sounds like YOU. The more you use me, the better I get.",
    "foundation": "Foundation is where it all starts. In 20 minutes, we define your ICP, positioning, and brand voice. It's the strategic bedrock everything else builds on.",

    // Comparison
    "vs buffer": "Unlike Buffer, we don't just schedule—we generate. Your strategy, your voice, your content, all connected. It's like having a marketing team in your pocket.",
    "vs notion": "Notion is great for docs, but RaptorFlow is purpose-built for marketing execution. Strategy → Content → Analytics, all unified.",
};

function findResponse(input: string): string {
    const lowerInput = input.toLowerCase().trim();

    // Check for exact or partial matches
    for (const [key, response] of Object.entries(AI_RESPONSES)) {
        if (lowerInput.includes(key)) {
            return response;
        }
    }

    // Fallback
    return "Great question! 🤔 I'd love to explain more. Book a quick demo and our team will walk you through everything → [Book Demo](/signup)";
}

export default function AIDemoChat() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        { role: "ai", content: "Hey! 👋 I'm Muse, RaptorFlow's AI assistant. Ask me anything about how we can transform your marketing!" }
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = () => {
        if (!input.trim()) return;

        const userMessage = input.trim();
        setMessages(prev => [...prev, { role: "user", content: userMessage }]);
        setInput("");
        setIsTyping(true);

        // Simulate AI thinking
        setTimeout(() => {
            const response = findResponse(userMessage);
            setMessages(prev => [...prev, { role: "ai", content: response }]);
            setIsTyping(false);
        }, 1000 + Math.random() * 1000);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const suggestedQuestions = [
        "What is RaptorFlow?",
        "How do Moves work?",
        "Pricing?",
    ];

    return (
        <>
            {/* Chat bubble trigger */}
            <motion.button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-[var(--rf-coral)] to-[var(--rf-ocean)] text-white shadow-2xl flex items-center justify-center"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                animate={{
                    boxShadow: isOpen
                        ? "0 0 0 0 rgba(224, 141, 121, 0)"
                        : ["0 0 0 0 rgba(224, 141, 121, 0.4)", "0 0 0 15px rgba(224, 141, 121, 0)", "0 0 0 0 rgba(224, 141, 121, 0.4)"]
                }}
                transition={{ duration: 2, repeat: isOpen ? 0 : Infinity }}
            >
                <AnimatePresence mode="wait">
                    <motion.span
                        key={isOpen ? "close" : "chat"}
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        exit={{ scale: 0, rotate: 180 }}
                        className="text-2xl"
                    >
                        {isOpen ? "×" : "💬"}
                    </motion.span>
                </AnimatePresence>
            </motion.button>

            {/* Chat window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        className="fixed bottom-24 right-6 z-50 w-[380px] h-[500px] bg-[var(--canvas)] rounded-2xl shadow-2xl border border-[var(--border)] flex flex-col overflow-hidden"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-[var(--border)] bg-gradient-to-r from-[var(--rf-coral)]/10 to-[var(--rf-ocean)]/10">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--rf-coral)] to-[var(--rf-ocean)] flex items-center justify-center text-white font-bold">
                                    M
                                </div>
                                <div>
                                    <p className="font-semibold">Muse AI</p>
                                    <p className="text-xs text-[var(--muted)] flex items-center gap-1">
                                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                        Online
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.map((msg, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                                >
                                    <div className={`
                                        max-w-[80%] px-4 py-2.5 rounded-2xl text-sm
                                        ${msg.role === "user"
                                            ? "bg-[var(--ink)] text-white rounded-br-sm"
                                            : "bg-[var(--surface)] text-[var(--ink)] rounded-bl-sm"
                                        }
                                    `}>
                                        {msg.content}
                                    </div>
                                </motion.div>
                            ))}

                            {/* Typing indicator */}
                            {isTyping && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex gap-1 px-4 py-3 bg-[var(--surface)] rounded-2xl rounded-bl-sm w-fit"
                                >
                                    {[0, 1, 2].map(i => (
                                        <motion.span
                                            key={i}
                                            className="w-2 h-2 rounded-full bg-[var(--muted)]"
                                            animate={{ y: [0, -4, 0] }}
                                            transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
                                        />
                                    ))}
                                </motion.div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Suggested questions */}
                        {messages.length <= 2 && (
                            <div className="px-4 pb-2 flex gap-2 flex-wrap">
                                {suggestedQuestions.map(q => (
                                    <button
                                        key={q}
                                        onClick={() => {
                                            setInput(q);
                                            setTimeout(handleSend, 100);
                                        }}
                                        className="px-3 py-1 text-xs bg-[var(--surface)] border border-[var(--border)] rounded-full hover:border-[var(--ink)] transition-colors"
                                    >
                                        {q}
                                    </button>
                                ))}
                            </div>
                        )}

                        {/* Input */}
                        <div className="p-4 border-t border-[var(--border)]">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Ask me anything..."
                                    className="flex-1 px-4 py-2.5 bg-[var(--surface)] border border-[var(--border)] rounded-xl text-sm outline-none focus:border-[var(--ink)]"
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={!input.trim()}
                                    className="px-4 py-2.5 bg-[var(--ink)] text-white rounded-xl font-medium text-sm disabled:opacity-50 hover:bg-[var(--ink)]/90 transition-colors"
                                >
                                    Send
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
