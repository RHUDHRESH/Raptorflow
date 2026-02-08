/** @type {import('next').NextConfig} */
import { withSentryConfig } from '@sentry/nextjs';

const nextConfig = {
  // Your existing Next.js configuration
  reactStrictMode: true,
  experimental: {
    // `next build` uses jest-worker which forks processes on Windows by default and can fail with EPERM
    // (common under OneDrive/AV locked down environments). Worker threads avoid `child_process.spawn`.
    workerThreads: true,
  },
  typescript: {
    // We enforce types via `npm run type-check` (see package.json).
    // Keeping Next's internal type-check disabled avoids duplicate work and Windows EPERM issues.
    ignoreBuildErrors: true,
  },
  eslint: {
    // We enforce lint via `npm run lint` (see package.json).
    // Next's built-in lint uses different config resolution and can fail on legacy files.
    ignoreDuringBuilds: true,
  },
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.externals.push('@sentry/profiling-node');
    }
    return config;
  },
};

export default withSentryConfig(
  nextConfig,
  {
    // For all available options, see:
    // https://github.com/getsentry/sentry-webpack-plugin#options

    // Suppresses source map uploading logs during build
    silent: true,
    org: "raptorflow",
    project: "raptorflow-nextjs",
  },
  {
    // For all available options, see:
    // https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/

    // Upload a larger set of source maps for prettier stack traces (increases build time)
    widenClientFileUpload: true,

    // Transpiles SDK to be compatible with IE11 (increases bundle size)
    transpileClientSDK: false,

    // Routes browser requests to Sentry through a Next.js rewrite to circumvent ad-blockers (increases server load)
    tunnelRoute: "/monitoring",

    // Hides source maps from generated client bundles
    hideSourceMaps: true,

    // Automatically tree-shake Sentry logger statements to reduce bundle size
    disableLogger: true,
  }
);
