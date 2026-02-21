import { withSentryConfig } from "@sentry/nextjs";

const nextConfig = {
  reactStrictMode: true,
  // Keep build artifacts out of the repo root (and out of `.next/`).
  distDir: ".build/next",
  experimental: {
    workerThreads: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  webpack: (config, { isServer, dev }) => {
    if (isServer) {
      config.externals.push("@sentry/profiling-node");
    }

    // Avoid large on-disk webpack caches (especially in CI / constrained environments).
    if (!dev) {
      config.cache = { type: "memory" };
    }

    return config;
  },
};

export default withSentryConfig(
  nextConfig,
  {
    silent: true,
    org: "raptorflow",
    project: "raptorflow-nextjs",
  },
  {
    widenClientFileUpload: true,
    transpileClientSDK: false,
    tunnelRoute: "/monitoring",
    hideSourceMaps: true,
    disableLogger: true,
  }
);
