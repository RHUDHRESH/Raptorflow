# 🚀 RaptorFlow Deployment Guide

## Overview
This guide covers deploying the RaptorFlow Marketing Operating System to production environments.

## Prerequisites

### Frontend Requirements
- Node.js 18+
- npm or yarn
- Modern web browser with JavaScript enabled

### Backend Requirements (Optional)
- Python 3.9+
- FastAPI
- PostgreSQL/MySQL for production database
- Redis for caching (recommended)

## Environment Setup

### 1. Clone and Install
```bash
git clone <repository-url>
cd raptorflow/frontend
npm install
```

### 2. Environment Variables
Create `.env.local` in the frontend root:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_WS_URL=wss://your-websocket-domain.com

# Feature Flags
NEXT_PUBLIC_ENABLE_AI=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=your-google-analytics-id
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# Deployment
NEXT_PUBLIC_DEPLOYMENT_ENV=production
```

### 3. Build and Deploy

#### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

#### Netlify
```bash
# Build
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=.next
```

#### Docker
```dockerfile
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM base AS builder
COPY . .
RUN npm run build

FROM base AS runner
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./

EXPOSE 3000
CMD ["npm", "start"]
```

#### AWS Amplify
```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize and deploy
amplify init
amplify add hosting
amplify publish
```

## Backend Deployment (Optional)

### FastAPI Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Docker Compose
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/raptorflow
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=raptorflow
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Production Optimizations

### 1. Performance
- Enable Next.js Image Optimization
- Implement proper caching strategies
- Use CDN for static assets
- Enable gzip compression

### 2. Security
- Implement rate limiting
- Add CSRF protection
- Use HTTPS everywhere
- Sanitize user inputs
- Implement proper authentication

### 3. Monitoring
- Set up error tracking (Sentry)
- Implement performance monitoring
- Add uptime monitoring
- Set up logging and alerting

### 4. SEO
- Implement proper meta tags
- Add structured data
- Create sitemap.xml
- Set up robots.txt

## Database Setup

### PostgreSQL (Production)
```sql
-- Create database
CREATE DATABASE raptorflow;

-- Create user
CREATE USER raptorflow_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE raptorflow TO raptorflow_user;

-- Run migrations
psql -U raptorflow_user -d raptorflow -f migrations.sql
```

### Redis (Caching)
```bash
# Install Redis
sudo apt-get install redis-server

# Configure
sudo nano /etc/redis/redis.conf
# Set: requirepass your_redis_password

# Start
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## CI/CD Pipeline

### GitHub Actions
```yaml
name: Deploy RaptorFlow
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## Environment-Specific Configurations

### Development
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_DEBUG=true
NEXT_PUBLIC_LOG_LEVEL=debug
```

### Staging
```env
NEXT_PUBLIC_API_URL=https://staging-api.raptorflow.com
NEXT_PUBLIC_ENABLE_DEBUG=false
NEXT_PUBLIC_LOG_LEVEL=info
```

### Production
```env
NEXT_PUBLIC_API_URL=https://api.raptorflow.com
NEXT_PUBLIC_ENABLE_DEBUG=false
NEXT_PUBLIC_LOG_LEVEL=error
```

## Monitoring and Analytics

### Google Analytics
```javascript
// In _app.tsx
import { GoogleAnalytics } from '@next/third-parties/google'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <GoogleAnalytics gaId="GA_MEASUREMENT_ID" />
      </body>
    </html>
  )
}
```

### Sentry Error Tracking
```javascript
// In sentry.client.config.js
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_DEPLOYMENT_ENV,
})
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancers
- Implement session affinity
- Scale database connections
- Use read replicas

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Implement caching layers
- Use CDN for static assets

## Backup and Recovery

### Database Backups
```bash
# Daily backup
pg_dump -U raptorflow_user raptorflow > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/raptorflow"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U raptorflow_user raptorflow > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### File Backups
- Backup user uploads to cloud storage
- Version control for configuration
- Document recovery procedures

## Troubleshooting

### Common Issues
1. **Build failures** - Check Node.js version and dependencies
2. **API errors** - Verify environment variables and API endpoints
3. **Database connection** - Check connection strings and firewall rules
4. **Performance issues** - Monitor resource usage and optimize queries

### Health Checks
```javascript
// /api/health
export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version,
    environment: process.env.NODE_ENV
  })
}
```

## Security Best Practices

### Authentication
- Implement JWT tokens
- Use secure cookie settings
- Add multi-factor authentication
- Implement session management

### Data Protection
- Encrypt sensitive data
- Implement data retention policies
- Add audit logging
- Use secure communication protocols

### Network Security
- Configure firewalls
- Use VPN for admin access
- Implement DDoS protection
- Monitor for suspicious activity

## Support and Maintenance

### Regular Tasks
- Update dependencies
- Monitor performance metrics
- Review security logs
- Update documentation

### Emergency Procedures
- Incident response plan
- Rollback procedures
- Communication protocols
- Recovery time objectives

## Cost Optimization

### Frontend
- Optimize bundle size
- Use efficient image formats
- Implement lazy loading
- Minimize third-party dependencies

### Backend
- Optimize database queries
- Use connection pooling
- Implement caching strategies
- Monitor resource usage

### Infrastructure
- Use auto-scaling
- Optimize cloud resource allocation
- Implement reserved instances
- Monitor and reduce waste

---

## 🎯 Deployment Checklist

- [ ] Environment variables configured
- [ ] Database set up and migrated
- [ ] SSL certificates installed
- [ ] CDN configured
- [ ] Monitoring tools set up
- [ ] Backup procedures implemented
- [ ] Security measures in place
- [ ] Performance optimizations applied
- [ ] Error tracking configured
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Support procedures documented

**Ready for production deployment! 🚀**
