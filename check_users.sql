-- Check existing users and their onboarding status
SELECT 
  id,
  email,
  full_name,
  onboarding_status,
  created_at,
  last_login_at
FROM users 
ORDER BY created_at DESC;
