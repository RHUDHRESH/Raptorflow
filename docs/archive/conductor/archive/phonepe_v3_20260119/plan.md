# Implementation Plan: PhonePe SDK v3 Integration

## Phase 1: Environment & SDK Readiness
- [x] Task: Update `.env` with latest PhonePe credentials (Merchant ID, Salt Key, Salt Index) [checkpoint: env_configured]
- [x] Task: Verify `phonepe-sdk-python` installation and version compatibility [checkpoint: sdk_verified]
- [x] Task: Create a standalone test script to verify SDK connectivity with PhonePe Sandbox [checkpoint: connectivity_verified]

## Phase 2: Backend Refactoring
- [x] Task: Update `backend/services/phonepe_sdk_gateway.py` to use `StandardCheckoutClient` [checkpoint: gateway_refactor_done]
- [x] Task: Refactor `initiate_payment` method to utilize official SDK request builders [checkpoint: initiation_refactor_done]
- [x] Task: Refactor `check_payment_status` to use the SDK's order status method [checkpoint: status_refactor_done]
- [x] Task: Implement/Update webhook validation using SDK utilities [checkpoint: webhook_refactor_done]
- [x] Task: Write unit tests for the updated gateway service [checkpoint: gateway_tests_pass]

## Phase 3: Frontend & Integration
- [x] Task: Update `src/lib/phonepe.ts` to act as a clean proxy to the backend SDK endpoints [checkpoint: frontend_proxy_done]
- [x] Task: Ensure the payment initiation UI correctly handles the redirect response [checkpoint: ui_integration_done]
- [x] Task: Update the payment success/failure landing pages to trigger status verification [checkpoint: landing_pages_sync_done]
- [x] Task: Conductor - User Manual Verification 'PhonePe V3 Integration' (Protocol in workflow.md) [checkpoint: verification_complete]
