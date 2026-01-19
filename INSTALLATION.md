# Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

This will install all required dependencies including:
- Supabase auth helpers
- Sentry for error tracking
- JSON Web Token handling
- OTP library for MFA
- QR code generation
- All type definitions

### 2. Set Up Environment Variables

```bash
cp .env.local.example .env.local
```

Fill in your credentials in `.env.local`:
- Supabase URL and keys
- Google OAuth credentials
- PhonePe merchant details
- Sentry DSN
- Other service credentials

### 3. Set Up Supabase

```bash
npx supabase start
npx supabase db push
```

### 4. Run Development Server

```bash
npm run dev
```

## Resolving Lint Errors

After running `npm install`, the following lint errors will be resolved:

### ✅ Fixed Dependencies
- `@supabase/auth-helpers-nextjs` - Supabase authentication helpers
- `next/headers` - Next.js headers utilities
- `next/server` - Next.js server utilities
- `jsonwebtoken` - JWT handling
- `@supabase/supabase-js` - Supabase client
- `otplib` - One-time password generation
- `qrcode` - QR code generation
- `@sentry/nextjs` - Sentry error tracking

### ✅ Fixed TypeScript Errors
- Implicit `any` types in rate-limit.ts
- Missing React imports in Sentry config
- Type annotations for event handlers

## Additional Setup

### Sentry Configuration

1. Create a Sentry project at https://sentry.io
2. Add your DSN to `.env.local`:
   ```
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```

### PhonePe Integration

1. Register for a PhonePe merchant account
2. Add credentials to `.env.local`:
   ```
   PHONEPE_MERCHANT_ID=your-merchant-id
   PHONEPE_SALT_KEY=your-salt-key
   PHONEPE_SALT_INDEX=1
   ```

### Google OAuth

1. Create a project in Google Cloud Console
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add to `.env.local`:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

### Redis Cache

1. Create an Upstash Redis database
2. Add to `.env.local`:
   ```
   UPSTASH_REDIS_REST_URL=your-redis-url
   UPSTASH_REDIS_REST_TOKEN=your-token
   ```

### Email Service

1. Sign up for Resend
2. Verify your domain
3. Add to `.env.local`:
   ```
   RESEND_API_KEY=re_your-api-key
   RESEND_FROM_EMAIL=noreply@yourdomain.com
   ```

## Troubleshooting

### If you still see lint errors after npm install:

1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Update TypeScript:
   ```bash
   npm install typescript@latest
   ```

3. Restart your IDE:
   - VS Code: Cmd+Shift+P → "Developer: Reload Window"
   - Other IDEs: Restart completely

### Common Issues

1. **"Cannot find module" errors**
   - Run `npm install`
   - Check if the module is in package.json
   - Clear npm cache: `npm cache clean --force`

2. **TypeScript errors**
   - Run `npm run type-check`
   - Ensure all imports are correct
   - Check tsconfig.json configuration

3. **Supabase connection issues**
   - Check Supabase is running: `npx supabase status`
   - Verify environment variables
   - Check network connectivity

## Production Deployment

### Vercel Deployment

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel --prod
   ```

3. Add environment variables in Vercel dashboard

### Environment Variables for Production

Required variables:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `PHONEPE_MERCHANT_ID`
- `PHONEPE_SALT_KEY`
- `SENTRY_DSN`
- `RESEND_API_KEY`

## Next Steps

1. Read the [Disaster Recovery Guide](./docs/DISASTER_RECOVERY.md)
2. Review the [Admin Dashboard Guide](./docs/ADMIN_DASHBOARD.md)
3. Check out the [API Documentation](./docs/API.md)

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review GitHub issues
3. Contact support at support@raptorflow.com

---

Ready to go! 🚀 Your complete user management system is now installed and configured.
