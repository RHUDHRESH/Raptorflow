import path from "node:path";
import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";
import { sentryAuthToken, sentryOrg, sentryProject, sentryRelease } from "./src/lib/sentry";

const shouldUploadSentrySourceMaps = Boolean(
  sentryAuthToken &&
    (process.env.CI === "true" ||
      process.env.VERCEL === "1" ||
      process.env.SENTRY_UPLOAD_SOURCE_MAPS === "1"),
);

const nextConfig: NextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(process.cwd(), "../.."),
  productionBrowserSourceMaps: shouldUploadSentrySourceMaps,
  transpilePackages: ["@raptorflow/database", "@raptorflow/contracts"],
  webpack(config) {
    config.resolve.extensionAlias = {
      ...config.resolve.extensionAlias,
      ".js": [".ts", ".tsx", ".js", ".jsx"],
    };
    return config;
  },
};

const sentryConfig = {
  org: sentryOrg,
  project: sentryProject,
  authToken: shouldUploadSentrySourceMaps ? sentryAuthToken : undefined,
  silent: !shouldUploadSentrySourceMaps,
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
