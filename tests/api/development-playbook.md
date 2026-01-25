# 🚀 RAPTORFLOW API DEVELOPMENT PLAYBOOK

## 🎯 QUICK START GUIDE

### Step 1: Verify API Status
```bash
# Run the quick test to confirm everything is working
node tests/api/quick-test-runner.cjs
```

### Step 2: Test Core User Flows
```bash
# Test password reset
curl -X POST http://localhost:3000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Test workspace creation
curl -X POST http://localhost:3000/api/onboarding/create-workspace \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Workspace", "userId": "user123"}'

# Test mock payment
curl -X POST http://localhost:3000/api/complete-mock-payment \
  -H "Content-Type: application/json" \
  -d '{"transactionId": "txn123", "phonePeTransactionId": "pp456"}'
```

---

## 🛠️ DEVELOPMENT WORKFLOWS

### User Authentication Flow
1. **Signup** → `/api/auth/forgot-password` (for password reset)
2. **Login** → Use Supabase Auth directly
3. **Session Check** → `/api/me/subscription` (401 = not logged in)
4. **Password Reset** → `/api/auth/reset-password-simple`

### Workspace Management Flow
1. **Create Workspace** → `/api/onboarding/create-workspace`
2. **Complete Onboarding** → `/api/onboarding/complete`
3. **Admin Testing** → `/api/admin/impersonate` (for multi-user testing)

### Payment Testing Flow
1. **Create Payment** → `/api/create-payment` (mock response)
2. **Complete Payment** → `/api/complete-mock-payment`
3. **Verify Subscription** → `/api/me/subscription`

---

## 🧪 TESTING SCENARIOS

### Scenario 1: New User Onboarding
```bash
# 1. User signs up (via Supabase Auth)
# 2. Create workspace
curl -X POST http://localhost:3000/api/onboarding/create-workspace \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company", "userId": "new-user-123"}'

# 3. Complete onboarding
curl -X POST http://localhost:3000/api/onboarding/complete \
  -H "Content-Type: application/json" \
  -d '{"workspaceId": "ws123", "userId": "new-user-123", "steps": [1,2,3]}'

# 4. Test payment flow
curl -X POST http://localhost:3000/api/complete-mock-payment \
  -H "Content-Type: application/json" \
  -d '{"transactionId": "txn789", "phonePeTransactionId": "pp012"}'
```

### Scenario 2: Admin Testing
```bash
# 1. Impersonate user for testing
curl -X POST http://localhost:3000/api/admin/impersonate \
  -H "Content-Type: application/json" \
  -d '{"userId": "test-user-456"}'

# 2. Check subscription status
curl -X GET http://localhost:3000/api/me/subscription

# 3. Setup MFA for admin
curl -X POST http://localhost:3000/api/admin/mfa/setup \
  -H "Content-Type: application/json" \
  -d '{"userId": "admin-user"}'
```

---

## 🔧 COMMON DEVELOPMENT TASKS

### Adding New API Endpoints
1. Create file in `src/app/api/[endpoint]/route.ts`
2. Follow the simple pattern:
```typescript
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const data = await request.json();
    
    // Your logic here
    return NextResponse.json({ success: true, data });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
```

### Debugging API Issues
1. **Check the error**: Look at the actual error message in browser dev tools
2. **Test with curl**: Use curl to test endpoints directly
3. **Check server logs**: Look at the dev server output for compilation errors
4. **Verify imports**: Make sure all imports are correct and modules exist

### Testing with Different HTTP Methods
```bash
# GET request
curl -X GET http://localhost:3000/api/health

# POST with data
curl -X POST http://localhost:3000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# PUT request
curl -X PUT http://localhost:3000/api/user/profile \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# DELETE request
curl -X DELETE http://localhost:3000/api/user/session \
  -H "Content-Type: application/json"
```

---

## 📊 MONITORING & DEBUGGING

### Health Check
```bash
# Check system health
curl -X GET http://localhost:3000/api/health
```

### Session Management
```bash
# Check session status
curl -X GET "http://localhost:3000/api/auth/session-management?userId=user123"

# Manage sessions
curl -X POST http://localhost:3000/api/auth/session-management \
  -H "Content-Type: application/json" \
  -d '{"action": "list", "userId": "user123"}'
```

### Subscription Status
```bash
# Check user subscription
curl -X GET http://localhost:3000/api/me/subscription
```

---

## 🚀 PRODUCTION READINESS CHECKLIST

### Before Going Live
- [ ] All critical endpoints return expected responses
- [ ] Error handling is implemented for all endpoints
- [ ] Environment variables are properly configured
- [ ] Database connections are tested
- [ ] External services (email, AI, payment) are configured

### Security Checklist
- [ ] Input validation is implemented
- [ ] Authentication is required for protected endpoints
- [ ] Rate limiting is considered
- [ ] CORS is properly configured
- [ ] Sensitive data is not exposed in responses

### Performance Checklist
- [ ] Response times are under 1 second
- [ ] Database queries are optimized
- [ ] Caching is implemented where appropriate
- [ ] Error responses are consistent
- [ ] Logging is implemented for debugging

---

## 💡 DEVELOPMENT TIPS

### 1. Start Simple, Add Complexity Later
- Get basic functionality working first
- Add database persistence later
- Implement external integrations when needed

### 2. Use Mock Responses for Testing
- Create realistic mock responses
- Test edge cases with mock data
- Document expected response formats

### 3. Graceful Degradation
- Return meaningful errors when services are unavailable
- Provide fallback behavior for missing dependencies
- Log issues for debugging without breaking functionality

### 4. Consistent Error Handling
```typescript
// Use this pattern for all endpoints
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

### 5. Environment Configuration
- Use environment variables for all configuration
- Provide sensible defaults
- Document required environment variables

---

## 🆘 TROUBLESHOOTING GUIDE

### Common Issues & Solutions

#### 500 Internal Server Error
- **Cause**: Import errors, missing dependencies, syntax errors
- **Solution**: Check dev server logs, verify imports, fix syntax

#### 404 Not Found
- **Cause**: Endpoint doesn't exist or wrong path
- **Solution**: Verify file path and method, check route structure

#### 401 Unauthorized
- **Cause**: Missing authentication or invalid session
- **Solution**: Implement proper auth, check session validity

#### 400 Bad Request
- **Cause**: Invalid input data or missing required fields
- **Solution**: Add input validation, check request body format

#### Timeout Errors
- **Cause**: Long-running operations or external service calls
- **Solution**: Add timeouts, implement async operations, optimize queries

---

## 📞 GETTING HELP

### Resources
1. **API Documentation**: Check endpoint files for implementation details
2. **Error Logs**: Dev server output shows compilation and runtime errors
3. **Test Scripts**: Use the provided test scripts for verification
4. **Code Examples**: Follow the patterns in working endpoints

### Debug Commands
```bash
# Test specific endpoint
curl -v http://localhost:3000/api/endpoint

# Check server status
curl -X GET http://localhost:3000/api/health

# Run all tests
node tests/api/quick-test-runner.cjs

# Check comprehensive status
node tests/api/comprehensive-api-test.cjs
```

---

## 🎯 NEXT STEPS

### Immediate (Today)
1. Test core user flows with working endpoints
2. Implement frontend integration with auth
3. Create workspace management UI
4. Test payment flow with mock responses

### Short Term (This Week)
1. Configure email service for verification
2. Add database tables for session persistence
3. Implement real payment processing
4. Add comprehensive error handling

### Long Term (This Month)
1. Add AI services for onboarding
2. Implement advanced monitoring
3. Add storage and file handling
4. Optimize performance and security

**Happy coding! 🚀**
