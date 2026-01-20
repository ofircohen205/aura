/** @type {import('next').NextConfig} */
const nextConfig = {
  // Only use standalone output for Docker builds, not for Vercel
  // Vercel has its own optimized build process
  ...(process.env.DOCKER_BUILD === "true" && { output: "standalone" }),

  // Optimize for production builds
  swcMinify: true,
  compress: true,

  // Exclude devDependencies from serverless functions
  experimental: {
    serverComponentsExternalPackages: [],
  },

  // Optimize images
  images: {
    formats: ["image/avif", "image/webp"],
  },

  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
