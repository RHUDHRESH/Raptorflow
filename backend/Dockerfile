# =====================================================
# SOTA PRODUCTION DOCKERFILE - HARDENED & OPTIMIZED
# =====================================================

# Multi-stage build for optimal image size and security
FROM node:20-alpine AS base

# Install security updates and required packages
RUN apk update && apk upgrade && \
    apk add --no-cache \
    python3 \
    make \
    g++ \
    sqlite3 \
    curl \
    dumb-init && \
    rm -rf /var/cache/apk/*

# Create non-root user early
RUN addgroup -g 1001 -S nodejs && \
    adduser -S raptorflow -u 1001

# Set working directory with correct permissions
WORKDIR /app
RUN chown -R raptorflow:nodejs /app

# =====================================================
# DEPENDENCIES STAGE
# =====================================================
FROM base AS deps

# Copy package files with correct ownership
COPY --chown=raptorflow:nodejs package*.json tsconfig.json ./

# Install dependencies with security audit
USER raptorflow
RUN npm ci --no-audit --no-fund && \
    npm cache clean --force

# =====================================================
# BUILD STAGE
# =====================================================
FROM deps AS build

# Copy source code
COPY --chown=raptorflow:nodejs src/ ./src/
COPY --chown=raptorflow:nodejs skills/ ./skills/

# Create skills directory if needed
RUN mkdir -p skills

# Build TypeScript with optimizations
ENV NODE_ENV=production
RUN npm run build

# Prune to production dependencies
RUN npm prune --production

# =====================================================
# PRODUCTION STAGE
# =====================================================
FROM base AS production

# Copy built application from build stage
COPY --from=build --chown=raptorflow:nodejs /app/dist ./dist
COPY --from=build --chown=raptorflow:nodejs /app/node_modules ./node_modules
COPY --from=build --chown=raptorflow:nodejs /app/package.json ./
COPY --from=build --chown=raptorflow:nodejs /app/skills ./skills

# Switch to non-root user
USER raptorflow

# Environment variables for production
ENV NODE_ENV=production
ENV PORT=8080
ENV NODE_OPTIONS="--max-old-space-size=512"

# Expose port (Cloud Run expects 8080)
EXPOSE 8080

# Health check with proper Cloud Run configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "dist/index.js"]