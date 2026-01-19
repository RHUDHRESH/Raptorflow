# 📧 Supabase SMTP Configuration with Resend
## Email Service Setup Guide

---

## 📋 **OVERVIEW**
This guide explains how to configure Supabase to use Resend as the SMTP provider for sending authentication emails, password reset emails, and other transactional emails.

---

## 🎯 **PREREQUISITES**
- ✅ Resend account created and verified
- ✅ Domain verified in Resend
- ✅ Resend API key available
- ✅ Supabase project access

---

## 🔧 **CONFIGURATION STEPS**

### **Step 1: Verify Domain in Resend**
1. **Login to Resend Dashboard**: https://resend.com/dashboard
2. **Go to Domains**: Click "Domains" in the sidebar
3. **Add Your Domain**: 
   - Enter: `raptorflow.com` (or your actual domain)
   - Click "Add Domain"
4. **Verify Domain**:
   - Add DNS records as instructed by Resend
   - Wait for verification (usually takes 5-10 minutes)
   - Domain status should show "Verified"

### **Step 2: Configure SMTP in Supabase**
1. **Go to Supabase Dashboard**: https://app.supabase.com
2. **Select Your Project**: Choose your Raptorflow project
3. **Navigate to Authentication**: Click "Authentication" in the sidebar
4. **Go to Email Settings**: Click "Email" tab
5. **Configure SMTP**:
   - **SMTP Provider**: Choose "Custom SMTP"
   - **SMTP Host**: `smtp.resend.com`
   - **SMTP Port**: `587`
   - **SMTP User**: `resend`
   - **SMTP Password**: Your Resend API key
   - **From Email**: `noreply@your-verified-domain.com`

### **Step 3: Update Environment Variables**
Add these to your `.env.production` file:
```bash
# Resend Configuration
RESEND_API_KEY=re_your_production_resend_api_key
RESEND_FROM_EMAIL=noreply@raptorflow.com
RESEND_VERIFIED_EMAIL=your-verified-email@raptorflow.com

# Supabase Email Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

---

## 📧 **SMTP SETTINGS**

### **Resend SMTP Configuration**
```yaml
Host: smtp.resend.com
Port: 587
Username: resend
Password: re_your_api_key
Encryption: STARTTLS
Authentication: PLAIN
```

### **Email Templates Configuration**
In Supabase Dashboard → Authentication → Email Templates:

#### **Confirmation Email**
- **Subject**: "Confirm your email address"
- **Template**: Professional welcome template
- **Variables**: `{{ .ConfirmationURL }}`

#### **Magic Link Email**
- **Subject**: "Your magic link for Raptorflow"
- **Template**: Clean, professional design
- **Variables**: `{{ .MagicLink }}`

#### **Password Reset Email**
- **Subject**: "Reset your RaptorFlow password"
- **Template**: Professional reset template
- **Variables**: `{{ .ResetLink }}`

---

## 📧 **EMAIL TEMPLATES**

### **Confirmation Email Template**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirm your email address</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 20px 0; border-bottom: 1px solid #eee; }
        .logo { font-size: 24px; font-weight: bold; color: #2563eb; }
        .content { padding: 30px 0; }
        .button { display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; }
        .footer { text-align: center; padding: 20px 0; border-top: 1px solid #eee; font-size: 14px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🦅 RaptorFlow</div>
        </div>
        
        <div class="content">
            <h2>Confirm Your Email Address</h2>
            <p>Thank you for signing up for Raptorflow! Please confirm your email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{ .ConfirmationURL }}" class="button">Confirm Email Address</a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                This link will expire in 24 hours for security reasons.
            </p>
        </div>
        
        <div class="footer">
            <p>© 2026 Raptorflow. All rights reserved.</p>
            <p>If you didn't sign up for Raptorflow, you can safely ignore this email.</p>
        </div>
    </div>
</body>
</html>
```

### **Magic Link Email Template**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your magic link for Raptorflow</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 20px 0; border-bottom: 1px solid #eee; }
        .logo { font-size: 24px; font-weight: bold; color: #2563eb; }
        .content { padding: 30px 0; }
        .button { display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; }
        .footer { text-align: center; padding: 20px 0; border-top: 1px solid #eee; font-size: 14px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🦅 RaptorFlow</div>
        </div>
        
        <div class="content">
            <h2>Your Magic Link for Raptorflow</h2>
            <p>Click the button below to sign in to your Raptorflow account:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{ .MagicLink }}" class="button">Sign In to RaptorFlow</a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                This link will expire in 1 hour for security reasons.
            </p>
        </div>
        
        <div class="footer">
            <p>© 2026 Raptorflow. All rights reserved.</p>
            <p>If you didn't request this magic link, you can safely ignore this email.</p>
        </div>
    </div>
</body>
</html>
```

### **Password Reset Email Template**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your RaptorFlow Password</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 20px 0; border-bottom: 1px solid #eee; }
        .logo { font-size: 24px; font-weight: bold; color: #2563eb; }
        .content { padding: 30px 0; }
        .button { display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; }
        .footer { text-align: center; padding: 20px 0; border-top: 1px solid #eee; font-size: 14px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🦅 RaptorFlow</div>
        </div>
        
        <div class="content">
            <h2>Reset Your RaptorFlow Password</h2>
            <p>We received a request to reset the password for your Raptorflow account.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{ .ResetLink }}" class="button">Reset Password</a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; background: #f4f4f4; padding: 10px; border-radius: 4px;">
                {{ .ResetLink }}
            </p>
            
            <p style="color: #666; font-size: 14px;">
                This link will expire in 1 hour for security reasons.
            </p>
        </div>
        
        <div class="footer">
            <p>© 2026 Raptorflow. All rights reserved.</p>
            <p>If you didn't request this password reset, you can safely ignore this email.</p>
        </div>
    </div>
</body>
</html>
```

---

## 🔍 **VERIFICATION**

### **Test SMTP Configuration**
```bash
# Test email sending
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer re_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
      "from": "noreply@raptorflow.com",
      "to": "test@example.com",
      "subject": "Test Email",
      "html": "<h1>Test Email</h1><p>This is a test email from Raptorflow.</p>"
    }'
```

### **Test Supabase Email**
```bash
# Test password reset flow
curl -X POST http://localhost:3000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## 📧 **ENVIRONMENT VARIABLES**

### **Required Variables**
```bash
# Resend Configuration
RESEND_API_KEY=re_your_production_resend_api_key
RESEND_FROM_EMAIL=noreply@raptorflow.com
RESEND_VERIFIED_EMAIL=your-verified-email@raptorflow.com

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### **Optional Variables**
```bash
# Email Configuration
EMAIL_FROM_NAME=RaptorFlow
EMAIL_REPLY_TO=support@raptorflow.com
EMAIL_TEMPLATE_PATH=/path/to/templates

# SMTP Configuration (if not using Resend)
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_your_api_key
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

#### **Email Not Sending**
1. **Check API Key**: Verify RESEND_API_KEY is correct
2. **Check Domain**: Ensure domain is verified in Resend
3. **Check SMTP Settings**: Verify SMTP configuration in Supabase
4. **Check Logs**: Check Supabase logs for email errors

#### **Domain Verification Failed**
1. **DNS Records**: Ensure DNS records are correct
2. **Propagation**: Wait for DNS propagation (up to 48 hours)
3. **TXT Records**: Ensure TXT records are correct
4. **Contact Support**: Contact Resend support if needed

#### **SMTP Authentication Failed**
1. **API Key**: Ensure API key is correct and active
2. **Username**: Use "resend" as username
3. **Password**: Use your Resend API key as password
4. **Encryption**: Use STARTTLS encryption

### **Debug Commands**
```bash
# Check Resend API status
curl -H "Authorization: Bearer re_your_api_key" \
  https://api.resend.com/domains

# Check email delivery status
curl -H "Authorization: Bearer re_your_api_key" \
  https://api.resend.com/emails/[email_id]

# Test Supabase email configuration
curl -X POST https://your-project.supabase.co/auth/v1/signup \
  -H "apikey: your_anon_key" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

---

## 📧 **BEST PRACTICES**

### **Security**
- ✅ Use environment variables for API keys
- ✅ Never commit API keys to version control
- ✅ Use verified domains for sending
- ✅ Implement rate limiting on email sending
- ✅ Monitor email delivery rates

### **Deliverability**
- ✅ Use professional email templates
- ✅ Include clear call-to-action buttons
- ✅ Provide fallback links
- ✅ Test email rendering on multiple clients
- ✅ Monitor bounce rates and spam complaints

### **Performance**
- ✅ Use email templates for consistent rendering
- ✅ Batch email sends when possible
- ✅ Implement email queue for high volume
- ✅ Monitor email sending performance
- ✅ Use appropriate email providers for scale

---

## 📧 **MONITORING**

### **Email Metrics to Track**
- **Delivery Rate**: Percentage of emails successfully delivered
- **Bounce Rate**: Percentage of emails that bounced
- **Spam Complaints**: Number of spam complaints received
- **Open Rate**: Percentage of emails opened
- **Click Rate**: Percentage of emails clicked

### **Alerting**
- **High Bounce Rate**: Alert if bounce rate > 5%
- **Spam Complaints**: Alert on any spam complaints
- **SMTP Failures**: Alert on SMTP authentication failures
- **API Errors**: Alert on Resend API errors

---

## 📧 **MAINTENANCE**

### **Regular Tasks**
- **Monthly**: Review email templates and update as needed
- **Quarterly**: Check domain verification status
- **Quarterly**: Review API key usage and limits
- **Annually**: Audit email security practices

### **Backup & Recovery**
- **Backup Templates**: Keep copies of email templates
- **Backup Configuration**: Document SMTP settings
- **Test Recovery**: Test email sending after changes
- **Monitor Logs**: Review email delivery logs regularly

---

## 📧 **SUPPORT**

### **Resend Support**
- **Email**: support@resend.com
- **Documentation**: https://resend.com/docs
- **Status Page**: https://resend.com/status

### **Supabase Support**
- **Email**: support@supabase.com
- **Documentation**: https://supabase.com/docs
- **Community**: https://github.com/supabase/supabase

### **Community Support**
- **Discord**: Raptorflow Discord server
- **GitHub**: Create issues for bugs
- **Stack Overflow**: Tag questions with #supabase #resend

---

## 📧 **UPDATES**

### **Version History**
- **v1.0**: Initial configuration
- **v1.1**: Added email templates
- **v1.2**: Added troubleshooting guide
- **v1.3**: Added monitoring section

### **Last Updated**
- **Date**: January 16, 2026
- **Author**: Cascade AI Assistant
- **Version**: 1.3

---

## 🎯 **NEXT STEPS**

1. **Apply Configuration**: Follow the steps above to configure SMTP
2. **Test Email Flow**: Test password reset and confirmation emails
3. **Monitor Performance**: Set up email delivery monitoring
4. **Update Templates**: Customize email templates as needed
5. **Document Process**: Document email configuration for team

---

*Last Updated: January 16, 2026*
*Status: Ready for Implementation* ✅
