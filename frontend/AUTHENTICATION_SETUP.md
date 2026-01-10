# RaptorFlow Authentication & Payment Setup

## Overview
Complete authentication and payment system has been implemented with the following features:
- Supabase authentication with Google OAuth and email/password
- Three-tier subscription system (Soar ₹5000, Ascent ₹7000, Glide ₹10000)
- PhonePe payment gateway integration (test mode)
- Route protection based on authentication and subscription status
- Beautiful UI matching RaptorFlow's design system

## Setup Instructions

### 1. Environment Variables
Update your `.env.local` file with the following:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# PhonePe Configuration (Test Mode)
NEXT_PUBLIC_PHONEPE_MERCHANT_ID=PGTESTPAYUAT
NEXT_PUBLIC_PHONEPE_SALT_KEY=099eb0cd-02cf-4e2a-8aca-3e6c6aff0399
NEXT_PUBLIC_PHONEPE_ENV=TEST
```

### 2. Supabase Setup
1. Run the migration to create required tables:
   ```bash
   supabase db push
   ```

2. Configure Google OAuth in Supabase Dashboard:
   - Go to Authentication > Providers
   - Enable Google provider
   - Add your Google OAuth credentials

### 3. Database Tables
The following tables are created:
- `user_profiles`: Stores user information and subscription details
- `payments`: Tracks all payment transactions

## Flow Overview

### Authentication Flow
1. User clicks "Get Started" or "Login" on landing page
2. Redirected to login page with Google/email options
3. After authentication, checks subscription status
4. If active subscription → redirects to workspace
5. If no subscription → redirects to pricing page

### Payment Flow
1. User selects a plan on pricing page
2. Creates payment order via PhonePe API
3. Redirects to PhonePe payment page
4. After payment, webhook updates subscription status
5. User redirected to success page and then to workspace

## Route Protection
- `/workspace` - Requires authentication AND active subscription
- `/login` - Redirects to workspace if already authenticated
- `/pricing` - Public but checks auth state for personalized display

## Key Components

### AuthContext (`/src/contexts/AuthContext.tsx`)
- Provides authentication state and methods
- Handles user profile fetching
- Manages subscription status

### Middleware (`/src/middleware.ts`)
- Protects routes based on auth and subscription
- Handles redirects for unauthorized access

### Payment APIs
- `/api/payment/create-order` - Creates PhonePe payment order
- `/api/payment/verify` - Verifies payment completion
- `/api/payment/webhook` - Handles PhonePe webhooks

## Testing
- Use PhonePe test credentials for payment testing
- Test cards: Any valid card number with future expiry
- No actual charges will be made in test mode

## Styling
All pages follow RaptorFlow's unique design system:
- Blueprint grid backgrounds
- Architectural measurement marks
- Sharp corners and borders
- Custom typography (Crimson Pro + Inter + JetBrains Mono)
- Ink bleed shadows and hover effects

## Next Steps
1. Configure production PhonePe credentials
2. Set up proper domain in Supabase
3. Configure email templates for confirmations
4. Add more payment methods if needed
5. Implement subscription management features
