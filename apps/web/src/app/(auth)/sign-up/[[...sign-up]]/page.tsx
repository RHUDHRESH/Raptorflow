"use client";

import { useState, useEffect } from "react";
import type * as React from "react";
import { useSearchParams } from "next/navigation";
import { SignUp } from "@clerk/nextjs";
import { normalizeReferralCode, type ReferralCode } from "@/lib/referrals";

const REFERRAL_PLANS = [
  { code: "LOKI" as ReferralCode, plan: "Ascend", desc: "Full access" },
  { code: "R2005" as ReferralCode, plan: "Glide", desc: "Growth access" },
  { code: "DUNE" as ReferralCode, plan: "Soar", desc: "Starter access" },
];

export default function SignUpPage(): React.ReactElement {
  const searchParams = useSearchParams();
  const [referralInput, setReferralInput] = useState("");
  const [appliedCode, setAppliedCode] = useState<ReferralCode | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const param = searchParams.get("referral") ?? searchParams.get("code") ?? searchParams.get("plan");
    if (param) {
      const normalized = normalizeReferralCode(param);
      if (normalized) {
        setAppliedCode(normalized);
        setReferralInput(normalized);
      }
    }
  }, [searchParams]);

  const handleApplyCode = (code?: string) => {
    const raw = (code ?? referralInput).trim();
    if (!raw) {
      setError("Enter a referral code to unlock your plan.");
      setAppliedCode(null);
      return;
    }
    const normalized = normalizeReferralCode(raw);
    if (!normalized) {
      setError("Invalid code. Check with the person who invited you.");
      setAppliedCode(null);
      return;
    }
    setError(null);
    setAppliedCode(normalized);
    setReferralInput(normalized);
  };

  return (
    <div className="space-y-6">
      <div className="rounded-none border border-[var(--border)] bg-[var(--card)] p-5 shadow-none">
        <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
          Referral code
        </p>
        <div className="mt-3 flex gap-2">
          <input
            type="text"
            value={referralInput}
            onChange={(e) => {
              setReferralInput(e.target.value);
              if (error) setError(null);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleApplyCode();
            }}
            placeholder="Enter your referral code"
            className="flex-1 bg-[var(--background)] border border-[var(--border)] rounded-none h-12 px-4 font-mono text-sm focus:outline-none focus:ring-1 focus:ring-[var(--primary)]"
          />
          <button
            type="button"
            onClick={() => handleApplyCode()}
            className="bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 rounded-none h-12 px-6 font-mono uppercase tracking-widest text-[10px] border border-[var(--primary)]"
          >
            Apply
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-500">{error}</p>
        )}
        {appliedCode ? (
          <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--primary)]">
            Applied code: {appliedCode} · Plan unlocked
          </p>
        ) : (
          <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
            No code applied yet. Enter the code you received to unlock your plan.
          </p>
        )}

        <div className="mt-4 border-t border-[var(--border)] pt-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)] mb-2">
            Available plans
          </p>
          <div className="grid gap-2 sm:grid-cols-3">
            {REFERRAL_PLANS.map((plan) => (
              <button
                key={plan.code}
                type="button"
                onClick={() => handleApplyCode(plan.code)}
                className={`border px-3 py-2 text-left transition-colors ${
                  appliedCode === plan.code
                    ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--foreground)]"
                    : "border-[var(--border)] bg-transparent text-[var(--muted-foreground)] hover:bg-[var(--accent)] hover:text-[var(--foreground)]"
                }`}
              >
                <div className="font-mono text-[10px] uppercase tracking-[0.24em]">{plan.code}</div>
                <div className="font-[family-name:var(--font-display)] text-lg text-[var(--foreground)]">{plan.plan}</div>
                <div className="text-xs uppercase tracking-[0.2em]">{plan.desc}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <SignUp
        forceRedirectUrl="/app"
        fallbackRedirectUrl="/app"
        unsafeMetadata={
          appliedCode
            ? {
                referralCode: appliedCode,
              }
            : undefined
        }
        appearance={{
          elements: {
            rootBox: "w-full",
            card: "bg-[var(--card)] shadow-none border border-[var(--border)] rounded-none p-4",
            headerTitle: "font-[family-name:var(--font-display)] text-2xl text-[var(--foreground)]",
            headerSubtitle: "font-body text-[var(--muted-foreground)]",
            formButtonPrimary:
              "bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 rounded-none h-12 uppercase tracking-wider text-xs font-mono border border-[var(--primary)]",
            formFieldInput:
              "bg-[var(--background)] border border-[var(--border)] rounded-none h-12 px-4 focus:ring-1 focus:ring-[var(--primary)]",
            formFieldLabel:
              "font-mono uppercase tracking-widest text-[10px] text-[var(--muted-foreground)] mb-1",
            footerActionLink: "text-[var(--primary)] hover:text-[var(--primary)]/80 font-bold",
            socialButtonsBlockButton: "border border-[var(--border)] rounded-none h-12 hover:bg-[var(--accent)]",
            dividerLine: "bg-[var(--border)]",
            dividerText: "text-[var(--muted-foreground)] font-mono uppercase text-[10px]",
          },
        }}
      />
    </div>
  );
}