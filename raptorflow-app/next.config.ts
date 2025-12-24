import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Externalize pg to avoid Turbopack symlink issues on Windows
  serverExternalPackages: ['pg'],
};

export default nextConfig;
