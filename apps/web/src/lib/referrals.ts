export type ReferralCode = "LOKI" | "R2005" | "DUNE";

export type ReferralOffer = {
  code: ReferralCode;
  planName: "Ascend" | "Glide" | "Soar";
  planTier: "ascend" | "glide" | "soar";
};

const REFERRAL_OFFERS: Record<ReferralCode, ReferralOffer> = {
  LOKI: {
    code: "LOKI",
    planName: "Ascend",
    planTier: "ascend",
  },
  R2005: {
    code: "R2005",
    planName: "Glide",
    planTier: "glide",
  },
  DUNE: {
    code: "DUNE",
    planName: "Soar",
    planTier: "soar",
  },
};

export function normalizeReferralCode(value: string | null | undefined): ReferralCode | null {
  const code = value?.trim().toUpperCase();
  if (!code) return null;
  return code in REFERRAL_OFFERS ? (code as ReferralCode) : null;
}

export function getReferralOffer(code: string | null | undefined): ReferralOffer | null {
  const normalized = normalizeReferralCode(code);
  return normalized ? REFERRAL_OFFERS[normalized] : null;
}

export function referralSignupHref(code: ReferralCode): string {
  return `/sign-up?referral=${encodeURIComponent(code)}`;
}

export function referralOfferLabel(code: ReferralCode): string {
  return `${REFERRAL_OFFERS[code].planName} via ${code}`;
}

