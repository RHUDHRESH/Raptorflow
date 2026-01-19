"use client";

import { Shell } from "@/components/shell/Shell";
import { BlueprintCommandPrompt } from "@/components/ui/BlueprintCommandPrompt";

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
