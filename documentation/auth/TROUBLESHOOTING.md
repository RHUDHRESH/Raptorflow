# Authentication Troubleshooting

## Common Issues

### Issue: "Supabase not configured"

**Symptoms:**
- Auth returns error: "Supabase not configured"

**Solution:**
1. Check `.env` file has:
   ```
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=eyJ...
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   ```

2. Verify keys match project:
   ```bash
   python scripts/verify_auth_env.py
   ```

---

### Issue: "Invalid email or password"

**Symptoms:**
- Login fails with "Invalid credentials"

**Solution:**
1. Check `AUTH_MODE` is set to `supabase`:
   ```
   AUTH_MODE=supabase
   ```

2. Verify user exists in Supabase:
   - Go to Supabase Dashboard → Authentication → Users
   - Check if user is confirmed

3. If using email confirmation:
   - User must confirm email before login works

---

### Issue: "Rate limit exceeded"

**Symptoms:**
- Error: "Rate limit exceeded. Try again later."

**Solution:**
1. Wait for the rate limit window to reset:
   - Login: 1 minute
   - Signup: 1 hour

2. For testing, use demo mode:
   ```
   AUTH_MODE=demo
   ```

---

### Issue: "Token expired"

**Symptoms:**
- API returns 401 after 1 hour

**Solution:**
1. Use refresh endpoint:
   ```
   POST /api/v1/auth/refresh
   ```

2. Frontend automatically handles refresh via Supabase JS

---

### Issue: "CORS error"

**Symptoms:**
- Browser console: "CORS policy: No 'Access-Control-Allow-Origin'"

**Solution:**
1. Check CORS_ORIGINS in backend/.env:
   ```
   CORS_ORIGINS=http://localhost:3000
   ```

2. For production, add your domain:
   ```
   CORS_ORIGINS=https://app.raptorflow.in
   ```

---

### Issue: "User not found" after login

**Symptoms:**
- Login succeeds but /auth/me returns 401

**Solution:**
1. Check database connection:
   ```bash
   python scripts/supabase_production_check.py
   ```

2. Verify RLS policies are applied:
   ```sql
   SELECT * FROM pg_policies WHERE schemaname = 'public';
   ```

---

### Issue: "Cookie not set"

**Symptoms:**
- Login works but no cookies in browser

**Solution:**
1. Check you're using HTTPS in production (Secure cookie requirement)
2. Check SameSite setting
3. Check third-party cookies not blocked

---

### Issue: Demo mode not working

**Symptoms:**
- Even with `AUTH_MODE=demo`, login still fails

**Solution:**
1. Make sure AUTH_MODE is set in correct .env file
 backend server after changing2. Restartenv
3. . Check logs for auth service initialization

---

## Verification Commands

### Check Auth Health
```bash
curl http://localhost:8000/api/v1/auth/health
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Test Token Verification
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"access_token":"your-token"}'
```

### Check Environment
```bash
python scripts/verify_auth_env.py
```

---

## Logs Location

- **Backend**: Check console output or logs folder
- **Supabase**: Supabase Dashboard → Logs
- **Browser**: Developer Tools → Console/Network

---

## Getting Help

1. Check `documentation/auth/` for full docs
2. Run verification script: `python scripts/verify_auth_env.py`
3. Check Supabase dashboard for auth issues
4. Review browser console for frontend errors
