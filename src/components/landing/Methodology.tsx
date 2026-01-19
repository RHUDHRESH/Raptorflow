"use client";

import React from "react";
import { CheckmarkCircle02Icon } from "hugeicons-react";
import { motion } from "framer-motion";

export function Methodology() {
    return (
        <section className="py-24 bg-[var(--surface)] border-y border-[var(--border)] overflow-hidden">
            <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

                {/* Left: Manifesto */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="space-y-8"
                >
                    <div className="inline-block px-3 py-1 bg-[var(--canvas)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--secondary)]">
                        The Injustice
                    </div>
                    <h2 className="text-4xl md:text-5xl font-editorial text-[var(--ink)] leading-tight">
                        Stop marketing by <br /> <span className="italic text-[var(--muted)]">vibes.</span>
                    </h2>
                    <div className="space-y-6 text-lg text-[var(--secondary)]">
                        <p>
                            You shouldn't have to guess if your marketing is working.
                            Most founders throw things at the wall and hope.
                        </p>
                        <p>
                            RaptorFlow forces you to answer the hard questions first.
                            <strong>With RaptorFlow, you won't guess.</strong> You will execute.
                        </p>
                    </div>

                    <ul className="space-y-4 mt-8">
                        {[
                            "Stop reinventing the wheel",
                            "Stop sounding like everyone else",
                            "Stop wasting time on tools"
                        ].map((item, i) => (
                            <motion.li
                                key={i}
                                initial={{ opacity: 0, x: -20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.5 + (i * 0.1), duration: 0.5 }}
                                className="flex items-center gap-3 text-[var(--ink)]"
                            >
                                {React.createElement(CheckmarkCircle02Icon as any, { className: "w-6 h-6 text-[var(--accent)]" })}
                                <span>{item}</span>
                            </motion.li>
                        ))}
                    </ul>
                </motion.div>

                {/* Right: Visual Abstract */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="relative h-[500px] w-full bg-[var(--canvas)] border border-[var(--border)] rounded-2xl p-8 flex flex-col justify-between overflow-hidden shadow-sm"
                >
                    <div className="absolute inset-0 bg-[linear-gradient(to_bottom_right,transparent_50%,var(--surface))] opacity-50" />

                    {/* Abstract UI Representation */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        whileInView={{ y: 0, opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.4, duration: 0.6 }}
                        className="relative z-10 w-full p-4 border border-[var(--border)] bg-[var(--canvas)] rounded-xl shadow-lg mb-4"
                    >
                        <div className="h-2 w-24 bg-[var(--ink)] rounded mb-4" />
                        <div className="h-2 w-full bg-[var(--border)] rounded mb-2" />
                        <div className="h-2 w-2/3 bg-[var(--border)] rounded" />
                    </motion.div>

                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        whileInView={{ y: 0, opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.6, duration: 0.6 }}
                        className="relative z-10 w-[90%] self-end p-4 border border-[var(--border)] bg-[var(--surface)] rounded-xl shadow-md opacity-80"
                    >
                        <div className="h-2 w-20 bg-[var(--secondary)] rounded mb-4" />
                        <div className="h-2 w-full bg-[var(--border)] rounded" />
                    </motion.div>
                </motion.div>

            </div>
        </section>
    );
}
