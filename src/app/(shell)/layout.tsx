"use client";

import { Shell } from "@/components/shell/Shell";
import { WorkspaceProvider } from "@/components/workspace/WorkspaceProvider";

export default function ShellLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <WorkspaceProvider>
            <Shell>
                {children}
            </Shell>
        </WorkspaceProvider>
    );
}
