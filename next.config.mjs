import { withSentryConfig } from '@sentry/nextjs';

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Your existing Next.js configuration
  reactStrictMode: true,
  experimental: {
    // `next build` uses jest-worker which forks processes on Windows by default and can fail with EPERM
    // (common under OneDrive/AV locked down environments). Worker threads avoid `child_process.spawn`.
    workerThreads: true,
    // Enable optimizePackageImports for better tree-shaking
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons', 'recharts'],
  },
  typescript: {
    // We enforce types via `npm run type-check` (see package.json).
    // Next's built-in type check can fail on legacy files during build.
    ignoreDuringBuilds: true,
  },
  eslint: {
    // We enforce lint via `npm run lint` (see package.json).
    // Next's built-in lint uses different config resolution and can fail on legacy files.
    ignoreDuringBuilds: true,
  },
  // Webpack configuration
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.externals.push('@sentry/profiling-node');
    }
    
    // Optimize bundle splitting
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          // Vendor chunk for node_modules
          vendor: {
            name: 'vendor',
            chunks: 'all',
            test: /node_modules/,
            priority: 20,
          },
          // Common chunk for shared code
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
            enforce: true,
          },
          // UI components chunk
          ui: {
            name: 'ui',
            test: /[\\/]src[\\/](shared|components)[\\/]ui[\\/]/,
            chunks: 'all',
            priority: 30,
          },
          // Feature chunks
          features: {
            name: 'features',
            test: /[\\/]src[\\/]features[\\/]/,
            chunks: 'async',
            priority: 25,
          },
        },
      },
    };
    
    return config;
  },
  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};

export default withBundleAnalyzer(withSentryConfig(
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
));
