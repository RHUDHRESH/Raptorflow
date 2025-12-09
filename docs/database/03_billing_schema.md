# Billing & Subscription Schema

This module handles subscriptions, payments, and invoices in an **RBI-compliant** manner (India specific).

## Key Features
-   **RBI E-Mandates**: Recurring payments flow adheres to RBI guidelines (limit notification, pre-debit notification).
-   **GST Compliance**: Invoices store tax breakdown (CGST, SGST, IGST).
-   **Plan Versioning**: Plans are defined in the database, not code.

## Tables

### `public.plans`
-   `code`: Enum-like key (free, starter, growth, enterprise)
-   `price_monthly_paise`: Amount in paise (1 INR = 100 paise)
-   `autopay_eligible`: Boolean (<= 5000 INR)

### `public.subscriptions`
State machine for subscription lifecycle.
-   `status`: `trialing`, `active`, `past_due`, `cancelled`, `expired`
-   `billing_cycle`: `monthly` or `yearly`
-   `current_period_end`: Expiry date tracking

### `public.payment_mandates`
Stores recurring payment authorization details.
-   `mandate_type`: `upi_autopay`, `card_recurring`
-   `max_amount_paise`: Upper limit for auto-debit
-   `valid_until`: Mandate expiry
-   `status`: `pending_authorization`, `active`, `revoked`

### `public.invoices`
Generated for every payment.
-   `invoice_number`: Sequential GST-compliant ID
-   `gstin`: Customer's tax ID
-   `tax_paise`: Calculated tax
-   `status`: `paid`, `void`, `uncollectible`

## Integration
Designed to work with **Razorpay** and **PhonePe** webhooks.
-   `payments` table tracks individual transaction attempts and provider IDs.
