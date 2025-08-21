/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    // For Docker containers, always use the service name during runtime
    // The backend service name is 'backend' as defined in docker-compose.yml
    const isProduction = process.env.NODE_ENV === 'production'
    const backendUrl = isProduction
      ? 'http://backend:8000' // Use Docker service name in production
      : 'http://localhost:8000' // Use localhost in development

    console.log(`API Rewrite configured for: ${backendUrl} (Production: ${isProduction})`)

    // Single rule; backend handles both with/without trailing slash
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
