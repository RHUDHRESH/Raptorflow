# PhonePe Sandbox Test Checklist

This checklist provides comprehensive manual testing procedures for PhonePe payment integration in the Raptorflow sandbox environment.

## Prerequisites

### Environment Setup
- [ ] Sandbox environment configured with test credentials
- [ ] Backend server running on `http://localhost:8000`
- [ ] Frontend application running on `http://localhost:3000`
- [ ] PhonePe sandbox credentials configured
- [ ] Resend email service configured
- [ ] Database migrations applied
- [ ] Redis server running

### Test Accounts
- [ ] Test PhonePe sandbox account with sufficient balance
- [ ] Test email account for receiving notifications
- [ ] Admin access to PhonePe developer dashboard
- [ ] Access to application logs

## Test Scenarios

### 1. Payment Initiation Tests

#### 1.1 Valid Payment Initiation
**Test Case**: User initiates payment with valid details
**Steps**:
1. Navigate to `/onboarding/plans`
2. Select "Starter" plan (₹49/month)
3. Click "Continue to Payment"
4. Verify payment page loads with correct plan details
5. Click "Pay with PhonePe" button
6. Verify redirect to PhonePe sandbox

**Expected Results**:
- Payment page displays correct plan and amount
- PhonePe redirect URL is generated
- Transaction record created in database with "pending" status
- Merchant order ID follows format `ORD{timestamp}{random}`

#### 1.2 Invalid Plan Selection
**Test Case**: User tries to pay with invalid plan
**Steps**:
1. Manipulate request to use invalid plan ID
2. Attempt payment initiation

**Expected Results**:
- Error message "Invalid plan"
- No transaction created
- HTTP 400 response

#### 1.3 Amount Mismatch
**Test Case**: Amount doesn't match plan configuration
**Steps**:
1. Manipulate request amount to differ from plan
2. Attempt payment initiation

**Expected Results**:
- Error message "Amount mismatch"
- No transaction created
- HTTP 400 response

### 2. PhonePe Payment Flow Tests

#### 2.1 Successful Payment
**Test Case**: User completes payment successfully
**Steps**:
1. Initiate payment as per 1.1
2. On PhonePe sandbox page, select UPI payment
3. Enter test UPI ID and complete payment
4. Verify redirect back to application

**Expected Results**:
- Redirect to payment callback URL
- Payment status polling starts automatically
- Progress indicator shows "Processing" → "Completed"
- Success email sent to user
- Subscription activated in database
- Redirect to onboarding session after 2 seconds

#### 2.2 Failed Payment
**Test Case**: User payment fails
**Steps**:
1. Initiate payment
2. On PhonePe sandbox, simulate payment failure
3. Verify error handling

**Expected Results**:
- Payment status shows "Failed"
- Error message displayed to user
- Retry button available
- Failure email sent to user
- No subscription created

#### 2.3 Payment Timeout
**Test Case**: Payment verification times out
**Steps**:
1. Initiate payment
2. Don't complete payment on PhonePe
3. Wait for 5-minute timeout

**Expected Results**:
- Status shows "Timeout"
- Timeout message displayed
- Retry option available
- User can check payment status manually

#### 2.4 Payment Cancellation
**Test Case**: User cancels payment
**Steps**:
1. Initiate payment
2. Click cancel button during polling
3. Verify cancellation behavior

**Expected Results**:
- Polling stops immediately
- User redirected back to plans page
- Transaction marked as cancelled
- No email sent

### 3. Payment Status Polling Tests

#### 3.1 Polling Behavior
**Test Case**: Verify polling mechanism
**Steps**:
1. Initiate payment
2. Monitor network requests for status polling
3. Verify exponential backoff

**Expected Results**:
- Polling starts 2 seconds after initiation
- Requests to `/api/payments/status/{order_id}`
- Exponential backoff: 2s → 3s → 4.5s → max 10s
- Progress bar updates correctly
- Time remaining countdown works

#### 3.2 Polling Recovery
**Test Case**: Network interruption during polling
**Steps**:
1. Initiate payment
2. Disable network temporarily
3. Re-enable network
4. Verify polling resumes

**Expected Results**:
- Polling handles network errors gracefully
- Continues after network restoration
- No duplicate status updates

### 4. Webhook Processing Tests

#### 4.1 Successful Webhook
**Test Case**: PhonePe sends success webhook
**Steps**:
1. Use PhonePe dashboard to trigger test webhook
2. Verify webhook processing

**Expected Results**:
- Webhook signature validation passes
- Transaction status updated to "completed"
- Subscription activated
- Confirmation email sent
- Webhook marked as processed (replay protection)

#### 4.2 Failed Webhook
**Test Case**: PhonePe sends failure webhook
**Steps**:
1. Trigger failure webhook from dashboard
2. Verify error handling

**Expected Results**:
- Transaction status updated to "failed"
- Failure email sent
- No subscription created

#### 4.3 Invalid Webhook Signature
**Test Case**: Webhook with invalid signature
**Steps**:
1. Send webhook with incorrect signature
2. Verify rejection

**Expected Results**:
- Webhook rejected with 401 status
- No database updates
- Error logged

#### 4.4 Duplicate Webhook
**Test Case**: Same webhook sent twice
**Steps**:
1. Send successful webhook
2. Send identical webhook again
3. Verify idempotency

**Expected Results**:
- Second webhook accepted (idempotency)
- No duplicate database updates
- No duplicate emails sent

### 5. Email Notification Tests

#### 5.1 Payment Confirmation Email
**Test Case**: Verify confirmation email content
**Steps**:
1. Complete successful payment
2. Check email inbox

**Expected Results**:
- Email received within 30 seconds
- Subject: "Payment Successful - Raptorflow"
- Contains: Plan name, amount, transaction ID
- Proper HTML formatting
- Correct sender: noreply@raptorflow.dev

#### 5.2 Payment Failure Email
**Test Case**: Verify failure email content
**Steps**:
1. Fail a payment
2. Check email inbox

**Expected Results**:
- Email received within 30 seconds
- Subject: "Payment Failed - Raptorflow"
- Contains: Error reason, transaction ID
- Support contact information
- Retry instructions

#### 5.3 Email Template Rendering
**Test Case**: Verify email templates
**Steps**:
1. Test various payment scenarios
2. Check email rendering on different clients

**Expected Results**:
- Emails render correctly on Gmail, Outlook
- Mobile-friendly formatting
- No broken images or links
- Proper unsubscribe links

### 6. Subscription Management Tests

#### 6.1 Subscription Activation
**Test Case**: Verify subscription creation
**Steps**:
1. Complete successful payment
2. Check database subscriptions table

**Expected Results**:
- Subscription record created
- Status: "active"
- Correct plan and workspace ID
- Proper period start/end dates
- Trial period applied if applicable

#### 6.2 Subscription Lookup
**Test Case**: Verify subscription retrieval
**Steps**:
1. Query subscription via API
2. Check response format

**Expected Results**:
- Correct subscription details returned
- Includes plan information
- Shows current period
- Includes payment history

### 7. Error Handling Tests

#### 7.1 Network Errors
**Test Case**: Handle network failures
**Steps**:
1. Disable network during payment initiation
2. Verify error handling

**Expected Results**:
- User-friendly error message
- No partial database updates
- Retry options available

#### 7.2 API Rate Limits
**Test Case**: Handle rate limiting
**Steps**:
1. Make rapid API calls
2. Verify rate limiting

**Expected Results**:
- HTTP 429 responses after threshold
- Proper retry headers
- Graceful degradation

#### 7.3 Database Errors
**Test Case**: Handle database failures
**Steps**:
1. Temporarily disable database
2. Attempt payment
3. Verify error handling

**Expected Results**:
- Error message without technical details
- No partial updates
- System recovery after database restored

### 8. Security Tests

#### 8.1 Signature Validation
**Test Case**: Verify webhook security
**Steps**:
1. Send webhook with altered payload
2. Verify signature validation

**Expected Results**:
- Invalid signature rejected
- No processing of altered webhooks
- Security events logged

#### 8.2 Replay Attack Prevention
**Test Case**: Prevent webhook replay
**Steps**:
1. Send successful webhook
2. Send same webhook with old timestamp
3. Verify rejection

**Expected Results**:
- Old webhook rejected
- Timestamp validation working
- Replay protection active

#### 8.3 Data Validation
**Test Case**: Input validation
**Steps**:
1. Send malformed payment requests
2. Verify validation

**Expected Results**:
- Invalid data rejected
- Proper error responses
- No database corruption

### 9. Performance Tests

#### 9.1 Payment Initiation Speed
**Test Case**: Measure API response times
**Steps**:
1. Initiate payment multiple times
2. Measure response times

**Expected Results**:
- Response time < 2 seconds
- Consistent performance
- No memory leaks

#### 9.2 Polling Efficiency
**Test Case**: Verify polling performance
**Steps**:
1. Monitor polling requests
2. Check resource usage

**Expected Results**:
- Reasonable polling frequency
- No excessive API calls
- Proper cleanup after completion

### 10. Cross-Browser Tests

#### 10.1 Desktop Browsers
**Test Case**: Test on different browsers
**Steps**:
1. Test payment flow on Chrome, Firefox, Safari
2. Verify UI compatibility

**Expected Results**:
- Consistent experience across browsers
- No JavaScript errors
- Proper responsive design

#### 10.2 Mobile Browsers
**Test Case**: Test on mobile devices
**Steps**:
1. Test on iOS Safari, Android Chrome
2. Verify mobile experience

**Expected Results**:
- Mobile-optimized UI
- Touch-friendly interactions
- Proper PhonePe app integration

## Test Data and Scenarios

### Test Payment Amounts
| Plan | Amount (₹) | Amount (Paise) | Test Cases |
|------|------------|---------------|------------|
| Starter | 49 | 4900 | Success, failure, timeout |
| Growth | 149 | 14900 | Success, failure, timeout |
| Enterprise | 499 | 49900 | Success, failure, timeout |

### Test UPI IDs (Sandbox)
| Type | UPI ID | Expected Result |
|------|--------|-----------------|
| Success | test@ybl | Payment successful |
| Failure | fail@ybl | Payment failed |
| Timeout | timeout@ybl | Payment timeout |

### Error Scenarios
| Error Type | Trigger | Expected Handling |
|------------|---------|-----------------|
| Insufficient funds | Low balance UPI | Clear error message |
| Invalid UPI | Wrong format | Validation error |
| Network error | Disable network | Retry option |
| Timeout | No response | Timeout handling |

## Validation Checklist

### Pre-Test Validation
- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Redis connection working
- [ ] PhonePe sandbox accessible
- [ ] Email service working
- [ ] SSL certificates valid
- [ ] API endpoints responding

### Post-Test Validation
- [ ] All test cases executed
- [ ] No database inconsistencies
- [ ] Email delivery verified
- [ ] Performance metrics collected
- [ ] Security checks passed
- [ ] Cross-browser compatibility confirmed
- [ ] Mobile experience verified

### Sign-off Requirements
- [ ] Developer sign-off: _________________ Date: _______
- [ ] QA sign-off: _________________ Date: _______
- [ ] Product owner sign-off: _________________ Date: _______

## Troubleshooting Guide

### Common Issues

#### Payment Not Redirecting
**Symptoms**: Clicking pay button doesn't redirect
**Causes**:
- Frontend API call failing
- PhonePe credentials invalid
- Network connectivity issues

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify PhonePe credentials in environment
3. Test API endpoint directly
4. Check network connectivity

#### Webhook Not Received
**Symptoms**: Payment completes but webhook not processed
**Causes**:
- Webhook URL incorrect
- Firewall blocking requests
- Signature validation failing

**Solutions**:
1. Verify webhook URL accessibility
2. Check server logs for webhook attempts
3. Validate signature calculation
4. Test webhook manually

#### Email Not Sent
**Symptoms**: Payment successful but no email received
**Causes**:
- Resend API key invalid
- Domain not verified
- Email in spam folder

**Solutions**:
1. Verify Resend API key
2. Check domain verification status
3. Check spam/junk folders
4. Test Resend API directly

#### Subscription Not Activated
**Symptoms**: Payment successful but subscription not active
**Causes**:
- Webhook processing failed
- Database error
- Subscription logic error

**Solutions**:
1. Check webhook processing logs
2. Verify database connectivity
3. Manually activate subscription
4. Debug subscription creation logic

### Debug Tools

#### Browser Developer Tools
- Network tab for API calls
- Console for JavaScript errors
- Application tab for local storage

#### Backend Logs
- Payment initiation logs
- Webhook processing logs
- Email sending logs
- Database query logs

#### PhonePe Dashboard
- Transaction history
- Webhook delivery status
- API usage metrics
- Error reports

#### Email Service Dashboard
- Delivery status
- Open/click rates
- Bounce reports
- API usage

## Success Criteria

### Functional Requirements
- [ ] All payment flows work correctly
- [ ] Webhook processing reliable
- [ ] Email notifications sent
- [ ] Subscriptions activated properly
- [ ] Error handling comprehensive

### Performance Requirements
- [ ] Payment initiation < 2 seconds
- [ ] Status polling efficient
- [ ] Email delivery < 30 seconds
- [ ] Webhook processing < 5 seconds

### Security Requirements
- [ ] Signature validation working
- [ ] Replay protection active
- [ ] Input validation comprehensive
- [ ] Error messages sanitized

### Usability Requirements
- [ ] Clear payment flow
- [ ] Helpful error messages
- [ ] Mobile-friendly interface
- [ ] Accessible design

---

**Last Updated**: January 29, 2026
**Version**: 1.0
**Next Review**: February 29, 2026
**Maintainer**: Raptorflow QA Team
