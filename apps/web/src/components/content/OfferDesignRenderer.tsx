"use client";

import type { ReactElement } from "react";

interface ObjectionItem {
  objection?: string;
  response?: string;
}

export interface OfferDesignBody {
  offer_name?: string;
  promise?: string;
  included_items?: string[];
  pricing_notes?: string;
  risk_reversals?: string[];
  objections?: ObjectionItem[];
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

function isObjectionItem(value: unknown): value is ObjectionItem {
  return isRecord(value);
}

function isObjectionArray(value: unknown): value is ObjectionItem[] {
  return Array.isArray(value) && value.every(isObjectionItem);
}

export function isOfferDesignBody(body: unknown): body is OfferDesignBody {
  return isRecord(body);
}

export function OfferDesignRenderer({ body }: { body: unknown }): ReactElement {
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
      {isString(b.offer_name) && (
        <Section label="Offer Name">
          <p className="text-[var(--foreground)] font-[family-name:var(--font-display)] text-lg">
            {b.offer_name}
          </p>
        </Section>
      )}

      {isString(b.promise) && (
        <Section label="Promise">
          <p className="text-[var(--foreground)]">{b.promise}</p>
        </Section>
      )}

      {isStringArray(b.included_items) && b.included_items.length > 0 && (
        <Section label="What's Included">
          <UlList items={b.included_items} />
        </Section>
      )}

      {isString(b.pricing_notes) && (
        <Section label="Pricing / Packaging">
          <p className="text-[var(--foreground)]">{b.pricing_notes}</p>
        </Section>
      )}

      {isStringArray(b.risk_reversals) && b.risk_reversals.length > 0 && (
        <Section label="Risk Reversals">
          <UlList items={b.risk_reversals} />
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
