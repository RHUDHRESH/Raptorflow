"use client";

import { Shell } from "@/components/shell/Shell";
import { AuthGuard } from "@/components/auth/AuthGuard";

export default function ShellLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <AuthGuard>
            <Shell>
                <BlueprintCommandPrompt />
                {children}
            </Shell>
        </AuthGuard>
    );
}

import { BlueprintCommandPrompt } from "@/components/ui/BlueprintCommandPrompt";
