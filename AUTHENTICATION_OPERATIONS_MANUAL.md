# 🔐 RaptorFlow Authentication Operations Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Procedures](#deployment-procedures)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Security Procedures](#security-procedures)
8. [Backup and Recovery](#backup-and-recovery)
9. [Performance Optimization](#performance-optimization)
10. [Emergency Procedures](#emergency-procedures)

---

## System Overview

### Components
- **Next.js Application**: Frontend authentication pages and API routes
- **Supabase**: Database and authentication backend
- **Resend**: Email service for password reset
- **Nginx**: Reverse proxy and SSL termination
- **GitHub Actions**: CI/CD pipeline

### Key Features
- User registration and login
- Password reset via email
- OAuth authentication (Google, GitHub, Microsoft, Apple)
- Session management
- Rate limiting and security headers
- Comprehensive monitoring

---

## Architecture

### Frontend Components
```
src/app/
├── login/                    # Login page
├── signup/                   # Registration page
├── forgot-password/          # Password reset request
├── auth/reset-password/      # Password reset form
└── auth/callback/            # OAuth callback handler
```

### API Endpoints
```
src/app/api/auth/
├── forgot-password/          # Send reset email
├── reset-password-simple/    # Reset password
├── validate-reset-token-simple/ # Validate token
└── callback/                 # OAuth callbacks
```

### Database Tables
- `profiles` - User profiles and metadata
- `password_reset_tokens` - Password reset tokens
- `sessions` - Active sessions (if implemented)

---

## Environment Configuration

### Required Environment Variables

#### Database & Authentication
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://connection-string
```

#### Email Service
```bash
RESEND_API_KEY=your-resend-api-key
RESEND_FROM_EMAIL=onboarding@resend.dev
RESEND_VERIFIED_EMAIL=verified@example.com
```

#### Application
```bash
NEXT_PUBLIC_APP_URL=https://your-domain.com
NODE_ENV=production
```

#### OAuth Providers
```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# Apple OAuth
APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret
```

### Environment Setup Checklist
- [ ] All required variables are set
- [ ] OAuth providers are configured
- [ ] Database connection is working
- [ ] Email service is verified
- [ ] SSL certificates are installed

---

## Deployment Procedures

### Automated Deployment
```bash
# Linux/Unix
./scripts/deploy-authentication.sh deploy

# Windows
.\scripts\deploy-authentication.ps1 -Action deploy
```

### Manual Deployment Steps

#### 1. Pre-deployment Checks
```bash
# Verify environment variables
./scripts/deploy-authentication.sh check

# Test database connection
curl -X GET "$NEXT_PUBLIC_APP_URL/api/setup/create-db-table"

# Test email service
curl -X POST "$NEXT_PUBLIC_APP_URL/api/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

#### 2. Build Application
```bash
npm run build
npm run start
```

#### 3. Configure Nginx
```bash
# Copy SSL configuration
sudo cp nginx/auth-ssl.conf /etc/nginx/sites-available/raptorflow-auth

# Enable site
sudo ln -s /etc/nginx/sites-available/raptorflow-auth /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### 4. Post-deployment Verification
```bash
# Verify all endpoints
curl -f "$NEXT_PUBLIC_APP_URL/login"
curl -f "$NEXT_PUBLIC_APP_URL/signup"
curl -f "$NEXT_PUBLIC_APP_URL/forgot-password"

# Test authentication flow
./scripts/deploy-authentication.sh verify
```

---

## Monitoring and Maintenance

### Health Check Endpoint
```bash
curl -X GET "$NEXT_PUBLIC_APP_URL/api/health"
```

### Monitoring Dashboard
```bash
curl -X GET "$NEXT_PUBLIC_APP_URL/api/monitoring/dashboard"
```

### Key Metrics to Monitor
- API response times
- Error rates
- Database connection status
- Email delivery rates
- Authentication success/failure rates
- Rate limiting effectiveness

### Log Files
- Application logs: `/var/log/raptorflow/app.log`
- Nginx logs: `/var/log/nginx/raptorflow-auth.*`
- Database logs: Supabase dashboard

### Automated Monitoring
Set up alerts for:
- High error rates (>5%)
- Slow response times (>2s)
- Database connection failures
- Email delivery failures
- SSL certificate expiration

---

## Troubleshooting Guide

### Common Issues

#### 1. Database Connection Failed
**Symptoms**: 500 errors, database timeouts
**Causes**: Network issues, incorrect credentials, database down
**Solutions**:
```bash
# Check database connection
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

# Verify environment variables
echo $DATABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# Restart application
sudo systemctl restart raptorflow
```

#### 2. Email Not Sending
**Symptoms**: Password reset emails not received
**Causes**: Invalid API key, domain not verified, rate limits
**Solutions**:
```bash
# Test Resend API
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from": "onboarding@resend.dev", "to": "test@example.com", "subject": "Test", "html": "Test"}'

# Check domain verification
# Login to Resend dashboard and verify domain
```

#### 3. OAuth Login Failed
**Symptoms**: OAuth redirect errors, token exchange failures
**Causes**: Incorrect client credentials, redirect URI mismatch
**Solutions**:
```bash
# Verify OAuth configuration
curl -X GET "$NEXT_PUBLIC_APP_URL/api/monitoring/dashboard" | jq '.oauth'

# Check redirect URI in OAuth provider console
# Ensure it matches: $NEXT_PUBLIC_APP_URL/auth/callback/{provider}
```

#### 4. Rate Limiting Too Aggressive
**Symptoms**: Legitimate users getting 429 errors
**Causes**: Rate limit set too low
**Solutions**:
```bash
# Check current rate limits
grep -r "rate_limit" nginx/

# Adjust rate limits in nginx configuration
# Edit /etc/nginx/sites-available/raptorflow-auth
```

### Debugging Commands
```bash
# Check application status
sudo systemctl status raptorflow

# View recent logs
sudo journalctl -u raptorflow -f

# Check Nginx status
sudo systemctl status nginx

# Test API endpoints
curl -v "$NEXT_PUBLIC_APP_URL/api/health"

# Monitor real-time traffic
sudo tail -f /var/log/nginx/raptorflow-auth.access.log
```

---

## Security Procedures

### Security Headers Verification
```bash
curl -I "$NEXT_PUBLIC_APP_URL/login" | grep -E "(x-|content-security|referrer)"
```

### SSL Certificate Management
```bash
# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/raptorflow.com/cert.pem -noout -dates

# Renew certificates
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

### Security Audit Checklist
- [ ] SSL certificates are valid
- [ ] Security headers are present
- [ ] Rate limiting is active
- [ ] OAuth secrets are secure
- [ ] Database access is restricted
- [ ] Error messages don't leak information

### Incident Response
1. **Detection**: Monitor alerts and logs
2. **Assessment**: Determine scope and impact
3. **Containment**: Block malicious IPs, rotate secrets
4. **Eradication**: Patch vulnerabilities
5. **Recovery**: Restore services, verify integrity
6. **Lessons**: Update procedures, improve monitoring

---

## Backup and Recovery

### Automated Backups
```bash
# Run backup script
./scripts/backup-auth-database.sh backup

# List available backups
./scripts/backup-auth-database.sh list

# Restore from backup
./scripts/backup-auth-database.sh restore auth_backup_20240116_120000.sql
```

### Manual Backup
```bash
# Create database backup
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  --format=custom --compress=9 \
  --file=manual_backup_$(date +%Y%m%d_%H%M%S).sql \
  --table=profiles \
  --table=password_reset_tokens
```

### Disaster Recovery Procedures

#### 1. Database Corruption
```bash
# Stop application
sudo systemctl stop raptorflow

# Restore from latest backup
./scripts/backup-auth-database.sh restore $(ls -t /backups/raptorflow-auth/auth_backup_*.sql | head -1)

# Restart application
sudo systemctl start raptorflow

# Verify functionality
curl -X GET "$NEXT_PUBLIC_APP_URL/api/health"
```

#### 2. Complete System Failure
```bash
# Restore from cloud backup
# Rebuild servers
# Restore database
# Update DNS
# Verify all services
```

### Backup Retention
- Daily backups: 30 days
- Weekly backups: 12 weeks
- Monthly backups: 12 months
- Annual backups: 7 years

---

## Performance Optimization

### Database Optimization
```sql
-- Create indexes for frequently queried fields
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires ON password_reset_tokens(expires_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM profiles WHERE email = 'user@example.com';
```

### Application Optimization
```bash
# Enable gzip compression in Nginx
# Configure CDN for static assets
# Implement caching headers
# Optimize database queries
# Use connection pooling
```

### Monitoring Performance
```bash
# Check response times
curl -w "%{time_total}\n" -o /dev/null -s "$NEXT_PUBLIC_APP_URL/login"

# Monitor database performance
# Check slow query log
# Monitor memory usage
# Track error rates
```

---

## Emergency Procedures

### Service Outage
1. **Identify**: Check monitoring dashboard
2. **Assess**: Determine affected services
3. **Communicate**: Notify stakeholders
4. **Fix**: Apply appropriate solution
5. **Verify**: Confirm service restoration
6. **Document**: Update incident log

### Security Breach
1. **Contain**: Block malicious IPs, rotate secrets
2. **Investigate**: Analyze logs, determine scope
3. **Notify**: Report to authorities if required
4. **Remediate**: Patch vulnerabilities
5. **Recover**: Restore secure state
6. **Review**: Improve security measures

### Data Corruption
1. **Stop**: Halt affected services
2. **Assess**: Determine corruption scope
3. **Restore**: Use latest clean backup
4. **Verify**: Data integrity checks
5. **Monitor**: Watch for recurrence
6. **Prevent**: Update procedures

### Contact Information
- **Primary Admin**: admin@raptorflow.com
- **Infrastructure Team**: infra@raptorflow.com
- **Security Team**: security@raptorflow.com
- **Emergency Hotline**: +1-555-XXX-XXXX

### Escalation Matrix
| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Critical | 15 minutes | CTO, CEO |
| High | 1 hour | Engineering Lead |
| Medium | 4 hours | Team Lead |
| Low | 24 hours | Team Member |

---

## Maintenance Schedule

### Daily Tasks
- [ ] Check system health dashboard
- [ ] Review error logs
- [ ] Monitor performance metrics
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review security logs
- [ ] Update SSL certificates (if expiring soon)
- [ ] Check disk space usage
- [ ] Review rate limiting effectiveness

### Monthly Tasks
- [ ] Security audit
- [ ] Performance review
- [ ] Backup verification
- [ ] Update dependencies

### Quarterly Tasks
- [ ] Disaster recovery test
- [ ] Security penetration test
- [ ] Performance optimization review
- [ ] Documentation update

---

## Appendix

### Useful Commands
```bash
# System status
systemctl status raptorflow nginx postgresql

# Log monitoring
tail -f /var/log/raptorflow/app.log
tail -f /var/log/nginx/raptorflow-auth.access.log

# Database operations
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

# SSL management
certbot certificates
openssl x509 -in cert.pem -noout -dates

# Performance testing
ab -n 1000 -c 10 "$NEXT_PUBLIC_APP_URL/login"
```

### Configuration Files
- `/etc/nginx/sites-available/raptorflow-auth` - Nginx configuration
- `/etc/letsencrypt/live/raptorflow.com/` - SSL certificates
- `/var/www/raptorflow/.env` - Environment variables
- `/etc/systemd/system/raptorflow.service` - Systemd service

### External Services
- **Supabase**: https://app.supabase.com
- **Resend**: https://resend.com/dashboard
- **GitHub Actions**: https://github.com/raptorflow/actions
- **SSL Provider**: Let's Encrypt

---

**Last Updated**: January 16, 2026  
**Version**: 1.0.0  
**Maintainer**: RaptorFlow Team
