"use client";

import { ArrowLeft } from "lucide-react";

export default function TermsPage() {
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
                    <h1 className="font-serif text-4xl text-[var(--ink)] mb-2">Terms of Service</h1>
                    <p className="font-technical text-[var(--ink-muted)] text-xs uppercase tracking-widest mb-12">
                        LAST UPDATED: JANUARY 15, 2026
                    </p>

                    <div className="prose prose-slate max-w-none text-[var(--ink)]">
                        <h3>1. Acceptance of Terms</h3>
                        <p>
                            By accessing and using RaptorFlow (&quot;the Service&quot;), you accept and agree to be bound by the terms and provision of this agreement.
                        </p>

                        <h3>2. Concept of Operations</h3>
                        <p>
                            RaptorFlow provides a marketing operating system for founders. You agree to use this system only for lawful purposes related to business growth and market analysis.
                        </p>

                        <h3>3. Data Intelligence</h3>
                        <p>
                            Our proprietary algorithms process market data to provide strategic insights. While we strive for accuracy, market conditions are volatile. RaptorFlow provides intelligence, not financial advice.
                        </p>

                        <h3>4. Membership & Access</h3>
                        <p>
                            Access to RaptorFlow is granted on a subscription basis. We reserve the right to revoke access for violations of community standards or misuse of the platform.
                        </p>

                        <h3>5. Limitation of Liability</h3>
                        <p>
                            In no event shall RaptorFlow be liable for any indirect, incidental, special, consequential or punitive damages, including without limitation, loss of profits.
                        </p>
                    </div>
                </div>

                <div className="mt-8 text-center">
                    <p className="text-xs text-[var(--ink-muted)]">
                        &copy; 2026 RaptorFlow Inc. All rights reserved.
                    </p>
                </div>
            </div>
        </div>
    );
}
