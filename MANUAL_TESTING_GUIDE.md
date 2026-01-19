# 🧪 MANUAL AUTHENTICATION TESTING GUIDE
## Step-by-Step Browser Testing Instructions

---

## 📋 **PRE-TEST CHECKLIST**
- [x] Server running on `http://localhost:3000`
- [x] Test user created: `rhudhreshr@gmail.com`
- [x] Password: `TestPassword123`
- [x] Email service configured: Resend API
- [x] Target email: `rhudhresh3697@gmail.com`

---

## 🔧 **BROWSER SETUP**
1. **Use regular browser** (Chrome, Firefox, Safari, Edge)
2. **Clear cache and cookies** before testing
3. **Open Developer Tools** (F12) to monitor network requests
4. **Disable ad blockers** for localhost

---

## 📝 **TESTING STEPS**

### **Task 21: Navigate to Login Page**
1. Open browser
2. Go to: `http://localhost:3000/login`
3. **Expected**: Login page loads with email and password fields
4. **Check**: Page title, form elements, styling

### **Task 22: Test Login with Credentials**
1. Enter email: `rhudhreshr@gmail.com`
2. Enter password: `TestPassword123`
3. Click "Sign In" button
4. **Expected**: Form submits without errors
5. **Check**: Network request to `/api/auth/signin` or similar

### **Task 23: Verify Dashboard Redirect**
1. After successful login
2. **Expected**: Redirect to `/dashboard` or similar
3. **Check**: URL change, page content, user info display
4. **Screenshot**: Take screenshot of dashboard

### **Task 24: Test Logout Functionality**
1. Look for user profile/avatar (top right corner)
2. Click on profile/menu
3. Click "Sign Out" or "Logout"
4. **Expected**: Redirect back to login page
5. **Check**: Session cleared, cookies removed

### **Task 25: Navigate to Forgot Password**
1. On login page, click "Forgot your password?" link
2. **Expected**: Navigate to `/forgot-password`
3. **Check**: Page loads with email input field
4. **Alternative**: Direct navigation to `http://localhost:3000/forgot-password`

### **Task 26: Test Forgot Password Form**
1. Enter email: `rhudhreshr@gmail.com`
2. Click "Send Reset Link" or similar button
3. **Expected**: Success message appears
4. **Check**: Network request to `/api/auth/forgot-password`
5. **Screenshot**: Capture success message

### **Task 27: Verify Email Delivery**
1. Check email: `rhudhresh3697@gmail.com`
2. Look in: Inbox, Spam, Promotions folders
3. **Expected**: Email with subject "Reset Your RaptorFlow Password"
4. **Check**: From address `onboarding@resend.dev`
5. **Verify**: Reset link contains token parameter

### **Task 28: Test Password Reset**
1. Click reset link in email OR copy URL to browser
2. **Expected**: Reset password page loads
3. Enter new password: `NewPassword123`
4. Confirm password: `NewPassword123`
5. Click "Reset Password" button
6. **Expected**: Success message appears

### **Task 29: Verify Login with New Password**
1. Go back to login page
2. Enter email: `rhudhreshr@gmail.com`
3. Enter new password: `NewPassword123`
4. Click "Sign In"
5. **Expected**: Successful login to dashboard
6. **Check**: Old password no longer works

### **Task 30: Complete End-to-End Verification**
1. Test full flow from login → logout → password reset → new login
2. **Expected**: All steps work seamlessly
3. **Check**: No errors, proper redirects, email delivery
4. **Document**: Any issues or improvements needed

---

## 🔍 **DEBUGGING CHECKPOINTS**

### **If Login Page Shows "Forbidden"**
- Check middleware.ts for headless browser detection
- Temporarily comment out `/headless/i` in BLOCKED_USER_AGENTS
- Restart server and try again

### **If API Returns 500 Error**
- Check server logs in terminal
- Verify environment variables are set
- Check Supabase connection

### **If Email Not Received**
1. Check Resend API key is valid
2. Verify target email is `rhudhresh3697@gmail.com`
3. Check spam/promotions folders
4. Verify API call succeeded (check network tab)

### **If Reset Link Doesn't Work**
1. Check token format in URL
2. Verify token hasn't expired (1 hour)
3. Check reset password page loads correctly
4. Verify token validation API working

---

## 📊 **EXPECTED RESULTS**

### **Successful Test Indicators**
- ✅ Login page loads without errors
- ✅ Authentication works with test credentials
- ✅ Dashboard accessible after login
- ✅ Logout redirects to login page
- ✅ Forgot password form submits successfully
- ✅ Reset email received at target address
- ✅ Reset link works and loads password form
- ✅ New password accepted and functional
- ✅ Complete flow works end-to-end

### **Performance Metrics**
- Page load time: < 2 seconds
- API response time: < 500ms
- Email delivery time: < 10 seconds
- Redirect time: < 1 second

---

## 🐛 **COMMON ISSUES & SOLUTIONS**

### **Issue: "Internal Server Error"**
**Solution**: Check server logs, restart dev server

### **Issue: "Forbidden" Page**
**Solution**: Disable headless browser detection in middleware

### **Issue: Email Not Received**
**Solution**: Verify Resend API key, check email configuration

### **Issue: Token Invalid/Expired**
**Solution**: Generate new token, check expiration time

### **Issue: Password Reset Fails**
**Solution**: Check Supabase permissions, verify user exists

---

## 📸 **SCREENSHOT CHECKLIST**

Take screenshots at these points:
1. [ ] Login page loaded
2. [ ] Dashboard after successful login
3. [ ] Forgot password page
4. [ ] Success message after forgot password
5. [ ] Password reset page with token
6. [ ] Success message after password reset
7. [ ] Dashboard after login with new password

---

## 📝 **TEST RESULTS LOG**

```
Date: _____________
Tester: ___________
Browser: ___________

Task 21 - Login Page: ____ Pass/Fail ____ Notes: ___________
Task 22 - Login Test: ____ Pass/Fail ____ Notes: ___________
Task 23 - Dashboard: ____ Pass/Fail ____ Notes: ___________
Task 24 - Logout: ____ Pass/Fail ____ Notes: ___________
Task 25 - Forgot Page: ____ Pass/Fail ____ Notes: ___________
Task 26 - Forgot Form: ____ Pass/Fail ____ Notes: ___________
Task 27 - Email: ____ Pass/Fail ____ Notes: ___________
Task 28 - Reset: ____ Pass/Fail ____ Notes: ___________
Task 29 - New Login: ____ Pass/Fail ____ Notes: ___________
Task 30 - E2E: ____ Pass/Fail ____ Notes: ___________

Overall Result: ____ SUCCESS/NEEDS_FIXTURES ____
Issues Found: ________________________________________
Recommendations: ____________________________________
```

---

## 🎯 **FINAL VERIFICATION**

After completing all tasks:
1. **All tests pass** ✅ Authentication system ready
2. **Some tests fail** ❌ Review issues, fix, retest
3. **Critical issues** 🚫 Stop deployment, fix major problems

---

## 📞 **SUPPORT CONTACT**

If you encounter issues:
1. Check server logs in terminal
2. Review browser console for errors
3. Verify environment variables
4. Check Supabase configuration
5. Review Resend API dashboard

---

*Last Updated: January 16, 2026*
*Version: 1.0*
