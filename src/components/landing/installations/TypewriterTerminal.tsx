"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Command {
    input: string;
    output: string[];
    delay?: number;
}

const COMMANDS: Command[] = [
    {
        input: "rf init --founder \"TechStartup Inc\"",
        output: [
            "⚡ Initializing Foundation...",
            "✓ ICP defined: B2B SaaS founders, Series A-B",
            "✓ Positioning: \"The developer-first marketing OS\"",
            "✓ Voice profile: Confident, technical, witty",
            "",
            "🎉 Foundation ready. Run 'rf generate-move' to start."
        ]
    },
    {
        input: "rf generate-move --channel linkedin",
        output: [
            "🧠 Analyzing ICP behavior patterns...",
            "📊 Scanning top-performing hooks...",
            "✍️  Generating Move #247...",
            "",
            "✓ Move ready: \"Why we ditched our $50K agency\"",
            "  → 3 LinkedIn posts drafted",
            "  → CTA: Demo booking link",
            "  → Best time: Tuesday 9:15 AM IST"
        ]
    },
    {
        input: "rf analytics --week 12",
        output: [
            "📈 Performance Report — Week 12",
            "─────────────────────────────────",
            "  Impressions:  45,200  (+127%)",
            "  Engagement:   3,840   (+89%)",
            "  Demo Calls:   12      (+300%)",
            "  Pipeline:     ₹4.2L   added",
            "",
            "🎯 Top Move: \"The founding team Friday\" (12K views)"
        ]
    }
];

function TypewriterLine({ text, onComplete }: { text: string; onComplete: () => void }) {
    const [displayText, setDisplayText] = useState("");
    const index = useRef(0);

    useEffect(() => {
        if (index.current < text.length) {
            const timeout = setTimeout(() => {
                setDisplayText(text.slice(0, index.current + 1));
                index.current++;
            }, 20 + Math.random() * 30); // Variable typing speed for realism
            return () => clearTimeout(timeout);
        } else {
            onComplete();
        }
    }, [displayText, text, onComplete]);

    return <span>{displayText}</span>;
}

export default function TypewriterTerminal() {
    const [currentCommand, setCurrentCommand] = useState(0);
    const [phase, setPhase] = useState<"typing" | "output" | "waiting">("typing");
    const [outputLines, setOutputLines] = useState<string[]>([]);
    const [currentLine, setCurrentLine] = useState(0);
    const [isTypingInput, setIsTypingInput] = useState(true);
    const terminalRef = useRef<HTMLDivElement>(null);

    const command = COMMANDS[currentCommand];

    // Handle command input typing completion
    const handleInputComplete = () => {
        setIsTypingInput(false);
        setPhase("output");
        setCurrentLine(0);
    };

    // Type out output lines one by one
    useEffect(() => {
        if (phase === "output" && command) {
            if (currentLine < command.output.length) {
                const timeout = setTimeout(() => {
                    setOutputLines(prev => [...prev, command.output[currentLine]]);
                    setCurrentLine(prev => prev + 1);
                }, 100 + Math.random() * 150);
                return () => clearTimeout(timeout);
            } else {
                // Done with this command
                setTimeout(() => {
                    setPhase("waiting");
                    // Move to next command after pause
                    setTimeout(() => {
                        if (currentCommand < COMMANDS.length - 1) {
                            setCurrentCommand(prev => prev + 1);
                            setOutputLines([]);
                            setIsTypingInput(true);
                            setPhase("typing");
                        } else {
                            // Loop back
                            setTimeout(() => {
                                setCurrentCommand(0);
                                setOutputLines([]);
                                setIsTypingInput(true);
                                setPhase("typing");
                            }, 3000);
                        }
                    }, 2000);
                }, 500);
            }
        }
    }, [phase, currentLine, command, currentCommand]);

    // Scroll to bottom when new output
    useEffect(() => {
        if (terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
    }, [outputLines]);

    return (
        <div className="max-w-2xl mx-auto">
            {/* Terminal header */}
            <div className="bg-[var(--ink)] rounded-t-xl px-4 py-3 flex items-center gap-2">
                <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <span className="text-white/60 text-sm font-mono ml-4">raptorflow-cli</span>
            </div>

            {/* Terminal body */}
            <div
                ref={terminalRef}
                className="bg-[#1a1a1a] rounded-b-xl p-6 font-mono text-sm h-[400px] overflow-y-auto"
            >
                {/* Previous commands & outputs would stack here */}
                <div className="space-y-4">
                    {/* Current command */}
                    <div>
                        <div className="flex items-start gap-2">
                            <span className="text-green-400">❯</span>
                            <span className="text-white">
                                {isTypingInput ? (
                                    <TypewriterLine text={command.input} onComplete={handleInputComplete} />
                                ) : (
                                    command.input
                                )}
                                {isTypingInput && (
                                    <motion.span
                                        animate={{ opacity: [1, 0] }}
                                        transition={{ duration: 0.5, repeat: Infinity }}
                                        className="inline-block w-2 h-4 bg-white ml-0.5"
                                    />
                                )}
                            </span>
                        </div>

                        {/* Output lines */}
                        <AnimatePresence>
                            {outputLines.map((line, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 5 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`ml-4 ${line.startsWith("✓") ? "text-green-400" :
                                            line.startsWith("⚡") || line.startsWith("🎉") || line.startsWith("🎯") ? "text-yellow-400" :
                                                line.startsWith("📈") || line.startsWith("📊") ? "text-blue-400" :
                                                    line.startsWith("✍️") || line.startsWith("🧠") ? "text-purple-400" :
                                                        line.includes("→") ? "text-[var(--rf-coral)]" :
                                                            "text-gray-400"
                                        }`}
                                >
                                    {line || <br />}
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>
            </div>

            {/* Command hint */}
            <div className="mt-4 text-center text-sm text-[var(--muted)]">
                <span className="inline-flex items-center gap-2">
                    <kbd className="px-2 py-1 bg-[var(--surface)] border border-[var(--border)] rounded text-xs">
                        ↵
                    </kbd>
                    See RaptorFlow in action
                </span>
            </div>
        </div>
    );
}
