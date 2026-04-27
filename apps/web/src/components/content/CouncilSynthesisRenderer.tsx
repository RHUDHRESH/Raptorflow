"use client";

import type { ReactElement } from "react";

interface RiskItem {
  risk?: string;
  severity?: string;
  mitigation?: string;
}

interface ActionItem {
  action?: string;
  owner?: string;
  priority?: string;
}

export interface CouncilSynthesisBody {
  strategic_recommendation?: string;
  known_facts?: string[];
  assumptions?: string[];
  risks?: RiskItem[];
  next_actions?: ActionItem[];
  open_questions?: string[];
  synthesized_by?: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((v) => typeof v === "string");
}

function isRiskItem(value: unknown): value is RiskItem {
  return isRecord(value);
}

function isRiskArray(value: unknown): value is RiskItem[] {
  return Array.isArray(value) && value.every(isRiskItem);
}

function isActionItem(value: unknown): value is ActionItem {
  return isRecord(value);
}

function isActionArray(value: unknown): value is ActionItem[] {
  return Array.isArray(value) && value.every(isActionItem);
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

export function isCouncilSynthesisBody(body: unknown): body is CouncilSynthesisBody {
  if (!isRecord(body)) return false;
  return true;
}

export function CouncilSynthesisRenderer({ body }: { body: unknown }): ReactElement {
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
      {isString(b.strategic_recommendation) && (
        <Section label="Strategic Recommendation">
          <p className="text-[var(--foreground)]">{b.strategic_recommendation}</p>
        </Section>
      )}

      {isStringArray(b.known_facts) && b.known_facts.length > 0 && (
        <Section label="Known Facts">
          <UlList items={b.known_facts} />
        </Section>
      )}

      {isStringArray(b.assumptions) && b.assumptions.length > 0 && (
        <Section label="Assumptions">
          <UlList items={b.assumptions} />
        </Section>
      )}

      {isRiskArray(b.risks) && b.risks.length > 0 && (
        <Section label="Risks">
          <div className="space-y-2">
            {b.risks.map((r, i) => (
              <div key={i} className="border-l-2 border-[var(--border)] pl-3">
                <p className="text-[var(--foreground)]">{r.risk ?? "Unnamed risk"}</p>
                <div className="mt-1 flex gap-3 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)]">
                  {r.severity && <span>Severity: {r.severity}</span>}
                  {r.mitigation && <span>Mitigation: {r.mitigation}</span>}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {isActionArray(b.next_actions) && b.next_actions.length > 0 && (
        <Section label="Next Actions">
          <div className="space-y-2">
            {b.next_actions.map((a, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#D97757]" />
                <div>
                  <p className="text-[var(--foreground)]">{a.action ?? "Unnamed action"}</p>
                  <div className="flex gap-3 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)]">
                    {a.owner && <span>Owner: {a.owner}</span>}
                    {a.priority && <span>Priority: {a.priority}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {isStringArray(b.open_questions) && b.open_questions.length > 0 && (
        <Section label="Open Questions">
          <UlList items={b.open_questions} />
        </Section>
      )}

      {isString(b.synthesized_by) && (
        <p className="font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)]">
          Synthesized by: {b.synthesized_by}
        </p>
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
