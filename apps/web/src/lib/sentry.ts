const DEFAULT_ORG = "raptorflow";
const DEFAULT_PROJECT = "javascript-nextjs";

function read(value: string | undefined | null): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

export const sentryOrg = read(process.env.SENTRY_ORG) ?? DEFAULT_ORG;
export const sentryProject = read(process.env.SENTRY_PROJECT) ?? DEFAULT_PROJECT;
export const sentryAuthToken = read(process.env.SENTRY_AUTH_TOKEN);
export const sentryRelease =
  read(process.env.SENTRY_RELEASE) ??
  read(process.env.VERCEL_GIT_COMMIT_SHA) ??
  read(process.env.VERCEL_GITHUB_COMMIT_SHA);
export const sentryEnvironment =
  read(process.env.SENTRY_ENVIRONMENT) ??
  read(process.env.NEXT_PUBLIC_APP_ENV) ??
  read(process.env.APP_ENV) ??
  read(process.env.NODE_ENV) ??
  "development";
export const sentryPublicDsn =
  read(process.env.NEXT_PUBLIC_SENTRY_DSN) ??
  read(process.env.SENTRY_DSN) ??
  read(process.env.RAPTORFLOW_SENTRY_DSN);
export const sentryServerDsn =
  read(process.env.RAPTORFLOW_SENTRY_DSN) ??
  read(process.env.SENTRY_DSN) ??
  read(process.env.NEXT_PUBLIC_SENTRY_DSN);
