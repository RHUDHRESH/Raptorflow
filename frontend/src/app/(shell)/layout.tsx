"use client";

import { Shell } from "@/components/shell/Shell";

export default function ShellLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <Shell>
            <BlueprintCommandPrompt />
            {children}
        </Shell>
    );
}

import { BlueprintCommandPrompt } from "@/components/ui/BlueprintCommandPrompt";
