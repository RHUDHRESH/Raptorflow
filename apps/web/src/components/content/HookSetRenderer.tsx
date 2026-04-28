"use client";

import type { ReactElement } from "react";

interface HookItem {
  hook?: string;
  angle?: string;
  trigger?: string;
}

export interface HookSetBody {
  hooks?: HookItem[];
  winning_angles?: string[];
  proof_gaps?: string[];
  learnings?: string[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((v) => typeof v === "string");
}

function isHookItem(value: unknown): value is HookItem {
  return isRecord(value);
}

function isHookArray(value: unknown): value is HookItem[] {
  return Array.isArray(value) && value.every(isHookItem);
}

export function isHookSetBody(body: unknown): body is HookSetBody {
  return isRecord(body);
}

export function HookSetRenderer({ body }: { body: unknown }): ReactElement {
  if (!isRecord(body)) {
    return (
      <pre className="mt-4 overflow-x-auto whitespace-pre-wrap text-xs text-[var(--muted-foreground)]">
        {JSON.stringify(body, null, 2)}
      </pre>
    );
  }

  const b = body as Record<string, unknown>;

  return (
    <div className="mt-4 space-y-4 text-sm">
      {isHookArray(b.hooks) && b.hooks.length > 0 && (
        <Section label="Hooks">
          <div className="space-y-2">
            {b.hooks.map((h, i) => (
              <div key={i} className="border-l-2 border-[var(--border)] pl-3">
                <p className="text-[var(--foreground)]">{h.hook ?? "Unnamed hook"}</p>
                <div className="mt-1 flex flex-wrap gap-3 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)]">
                  {h.angle && <span>Angle: {h.angle}</span>}
                  {h.trigger && <span>Trigger: {h.trigger}</span>}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {isStringArray(b.winning_angles) && b.winning_angles.length > 0 && (
        <Section label="Winning Angles">
          <UlList items={b.winning_angles} />
        </Section>
      )}

      {isStringArray(b.proof_gaps) && b.proof_gaps.length > 0 && (
        <Section label="Proof Gaps">
          <UlList items={b.proof_gaps} />
        </Section>
      )}

      {isStringArray(b.learnings) && b.learnings.length > 0 && (
        <Section label="Learnings">
          <UlList items={b.learnings} />
        </Section>
      )}
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }): ReactElement {
  return (
    <div>
      <p className="font-mono text-[10px] font-bold uppercase tracking-[0.2em] text-[var(--muted-foreground)] mb-1.5">
        {label}
      </p>
      {children}
    </div>
  );
}

function UlList({ items }: { items: string[] }): ReactElement {
  return (
    <ul className="space-y-1">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2">
          <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--muted-foreground)]" />
          <span className="text-[var(--foreground)]">{item}</span>
        </li>
      ))}
    </ul>
  );
}
