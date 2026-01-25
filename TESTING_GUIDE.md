# 🧪 RAPTORFLOW - COMPLETE TESTING GUIDE

## 🚀 **SERVICES RUNNING**

### **Frontend (Next.js)**
- 🌐 **URL**: http://localhost:3000
- ✅ **Status**: RUNNING
- 📋 **Features**: Authentication, Payment, Onboarding, Dashboard

### **Backend (Python/FastAPI)**
- 🌐 **URL**: http://localhost:8000
- ✅ **Status**: RUNNING
- 📋 **Features**: PhonePe SDK, BCM Processing, OCR Services

---

## 🎯 **COMPLETE USER FLOW TESTING**

### **1. LANDING PAGE TEST**
```
📍 URL: http://localhost:3000
✅ Check: No "free" mentions
✅ Check: Start button redirects to login
✅ Check: Pricing link works
```

### **2. AUTHENTICATION TEST**
```
📍 URL: http://localhost:3000/login
✅ Check: Google OAuth button
✅ Check: No email/password forms
✅ Test: Click Google login (mock mode enabled)

📍 URL: http://localhost:3000/signup
✅ Check: Google OAuth button
✅ Check: No email/password forms
✅ Test: Click Google signup (mock mode enabled)
```

### **3. PLAN SELECTION TEST**
```
📍 URL: http://localhost:3000/onboarding/plans
✅ Check: Three pricing tiers
✅ Check: No "free" options
✅ Test: Click "Choose Plan" on any tier
```

### **4. PAYMENT FLOW TEST**
```
📍 URL: http://localhost:3000/onboarding/payment
✅ Check: PhonePe SDK loads
✅ Check: Payment methods display
✅ Test: Initiate payment (UAT mode)

📍 Webhook Test:
curl -X POST http://localhost:3000/api/payments/webhook \
  -H "Content-Type: application/json" \
  -H "x-verify: test" \
  -H "authorization: Basic cmFwdG9yZmxvd193ZWJob29rX1VBVDp3aF9zZWNyZXRfOWY4ZTdkNmM1YjQzYTJkYzFlZjBmN2M4ZmQyM2E1Yg==" \
  -d '{"type":"PAYMENT_SUCCESS","data":{"transactionId":"TEST123","merchantTransactionId":"TEST123","amount":10000}}'
```

### **5. PAYMENT STATUS TEST**
```
📍 URL: http://localhost:3000/onboarding/payment/status?code=PAYMENT_SUCCESS&transactionId=TEST123
✅ Check: Success message displays
✅ Check: Redirects to onboarding
```

### **6. ONBOARDING TEST**
```
📍 URL: http://localhost:3000/onboarding
✅ Check: Step 1 loads
✅ Test: Complete onboarding steps
✅ Check: Business context generation

API Test:
curl -X POST http://localhost:3000/api/onboarding/complete \
  -H "Content-Type: application/json" \
  -d '{"workspaceId":"test123","userId":"test123","steps":[],"businessContext":{"version":"1.0","company":"Test Corp"}}'
```

### **7. DASHBOARD TEST**
```
📍 URL: http://localhost:3000/dashboard
✅ Check: Requires authentication
✅ Test: Try access without login (should redirect to login)
✅ Test: Access after login
```

---

## 🔧 **API ENDPOINTS TESTING**

### **Authentication Required**
```bash
# Get current user subscription
curl http://localhost:3000/api/me/subscription
# Expected: 401 Unauthorized (without session)

# Verify payment
curl -X POST http://localhost:3000/api/payments/verify \
  -H "Content-Type: application/json" \
  -d '{"transactionId":"TEST123"}'
# Expected: 401 Unauthorized (without session)
```

### **Public Endpoints**
```bash
# Webhook (with headers)
curl -X POST http://localhost:3000/api/payments/webhook \
  -H "Content-Type: application/json" \
  -H "x-verify: test" \
  -H "authorization: Basic cmFwdG9yZmxvd193ZWJob29rX1VBVDp3aF9zZWNyZXRfOWY4ZTdkNmM1YjQzYTJkYzFlZjBmN2M4ZmQyM2E1Yg==" \
  -d '{"type":"PAYMENT_SUCCESS","data":{"transactionId":"TEST123"}}'
# Expected: 200 OK

# Onboarding completion
curl -X POST http://localhost:3000/api/onboarding/complete \
  -H "Content-Type: application/json" \
  -d '{"workspaceId":"test","userId":"test","steps":[],"businessContext":{"version":"1.0"}}'
# Expected: 500 (needs real Supabase service key)
```

---

## 🎮 **MOCK LOGIN TESTING**

Since `NEXT_PUBLIC_MOCK_GOOGLE_LOGIN=true`, you can test with:

**Email**: any@gmail.com
**Password**: test123456

This will create a mock user and allow you to test the complete flow without real Google OAuth.

---

## 📊 **BACKEND TESTING**

### **Backend API**
```bash
# Health check
curl http://localhost:8000/health

# PhonePe payment status
curl http://localhost:8000/api/v1/payments/v2/status/TEST123

# BCM processing
curl -X POST http://localhost:8000/api/v1/bcm/process \
  -H "Content-Type: application/json" \
  -d '{"business_context":{"company":"Test Corp"}}'
```

---

## 🔍 **DEBUGGING**

### **Check Server Logs**
- Frontend logs in terminal running `npm run dev`
- Backend logs in terminal running Python server
- Check browser console for JavaScript errors

### **Common Issues**
1. **401 Unauthorized**: Need to login first
2. **403 Forbidden**: Check API keys in .env.local
3. **500 Internal**: Check server logs for details
4. **CORS Issues**: Backend should handle CORS

---

## 🎯 **SUCCESS CRITERIA**

### ✅ **Complete Flow Success**
1. ✅ Landing page loads
2. ✅ Login works (mock mode)
3. ✅ Plan selection works
4. ✅ Payment initiates
5. ✅ Webhook processes payment
6. ✅ Onboarding completes
7. ✅ Dashboard accessible

### 🎉 **You're Ready for Production!**

Once all these tests pass, your Raptorflow application is fully functional and ready for real users!

---

## 📞 **NEED HELP?**

If you encounter any issues:
1. Check the terminal logs
2. Verify .env.local has all required keys
3. Ensure both frontend and backend are running
4. Check browser console for JavaScript errors

**Happy Testing! 🚀**
