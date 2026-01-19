# Disaster Recovery Plan

## Overview

This document outlines the disaster recovery procedures for Raptorflow, including backup strategies, recovery procedures, and business continuity plans.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Backup Strategy](#backup-strategy)
3. [Recovery Procedures](#recovery-procedures)
4. [Incident Response](#incident-response)
5. [Communication Plan](#communication-plan)
6. [Testing and Maintenance](#testing-and-maintenance)

## System Architecture

### Primary Components

- **Frontend**: Next.js application hosted on Vercel
- **Backend**: Supabase (PostgreSQL database + Auth + Storage)
- **Payment**: PhonePe payment gateway
- **Email**: Resend email service
- **Cache**: Upstash Redis
- **Monitoring**: Sentry + Grafana
- **Storage**: Google Cloud Storage (GCS)

### Dependencies

| Service | Criticality | Backup Available | Failover |
|---------|-------------|------------------|----------|
| Supabase DB | Critical | Daily + Point-in-time | Yes (via WAL) |
| Supabase Auth | Critical | Daily | Yes |
| GCS Storage | High | Daily | Yes (Multi-region) |
| Redis Cache | Medium | No | Yes (Automatic failover) |
| PhonePe | Critical | N/A | Yes (Production + Sandbox) |
| Resend | High | N/A | Yes (Multiple regions) |

## Backup Strategy

### Database Backups

1. **Automated Daily Backups**
   - Full database backup at 2:00 AM UTC
   - Schema-only backup at 2:30 AM UTC
   - Stored in GCS with 30-day retention
   - Encrypted at rest

2. **Point-in-Time Recovery**
   - WAL (Write-Ahead Logging) enabled
   - 7-day retention for PITR
   - Can restore to any point within 7 days

3. **Manual Backups**
   - Before major deployments
   - Before schema changes
   - Ad-hoc backups via admin dashboard

### File Storage Backups

1. **User Data**
   - Daily sync to secondary GCS bucket
   - Cross-region replication (US → EU)
   - 90-day retention

2. **System Assets**
   - Version controlled in Git
   - CDN caching with purge capability
   - Static assets on multiple CDNs

### Configuration Backups

1. **Environment Variables**
   - Stored in 1Password
   - Automated export to secure storage
   - Version history maintained

2. **DNS Records**
   - Managed via Cloudflare
   - Automatic backups
   - Change history tracked

## Recovery Procedures

### Scenario 1: Database Corruption

**Severity**: Critical  
**RTO**: 4 hours  
**RPO**: 1 hour

1. **Detection**
   - Automated monitoring alerts
   - Health check failures
   - User reports of data issues

2. **Immediate Actions**
   - Declare incident
   - Activate incident response team
   - Estimate impact scope

3. **Recovery Steps**
   ```bash
   # 1. Identify last good backup
   gsutil ls gs://raptorflow-backups/database/ | tail -1
   
   # 2. Restore from backup
   supabase db restore --db-url "$SUPABASE_URL" \
     --file backup_file.sql.gz
   
   # 3. Apply WAL logs for PITR
   supabase db restore --db-url "$SUPABASE_URL" \
     --point-in-time "2024-01-15 14:30:00 UTC"
   
   # 4. Verify data integrity
   supabase db diff --schema public
   ```

4. **Post-Recovery**
   - Run data validation scripts
   - Monitor system performance
   - Communicate with stakeholders

### Scenario 2: Regional Outage

**Severity**: High  
**RTO**: 2 hours  
**RPO**: 15 minutes

1. **Detection**
   - Multi-region health checks
   - CDN failover triggers
   - User access reports

2. **Recovery Steps**
   - Activate traffic routing to backup region
   - Update DNS records via automated script
   - Verify service availability
   - Monitor performance metrics

3. **Automation Script**
   ```bash
   #!/bin/bash
   # Failover to backup region
   
   # Update DNS
   cfcli api --zone raptorflow.com \
     --action update --name @ \
     --content backup-region-ip \
     --type A --ttl 300
   
   # Update environment variables
   vercel env pull .env.production
   sed -i 's/primary-region/backup-region/g' .env.production
   vercel env push .env.production
   
   # Verify
   curl -f https://raptorflow.com/health
   ```

### Scenario 3: Security Breach

**Severity**: Critical  
**RTO**: 1 hour  
**RPO**: Immediate

1. **Immediate Actions**
   - Isolate affected systems
   - Force password reset for all users
   - Revoke all active sessions
   - Enable enhanced monitoring

2. **Investigation**
   - Preserve forensic evidence
   - Analyze audit logs
   - Identify breach vector
   - Assess data exposure

3. **Recovery**
   - Patch vulnerabilities
   - Rotate all secrets/keys
   - Restore from clean backup if needed
   - Implement additional security measures

### Scenario 4: Data Deletion

**Severity**: High  
**RTO**: 6 hours  
**RPO**: 24 hours

1. **Recovery Options**
   - Restore from daily backup
   - Use point-in-time recovery
   - Recover from replication lag
   - Extract from audit logs

2. **Procedure**
   ```sql
   -- Identify deleted data
   SELECT * FROM audit_logs 
   WHERE action = 'DELETE' 
     AND created_at > '2024-01-15 10:00:00';
   
   -- Restore from backup
   CREATE TABLE users_restored AS 
   SELECT * FROM users_backup 
   WHERE deleted_at IS NULL;
   
   -- Merge with current data
   INSERT INTO users 
   SELECT * FROM users_restored 
   WHERE id NOT IN (SELECT id FROM users);
   ```

## Incident Response

### Incident Classification

| Severity | Response Time | Escalation | Communication |
|----------|---------------|------------|---------------|
| P0 - Critical | 15 minutes | Immediate | Public within 1 hour |
| P1 - High | 1 hour | 4 hours | Internal within 2 hours |
| P2 - Medium | 4 hours | 24 hours | Team within 8 hours |
| P3 - Low | 24 hours | 72 hours | Team within 48 hours |

### Response Team

1. **Incident Commander** - Technical Lead
2. **Communications Lead** - Product Manager
3. **Technical Lead** - Senior Engineer
4. **Support Lead** - Customer Success
5. **Security Lead** - Security Engineer

### Incident Process

1. **Detection**
   - Automated alerts
   - Customer reports
   - Internal monitoring

2. **Assessment**
   - Determine severity
   - Identify affected systems
   - Estimate impact

3. **Response**
   - Implement fix
   - Monitor progress
   - Document actions

4. **Recovery**
   - Verify service restoration
   - Run post-incident tests
   - Update documentation

5. **Post-Mortem**
   - Root cause analysis
   - Improvement actions
   - Share learnings

## Communication Plan

### Internal Communication

1. **Slack Channels**
   - `#incidents` - Active incidents
   - `#engineering` - Technical updates
   - `#company` - Company-wide updates

2. **Email Templates**
   - Initial alert
   - Progress updates
   - Resolution notice

### External Communication

1. **Status Page**
   - status.raptorflow.com
   - Real-time updates
   - Historical incidents

2. **Customer Communication**
   - Email notifications
   - In-app banners
   - Social media updates

3. **Stakeholder Updates**
   - Executive team
   - Board members
   - Key partners

### Communication Templates

#### Initial Incident Alert (P0/P1)
```
🚨 INCIDENT DECLARED 🚨

Service: [Service Name]
Severity: [P0/P1]
Started: [Time]
Impact: [Description]

Investigation in progress. Next update in 30 minutes.
#incident-123
```

#### Customer Notification
```
Subject: Service Disruption - [Service Name]

Dear Customers,

We are currently experiencing a disruption in [Service Name]. 
Our team is actively working to resolve the issue.

Started: [Time]
Impact: [Customer impact]
ETA: [Estimated resolution]

We apologize for the inconvenience and appreciate your patience.

Updates will be posted at: status.raptorflow.com
```

## Testing and Maintenance

### Backup Testing

1. **Monthly Tests**
   - Restore random backup to staging
   - Verify data integrity
   - Test application functionality
   - Document results

2. **Quarterly Drills**
   - Full disaster recovery simulation
   - Cross-team participation
   - Time recovery procedures
   - Update procedures based on findings

### Maintenance Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Backup verification | Monthly | DevOps |
| Recovery drill | Quarterly | DevOps |
| Documentation review | Quarterly | Tech Lead |
| Security audit | Annually | Security |
| Plan update | Annually | All teams |

### Success Metrics

- **RTO Achievement**: < 4 hours for critical systems
- **RPO Achievement**: < 1 hour data loss
- **Backup Success Rate**: 99.9%
- **Recovery Test Success**: 100%

## Contact Information

### Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| CEO | [Name] | +1-XXX-XXX-XXXX | ceo@raptorflow.com |
| CTO | [Name] | +1-XXX-XXX-XXXX | cto@raptorflow.com |
| DevOps Lead | [Name] | +1-XXX-XXX-XXXX | devops@raptorflow.com |
| Security Lead | [Name] | +1-XXX-XXX-XXXX | security@raptorflow.com |

### Service Providers

| Service | Contact | Support |
|---------|---------|---------|
| Supabase | support@supabase.com | 24/7 |
| Vercel | support@vercel.com | 24/7 |
| Google Cloud | support@google.com | 24/7 |
| PhonePe | merchant@phonepe.com | Business hours |

## Appendix

### A. Backup Script Location
- Path: `/scripts/backup-database.sh`
- Repository: `raptorflow/infrastructure`
- Schedule: Daily at 2:00 AM UTC

### B. Monitoring Dashboards
- System Health: Grafana - https://grafana.raptorflow.com
- Error Tracking: Sentry - https://sentry.raptorflow.com
- Performance: Vercel Analytics - https://vercel.com/analytics

### C. Runbooks
- Database Recovery: `/runbooks/database-recovery.md`
- Service Failover: `/runbooks/failover.md`
- Security Incident: `/runbooks/security-incident.md`

---

**Document Version**: 2.0  
**Last Updated**: January 15, 2024  
**Next Review**: July 15, 2024  
**Approved by**: CTO, Raptorflow
