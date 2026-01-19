/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      // GCS Storage domains
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
      },
      // CDN domain (if configured)
      ...(process.env.GCS_CDN_URL ? [{
        protocol: 'https',
        hostname: new URL(process.env.GCS_CDN_URL).hostname,
      }] : []),
    ],
    formats: ['image/webp', 'image/avif'],
    unoptimized: true
  },
  async rewrites() {
    const rewrites = [];

    // Add GCS storage rewrite if CDN URL is not configured
    if (!process.env.GCS_CDN_URL && process.env.GCS_BUCKET_NAME) {
      rewrites.push({
        source: '/storage/:path*',
        destination: `https://storage.googleapis.com/${process.env.GCS_BUCKET_NAME}/:path*`,
      });
    }

    // Add CDN rewrite if configured
    if (process.env.GCS_CDN_URL) {
      rewrites.push({
        source: '/storage/:path*',
        destination: `${process.env.GCS_CDN_URL}/:path*`,
      });
    }

    return rewrites;
  },
  // Environment variables for client-side access
  env: {
    GCS_CDN_URL: process.env.GCS_CDN_URL || '',
    STORAGE_BASE_URL: process.env.GCS_CDN_URL ||
      (process.env.GCS_BUCKET_NAME ? `https://storage.googleapis.com/${process.env.GCS_BUCKET_NAME}` : ''),
  },
  // webpack config removed (Sentry uninstalled)
}

// module.exports = withSentryConfig(nextConfig, ...); // Disabled
module.exports = nextConfig;
