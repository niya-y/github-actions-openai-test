import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // reactCompiler: true,
  // output: 'export',
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Image optimization 비활성화 (400 에러 해결)
  images: {
    unoptimized: true,
  },

  // Performance optimization
  // 1. Production code splitting and bundling
  productionBrowserSourceMaps: false, // Production에서 source map 비활성화

  // 2. Compression settings
  compress: true,

  // 3. Static generation optimization
  staticPageGenerationTimeout: 60,

  // 4. Webpack optimization
  webpack: (config) => {
    // Development 환경에서도 최소화하여 번들 크기 확인 가능
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        ...config.optimization?.splitChunks,
        chunks: 'all',
        cacheGroups: {
          // 공통 라이브러리를 별도 번들로 분리
          common: {
            minChunks: 2,
            priority: 10,
            reuseExistingChunk: true,
          },
          // React 관련 라이브러리
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom|react-datepicker)[\\/]/,
            name: 'react-vendor',
            priority: 20,
            reuseExistingChunk: true,
          },
          // UI 라이브러리
          ui: {
            test: /[\\/]node_modules[\\/](@radix-ui|lucide-react|clsx|tailwind-merge)[\\/]/,
            name: 'ui-vendor',
            priority: 15,
            reuseExistingChunk: true,
          },
          // Animation 라이브러리
          animation: {
            test: /[\\/]node_modules[\\/](framer-motion)[\\/]/,
            name: 'animation-vendor',
            priority: 12,
            reuseExistingChunk: true,
          },
        },
      },
    };

    return config;
  },

  // 5. Experimental features for optimization
  experimental: {
    // Optimized package imports for lucide-react, clsx, etc
    optimizePackageImports: [
      'lucide-react',
      'clsx',
      'class-variance-authority',
    ],
  },

  // 6. Trailing slash 설정 (SEO optimization)
  trailingSlash: false,

  // 7. Internationalization (필요시 추가)
  // i18n: { ... }
};

export default nextConfig;
