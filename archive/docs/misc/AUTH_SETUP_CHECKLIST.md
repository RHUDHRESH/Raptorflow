# RaptorFlow Authentication Setup Checklist

## ✅ Completed Implementation

### 1. **Authentication System**
- [x] Supabase client configured
- [x] AuthContext with session management
- [x] Google OAuth integration
- [x] Email/password authentication
- [x] Automatic profile creation on signup
- [x] Session persistence

### 2. **Database Schema**
- [x] `user_profiles` table with subscription tracking
- [x] `payments` table for transaction history
- [x] RLS policies for security
- [x] Triggers for automatic profile creation

### 3. **UI Components**
- [x] Login/Signup page with dual auth options
- [x] Pricing page with 3 tiers (Soar ₹5k, Ascent ₹7k, Glide ₹10k)
- [x] Workspace page (protected)
- [x] Auth callback handler
- [x] Payment success/failed pages

### 4. **Payment Integration**
- [x] PhonePe test mode integration
- [x] Order creation API
- [x] Payment verification
- [x] Webhook handler

### 5. **Route Protection**
- [x] Middleware for protected routes
- [x] Subscription status checks
- [x] Automatic redirects

## 🔧 Required Actions

### 1. **Supabase Dashboard Configuration**
- [ ] Go to https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc
- [ ] Authentication → Settings:
  - [ ] Set Site URL: `https://raptorflow.in`
  - [ ] Add Redirect URLs: `https://raptorflow.in/auth/callback`
  - [ ] Disable email confirmations for testing (or keep enabled)
- [ ] Authentication → Providers:
  - [ ] Enable Google provider
  - [ ] Add Google OAuth credentials
  - [ ] Set Authorized redirect URI: `https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback`

### 2. **Environment Variables**
Update `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. **Database Migration**
Run the migration to create tables:
```bash
cd supabase
supabase db push
```

### 4. **Google OAuth Setup**
1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add authorized redirect: `https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback`
4. Copy Client ID and Secret to Supabase

## 🚀 Testing Flow

### 1. **Email Authentication (Should work immediately)**
1. Visit `https://raptorflow.in/login`
2. Click "Sign Up"
3. Enter email, password, and name
4. Account created → Can sign in
5. Redirected to pricing page
6. Select plan → PhonePe payment
7. After payment → Access workspace

### 2. **Google Authentication (After OAuth setup)**
1. Visit `https://raptorflow.in/login`
2. Click "Continue with Google"
3. Complete Google OAuth
4. Redirected to pricing page (new user)
5. Select plan → PhonePe payment
6. After payment → Access workspace

### 3. **Protected Routes**
- `/workspace` - Requires auth + active subscription
- `/pricing` - Public but checks auth state
- `/login` - Redirects to workspace if logged in

## 🐛 Troubleshooting

### "Deployment temporarily paused"
- Check Supabase project status
- Resume project if paused
- Verify correct URL in environment

### OAuth redirect errors
- Ensure redirect URLs match exactly
- Check Google OAuth configuration
- Verify site URL in Supabase

### Payment issues
- Using test mode (no real charges)
- Test with any card number with future expiry
- Check PhonePe test credentials

## 📝 Notes

- Email confirmation is disabled by default for easier testing
- All new users start with no subscription
- Only paid users can access workspace
- PhonePe is in test mode
- Database triggers automatically create user profiles
- Middleware handles route protection automatically
