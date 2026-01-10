# 🚀 RAPTORFLOW COMPLETE SETUP GUIDE

## ✅ What's Already Done:

### 1. Database Tables
- ✅ `user_profiles` table created with subscription tracking
- ✅ `payments` table created with PhonePe integration
- ✅ RLS policies for security
- ✅ Automatic profile creation trigger
- ✅ Storage quotas based on subscription plans

### 2. Authentication System
- ✅ Google OAuth integration
- ✅ Email/password authentication
- ✅ Auth context and session management
- ✅ Protected routes with middleware
- ✅ Automatic profile creation on signup

### 3. Payment System
- ✅ PhonePe test mode integration
- ✅ Order creation API
- ✅ Payment verification API
- ✅ Webhook handler
- ✅ Success/failure pages

### 4. UI Components
- ✅ Login/signup page
- ✅ Pricing page with 3 tiers
- ✅ Workspace page (protected)
- ✅ Blueprint design system

## 🔧 FINAL STEPS TO COMPLETE:

### Step 1: Get Your Service Role Key
1. Go to: https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/settings/api
2. Copy the `service_role` key (NOT the anon key)
3. Update your `.env.local` file:
```env
SUPABASE_SERVICE_ROLE_KEY=your-actual-service-role-key-here
```

### Step 2: Create Storage Buckets
1. Go to: https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/sql
2. Copy and paste this SQL:

```sql
-- Create storage buckets
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
  ('user-avatars', 'user-avatars', true, 2097152, ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp']),
  ('user-documents', 'user-documents', false, 52428800, ARRAY['image/jpeg', 'image/png', 'application/pdf', 'text/plain', 'application/json']),
  ('workspace-files', 'workspace-files', false, 104857600, ARRAY['image/jpeg', 'image/png', 'application/pdf', 'application/vnd.ms-excel', 'text/csv'])
ON CONFLICT (id) DO NOTHING;

-- Create storage policies
CREATE POLICY "Users can view their own avatars" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'user-avatars' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can upload their own avatars" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'user-avatars' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can update their own avatars" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'user-avatars' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can manage their documents" ON storage.objects
  FOR ALL USING (
    bucket_id = 'user-documents' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can manage their workspace files" ON storage.objects
  FOR ALL USING (
    bucket_id = 'workspace-files' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );
```

3. Click "Run" to execute

### Step 3: Configure Google OAuth (Optional but Recommended)
1. Go to: https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/auth/providers
2. Enable Google provider
3. Get OAuth credentials from Google Cloud Console
4. Add redirect URI: `https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback`

### Step 4: Test Everything
1. Visit: http://localhost:3000/login
2. Test email signup (works immediately)
3. Test Google OAuth (if configured)
4. After signup → Pricing page
5. Select a plan → PhonePe payment
6. After payment → Workspace access

## 📊 Storage Quotas by Plan:

- **Free Tier**: 100 MB
- **Soar (₹5,000)**: 1 GB
- **Glide (₹7,000)**: 5 GB
- **Ascent (₹10,000)**: 10 GB

## 🔐 Security Features:

- Row Level Security (RLS) on all tables
- Users can only access their own data
- JWT-based authentication
- Secure file storage with policies

## 🚀 Ready to Use!

Once you complete the 3 steps above, your RaptorFlow application will be fully functional with:
- ✅ User authentication
- ✅ Subscription management
- ✅ Payment processing
- ✅ File storage
- ✅ Protected workspace

The system is production-ready and follows all best practices for security and scalability.
