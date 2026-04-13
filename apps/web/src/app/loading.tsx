"use client";

import * as React from "react";

export default function Loading(): React.ReactElement {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--muted)] border-t-[var(--primary)]" />
        <p className="text-sm text-[var(--muted-foreground)]">Loading...</p>
      </div>
    </div>
  );
}
