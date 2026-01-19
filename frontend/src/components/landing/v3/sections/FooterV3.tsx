"use client";

import React from "react";

export function FooterV3() {
    return (
        <footer className="bg-[#050505] text-[#FAFAFA] border-t border-white/10 pt-24 pb-12">
            <div className="max-w-[1440px] mx-auto px-6 md:px-12">

                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-12 mb-24">
                    <div className="col-span-2">
                        <div className="w-8 h-8 bg-white mb-6" />
                        <p className="font-mono text-xs opacity-50 uppercase tracking-widest max-w-xs leading-relaxed">
                            RaptorFlow Inc.<br />
                            System Version 3.0.1<br />
                            San Francisco, CA
                        </p>
                    </div>

                    <div>
                        <h4 className="font-mono text-xs text-[#00FF94] uppercase tracking-widest mb-6">Module_Index</h4>
                        <ul className="space-y-4 font-mono text-sm text-white/60">
                            <li className="hover:text-white cursor-pointer">Foundation</li>
                            <li className="hover:text-white cursor-pointer">Muse_AI</li>
                            <li className="hover:text-white cursor-pointer">Matrix</li>
                            <li className="hover:text-white cursor-pointer">Moves</li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-mono text-xs text-[#00FF94] uppercase tracking-widest mb-6">Protocol</h4>
                        <ul className="space-y-4 font-mono text-sm text-white/60">
                            <li className="hover:text-white cursor-pointer">Manifesto</li>
                            <li className="hover:text-white cursor-pointer">Pricing</li>
                            <li className="hover:text-white cursor-pointer">Login</li>
                            <li className="hover:text-white cursor-pointer">API_Docs</li>
                        </ul>
                    </div>

                    <div className="col-span-2">
                        <h4 className="font-mono text-xs text-[#00FF94] uppercase tracking-widest mb-6">Newsletter_Subroutine</h4>
                        <div className="flex border-b border-white/20 pb-2">
                            <input
                                type="email"
                                placeholder="ENTER_EMAIL_ADDRESS"
                                className="bg-transparent w-full outline-none font-mono text-sm placeholder:text-white/20"
                            />
                            <button className="text-xs font-mono uppercase hover:text-[#00FF94]">Submit</button>
                        </div>
                    </div>
                </div>

                <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4 font-mono text-[10px] uppercase tracking-widest text-white/30">
                    <p>© 2024 RaptorFlow Inc. All Systems Operational.</p>
                    <div className="flex gap-8">
                        <span className="hover:text-white cursor-pointer">Privacy_Check</span>
                        <span className="hover:text-white cursor-pointer">Terms_Of_Service</span>
                    </div>
                </div>

            </div>
        </footer>
    );
}
