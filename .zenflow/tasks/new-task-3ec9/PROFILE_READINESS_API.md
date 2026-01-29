# Profile Readiness API Documentation

## Overview

The Profile Readiness API provides a robust system for verifying user profile completeness, workspace existence, and payment status before granting access to protected routes. This API ensures that users have completed all necessary onboarding steps and have valid payment arrangements before accessing the application.

## Architecture

### Components

1. **Profile Service** (`backend/services/profile_service.py`)
   - Core business logic for profile verification
   - Handles subscription state management with timestamp validation
   - Provides structured error handling

2. **API Endpoints** (`backend/api/v1/auth.py`)
   - `/auth/ensure-profile` - Creates missing profile/workspace records
   - `/auth/verify-profile` - Returns current profile readiness status

3. **Frontend AuthProvider** (`src/components/auth/AuthProvider.tsx`)
   - Manages authentication state
   - Implements caching and debouncing for profile checks
   - Handles smart redirects with state tracking

4. **ProfileGate** (`src/components/auth/ProfileGate.tsx`)
   - Route protection component
   - Prevents endless redirects
   - Provides error UI for failed verifications

5. **Middleware** (`src/middleware.ts`)
   - Server-side profile verification
   - Fail-closed security behavior
   - Multi-domain deployment support

## API Endpoints

### POST /api/v1/auth/ensure-profile

Creates missing user profile, workspace, and membership records.

**Request:**
```http
POST /api/v1/auth/ensure-profile
Authorization: Bearer <token>
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "workspace_id": "workspace-uuid",
  "subscription_plan": "pro",
  "subscription_status": "active"
}
```

**Error Responses:**
- `422 Unprocessable Entity` - Profile service errors
- `500 Internal Server Error` - Unexpected errors

### GET /api/v1/auth/verify-profile

Returns current profile readiness status for gating access.

**Request:**
```http
GET /api/v1/auth/verify-profile
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "profile_exists": true,
  "workspace_exists": true,
  "workspace_id": "workspace-uuid",
  "subscription_plan": "pro",
  "subscription_status": "active",
  "needs_payment": false
}
```

**Error Responses:**
- `422 Unprocessable Entity` - Profile service errors
- `500 Internal Server Error` - Unexpected errors

## Subscription State Handling

The system handles explicit subscription states with timestamp validation:

| Status | Payment Required | Conditions |
|--------|------------------|------------|
| `active` | No | Current subscription is valid |
| `trialing` | No* | Trial hasn't expired (`trial_end` timestamp) |
| `past_due` | No* | Within grace period (`grace_period_end` timestamp) |
| `canceled` | No* | Access continues until `current_period_end` |
| `unpaid` | Yes | Immediate payment required |
| `incomplete` | Yes | Payment processing incomplete |
| `incomplete_expired` | Yes | Payment expired |
| `paused` | Yes | Subscription paused |

*Timestamp validation applies

## Frontend Integration

### AuthProvider Usage

```typescript
import { useAuth } from '@/components/auth/AuthProvider';

function MyComponent() {
  const { isAuthenticated, profileStatus, isCheckingProfile } = useAuth();

  if (!isAuthenticated) return <Login />;
  if (isCheckingProfile) return <Loading />;
  if (!profileStatus.isReady) return <Onboarding />;

  return <ProtectedContent />;
}
```

### ProfileGate Usage

```typescript
import { ProfileGate } from '@/components/auth/ProfileGate';

function App() {
  return (
    <AuthProvider>
      <ProfileGate>
        <Routes />
      </ProfileGate>
    </AuthProvider>
  );
}
```

## Middleware Behavior

The middleware performs server-side profile verification for protected routes:

1. **Direct Backend Communication**: Uses `BACKEND_URL` instead of proxy routes
2. **Timeout Protection**: 5-second timeout for profile checks
3. **Fail-Closed Security**: Blocks access if verification fails
4. **Comprehensive Logging**: Logs all verification attempts and failures

### Environment Variables

```bash
# Backend URL for direct communication
BACKEND_URL=https://api.raptorflow.com

# Fallback API URL
NEXT_PUBLIC_API_URL=https://api.raptorflow.com
```

## Error Handling

### Structured Errors

All profile service errors include structured information:

```json
{
  "error": "PROFILE_VERIFICATION_ERROR",
  "message": "Profile verification failed: Database connection error",
  "context": {
    "user_id": "user-uuid",
    "email": "user@example.com"
  }
}
```

### Frontend Error States

- **Network Errors**: Automatic retry with exponential backoff
- **Server Errors**: Error UI with retry options
- **Timeout Errors**: Graceful degradation with manual retry

## Security Features

### Fail-Closed Behavior

- Middleware blocks access if profile verification fails
- Frontend prevents access to protected routes
- Automatic logout on critical errors

### Rate Limiting

- Profile checks are debounced (500ms)
- Results cached for 30 seconds
- Maximum 3 retry attempts

### Monitoring

- All verification attempts logged
- Security events recorded for failures
- Performance metrics tracked

## Database Schema

### Key Tables

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  auth_user_id VARCHAR UNIQUE,
  email VARCHAR UNIQUE,
  full_name TEXT,
  subscription_plan VARCHAR DEFAULT 'free',
  subscription_status VARCHAR DEFAULT 'trial',
  trial_end TIMESTAMPTZ,
  grace_period_end TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workspaces table (owner_id only, no user_id)
CREATE TABLE workspaces (
  id UUID PRIMARY KEY,
  owner_id UUID REFERENCES users(id),
  name TEXT NOT NULL,
  slug TEXT UNIQUE,
  is_trial BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workspace members table
CREATE TABLE workspace_members (
  workspace_id UUID REFERENCES workspaces(id),
  user_id UUID REFERENCES users(id),
  role VARCHAR DEFAULT 'member',
  is_active BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (workspace_id, user_id)
);

-- Subscriptions table
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  workspace_id UUID REFERENCES workspaces(id),
  plan VARCHAR NOT NULL,
  status VARCHAR NOT NULL,
  trial_end TIMESTAMPTZ,
  grace_period_end TIMESTAMPTZ,
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Testing

### Backend Tests

```bash
# Run profile service tests
pytest backend/tests/services/test_profile_service.py -v

# Run API endpoint tests
pytest backend/tests/api/test_auth_endpoints.py -v
```

### Frontend Tests

```bash
# Run AuthProvider tests
npm test -- src/components/auth/__tests__/AuthProvider.test.tsx

# Run integration tests
npm test -- src/components/auth/__tests__/
```

## Deployment Considerations

### Environment Configuration

1. **Development**: Uses `http://localhost:8000` as backend URL
2. **Staging**: Uses staging API endpoint
3. **Production**: Uses production API endpoint with proper SSL

### Monitoring Setup

1. **Logs**: Profile verification logs sent to monitoring service
2. **Metrics**: Success/failure rates tracked
3. **Alerts**: High failure rate triggers alerts

### Performance Optimization

1. **Caching**: 30-second cache for profile status
2. **Debouncing**: 500ms debounce for repeated checks
3. **Timeout**: 5-second timeout for API calls

## Troubleshooting

### Common Issues

1. **Middleware Fails Closed**
   - Check backend URL configuration
   - Verify network connectivity
   - Check authentication token validity

2. **Endless Redirects**
   - Clear browser cache and cookies
   - Check profile status in database
   - Verify subscription state timestamps

3. **Profile Verification Errors**
   - Check database connectivity
   - Verify user record exists
   - Check workspace membership

### Debug Commands

```bash
# Check profile status directly
curl -H "Authorization: Bearer <token>" \
     https://api.raptorflow.com/api/v1/auth/verify-profile

# Check middleware logs
grep "profile verification" /var/log/nginx/access.log

# Test database connection
psql $DATABASE_URL -c "SELECT * FROM users WHERE id = 'user-uuid';"
```

## Migration Notes

### From Legacy System

1. **User ID Migration**: Legacy `user_id` column removed from workspaces
2. **Subscription States**: Enhanced state handling with timestamps
3. **Error Handling**: Structured error responses
4. **Security**: Fail-closed behavior implemented

### Breaking Changes

- API endpoints now return structured errors
- Middleware requires direct backend URL configuration
- Frontend components updated for new error handling

## Future Enhancements

1. **Real-time Updates**: WebSocket notifications for profile changes
2. **Advanced Analytics**: Detailed profile completion metrics
3. **Multi-tenant Support**: Enhanced workspace isolation
4. **Mobile Optimization**: Improved mobile experience
