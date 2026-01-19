"use client";

import { ArrowLeft, Search, MessageSquare, Mail, FileText } from "lucide-react";

export default function SupportPage() {
    return (
        <div className="min-h-screen bg-[var(--canvas)] flex justify-center py-20 px-6">
            <div className="max-w-4xl w-full">
                <button
                    onClick={() => window.history.back()}
                    className="mb-8 flex items-center gap-2 text-sm text-[var(--ink-secondary)] hover:text-[var(--ink)] transition-colors"
                >
                    <ArrowLeft size={16} /> Back
                </button>

                <div className="text-center mb-16">
                    <span className="font-technical text-[var(--ink-muted)] text-xs uppercase tracking-widest mb-4 block">
                        RaptorFlow Concierge
                    </span>
                    <h1 className="font-serif text-5xl text-[var(--ink)] mb-6">How can we assist?</h1>

                    <div className="max-w-xl mx-auto relative">
                        <input
                            type="text"
                            placeholder="Search documentation..."
                            className="w-full h-14 pl-12 pr-4 rounded-[var(--radius-md)] bg-[var(--paper)] border border-[var(--border)] focus:ring-1 focus:ring-[var(--ink)] focus:outline-none shadow-sm"
                        />
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--ink-muted)]" size={20} />
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                    {/* Card 1 */}
                    <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-8 hover:shadow-md transition-shadow cursor-pointer group">
                        <div className="w-12 h-12 bg-[var(--surface)] rounded-full flex items-center justify-center mb-6 group-hover:bg-[var(--ink)] group-hover:text-[var(--paper)] transition-colors">
                            <FileText size={24} strokeWidth={1.5} />
                        </div>
                        <h3 className="font-serif text-xl text-[var(--ink)] mb-2">Knowledge Base</h3>
                        <p className="text-[var(--ink-secondary)] text-sm mb-4">
                            Detailed guides on implementing the RaptorFlow operating system.
                        </p>
                        <span className="text-xs font-bold text-[var(--ink)] uppercase tracking-wide">Read Guides &rarr;</span>
                    </div>

                    {/* Card 2 */}
                    <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-8 hover:shadow-md transition-shadow cursor-pointer group">
                        <div className="w-12 h-12 bg-[var(--surface)] rounded-full flex items-center justify-center mb-6 group-hover:bg-[var(--ink)] group-hover:text-[var(--paper)] transition-colors">
                            <MessageSquare size={24} strokeWidth={1.5} />
                        </div>
                        <h3 className="font-serif text-xl text-[var(--ink)] mb-2">Live Chat</h3>
                        <p className="text-[var(--ink-secondary)] text-sm mb-4">
                            Connect with a support specialist for real-time assistance.
                        </p>
                        <span className="text-xs font-bold text-[var(--ink)] uppercase tracking-wide">Start Chat &rarr;</span>
                    </div>

                    {/* Card 3 */}
                    <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-8 hover:shadow-md transition-shadow cursor-pointer group">
                        <div className="w-12 h-12 bg-[var(--surface)] rounded-full flex items-center justify-center mb-6 group-hover:bg-[var(--ink)] group-hover:text-[var(--paper)] transition-colors">
                            <Mail size={24} strokeWidth={1.5} />
                        </div>
                        <h3 className="font-serif text-xl text-[var(--ink)] mb-2">Email Support</h3>
                        <p className="text-[var(--ink-secondary)] text-sm mb-4">
                            Deep dive inquiry? Send us a brief and we'll investigate.
                        </p>
                        <span className="text-xs font-bold text-[var(--ink)] uppercase tracking-wide">Send Email &rarr;</span>
                    </div>
                </div>

                <div className="mt-16 border-t border-[var(--border)] pt-8 text-center">
                    <p className="text-sm text-[var(--ink-muted)]">
                        Current System Status: <span className="text-[var(--success)] font-medium">● Operational</span>
                    </p>
                </div>
            </div>
        </div>
    );
}
