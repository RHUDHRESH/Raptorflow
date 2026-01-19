# 📧 EMAIL SETUP GUIDE FOR REAL EMAIL SENDING
## Send Password Reset Emails to rhudhreshr@gmail.com

---

## 🎯 **CURRENT STATUS:**
- ✅ Forgot password API working
- ✅ Reset link generation working  
- ❌ **Email not sending** - Need Resend API key

---

## 🔧 **SETUP INSTRUCTIONS:**

### **Step 1: Create Resend Account**
1. Go to [https://resend.com](https://resend.com)
2. Sign up for a free account
3. Verify your email address

### **Step 2: Get Your API Key**
1. Go to Resend Dashboard → API Keys
2. Click "Create API Key"
3. Copy the API key (starts with `re_`)

### **Step 3: Configure Environment**
Add your real API key to `.env.local`:

```env
# Replace this line with your real API key
RESEND_API_KEY=re_your_actual_resend_api_key_here
```

### **Step 4: Restart Development Server**
```bash
# Stop the current server (Ctrl+C)
# Then restart:
npm run dev
```

---

## 🧪 **TESTING AFTER SETUP:**

### **Test Email Sending:**
1. Go to: `http://localhost:3000/forgot-password-simple`
2. Enter: `rhudhreshr@gmail.com`
3. Click: "Test Reset Link"
4. **Check your Gmail inbox** for the reset email

### **Expected Email:**
- **From**: RaptorFlow <noreply@raptorflow.com>
- **Subject**: Reset Your RaptorFlow Password
- **Content**: Professional HTML email with reset button

---

## 📧 **EMAIL TEMPLATE PREVIEW:**

The email will look like this:
```
🦅 RaptorFlow
Marketing Operating System

Reset Your Password

Hello,

We received a request to reset the password for your RaptorFlow account...

[Reset Password Button]

Security Notice: This link will expire in 1 hour...
```

---

## 🔍 **TROUBLESHOOTING:**

### **If email doesn't arrive:**
1. Check spam/junk folder in Gmail
2. Verify API key is correct (starts with `re_`)
3. Check Resend dashboard for delivery status
4. Ensure server was restarted after adding API key

### **If API error:**
1. Check Resend account status
2. Verify domain is verified in Resend
3. Check API key permissions

---

## 🚀 **ALTERNATIVE: Gmail SMTP**

If Resend doesn't work, we can set up Gmail SMTP:

```env
# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASS=your-app-password
```

**Gmail Setup:**
1. Enable 2FA on your Gmail account
2. Generate App Password (not regular password)
3. Add credentials to .env.local

---

## 📊 **CURRENT EMAIL STATUS:**

### **✅ Working:**
- Email validation
- Reset token generation
- Professional email templates
- API endpoints ready

### **❌ Missing:**
- Real Resend API key
- Email delivery

### **🎯 Next Step:**
1. Get Resend API key
2. Update .env.local
3. Restart server
4. Test with `rhudhreshr@gmail.com`

---

## 🔗 **QUICK TEST LINK:**

After setup, test here:
- **Forgot Password**: http://localhost:3000/forgot-password-simple
- **Email**: rhudhreshr@gmail.com

**The email system is ready - just needs the API key!** 🎉
