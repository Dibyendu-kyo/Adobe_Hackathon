/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['python-shell'],
  },
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.externals.push('python-shell');
    }
    return config;
  },
  // Enable static exports for broader deployment compatibility
  output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,
  // Increase API timeout for Python processing
  api: {
    responseLimit: false,
    bodyParser: {
      sizeLimit: '50mb',
    },
  },
  // Enable CORS for universal access
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
};

export default nextConfig;