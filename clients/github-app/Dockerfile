FROM node:20-slim

LABEL org.opencontainers.image.source="https://github.com/ofircohen205/aura"
LABEL org.opencontainers.image.description="Aura GitHub App - Probot Application"
LABEL org.opencontainers.image.licenses="MIT"

# Create app directory
WORKDIR /app

# Install production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Set environment variables
ENV NODE_ENV=production
ENV LOG_LEVEL=info

# Expose port for webhook server
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))" || exit 1

# Run the application
CMD ["npm", "start"]
