# 🚀 RAPTORFLOW - QUICK START GUIDE

## 🎯 GET STARTED IN 5 MINUTES

### Step 1: Start Development Server
```bash
npm run dev
```

### Step 2: Verify API Status
```bash
node tests/api/quick-test-runner.cjs
```

### Step 3: Open Browser
Navigate to: `http://localhost:3000`

---

## 🛠️ DEVELOPMENT WORKFLOW

### 1. Test API Endpoints
```bash
# Quick test
curl -X POST http://localhost:3000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Create workspace
curl -X POST http://localhost:3000/api/onboarding/create-workspace \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Workspace", "userId": "user123"}'
```

### 2. Run Test Suite
```bash
# Complete automated testing
tests\api\api-test-suite.bat
```

### 3. Start Building Features
- **Authentication**: `src/app/login/page.tsx`
- **Dashboard**: `src/app/(shell)/dashboard/page.tsx`
- **Onboarding**: `src/app/onboarding/`

---

## 📁 KEY FILES TO KNOW

### API Endpoints (Working)
- `src/app/api/auth/forgot-password/route.ts` ✅
- `src/app/api/me/subscription/route.ts` ✅
- `src/app/api/onboarding/create-workspace/route.ts` ✅
- `src/app/api/complete-mock-payment/route.ts` ✅

### Frontend Pages
- `src/app/login/page.tsx` - Login interface
- `src/app/signup/page.tsx` - Signup process
- `src/app/(shell)/dashboard/page.tsx` - Main dashboard
- `src/app/onboarding/page.tsx` - Onboarding flow

### Components
- `src/components/ui/` - Reusable UI components
- `src/components/auth/` - Authentication components
- `src/components/onboarding/` - Onboarding components

---

## 🧪 TESTING COMMANDS

### Quick Tests
```bash
# Test critical endpoints
node tests/api/quick-test-runner.cjs

# Test all endpoints
node tests/api/comprehensive-api-test.cjs

# Automated suite
tests\api\api-test-suite.bat
```

### Manual Testing
```bash
# Test auth flow
curl -X GET http://localhost:3000/api/me/subscription

# Test workspace creation
curl -X POST http://localhost:3000/api/onboarding/create-workspace \
  -H "Content-Type: application/json" \
  -d '{"name": "My Workspace"}'

# Test payment
curl -X POST http://localhost:3000/api/complete-mock-payment \
  -H "Content-Type: application/json" \
  -d '{"transactionId": "test123"}'
```

---

## 🎨 FRONTEND DEVELOPMENT

### Component Pattern
```typescript
// Use this pattern for new components
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';

export default function MyComponent() {
  return (
    <BlueprintCard figure="FIG. 01" code="COMPONENT">
      <BlueprintButton variant="blueprint">
        Click Me
      </BlueprintButton>
    </BlueprintCard>
  );
}
```

### API Integration Pattern
```typescript
// Use this pattern for API calls
const response = await fetch('/api/endpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});

const result = await response.json();
```

---

## 🔧 COMMON TASKS

### Add New API Endpoint
1. Create file: `src/app/api/my-endpoint/route.ts`
2. Follow this pattern:
```typescript
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const data = await request.json();
    return NextResponse.json({ success: true, data });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process' },
      { status: 500 }
    );
  }
}
```

### Add New Page
1. Create file: `src/app/my-page/page.tsx`
2. Follow this pattern:
```typescript
export default function MyPage() {
  return (
    <div className="min-h-screen bg-[var(--canvas)]">
      <h1 className="font-serif text-3xl text-[var(--ink)]">
        My Page
      </h1>
    </div>
  );
}
```

### Style Components
```css
/* Use Blueprint design system */
.my-component {
  background: var(--canvas);
  color: var(--ink);
  padding: var(--spacing-lg);
  border: 1px solid var(--border);
}
```

---

## 📊 CURRENT STATUS

### ✅ Working Features
- User authentication (Supabase)
- Password reset flow
- Workspace creation
- Mock payment processing
- Admin impersonation
- Health monitoring

### ⚠️ Needs Configuration
- Email verification (Resend API)
- Real payment processing
- AI services integration
- Database tables for advanced features

### 📚 Documentation
- `tests/api/README.md` - API testing guide
- `tests/api/development-playbook.md` - Development workflow
- `NEXT_PHASE_FEATURE_DEVELOPMENT.md` - Feature development plan

---

## 🚀 QUICK DEVELOPMENT TASKS

### Task 1: Improve Login Page
```bash
# File to edit: src/app/login/page.tsx
# Add: Better form validation, loading states, error handling
```

### Task 2: Build Dashboard
```bash
# File to edit: src/app/(shell)/dashboard/page.tsx
# Add: Workspace overview, quick actions, user profile
```

### Task 3: Enhance Onboarding
```bash
# File to edit: src/app/onboarding/page.tsx
# Add: Progress tracking, better UX, form validation
```

### Task 4: Add Settings Page
```bash
# Create: src/app/settings/page.tsx
# Add: User profile, preferences, workspace settings
```

---

## 🔍 DEBUGGING

### Check API Status
```bash
# Health check
curl -X GET http://localhost:3000/api/health

# Check specific endpoint
curl -v http://localhost:3000/api/me/subscription
```

### Check Frontend
- Open browser dev tools (F12)
- Check Console for errors
- Check Network tab for API calls
- Verify environment variables

### Common Issues
- **500 errors**: Check dev server logs
- **404 errors**: Verify file paths
- **Authentication issues**: Check Supabase configuration
- **Environment issues**: Check .env.local file

---

## 📞 GETTING HELP

### Resources
1. **API Documentation**: `tests/api/README.md`
2. **Development Guide**: `tests/api/development-playbook.md`
3. **Component Examples**: Check existing components
4. **Design System**: Blueprint components in `src/components/ui/`

### Troubleshooting Steps
1. Run API test suite: `tests\api\api-test-suite.bat`
2. Check dev server output for errors
3. Verify environment variables
4. Test with curl before frontend integration
5. Check browser console for JavaScript errors

---

## 🎯 SUCCESS CRITERIA

### Your First Day Goals
- [ ] Dev server running without errors
- [ ] API test suite passes
- [ ] Can create a workspace via API
- [ ] Login page loads correctly
- [ ] Basic navigation works

### Your First Week Goals
- [ ] Complete user authentication flow
- [ ] Build basic dashboard
- [ ] Implement workspace creation UI
- [ ] Add payment flow UI
- [ ] Test complete user journey

---

## 🚀 START CODING!

**The foundation is ready. Start building!**

1. **Pick a task** from the list above
2. **Follow the patterns** shown in examples
3. **Test your work** with the API test suite
4. **Iterate quickly** and get feedback

**Happy coding! 🎯**

---

*Last updated: January 24, 2026*
*Status: READY FOR DEVELOPMENT*
