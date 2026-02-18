# Authentication Security

## Security Measures Implemented

### 1. Token Storage

| Feature | Implementation |
|---------|----------------|
| Storage Type | HTTP-only cookies |
| HttpOnly | ✅ Yes - JavaScript cannot access |
| Secure | ✅ Yes - HTTPS only in production |
| SameSite | ✅ Lax - Balance of security and usability |
| Access Token Expiry | 1 hour (3600s) |
| Refresh Token Expiry | 7 days (604800s) |

### 2. Password Security

| Feature | Implementation |
|---------|----------------|
| Minimum Length | 8 characters |
| Maximum Length | 72 characters (bcrypt limit) |
| Email Validation | Regex pattern |
| Hash Algorithm | Bcrypt (via Supabase) |

### 3. Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/login` | 5 attempts | 1 minute |
| `/auth/signup` | 3 attempts | 1 hour |
| `/auth/verify` | 30 attempts | 1 minute |

### 4. Database Security (RLS)

All tables have Row Level Security enabled:

| Table | Policy |
|-------|--------|
| profiles | Users can view own profiles |
| workspaces | Users can view own workspaces |
| workspace_members | Users can view own memberships |
| foundations | Users can view workspace foundations |
| business_context_manifests | Users can view workspace BCM |
| campaigns | Users can view workspace campaigns |
| moves | Users can view workspace moves |
| icp_profiles | Users can view workspace ICP |
| assets | Users can view workspace assets |

**Service Role Bypass:** All tables also allow service_role to bypass RLS for admin operations.

### 5. API Security

| Feature | Implementation |
|---------|----------------|
| Authentication | Bearer token + HTTP-only cookies |
| CORS | Configured per environment |
| Input Validation | Pydantic models |
| Error Messages | Generic (no sensitive info leaked) |

### 6. Frontend Security

| Feature | Implementation |
|---------|----------------|
| Route Protection | Next.js middleware |
| Session Management | Zustand store |
| Auth State | Server-side validation |
| Redirect Logic | AuthProvider component |

## Security Checklist

- [x] HTTP-only cookies
- [x] Secure flag in production
- [x] SameSite=Lax
- [x] Rate limiting on auth endpoints
- [x] Password minimum 8 characters
- [x] Email validation
- [x] Row Level Security on all tables
- [x] Service role separate from anon key

## Best Practices

### For Production

1. **Enable Email Confirmation**
   - Configure in Supabase dashboard
   - Users must verify email before logging in

2. **Use HTTPS**
   - Set `COOKIE_SECURE=true`
   - Configure SSL certificate

3. **Rotate JWT Secrets**
   - Regenerate periodically
   - Use Supabase dashboard

4. **Monitor Failed Attempts**
   - Set up alerts for rate limit triggers
   - Track failed login attempts

### For Development

1. **Use Demo Mode**
   - Set `AUTH_MODE=demo`
   - Any credentials work

2. **Test Security**
   - Run `python scripts/verify_auth_env.py`
   - Test RLS policies

## Known Limitations

1. **In-Memory Rate Limiting**
   - Not shared across multiple servers
   - Use Redis for distributed systems

2. **LocalStorage Alternative**
   - HTTP-only cookies are more secure
   - Some SSR scenarios may need localStorage fallback

## Incident Response

If authentication is compromised:

1. **Immediately rotate keys**
   - Generate new Supabase keys
   - Update environment variables

2. **Invalidate sessions**
   - Use Supabase dashboard
   - Call `/auth/logout` for all users

3. **Enable additional verification**
   - Turn on email confirmation
   - Add MFA (future)

4. **Review logs**
   - Check audit_logs table
   - Look for unauthorized access
