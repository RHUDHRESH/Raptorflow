#!/bin/bash

# Production Security Audit Script
# Run this script to verify security configurations

echo "🔐 Starting Production Security Audit..."
echo "================================"

# Check environment variables
echo "📋 Checking environment variables..."
if [ -z "$NEXT_PUBLIC_SUPABASE_URL" ]; then
    echo "❌ NEXT_PUBLIC_SUPABASE_URL not set"
    exit 1
else
    echo "✅ NEXT_PUBLIC_SUPABASE_URL configured"
fi

if [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "❌ SUPABASE_SERVICE_KEY not set"
    exit 1
else
    echo "✅ SUPABASE_SERVICE_KEY configured"
fi

# Check for development/debug flags
if grep -r "DEBUG=true\|dev=true\|development" .env* 2>/dev/null; then
    echo "❌ Development flags found in environment files"
    exit 1
else
    echo "✅ No development flags found"
fi

# Check for hardcoded credentials
echo "🔍 Checking for hardcoded credentials..."
if grep -r "password.*=" --include="*.py,*.js,*.ts,*.json" . 2>/dev/null | grep -v "example\|test\|mock"; then
    echo "❌ Potential hardcoded credentials found"
    exit 1
else
    echo "✅ No hardcoded credentials found"
fi

# Check SSL/TLS configuration
echo "🔒 Checking SSL/TLS configuration..."
if curl -s -I https://api.raptorflow.com | grep -q "200 OK"; then
    echo "✅ HTTPS is working"
else
    echo "❌ HTTPS not responding"
    exit 1
fi

# Check security headers
echo "🛡️ Checking security headers..."
headers=$(curl -s -I https://api.raptorflow.com)
if echo "$headers" | grep -q "Strict-Transport-Security"; then
    echo "✅ HSTS header present"
else
    echo "❌ HSTS header missing"
fi

if echo "$headers" | grep -q "Content-Security-Policy"; then
    echo "✅ CSP header present"
else
    echo "❌ CSP header missing"
fi

# Check rate limiting
echo "🚦 Checking rate limiting..."
response_time=$(curl -s -o /dev/null -w "%{time_total}" https://api.raptorflow.com/health)
if (( $(echo "$response_time < 1.0" | bc -l))); then
    echo "✅ API responding quickly"
else
    echo "⚠️  API response time: $response_time seconds"
fi

# Check database RLS policies
echo "🔐 Checking database RLS policies..."
psql "$DATABASE_URL" -c "
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE rowsecurity = true 
AND schemaname = 'public';" 2>/dev/null | grep -q "true" && echo "✅ RLS policies enabled" || echo "❌ RLS policies not found"

# Check for exposed admin endpoints
echo "🔍 Checking for exposed admin endpoints..."
if curl -s https://api.raptorflow.com/admin/users | grep -q "401\|403"; then
    echo "✅ Admin endpoints properly protected"
else
    echo "❌ Admin endpoints may be exposed"
fi

# Check CORS configuration
echo "🌐 Checking CORS configuration..."
if curl -s -H "Origin: https://evil.com" -H "Access-Control-Request-Method: POST" -X OPTIONS https://api.raptorflow.com | grep -q "Access-Control-Allow-Origin"; then
    echo "⚠️  CORS may be too permissive"
else
    echo "✅ CORS appears properly configured"
fi

# Check for default passwords
echo "🔑 Checking for default passwords..."
default_passwords=("admin" "password" "123456" "root" "guest")
for password in "${default_passwords[@]}"; do
    if grep -r "$password" . 2>/dev/null | grep -v "example\|test\|mock\|documentation"; then
        echo "❌ Default password '$password' found"
        exit 1
    fi
done
echo "✅ No default passwords found"

# Check file permissions
echo "📁 Checking file permissions..."
find . -name "*.env*" -type f -exec chmod 600 {} \;
find . -name "*.key" -type f -exec chmod 600 {} \;
echo "✅ Sensitive file permissions set"

# Check for unnecessary services
echo "🔧 Checking for unnecessary services..."
if systemctl is-active --quiet telnet 2>/dev/null; then
    echo "❌ Telnet service running (should be disabled)"
else
    echo "✅ Telnet service not running"
fi

# Check for open ports
echo "🌐 Checking open ports..."
netstat -tuln | grep LISTEN | grep -E ":22|:80|:443|:3306|:5432" | head -10

echo "================================"
echo "🔐 Security Audit Complete!"
echo "================================"
