# PhonePe Payment Gateway Integration

This document outlines the integration of PhonePe PG (Standard Checkout & Autopay) into the Raptorflow backend.

## Overview

We use PhonePe's v2 APIs for:
1. **Standard Checkout**: One-time payments (though we primarily use Autopay for subscriptions).
2. **Autopay (Subscriptions)**: Recurring billing via UPI Mandate.

## Configuration

Environment variables required:
- `PHONEPE_MERCHANT_ID`: Your Merchant ID (and Client ID for Auth).
- `PHONEPE_MERCHANT_KEY`: Client Secret / Salt Key.
- `PHONEPE_ENV`: `sandbox` or `production`.

## API Endpoints

### `POST /api/payments/create`
Creates a subscription setup request (UPI Intent flow).

- **Auth**: Required (`Authorization: Bearer <Supabase_JWT>`)
- **Body**:
  ```json
  {
    "planId": "string",
    "amount": 2000 // in paise (min 100)
  }
  ```
- **Response**:
  ```json
  {
    "orderId": "...",
    "intentUrl": "phonepe://..." // Use this to launch PhonePe app on mobile
  }
  ```

### `POST /api/payments/webhook`
Callback URL for PhonePe to notify payment status.

- **Auth**: Verified via PhonePe signature (TODO).
- **Events Handled**:
  - `subscription.setup.order.completed`: Subscription is active.

## Architecture

- **Client (`src/integrations/phonepe/client.ts`)**: Low-level HTTP wrapper around PhonePe APIs. Handles OAuth token generation and caching.
- **Service (`src/integrations/phonepe/service.ts`)**: Business logic. Constructs payloads, handles webhooks.
- **Routes (`src/routes/payments.ts`)**: Express handlers.

## Testing (Sandbox)

1. Use the PhonePe Sandbox credentials.
2. Use the **PhonePe Simulator App** (Android) to simulate payment success/failure.
3. Set `PHONEPE_ENV=sandbox`.
