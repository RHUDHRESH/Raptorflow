"use client";

import type { ReactElement } from "react";

export function UnknownContentRenderer({
  body,
  contentType,
}: {
  body: unknown;
  contentType: string;
}): ReactElement {
  return (
    <div className="mt-4">
      <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-yellow-500">
        Unsupported content type: {contentType}
      </p>
      <pre className="overflow-x-auto whitespace-pre-wrap rounded border border-[var(--border)] bg-[var(--background)] p-3 text-xs text-[var(--muted-foreground)]">
        {JSON.stringify(body, null, 2)}
      </pre>
    </div>
  );
}
