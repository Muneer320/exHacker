import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable Turbopack — use Webpack instead
  webpack: (config) => {
    return config;
  },
};

export default nextConfig;
