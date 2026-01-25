# 🚀 RAPTORFLOW API TESTING SUITE

## 📋 Overview

Complete testing infrastructure for Raptorflow API endpoints. This suite provides comprehensive testing, debugging, and development tools for all API functionality.

## 🎯 Quick Start

### Run Complete Test Suite
```bash
# Windows
tests\api\api-test-suite.bat

# Or run individual tests
node tests/api/quick-test-runner.cjs
```

### Check API Status
```bash
# Quick status check
node tests/api/quick-test-runner.cjs

# Comprehensive analysis
node tests/api/comprehensive-api-test.cjs
```

---

## 📁 Test Files Overview

### Core Test Scripts
- **`quick-test-runner.cjs`** - Tests 12 critical endpoints only
- **`comprehensive-api-test.cjs`** - Tests all 48 endpoints with detailed analysis
- **`debug-endpoint.cjs`** - Deep debugging for specific endpoints
- **`simple-api-test.cjs`** - Basic HTTP testing without dependencies

### Automation & Documentation
- **`api-test-suite.bat`** - Complete automated test suite (Windows)
- **`development-playbook.md`** - Development guide and workflows
- **`critical-endpoints-summary.md`** - Executive summary of API status
- **`final-status-report.md`** - Complete mission report

---

## 🧪 Test Categories

### ✅ Working Endpoints (7/12 Critical)
- Authentication flows (password reset, subscription status)
- Admin operations (impersonation, MFA setup)
- Workspace creation
- Mock payment processing

### ⚠️ Partially Working (5/12 Critical)
- Session management (basic functionality)
- Health monitoring (environment checks)
- Payment creation (validation only)
- Onboarding completion (method issues)

### ❌ Non-Critical Issues (34/48)
- Advanced monitoring endpoints
- Database creation endpoints
- AI service integrations
- Storage management

---

## 🛠️ Development Tools

### Testing Individual Endpoints
```bash
# Test specific endpoint
curl -X POST http://localhost:3000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Debug with verbose output
curl -v http://localhost:3000/api/health
```

### Monitoring Server Status
```bash
# Check if server is running
curl -s http://localhost:3000/api/health

# Monitor response times
node tests/api/debug-endpoint.cjs
```

### Error Debugging
```bash
# Check compilation errors
# Look at dev server output for detailed error messages

# Test with different methods
curl -X GET http://localhost:3000/api/me/subscription
curl -X POST http://localhost:3000/api/admin/impersonate \
  -H "Content-Type: application/json" \
  -d '{"userId": "test-user"}'
```

---

## 📊 Test Results Interpretation

### Status Codes
- **200** ✅ Success - Endpoint working correctly
- **400** ⚠️ Bad Request - Working but needs proper input
- **401** ⚠️ Unauthorized - Working but needs authentication
- **403** ⚠️ Forbidden - Working but needs admin rights
- **500** ❌ Server Error - Implementation issue
- **503** ❌ Service Unavailable - Configuration issue

### Response Times
- **< 100ms** 🟢 Excellent
- **100-500ms** 🟡 Good
- **500ms-2s** 🟠 Acceptable
- **> 2s** 🔴 Needs optimization

---

## 🚀 Development Workflow

### 1. Initial Setup
```bash
# Start dev server
npm run dev

# Run quick test to verify
node tests/api/quick-test-runner.cjs
```

### 2. Feature Development
```bash
# Test your new endpoint
curl -X POST http://localhost:3000/api/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"data": "test"}'

# Add to test suite if critical
# Update quick-test-runner.cjs with your endpoint
```

### 3. Integration Testing
```bash
# Test complete user flows
# 1. Authentication
# 2. Workspace creation  
# 3. Payment processing
# 4. Admin operations

# Run comprehensive test
node tests/api/comprehensive-api-test.cjs
```

### 4. Production Readiness
```bash
# Run complete test suite
tests\api\api-test-suite.bat

# Verify all critical endpoints work
# Check error handling
# Validate response formats
```

---

## 🔧 Common Issues & Solutions

### 500 Internal Server Error
**Cause**: Import errors, missing dependencies, syntax issues
**Solution**: Check dev server logs, verify imports, fix syntax

### Module Not Found Errors
**Cause**: Missing npm packages, incorrect import paths
**Solution**: Install missing packages, fix import statements

### Timeout Errors
**Cause**: Long-running operations, external service calls
**Solution**: Add timeouts, implement async operations

### Authentication Issues
**Cause**: Missing session, invalid tokens
**Solution**: Implement proper auth flow, check session management

---

## 📈 Performance Monitoring

### Response Time Tracking
```bash
# Monitor specific endpoint performance
node tests/api/debug-endpoint.cjs

# Track average response times
node tests/api/comprehensive-api-test.cjs
```

### Health Monitoring
```bash
# Regular health checks
curl -X GET http://localhost:3000/api/health

# Monitor system resources
# Check dev server memory usage
# Monitor database connections
```

---

## 🎯 Best Practices

### Endpoint Development
1. **Start Simple**: Basic HTTP response first
2. **Add Validation**: Input validation and error handling
3. **Implement Logic**: Business logic and database operations
4. **Add Tests**: Include in test suite
5. **Document**: Update API documentation

### Error Handling
```typescript
// Standard error handling pattern
try {
  // Your logic here
  return NextResponse.json({ success: true, data });
} catch (error) {
  console.error('Endpoint error:', error);
  return NextResponse.json(
    { error: 'Descriptive error message' },
    { status: appropriate_http_code }
  );
}
```

### Testing Strategy
1. **Unit Tests**: Test individual endpoints
2. **Integration Tests**: Test user flows
3. **Performance Tests**: Monitor response times
4. **Error Tests**: Verify error handling
5. **Security Tests**: Check authentication and authorization

---

## 🆘 Getting Help

### Debug Resources
1. **Dev Server Logs**: Check for compilation and runtime errors
2. **Browser Dev Tools**: Network tab for HTTP requests/responses
3. **Test Scripts**: Use provided scripts for systematic testing
4. **Documentation**: Refer to development playbook

### Common Debug Commands
```bash
# Test endpoint with verbose output
curl -v http://localhost:3000/api/endpoint

# Check server status
curl -X GET http://localhost:3000/api/health

# Run all tests
node tests/api/quick-test-runner.cjs

# Debug specific issues
node tests/api/debug-endpoint.cjs
```

---

## 📞 Support & Resources

### Documentation
- **Development Playbook**: Complete development guide
- **API Status Reports**: Current endpoint status
- **Test Results**: Historical test data and trends

### Troubleshooting
- Check dev server output for errors
- Verify environment variables
- Test with curl before frontend integration
- Use browser dev tools for debugging

### Next Steps
1. Review current API status
2. Identify endpoints needing work
3. Follow development playbook
4. Implement missing features incrementally

---

**Happy Testing! 🧪✨**
