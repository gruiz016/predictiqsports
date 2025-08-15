// web/next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Speed up dev by ignoring heavy folders when using Webpack (Turbopack ignores this).
  webpack: (config, { dev }) => {
    if (dev) {
      const ignored = [
        '**/.git/**',
        '**/.next/**',
        '**/node_modules/**',
        '../api/.venv/**',
        '../api/.pytest_cache/**',
        '../api/__pycache__/**',
        '**/*.pyc',
      ];
      config.watchOptions = {
        ...(config.watchOptions || {}),
        ignored,
      };
    }
    return config;
  },
};
export default nextConfig;
