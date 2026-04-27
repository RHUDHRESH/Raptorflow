"use client";

import type { ReactElement } from "react";

export interface PositioningBody {
  positioning_statement?: string;
  category?: string;
  differentiators?: string[];
  alternatives?: string[];
  proof_points?: string[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((v) => typeof v === "string");
}

export function isPositioningBody(body: unknown): body is PositioningBody {
  return isRecord(body);
}

export function PositioningRenderer({ body }: { body: unknown }): ReactElement {
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
      {isString(b.positioning_statement) && (
        <Section label="Positioning Statement">
          <p className="text-[var(--foreground)] italic">{b.positioning_statement}</p>
        </Section>
      )}

      {isString(b.category) && (
        <Section label="Category">
          <p className="text-[var(--foreground)]">{b.category}</p>
        </Section>
      )}

      {isStringArray(b.differentiators) && b.differentiators.length > 0 && (
        <Section label="Differentiators">
          <UlList items={b.differentiators} />
        </Section>
      )}

      {isStringArray(b.alternatives) && b.alternatives.length > 0 && (
        <Section label="Alternatives">
          <UlList items={b.alternatives} />
        </Section>
      )}

      {isStringArray(b.proof_points) && b.proof_points.length > 0 && (
        <Section label="Proof Points">
          <UlList items={b.proof_points} />
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
