#!/usr/bin/env node

const { execSync } = require("child_process");

function checkAwsPrincipal() {
  const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
  const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;

  if (!accessKeyId || !secretAccessKey) {
    console.log("[GUARD AWS] No AWS credentials found — skipping root check.");
    return;
  }

  console.log("[GUARD AWS] AWS credentials detected. Verifying principal...");

  let identity;
  try {
    const stdout = execSync("aws sts get-caller-identity --output json", {
      encoding: "utf-8",
      timeout: 10_000,
    });
    identity = JSON.parse(stdout);
  } catch (err) {
    console.error("[GUARD AWS] Failed to call sts get-caller-identity:", err.message);
    process.exit(1);
  }

  const arn = identity.Arn ?? "";
  if (arn.includes(":root:")) {
    console.error("[GUARD AWS] FATAL: AWS credentials resolve to the ROOT user:", arn);
    console.error(
      "[GUARD AWS] Root credentials give full, unrestricted access to the AWS account.",
    );
    console.error("[GUARD AWS] Do not use root access keys for local development or CI/CD.");
    console.error("");
    console.error("[GUARD AWS] To proceed anyway, set ALLOW_ROOT_AWS=1 in your environment.");
    console.error(
      "[GUARD AWS] For long-term fix: create an IAM user/role with least-privilege policies.",
    );

    if (process.env.ALLOW_ROOT_AWS !== "1") {
      process.exit(1);
    }
  }

  console.log("[GUARD AWS] Principal:", arn, "— OK");
}

checkAwsPrincipal();
