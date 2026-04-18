import type * as React from "react";
import Link from "next/link";
import type { Route } from "next";
import { SignUp } from "@clerk/nextjs";
import { getReferralOffer, referralSignupHref } from "@/lib/referrals";

type SignUpSearchParams = Record<string, string | string[] | undefined>;

function firstValue(value: string | string[] | undefined): string | null {
  if (Array.isArray(value)) return value[0] ?? null;
  return value ?? null;
}

export default async function SignUpPage({
  searchParams,
}: {
  searchParams?: Promise<SignUpSearchParams>;
}): Promise<React.ReactElement> {
  const resolvedSearchParams = await searchParams;
  const referralCode = getReferralOffer(
    firstValue(resolvedSearchParams?.referral) ??
      firstValue(resolvedSearchParams?.code) ??
      firstValue(resolvedSearchParams?.plan),
  );

  return (
    <div className="space-y-6">
      <div className="rounded-none border border-[var(--border)] bg-[var(--card)] p-5 shadow-none">
        <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
          Access codes
        </p>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          {[
            { code: "LOKI" as const, label: "Ascend", description: "100% off" },
            { code: "R2005" as const, label: "Glide", description: "100% off" },
            { code: "DUNE" as const, label: "Soar", description: "100% off" },
          ].map((offer) => (
            <Link
              key={offer.code}
              href={referralSignupHref(offer.code) as Route}
              className={`border px-4 py-3 transition-colors ${
                referralCode?.code === offer.code
                  ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--foreground)]"
                  : "border-[var(--border)] bg-transparent text-[var(--muted-foreground)] hover:bg-[var(--accent)] hover:text-[var(--foreground)]"
              }`}
            >
              <div className="font-mono text-[10px] uppercase tracking-[0.24em]">
                {offer.code}
              </div>
              <div className="mt-1 font-[family-name:var(--font-display)] text-lg text-[var(--foreground)]">
                {offer.label}
              </div>
              <div className="mt-1 text-xs uppercase tracking-[0.2em]">{offer.description}</div>
            </Link>
          ))}
        </div>
        <p className="mt-4 text-sm text-[var(--muted-foreground)] leading-6">
          Use one of the codes above if you were invited. The code is written into your
          Clerk signup metadata so the backend can activate the matching plan on first
          workspace creation.
        </p>
        {referralCode ? (
          <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--primary)]">
            Applied code: {referralCode.code} · {referralCode.planName} unlocked
          </p>
        ) : (
          <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
            No code selected yet. Pick one above to continue with the matching plan.
          </p>
        )}
      </div>

      <SignUp
        forceRedirectUrl="/app"
        fallbackRedirectUrl="/app"
        unsafeMetadata={
          referralCode
            ? {
                referralCode: referralCode.code,
                referralPlan: referralCode.planName,
                referralTier: referralCode.planTier,
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
