import { phonePeClient } from './client';
import { SubscriptionSetupRequest } from './types';

export const createSubscription = async (
  userId: string,
  planId: string,
  amount: number // in paise
) => {
  // Ensure unique IDs
  const uniqueSuffix = `${userId.substring(0, 5)}_${Date.now()}`;
  const merchantOrderId = `ORDER_${uniqueSuffix}`;
  
  const request: SubscriptionSetupRequest = {
    merchantOrderId,
    amount,
    paymentFlow: {
      type: 'SUBSCRIPTION_SETUP',
      merchantSubscriptionId: `SUB_${uniqueSuffix}`,
      authWorkflowType: 'TRANSACTION', // First transaction is real payment
      amountType: 'FIXED',
      maxAmount: amount,
      frequency: 'MONTHLY',
      paymentMode: {
        type: 'UPI_INTENT',
        targetApp: 'com.phonepe.app'
      }
    },
    deviceContext: {
      deviceOS: 'ANDROID' // Default to Android for now, or detect from request?
    }
  };

  const response = await phonePeClient.setupSubscription(request);
  
  return {
    orderId: response.orderId,
    intentUrl: response.intentUrl, // For UPI Intent
    merchantOrderId,
    merchantSubscriptionId: request.paymentFlow.merchantSubscriptionId
  };
};

export const handleWebhook = async (payload: any) => {
  // TODO: Verify checksum/signature?
  // Docs say "Authorization: SHA256(username:password)" for callbacks?
  // Need to check header validation in routes.
  
  // Process payload
  console.log('PhonePe Webhook:', JSON.stringify(payload, null, 2));
  
  if (payload.event === 'subscription.setup.order.completed') {
    // Subscription Active
    // Update DB
  }
  
  return { status: 'ok' };
};
