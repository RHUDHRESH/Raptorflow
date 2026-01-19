"use client";

import React from "react";

export function ManifestoV3() {
    return (
        <section className="relative py-48 bg-[#050505] text-[#FAFAFA]">
            <div className="max-w-4xl mx-auto px-6 md:px-12 text-center">

                <h4 className="font-mono text-xs text-[#00FF94] uppercase tracking-widest mb-12">
                     // The_Pledge
                </h4>

                <div className="font-serif text-3xl md:text-5xl lg:text-6xl leading-tight md:leading-tight cursor-default space-y-12">
                    <p className="opacity-90 hover:opacity-100 transition-opacity duration-300">
                        You didn't build a company to become a content creator.
                    </p>
                    <p className="opacity-60 hover:opacity-100 transition-opacity duration-300 text-white">
                        You built it to solve a problem.
                    </p>
                    <p className="opacity-60 hover:opacity-100 transition-opacity duration-300 text-white">
                        But in 2024, if you are invisible, <br />
                        <span className="text-red-500">you don't exist.</span>
                    </p>
                </div>

                <div className="mt-24 max-w-2xl mx-auto font-mono text-sm md:text-base leading-loose text-white/60 text-justify">
                    <p>
                        We built RaptorFlow because we were tired of seeing brilliant founders fail because they couldn't find their voice.
                        We believe marketing shouldn't be a lottery ticket. It should be an engineering problem. Solvable. Repeatable.
                        We aren't asking you to dance on TikTok. We are giving you the tools to articulate your life's work.
                    </p>
                </div>

                <div className="mt-16">
                    <div className="h-24 w-[1px] bg-white/20 mx-auto" />
                </div>
            </div>
        </section>
    );
}
