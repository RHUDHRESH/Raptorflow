"use client";

import { ReactNode } from "react";

/* ══════════════════════════════════════════════════════════════════════════════
   PAGE HEADER — Unified header component for all pages
   Ensures consistent typography, spacing, and technical prefixes across the app.
   ══════════════════════════════════════════════════════════════════════════════ */

interface PageHeaderProps {
    /** Module code for the technical prefix (e.g., "CAMPAIGNS", "SETTINGS") */
    moduleCode: string;
    /** Descriptor shown after the divider (e.g., "COMMAND", "ACCOUNT") */
    descriptor?: string;
    /** Main page title (serif typography) */
    title: string;
    /** Optional subtitle/description */
    subtitle?: string;
    /** Optional action buttons on the right */
    actions?: ReactNode;
}

export function PageHeader({
    moduleCode,
    descriptor,
    title,
    subtitle,
    actions,
}: PageHeaderProps) {
    return (
        <div className="align-end justify-between mb-8">
            <div>
                <div className="align-start gap-3 mb-1">
                    <span className="font-technical text-[var(--blueprint)]">
                        SYS.{moduleCode}
                    </span>
                    {descriptor && (
                        <>
                            <div className="h-px w-6 bg-[var(--structure)]" />
                            <span className="font-technical text-[var(--ink-muted)]">
                                {descriptor}
                            </span>
                        </>
                    )}
                </div>
                <h1 className="font-editorial text-4xl text-[var(--ink)]">{title}</h1>
                {subtitle && (
                    <p className="text-[var(--ink-secondary)] mt-1">{subtitle}</p>
                )}
            </div>
            {actions && <div className="align-start gap-3">{actions}</div>}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   PAGE FOOTER — Optional document marker
   ══════════════════════════════════════════════════════════════════════════════ */

interface PageFooterProps {
    /** Document name for the footer (e.g., "SETTINGS", "CAMPAIGNS") */
    document: string;
}

export function PageFooter({ document }: PageFooterProps) {
    return (
        <div className="flex justify-center pt-8 mt-8 border-t border-[var(--structure-subtle)]">
            <span className="font-technical text-[var(--ink-ghost)]">
                DOCUMENT: {document} | REVISION: {new Date().toISOString().split("T")[0]}
            </span>
        </div>
    );
}
