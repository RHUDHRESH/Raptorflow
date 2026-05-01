import { createClerkClient } from "@clerk/backend";
import { clerk } from "@clerk/testing/playwright";
import { existsSync, readFileSync } from "node:fs";
import type { Page } from "@playwright/test";
import { createHash } from "node:crypto";

export const E2E_AUTH_STATE_PATH = "playwright/.clerk/user.json";
export const E2E_CLERK_EMAIL = process.env.E2E_CLERK_USER_EMAIL ?? "e2e+clerk_test@example.com";
export const E2E_CLERK_PASSWORD = "LiveSmoke!12345";

type LiveSmokeIdentity = {
  userId: string;
  email: string;
  orgRole: string;
  orgName: string;
};

export function deriveInternalOrgId(clerkOrgId: string): string {
  const digest = createHash("sha256").update("raptorflow-clerk-org:").update(clerkOrgId).digest();
  const bytes = Buffer.from(digest.subarray(0, 16));
  bytes[6] = (bytes[6] & 0x0f) | 0x50;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = bytes.toString("hex");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(
    16,
    20,
  )}-${hex.slice(20, 32)}`;
}

function getClerkClient() {
  const secretKey = process.env.CLERK_SECRET_KEY;
  if (!secretKey) {
    throw new Error("CLERK_SECRET_KEY is required for live smoke auth setup");
  }

  return createClerkClient({
    secretKey,
    apiUrl: process.env.CLERK_API_URL,
  });
}

export async function ensureLiveSmokeIdentity(): Promise<LiveSmokeIdentity> {
  const client = getClerkClient();

  const existingUsers = await client.users.getUserList({
    emailAddress: [E2E_CLERK_EMAIL],
    limit: 1,
  });

  const user =
    existingUsers.data[0] ??
    (await client.users.createUser({
      emailAddress: [E2E_CLERK_EMAIL],
      firstName: "Live",
      lastName: "Smoke",
      password: E2E_CLERK_PASSWORD,
      skipPasswordChecks: true,
      skipPasswordRequirement: true,
    }));

  await client.users.updateUser(user.id, {
    createOrganizationEnabled: true,
    createOrganizationsLimit: 1,
  });

  return {
    userId: user.id,
    email: E2E_CLERK_EMAIL,
    orgRole: "org:admin",
    orgName: "Live Smoke Org",
  };
}

export async function createLiveSmokeOrganization(
  userId: string,
  orgName: string,
): Promise<string> {
  const client = getClerkClient();
  const existingOrganizations = await client.organizations.getOrganizationList({ limit: 20 });
  const existing =
    existingOrganizations.data.find((organization) => organization.name === orgName) ??
    existingOrganizations.data.find((organization) => organization.name === "My Organization");

  if (existing) {
    if (existing.name !== orgName) {
      await client.organizations.updateOrganization(existing.id, { name: orgName });
    }
    return existing.id;
  }

  const created = await client.organizations.createOrganization({
    name: orgName,
    createdBy: userId,
  });
  return created.id;
}

export async function stampLiveSmokeOrganizationMetadata(
  organizationId: string,
  internalOrgId: string,
  orgRole: string,
): Promise<void> {
  const client = getClerkClient();
  await client.organizations.updateOrganizationMetadata(organizationId, {
    publicMetadata: {
      org_id: internalOrgId,
      org_role: orgRole,
      smoke_test: true,
    },
  });
}

export async function signInLiveSmokeUser(page: Page): Promise<void> {
  const cookies = await page.context().cookies();
  if (
    cookies.some(
      (cookie) =>
        cookie.name === "__session" ||
        cookie.name.startsWith("__session_") ||
        cookie.name === "clerk_active_context" ||
        cookie.name === "__clerk_db_jwt" ||
        cookie.name.startsWith("__clerk_db_jwt_"),
    )
  ) {
    return;
  }

  if (existsSync(E2E_AUTH_STATE_PATH)) {
    try {
      const storageState = JSON.parse(readFileSync(E2E_AUTH_STATE_PATH, "utf8")) as {
        cookies?: Array<{
          name: string;
          value: string;
          domain: string;
          path: string;
          expires?: number;
          httpOnly?: boolean;
          secure?: boolean;
          sameSite?: "Lax" | "None" | "Strict";
        }>;
      };

      if (storageState.cookies?.length) {
        await page.context().addCookies(storageState.cookies);
        return;
      }
    } catch (error) {
      console.warn(
        "[auth] Failed to reuse saved Clerk auth state, falling back to UI sign-in:",
        error,
      );
    }
  }

  try {
    await page.goto("/", { waitUntil: "domcontentloaded" });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (
      !message.includes("ERR_ABORTED") &&
      !message.includes("frame was detached") &&
      !message.includes("Navigation timeout")
    ) {
      throw error;
    }
  }
  if (
    await page
      .getByRole("button", { name: /open user menu/i })
      .isVisible()
      .catch(() => false)
  ) {
    return;
  }

  try {
    await page.goto("/sign-in", { waitUntil: "domcontentloaded", timeout: 10_000 });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (
      !message.includes("ERR_ABORTED") &&
      !message.includes("frame was detached") &&
      !message.includes("Navigation timeout")
    ) {
      throw error;
    }
  }
  try {
    await clerk.signIn({
      page,
      emailAddress: E2E_CLERK_EMAIL,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (!message.includes("already signed in")) {
      throw error;
    }
  }
}

export async function activateLiveSmokeOrganization(page: Page, orgId: string): Promise<void> {
  const cookies = await page.context().cookies();
  if (
    cookies.some(
      (cookie) =>
        cookie.name === "__session" ||
        cookie.name.startsWith("__session_") ||
        cookie.name === "clerk_active_context" ||
        cookie.name === "__clerk_db_jwt" ||
        cookie.name.startsWith("__clerk_db_jwt_"),
    )
  ) {
    return;
  }

  await page.waitForFunction(() => {
    const clerk = (
      window as Window & {
        Clerk?: {
          loaded?: boolean;
          setActive?: (options: { organization: string }) => Promise<void>;
        };
      }
    ).Clerk;

    return Boolean(clerk?.loaded);
  });
  try {
    await page.evaluate((organizationId) => {
      const clerk = (
        window as Window & {
          Clerk?: {
            setActive?: (options: { organization: string }) => Promise<void>;
          };
        }
      ).Clerk;

      if (!clerk) {
        throw new Error("Clerk is not available in the browser context");
      }

      void clerk.setActive({ organization: organizationId });
    }, orgId);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (!message.includes("Execution context was destroyed")) {
      throw error;
    }
  }

  await page.waitForLoadState("domcontentloaded").catch(() => {});
  await page.waitForTimeout(1000);

  await page
    .waitForFunction(
      (organizationId) => {
        const clerk = (
          window as Window & {
            Clerk?: {
              organization?: { id?: string };
            };
          }
        ).Clerk;

        return clerk?.organization?.id === organizationId;
      },
      orgId,
      { timeout: 15_000 },
    )
    .catch(() => {});
}

export async function prepareLiveSmokePage(page: Page): Promise<void> {
  const identity = await ensureLiveSmokeIdentity();

  await signInLiveSmokeUser(page);
  const organizationId = await createLiveSmokeOrganization(identity.userId, identity.orgName);
  const internalOrgId = deriveInternalOrgId(organizationId);
  await stampLiveSmokeOrganizationMetadata(organizationId, internalOrgId, identity.orgRole);
  await activateLiveSmokeOrganization(page, organizationId);
}

export async function readSessionToken(page: Page): Promise<string> {
  const token = await page.evaluate(async () => {
    const clerk = (
      window as Window & {
        Clerk?: {
          session?: {
            getToken?: () => Promise<string | null>;
          };
        };
      }
    ).Clerk;

    return clerk?.session?.getToken ? clerk.session.getToken() : null;
  });

  if (token) {
    return token;
  }

  const cookies = await page.context().cookies();
  const sessionCookie = cookies.find(
    (cookie) => cookie.name === "__session" || cookie.name.startsWith("__session_"),
  )?.value;

  if (sessionCookie) {
    return sessionCookie;
  }

  throw new Error("Clerk session token was not available after sign-in");
}

export function decodeJwtPayload(token: string): Record<string, unknown> {
  const [, payload] = token.split(".");
  if (!payload) {
    throw new Error("Invalid JWT token");
  }

  return JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as Record<string, unknown>;
}
