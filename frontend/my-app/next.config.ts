import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  // Image optimization 비활성화 (400 에러 해결)
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
