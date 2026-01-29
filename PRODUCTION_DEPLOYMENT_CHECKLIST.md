# Production Deployment Checklist

## 🚀 Pre-Deployment Checklist

### Environment Setup ✅
- [ ] All environment variables are configured in production
- [ ] PhonePe production credentials are set
- [ ] Resend API key is verified and domain is verified
- [ ] Supabase production database is ready
- [ ] Upstash Redis is configured
- [ ] Google Cloud Vertex AI is enabled
- [ ] SSL certificates are valid and installed

### Database Preparation ✅
- [ ] Database migrations are applied in production
- [ ] RLS policies are enabled and tested
- [ ] Database backups are configured
- [ ] Database indexes are optimized
- [ ] Connection pooling is configured
- [ ] Database performance is benchmarked

### Security Configuration ✅
- [ ] API keys are rotated and secure
- [ ] Webhook endpoints are secured with HTTPS
- [ ] Rate limiting is configured
- [ ] CORS is properly configured
- [ ] Security headers are set
- [ ] Authentication is working correctly
- [ ] Audit logging is enabled

### Service Configuration ✅
- [ ] Backend services are running and healthy
- [ ] Frontend build is optimized for production
- [ ] API endpoints are accessible and tested
- [ ] Webhook endpoints are reachable
- [ ] Email service is configured and tested
- [ ] Payment service is integrated with PhonePe
- [ ] Redis cache is working

---

## 🧪 Testing Checklist

### Unit Tests ✅
- [ ] Backend unit tests pass (>90% coverage)
- [ ] Frontend unit tests pass (>85% coverage)
- [ ] Payment service tests pass
- [ ] Email service tests pass
- [ ] Integration tests pass

### Integration Tests ✅
- [ ] Payment initiation works correctly
- [ ] Payment status checking works
- [ ] Webhook processing works
- [ ] Email notifications are sent
- [ ] Subscription activation works
- [ ] Error handling works correctly

### End-to-End Tests ✅
- [ ] Complete payment flow works
- [ ] User can select plan and pay
- [ ] Payment redirects to PhonePe
- [ ] Webhook processes payment correctly
- [ ] User receives email confirmation
- [ ] Dashboard shows active subscription
- [ ] Failed payments show retry options

### Performance Tests ✅
- [ ] API response times are <2s for payment initiation
- [ ] API response times are <1s for status checks
- [ ] Frontend page load time is <3s
- [ ] Database queries are optimized
- [ ] Redis cache hit rate is >80%
- [ ] Memory usage is within limits

---

## 🔧 Deployment Steps

### 1. Database Deployment
```bash
# Apply migrations
supabase db push

# Verify schema
supabase db diff --schema public

# Check RLS policies
supabase db diff --schema auth
```

### 2. Backend Deployment
```bash
# Install dependencies
pip install -r requirements-prod.txt

# Run database migrations
python -m alembic upgrade head

# Start services
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend Deployment
```bash
# Build for production
npm run build

# Deploy to Vercel
vercel --prod

# Verify deployment
curl -f https://yourapp.com/api/health
```

### 4. Service Verification
```bash
# Test backend health
curl https://api.yourapp.com/api/health

# Test payment service
curl https://api.yourapp.com/api/payments/v2/health

# Test frontend
curl https://yourapp.com/
```

---

## 📊 Monitoring Setup

### Application Monitoring ✅
- [ ] Sentry error tracking is configured
- [ ] Performance monitoring is set up
- [ ] Custom metrics are defined
- [ ] Alert thresholds are configured
- [ ] Dashboard is created

### Infrastructure Monitoring ✅
- [ ] Server metrics are monitored
- [ ] Database performance is tracked
- [ ] Redis metrics are monitored
- [ ] API response times are tracked
- [ ] Error rates are monitored

### Business Metrics ✅
- [ ] Payment success rate is tracked
- [ ] Conversion funnel is monitored
- [ ] User activity is tracked
- [ ] Revenue metrics are monitored
- [ ] Support tickets are tracked

---

## 🚨 Rollback Plan

### Database Rollback
```bash
# Rollback migrations
supabase db reset

# Restore from backup
supabase db restore backup_file.sql
```

### Application Rollback
```bash
# Backend rollback
git checkout previous_tag
pip install -r requirements-prod.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend rollback
vercel rollback
```

### Service Rollback
- [ ] Previous version is tagged and accessible
- [ ] Database backups are available
- [ ] Configuration can be reverted
- [ ] Monitoring alerts are configured
- [ ] Team is trained on rollback procedures

---

## 📋 Post-Deployment Checklist

### Verification ✅
- [ ] All services are running
- [ ] API endpoints are responding
- [ ] Database is accessible
- [ ] Redis is connected
- [ ] Email service is working
- [ ] Payment service is integrated
- [ ] Frontend is loading correctly

### Testing ✅
- [ ] Payment flow works end-to-end
- [ ] Webhook processing works
- [ ] Email notifications are sent
- [ ] User authentication works
- [ ] Error handling works
- [ ] Performance is acceptable

### Monitoring ✅
- [ ] Monitoring dashboards are working
- [ ] Alerts are configured correctly
- [ ] Logs are being collected
- [ ] Metrics are being tracked
- [ ] Health checks are passing

### Documentation ✅
- [ ] Deployment guide is updated
- [ ] Environment variables are documented
- [ ] API documentation is updated
- [ ] Troubleshooting guide is updated
- [ ] Runbook is created

---

## 🔍 Health Checks

### API Health Endpoints
```bash
# Backend health
GET /api/health

# Payment service health
GET /api/payments/v2/health

# Database health
GET /api/health/database

# Redis health
GET /api/health/redis
```

### Expected Responses
```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "email": "healthy",
    "payment": "healthy"
  }
}
```

---

## 📈 Performance Benchmarks

### API Performance Targets
- **Payment Initiation**: <2s average response time
- **Payment Status Check**: <1s average response time
- **Webhook Processing**: <500ms average response time
- **Plan Loading**: <300ms average response time
- **Health Checks**: <100ms average response time

### Frontend Performance Targets
- **First Contentful Paint**: <1.5s
- **Largest Contentful Paint**: <2.5s
- **Time to Interactive**: <3.5s
- **Cumulative Layout Shift**: <0.1
- **First Input Delay**: <100ms

### Database Performance Targets
- **Query Response Time**: <100ms average
- **Connection Pool Usage**: <80%
- **Database CPU Usage**: <70%
- **Database Memory Usage**: <80%

### Infrastructure Performance Targets
- **Server CPU Usage**: <70%
- **Server Memory Usage**: <80%
- **Network Latency**: <50ms
- **Disk I/O**: <80ms average

---

## 🚨 Emergency Procedures

### Service Outage
1. **Identify the issue** through monitoring dashboards
2. **Check health endpoints** for service status
3. **Review recent deployments** for potential causes
4. **Rollback** if necessary
5. **Communicate** with stakeholders
6. **Document** the incident

### Payment Issues
1. **Check PhonePe status** and API connectivity
2. **Verify webhook processing** is working
3. **Check database** for payment records
4. **Review error logs** for specific issues
5. **Contact PhonePe support** if needed
6. **Communicate** with affected users

### Database Issues
1. **Check database connectivity** and performance
2. **Review recent migrations** for potential issues
3. **Check connection pool** usage
4. **Verify RLS policies** are working
5. **Restore from backup** if necessary
6. **Communicate** with team

---

## 📞 Contact Information

### Team Contacts
- **DevOps Lead**: devops@raptorflow.com
- **Backend Lead**: backend@raptorflow.com
- **Frontend Lead**: frontend@raptorflow.com
- **Database Admin**: dba@raptorflow.com

### Service Providers
- **PhonePe Support**: support@phonepe.com
- **Resend Support**: support@resend.com
- **Supabase Support**: support@supabase.com
- **Upstash Support**: support@upstash.com

### Emergency Contacts
- **On-call Engineer**: +1-XXX-XXX-XXXX
- **Product Manager**: +1-XXX-XXX-XXXX
- **CEO**: +1-XXX-XXX-XXXX

---

## ✅ Final Verification

Before going live, ensure:

- [ ] All checklist items are completed
- [ ] All tests are passing
- [ ] All services are healthy
- [ ] All monitoring is working
- [ ] All documentation is updated
- [ ] Team is trained on procedures
- [ ] Stakeholders are notified
- [ ] Rollback plan is tested

---

**Deployment Date**: ___________
**Deployed By**: ___________
**Version**: ___________
**Status**: ___________

---

**Last Updated**: January 28, 2026
**Version**: 1.0
