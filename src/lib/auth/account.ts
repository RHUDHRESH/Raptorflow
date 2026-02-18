export const ACCOUNT_PROFILE_REQUIRED_FIELDS = ["full_name"] as const;

type AuthUserLike = {
  user_metadata?: Record<string, unknown> | null;
  raw_user_meta_data?: Record<string, unknown> | null;
  account?: {
    profile_complete?: boolean;
  } | null;
} | null | undefined;

export type AccountProfileState = {
  profileComplete: boolean;
  missingRequiredFields: string[];
};

function isNonEmptyString(value: unknown): boolean {
  return typeof value === "string" && value.trim().length > 0;
}

export function getAccountProfileState(user: AuthUserLike): AccountProfileState {
  if (!user) {
    return {
      profileComplete: false,
      missingRequiredFields: [...ACCOUNT_PROFILE_REQUIRED_FIELDS],
    };
  }

  if (typeof user.account?.profile_complete === "boolean") {
    return {
      profileComplete: user.account.profile_complete,
      missingRequiredFields: user.account.profile_complete
        ? []
        : [...ACCOUNT_PROFILE_REQUIRED_FIELDS],
    };
  }

  const metadata = {
    ...(user.raw_user_meta_data ?? {}),
    ...(user.user_metadata ?? {}),
  };

  const missingRequiredFields = ACCOUNT_PROFILE_REQUIRED_FIELDS.filter(
    (field) => !isNonEmptyString(metadata[field])
  );

  return {
    profileComplete: missingRequiredFields.length === 0,
    missingRequiredFields,
  };
}

export function isAccountProfileComplete(user: AuthUserLike): boolean {
  return getAccountProfileState(user).profileComplete;
}
