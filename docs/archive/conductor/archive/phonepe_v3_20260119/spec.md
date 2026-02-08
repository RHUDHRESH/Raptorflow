# Track Specification: PhonePe SDK v3 Integration

## Overview
This track implements the latest PhonePe Python SDK (v3.2.1) and Standard Checkout API integration for RaptorFlow. We will replace the legacy manual checksum generation with the official SDK's client-based approach to ensure security, compliance, and maintainability.

## Functional Requirements
1.  **Backend Integration:**
    -   Utilize `phonepe-sdk-python` (v3.2.1) for all payment operations.
    -   Implement `StandardCheckoutClientV3` for payment initiation and status verification.
    -   Maintain singleton pattern for the SDK client.
    -   Support both UAT (Sandbox) and Production environments via environment variables.

2.  **Payment Flow (Standard Checkout):**
    -   Initiate payment using `client.initiate_payment`.
    -   Return the official PhonePe redirect URL to the frontend.
    -   Implement robust status verification using `client.get_order_status`.

3.  **Security & Compliance:**
    -   Offload card/UPI data handling to PhonePe's hosted page (PCI DSS compliant).
    -   Implement secure webhook validation using SDK utilities.
    -   Maintain idempotency for all payment requests.

## Acceptance Criteria
-   [ ] Payment initiation returns a valid PhonePe checkout URL.
-   [ ] User is successfully redirected to PhonePe and can complete a test transaction.
-   [ ] Server correctly verifies payment status upon redirect back to the app.
-   [ ] Webhooks are validated and processed successfully.
-   [ ] No manual checksum calculation is used in the codebase.

## Out of Scope
-   Custom API-based checkout (Direct card input on our UI).
-   Integration with other payment gateways (e.g., Stripe, Razorpay).
