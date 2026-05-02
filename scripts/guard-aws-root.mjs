#!/usr/bin/env node

import { execFileSync } from "node:child_process";

const MOCK_IDENTITY_ENV = "AWS_GUARD_MOCK_IDENTITY_JSON";

function hasAwsCredentials() {
  return Boolean(process.env.AWS_ACCESS_KEY_ID && process.env.AWS_SECRET_ACCESS_KEY);
}

function isRootArn(arn) {
  return /^arn:aws(?:-[a-z-]+)?:iam::\d{12}:root$/.test(arn);
}

function readMockIdentity() {
  const raw = process.env[MOCK_IDENTITY_ENV];
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch (err) {
    console.error(`[GUARD AWS] Invalid ${MOCK_IDENTITY_ENV}:`, err.message);
    process.exit(1);
  }
}

function getCallerIdentity() {
  const mockIdentity = readMockIdentity();
  if (mockIdentity) return mockIdentity;

  try {
    const stdout = execFileSync("aws", ["sts", "get-caller-identity", "--output", "json"], {
      encoding: "utf-8",
      timeout: 10_000,
    });
    return JSON.parse(stdout);
  } catch (err) {
    if (err.code === "ENOENT") {
      console.warn("[GUARD AWS] AWS CLI not found — skipping root principal check.");
      return null;
    }

    console.error("[GUARD AWS] Failed to call sts get-caller-identity:", err.message);
    process.exit(1);
  }
}

function checkAwsPrincipal() {
  if (!hasAwsCredentials() && !readMockIdentity()) {
    console.warn("[GUARD AWS] No AWS credentials found — skipping root principal check.");
    return;
  }

  console.log("[GUARD AWS] AWS credentials detected. Verifying principal...");

  const identity = getCallerIdentity();
  if (!identity) return;

  const arn = identity.Arn ?? "";
  if (isRootArn(arn)) {
    console.error("[GUARD AWS] FATAL: AWS credentials resolve to the ROOT user:", arn);
    console.error(
      "[GUARD AWS] Root credentials give full, unrestricted access to the AWS account.",
    );
    console.error("[GUARD AWS] Do not use root access keys for local development or CI/CD.");
    console.error(
      "[GUARD AWS] For long-term fix: create an IAM user/role with least-privilege policies.",
    );
    process.exit(1);
  }

  if (process.env.ALLOW_LIVE_AWS_WRITES === "1") {
    console.warn("[GUARD AWS] Live AWS writes are explicitly enabled for this environment.");
  }

  console.log("[GUARD AWS] Principal:", arn, "— OK");
}

checkAwsPrincipal();
