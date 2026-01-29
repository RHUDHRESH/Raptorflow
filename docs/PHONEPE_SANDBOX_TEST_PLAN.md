# PhonePe Sandbox Test Plan

## Overview
Comprehensive manual testing checklist for PhonePe payment integration in sandbox environment.

## Prerequisites

### Environment Setup
- [ ] PhonePe sandbox account configured
- [ ] Sandbox merchant ID and salt key obtained
- [ ] Webhook URL configured in PhonePe dashboard: `https://yourdomain.com/api/webhooks/phonepe`
- [ ] Backend environment variables set:
  ```bash
  PHONEPE_MERCHANT_ID=sandbox_merchant_id
  PHONEPE_SALT_KEY=sandbox_salt_key
  PHONEPE_SALT_INDEX=1
  PHONEPE_ENVIRONMENT=sandbox
  ```

### Test Accounts
- [ ] Sandbox test user credentials
- [ ] Test payment methods (cards, UPI, net banking)
- [ ] Test email addresses for webhook notifications

## Test Scenarios

### 1. Payment Initiation Tests

#### 1.1 Valid Payment Requests
- [ ] **Starter Plan (₹49)**
  - Initiate payment with valid email
  - Verify redirect URL generation
  - Confirm merchant order ID format
  - Check database transaction record

- [ ] **Growth Plan (₹149)**
  - Initiate payment with valid email and name
  - Verify correct amount calculation
  - Test custom redirect URL
  - Validate metadata storage

- [ ] **Enterprise Plan (₹499)**
  - Initiate payment with all optional fields
  - Test webhook URL customization
  - Verify idempotency key handling
  - Check transaction expiration

#### 1.2 Invalid Payment Requests
- [ ] **Invalid Plan**
  - Test with non-existent plan name
  - Verify 400 error response
  - Check error message clarity

- [ ] **Amount Mismatch**
  - Test with incorrect amount for plan
  - Verify validation error
  - Check database rollback

- [ ] **Missing Required Fields**
  - Test without workspace ID
  - Test without customer email
  - Verify appropriate error responses

### 2. Payment Processing Tests

#### 2.1 Successful Payment Flow
- [ ] **Complete Payment Journey**
  - Initiate starter plan payment
  - Redirect to PhonePe sandbox
  - Complete payment with test card
  - Verify redirect back to app
  - Check payment status polling
  - Confirm subscription activation

- [ ] **Email Notifications**
  - Verify payment confirmation email
  - Check email content and formatting
  - Test email delivery to spam folder
  - Verify unsubscribe link

#### 2.2 Failed Payment Flow
- [ ] **Payment Declined**
  - Use declined test card
  - Verify failure webhook processing
  - Check payment failure email
  - Confirm subscription not activated

- [ ] **Payment Timeout**
  - Abandon payment session
  - Verify timeout handling
  - Check payment status after timeout
  - Test retry mechanism

### 3. Webhook Processing Tests

#### 3.1 Webhook Validation
- [ ] **Signature Validation**
  - Test valid webhook signature
  - Test invalid signature format
  - Test missing signature header
  - Verify replay attack prevention

- [ ] **Webhook Structure**
  - Test valid webhook payload
  - Test missing required fields
  - Test malformed JSON
  - Verify error handling

#### 3.2 Webhook Processing
- [ ] **Success Webhook**
  - Simulate PAYMENT_SUCCESS webhook
  - Verify transaction status update
  - Check subscription activation
  - Confirm email notification

- [ ] **Failure Webhook**
  - Simulate PAYMENT_FAILED webhook
  - Verify transaction status update
  - Check failure email notification
  - Test error logging

- [ ] **Duplicate Webhooks**
  - Send same webhook twice
  - Verify idempotency handling
  - Check duplicate prevention
  - Test replay attack protection

### 4. Status Polling Tests

#### 4.1 Polling Behavior
- [ ] **Normal Polling**
  - Start payment polling after initiation
  - Verify exponential backoff
  - Check status updates
  - Confirm polling stops on completion

- [ ] **Polling Timeout**
  - Test timeout after 5 minutes
  - Verify timeout callback
  - Check cleanup on timeout
  - Test error handling

#### 4.2 Status Updates
- [ ] **Status Transitions**
  - PENDING → COMPLETED
  - PENDING → FAILED
  - FAILED → COMPLETED (retry scenarios)
  - Verify database updates

### 5. Error Handling Tests

#### 5.1 Network Errors
- [ ] **API Timeout**
  - Simulate PhonePe API timeout
  - Verify retry logic
  - Check error logging
  - Test graceful degradation

- [ ] **Connection Errors**
  - Test network connectivity issues
  - Verify fallback handling
  - Check user notification
  - Test recovery scenarios

#### 5.2 Database Errors
- [ ] **Transaction Failures**
  - Simulate database connection error
  - Verify transaction rollback
  - Check error logging
  - Test retry mechanism

- [ ] **Constraint Violations**
  - Test duplicate merchant order ID
  - Verify constraint handling
  - Check error response format

### 6. Integration Tests

#### 6.1 End-to-End Flow
- [ ] **Complete User Journey**
  - User signup → Plan selection → Payment → Dashboard access
  - Verify each step works correctly
  - Check data consistency
  - Test user experience

#### 6.2 Cross-Platform Tests
- [ ] **Mobile Browser**
  - Test payment flow on mobile
  - Verify responsive design
  - Check touch interactions

- [ ] **Desktop Browser**
  - Test payment flow on desktop
  - Verify keyboard navigation
  - Check accessibility

### 7. Performance Tests

#### 7.1 Load Testing
- [ ] **Concurrent Payments**
  - Test 10 concurrent payment initiations
  - Verify system stability
  - Check response times
  - Monitor resource usage

#### 7.2 Stress Testing
- [ ] **High Volume**
  - Test 100 payment initiations/minute
  - Verify rate limiting
  - Check database performance
  - Monitor error rates

## Test Data

### Test Payment Methods
| Method | Card Number | Expiry | CVV | Expected Result |
|--------|-------------|--------|-----|-----------------|
| Visa Success | 4111111111111111 | 12/25 | 123 | Success |
| Visa Declined | 4000000000000002 | 12/25 | 123 | Declined |
| Mastercard Success | 5555555555554444 | 12/25 | 123 | Success |
| Mastercard Declined | 5105105105105100 | 12/25 | 123 | Declined |

### Test Email Addresses
- `test-success@example.com` - For successful payments
- `test-failure@example.com` - For failed payments
- `test-timeout@example.com` - For timeout scenarios

## Expected Results

### Success Criteria
- [ ] Payment initiation success rate > 95%
- [ ] Webhook processing success rate > 99%
- [ ] Email delivery rate > 95%
- [ ] Payment completion time < 2 minutes
- [ ] Status polling accuracy > 99%

### Error Handling
- [ ] All error scenarios return appropriate HTTP status codes
- [ ] Error messages are user-friendly and actionable
- [ ] No sensitive data leaked in error responses
- [ ] Graceful degradation on service failures

### Security
- [ ] All webhooks properly validated
- [ ] No replay attacks successful
- [ ] Signature validation working correctly
- [ ] Rate limiting enforced

## Test Environment Cleanup

### After Testing
- [ ] Cancel all test subscriptions
- [ ] Clean up test transactions
- [ ] Reset test user data
- [ ] Clear Redis cache if used
- [ ] Verify no lingering test data

### Production Readiness
- [ ] Update environment variables for production
- [ ] Configure production webhook URLs
- [ ] Update PhonePe merchant credentials
- [ ] Test production payment flow
- [ ] Set up monitoring and alerts

## Documentation

### Test Results
- [ ] Document all test results
- [ ] Note any issues or discrepancies
- [ ] Record performance metrics
- [ ] Capture screenshots of key flows

### Sign-off
- [ ] QA engineer sign-off
- [ ] Product owner approval
- [ ] Security team review
- [ ] Operations team readiness

## Troubleshooting Guide

### Common Issues
1. **Webhook not received**
   - Check webhook URL configuration
   - Verify PhonePe dashboard settings
   - Check firewall/network rules

2. **Signature validation failed**
   - Verify salt key and index
   - Check webhook body encoding
   - Test with different signature formats

3. **Payment not completing**
   - Check PhonePe sandbox status
   - Verify test card details
   - Review error logs

4. **Email not sending**
   - Verify Resend API key
   - Check email templates
   - Review spam filter settings

### Contact Information
- PhonePe Sandbox Support: [support contact]
- Internal Development Team: [team contact]
- Emergency Contact: [emergency contact]
