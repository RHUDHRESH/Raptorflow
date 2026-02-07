# Supabase Setup Guide

## ✅ Status: FIXED

Your Supabase configuration has been set up correctly!

## What Was Done

1. **Created `.env` file** in the project root with proper Supabase credentials
2. **Configured environment variables**:
   - `VITE_SUPABASE_URL`: https://vpwwzsanuyhpkvgorcnc.supabase.co
   - `VITE_SUPABASE_ANON_KEY`: ✓ Set (from backend/.env)

## Next Steps

### 1. Restart Your Dev Server

**IMPORTANT**: Vite only loads environment variables on startup. You MUST restart your dev server:

```bash
# Stop the current dev server (Ctrl+C)
# Then restart:
npm run dev
```

### 2. Verify Supabase Connection

After restarting, the login page should:
- ✅ Show no "Configuration Missing" warning
- ✅ Allow Google OAuth login
- ✅ Allow email/password authentication

### 3. Enable Google OAuth (Optional)

If you want Google login to work:

1. Go to [Supabase Dashboard](https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc/auth/providers)
2. Navigate to: **Authentication → Providers → Google**
3. Enable Google provider
4. Add your OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

### 4. Dev Bypass (For Testing)

If you're still having issues, you can use the **Dev Bypass** button on the login page (only visible in development mode) to skip authentication temporarily.

## Troubleshooting

### "Configuration Missing" Still Shows

- Make sure you **restarted the dev server** after creating `.env`
- Check that `.env` is in the project root (same level as `package.json`)
- Verify the file contains `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`

### Google Login Not Working

- Check if Google provider is enabled in Supabase Dashboard
- Verify OAuth redirect URLs are configured correctly
- Use the Dev Bypass button for now

### Database Tables Missing

If you get errors about missing tables:
1. Go to Supabase Dashboard → SQL Editor
2. Run the migration scripts in `database/` folder
3. Or use the backend API to initialize tables

## Environment Variables Reference

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

### Backend (backend/.env)
```env
SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_KEY=<your-service-key>
```

## Quick Commands

```bash
# Start frontend dev server
npm run dev

# Start backend server
cd backend
python main.py

# Check if .env exists
ls .env

# View Supabase config (without exposing keys)
cat .env | grep VITE_SUPABASE_URL
```

---

**Need Help?** Check the [Supabase Documentation](https://supabase.com/docs) or the project's main README.
