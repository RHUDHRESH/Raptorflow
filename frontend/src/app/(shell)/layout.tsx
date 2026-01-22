"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Shell } from "@/components/shell/Shell";
import { BlueprintCommandPrompt } from "@/components/ui/BlueprintCommandPrompt";

export default function ShellLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ProtectedRoute>
            <Shell>
                <BlueprintCommandPrompt />
                {children}
            </Shell>
        </ProtectedRoute>
    );
}
