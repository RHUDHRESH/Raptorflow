"use client";

import type { ReactElement } from "react";

interface SegmentItem {
  name?: string;
  description?: string;
  priority?: string;
}

interface ObjectionItem {
  objection?: string;
  response?: string;
}

export interface IcpRefinedBody {
  segments?: SegmentItem[];
  pain_points?: string[];
  buying_triggers?: string[];
  objections?: ObjectionItem[];
  recommended_icp?: string;
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

function isSegmentItem(value: unknown): value is SegmentItem {
  return isRecord(value);
}

function isSegmentArray(value: unknown): value is SegmentItem[] {
  return Array.isArray(value) && value.every(isSegmentItem);
}

function isObjectionItem(value: unknown): value is ObjectionItem {
  return isRecord(value);
}

function isObjectionArray(value: unknown): value is ObjectionItem[] {
  return Array.isArray(value) && value.every(isObjectionItem);
}

export function isIcpRefinedBody(body: unknown): body is IcpRefinedBody {
  return isRecord(body);
}

export function IcpRefinedRenderer({ body }: { body: unknown }): ReactElement {
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
      {isSegmentArray(b.segments) && b.segments.length > 0 && (
        <Section label="Segments">
          <div className="space-y-2">
            {b.segments.map((s, i) => (
              <div key={i} className="border-l-2 border-[var(--border)] pl-3">
                <p className="text-[var(--foreground)] font-medium">
                  {s.name ?? `Segment ${i + 1}`}
                </p>
                {s.description && (
                  <p className="mt-0.5 text-[var(--muted-foreground)]">{s.description}</p>
                )}
                {s.priority && (
                  <p className="mt-1 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)]">
                    Priority: {s.priority}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {isStringArray(b.pain_points) && b.pain_points.length > 0 && (
        <Section label="Pain Points">
          <UlList items={b.pain_points} />
        </Section>
      )}

      {isStringArray(b.buying_triggers) && b.buying_triggers.length > 0 && (
        <Section label="Buying Triggers">
          <UlList items={b.buying_triggers} />
        </Section>
      )}

      {isObjectionArray(b.objections) && b.objections.length > 0 && (
        <Section label="Objections">
          <div className="space-y-2">
            {b.objections.map((o, i) => (
              <div key={i} className="border-l-2 border-[var(--border)] pl-3">
                <p className="text-[var(--foreground)]">
                  <span className="font-medium">Q:</span> {o.objection ?? "Unspecified objection"}
                </p>
                {o.response && (
                  <p className="mt-0.5 text-[var(--muted-foreground)]">
                    <span className="font-medium">A:</span> {o.response}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {isString(b.recommended_icp) && (
        <Section label="Recommended ICP">
          <p className="text-[var(--foreground)]">{b.recommended_icp}</p>
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
