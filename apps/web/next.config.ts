import path from "node:path";
import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";
import {
  sentryAuthToken,
  sentryOrg,
  sentryProject,
  sentryRelease,
} from "./src/lib/sentry";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(process.cwd(), "../.."),
  productionBrowserSourceMaps: true,
  transpilePackages: ["@raptorflow/database", "@raptorflow/contracts"],
};

const sentryConfig = {
  org: sentryOrg,
  project: sentryProject,
  authToken: sentryAuthToken,
  silent: !sentryAuthToken,
  debug: process.env.NODE_ENV === "development",
  widenClientFileUpload: true,
  release: {
    name: sentryRelease,
    create: true,
    finalize: true,
  },
  sourcemaps: {
    deleteSourcemapsAfterUpload: true,
  },
};

export default withSentryConfig(nextConfig, sentryConfig);
