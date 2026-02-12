# RaptorFlow Production Dockerfile
# Multi-stage build for optimized production images

# =============================================
# Stage 1: Backend Dependencies
# =============================================
FROM python:3.12-slim AS backend-deps

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =============================================
# Stage 2: Frontend Builder
# =============================================
FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source files
COPY . .

# Build Next.js app
RUN npm run build

# =============================================
# Stage 3: Production Runtime
# =============================================
FROM python:3.12-slim AS production

WORKDIR /app

# Install Node.js for Next.js runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY --from=backend-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-builder /app/.next ./.next
COPY --from=frontend-builder /app/public ./public
COPY --from=frontend-builder /app/package*.json ./
COPY --from=frontend-builder /app/node_modules ./node_modules

# Copy entrypoint
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Environment
ENV PYTHONPATH=/app
ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/api/ops/health || exit 1

CMD ["./docker-entrypoint.sh"]
