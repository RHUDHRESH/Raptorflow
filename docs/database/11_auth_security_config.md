# Auth Security Configuration Guide

This is a **manual configuration** step in the Supabase Dashboard (cannot be automated via migrations).

## Steps to Enable Leaked Password Protection

1. **Navigate to Auth Settings**
   - Open your Supabase project: https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc
   - Go to **Authentication** → **Policies**

2. **Enable Password Protection Features**
   
   **Password Strength**:
   - Find "Minimum Password Strength" setting
   - Select **"Good"** or **"Strong"** (recommended: Strong)
   - This enforces password complexity requirements

   **Leaked Password Protection**:
   - Toggle **"Enable leaked password protection"** to ON
   - This checks passwords against HaveIBeenPwned.org database
   - Prevents users from using compromised passwords

3. **Additional Security Recommendations**

   **Multi-Factor Authentication (MFA)**:
   - Enable MFA in Authentication → Providers
   - Recommend TOTP-based authenticators

   **Session Settings**:
   - Set reasonable session timeout (default 1 week is good)
   - Enable "Refresh token rotation" for better security
   
   **Email Verification**:
   - Ensure "Confirm email" is enabled
   - Prevents spam accounts

## Why This Matters

**Leaked Password Protection**: 
- Blocks passwords exposed in data breaches
- Reduces account takeover risk
- Complies with security best practices

**Password Strength**:
- Prevents weak passwords like "password123"
- Enforces length, complexity requirements
- Reduces brute-force attack success

## Verification

After enabling, test with a known compromised password (e.g., "password"):
1. Try to sign up with weak password → Should fail
2. Check error message mentions password strength/leaked password
3. Sign up with strong, unique password → Should succeed

## Impact on Users

**Existing Users**: No immediate impact (passwords not retroactively checked)

**New Signups**: Must use strong, non-leaked passwords

**Password Resets**: New passwords must meet strength requirements

## Rollback

If needed, disable via dashboard:
- Authentication → Policies
- Toggle settings back to OFF
- Users will immediately be able to use weaker passwords (not recommended)
