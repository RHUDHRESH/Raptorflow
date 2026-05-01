import { execFileSync } from "node:child_process";
import path from "node:path";
import { test as setup } from "@playwright/test";
import { clerkSetup } from "@clerk/testing/playwright";
import {
  createLiveSmokeOrganization,
  deriveInternalOrgId,
  ensureLiveSmokeIdentity,
  decodeJwtPayload,
  E2E_AUTH_STATE_PATH,
  E2E_CLERK_EMAIL,
  activateLiveSmokeOrganization,
  readSessionToken,
  stampLiveSmokeOrganizationMetadata,
  signInLiveSmokeUser,
} from "./auth";

setup.describe.configure({ mode: "serial" });

setup("configure Clerk testing", async () => {
  await clerkSetup();
});

setup("authenticate live smoke user and seed data", async ({ page }) => {
  const identity = await ensureLiveSmokeIdentity();

  await signInLiveSmokeUser(page);
  const organizationId = await createLiveSmokeOrganization(identity.userId, identity.orgName);
  const internalOrgId = deriveInternalOrgId(organizationId);
  await stampLiveSmokeOrganizationMetadata(organizationId, internalOrgId, identity.orgRole);
  await activateLiveSmokeOrganization(page, organizationId);

  const token = await readSessionToken(page);
  const claims = decodeJwtPayload(token);

  const clerkOrg = claims.o as
    | {
        id?: string;
        rol?: string;
      }
    | undefined;

  const userId = String(claims.sub ?? claims.user_id ?? "");
  const clerkOrgId = String(clerkOrg?.id ?? claims.org_id ?? "");
  const orgRole = String(claims.org_role ?? clerkOrg?.rol ?? "");
  const orgId = deriveInternalOrgId(clerkOrgId);

  if (!userId) {
    throw new Error("Clerk session token did not include a user id");
  }

  if (!clerkOrgId) {
    throw new Error("Clerk session token did not include an active organization claim.");
  }

  if (!/^[0-9a-fA-F-]{36}$/.test(orgId)) {
    throw new Error(
      `Derived org_id must be a UUID for this repo's tenant model, but received: ${orgId}`,
    );
  }

  if (orgId !== internalOrgId) {
    throw new Error(
      `Derived org_id did not match the smoke org UUID. Expected ${internalOrgId}, received ${orgId}.`,
    );
  }

  if (userId !== identity.userId) {
    throw new Error(
      `Clerk user id claim did not match the smoke user. Expected ${identity.userId}, received ${userId}.`,
    );
  }

  const scriptPath = path.resolve(
    "..",
    "..",
    "packages",
    "database",
    "scripts",
    "seed-live-smoke.mjs",
  );

  execFileSync(process.execPath, [scriptPath], {
    stdio: "inherit",
    env: {
      ...process.env,
      LIVE_SMOKE_USER_ID: userId,
      LIVE_SMOKE_USER_EMAIL: E2E_CLERK_EMAIL,
      LIVE_SMOKE_ORG_ID: orgId,
      LIVE_SMOKE_ORG_ROLE: orgRole || identity.orgRole,
      LIVE_SMOKE_SESSION_ID: String(claims.sid ?? ""),
      LIVE_SMOKE_ORGANIZATION_ID: organizationId,
    },
  });

  await page.context().storageState({ path: E2E_AUTH_STATE_PATH });
});
