"use client";

import React from "react";
import { Network, Database, MessageSquare, Mail, Globe, Share2, Workflow, Link as LinkIcon } from "lucide-react";

export function IntegrationsV3() {
    const integrations = [
        { name: "HubSpot", icon: Database },
        { name: "Slack", icon: MessageSquare },
        { name: "Gmail", icon: Mail },
        { name: "LinkedIn", icon: Globe },
        { name: "Twitter/X", icon: Share2 },
        { name: "Zapier", icon: Workflow },
        { name: "notion", icon: Network },
        { name: "API", icon: LinkIcon },
    ];

    return (
        <section className="bg-[#111] text-white py-32 border-b border-white/10 overflow-hidden relative">
            {/* Background Texture */}
            <div className="absolute inset-0 pointer-events-none opacity-[0.05]"
                style={{ backgroundImage: `linear-gradient(#333 2px, transparent 2px), linear-gradient(90deg, #333 2px, transparent 2px)`, backgroundSize: '40px 40px' }}
            />

            <div className="max-w-[1440px] mx-auto px-6 md:px-12 flex flex-col md:flex-row gap-24">

                {/* Description */}
                <div className="flex-1">
                    <h2 className="text-[5vw] md:text-[4rem] leading-none font-bold tracking-tighter mb-8">
                        The I/O<br />Port.
                    </h2>
                    <p className="font-mono text-sm opacity-60 max-w-sm mb-12">
                        RaptorFlow is not a walled garden. It is a router.
                        Connect your existing stack to the central intelligence.
                    </p>
                    <div className="font-mono text-xs uppercase tracking-widest text-[#00FF94]">
                        [ Supported_Protocols: 50+ ]
                    </div>
                </div>

                {/* The Grid / Patch Bay */}
                <div className="flex-1 grid grid-cols-4 gap-4">
                    {integrations.map((item, i) => (
                        <div
                            key={i}
                            className="aspect-square border border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/30 transition-all duration-300 flex flex-col items-center justify-center gap-4 group cursor-pointer"
                        >
                            <div className="w-2 h-2 rounded-full bg-white/20 group-hover:bg-[#00FF94] group-hover:shadow-[0_0_10px_#00FF94] transition-all duration-300 mb-2" />
                            <item.icon className="w-8 h-8 opacity-50 group-hover:opacity-100 transition-opacity" />
                            <span className="font-mono text-[10px] uppercase tracking-wider opacity-30 group-hover:opacity-100">
                                {item.name}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
