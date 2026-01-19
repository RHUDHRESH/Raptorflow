"use client";

import { ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-[var(--canvas)] flex justify-center py-20 px-6">
            <div className="max-w-3xl w-full">
                <button
                    onClick={() => window.history.back()}
                    className="mb-8 flex items-center gap-2 text-sm text-[var(--ink-secondary)] hover:text-[var(--ink)] transition-colors"
                >
                    <ArrowLeft size={16} /> Back
                </button>

                <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-12 shadow-sm">
                    <h1 className="font-serif text-4xl text-[var(--ink)] mb-2">Privacy Policy</h1>
                    <p className="font-technical text-[var(--ink-muted)] text-xs uppercase tracking-widest mb-12">
                        DATA PROTECTION PROTOCOL: ACTIVE
                    </p>

                    <div className="prose prose-slate max-w-none text-[var(--ink)]">
                        <h3>1. Data Collection</h3>
                        <p>
                            We collect information necessary to provide our strategic operating system. This includes business context, market positioning data, and usage metrics.
                        </p>

                        <h3>2. How We Use Information</h3>
                        <p>
                            Your data drives the core of RaptorFlow. It is used to:
                        </p>
                        <ul>
                            <li>Generate bespoke marketing strategies.</li>
                            <li>Analyze market gaps and opportunities.</li>
                            <li>Improve our proprietary models.</li>
                        </ul>

                        <h3>3. Data Sovereignty</h3>
                        <p>
                            Your strategic data belongs to you. We do not sell your data to third parties. We employ industry-standard encryption to ensure your competitive advantage remains confidential.
                        </p>

                        <h3>4. Third-Party Integrations</h3>
                        <p>
                            RaptorFlow integrates with select providers (e.g. Google Cloud, Stripe) to deliver its services. These partners adhere to strict security standards.
                        </p>
                    </div>
                </div>

                <div className="mt-8 text-center">
                    <p className="text-xs text-[var(--ink-muted)]">
                        RaptorFlow Security Division
                    </p>
                </div>
            </div>
        </div>
    );
}
