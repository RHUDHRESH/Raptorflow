# Frontend Action Inventory

This document inventories click actions in the `/frontend` UI and maps each to a backend endpoint or explains when it is a deliberate client-only action.

## Black Box Engine (`frontend/src/app/(shell)/blackbox/page.tsx`)
| UI Action | Trigger | Backend Mapping | Notes | 
| --- | --- | --- | --- |
| Back | Top-right back button | No-op (client state) | Moves user back in the multi-step flow. | 
| Select outcome card | Outcome card click | No-op (client state) | Selects an outcome and advances to volatility step. | 
| Generate Strategy | “Generate Strategy” button | No-op (client-only simulation) | Simulated generation; no backend endpoint wired. | 
| Discard | “Discard” button | No-op (client state) | Resets in-memory state. | 
| Accept & Create Move | “Accept & Create Move” button | `POST /api/proxy/api/v1/moves/` | Uses `createMoveFromBlackBox` in `movesStore`. | 
| Create Another | “Create Another” button | No-op (client state) | Resets in-memory state. | 
| View Created Move | “View Created Move” button | No-op (client navigation) | Navigates to `/moves?highlight=<id>`; data fetch happens in the Moves page. | 

## Campaign Settings (`frontend/src/components/campaigns/CampaignSettings.tsx`)
| UI Action | Trigger | Backend Mapping | Notes | 
| --- | --- | --- | --- |
| Cancel | “Cancel” button | No-op (client callback) | Delegates to `onClose`. | 
| Save Changes | “Save Changes” button | `PUT /api/proxy/api/v1/campaigns/:id` | Uses `updateCampaign` from `enhancedCampaignStore`. | 
| Tabs | General/Notifications/Team/Integrations/Advanced tabs | No-op (client state) | Updates active tab in local state. | 

## System Integration Dashboard (`frontend/src/components/SystemIntegrationDashboard.tsx`)
| UI Action | Trigger | Backend Mapping | Notes | 
| --- | --- | --- | --- |
| Run Integration Test | “Run Integration Test” button | Multiple endpoints: `POST /api/proxy/api/v1/moves/`, `POST /api/proxy/api/v1/daily_wins/generate`, `POST /api/proxy/api/v1/blackbox/generate-strategy`, `POST /api/proxy/api/v1/muse/generate`, `POST /api/proxy/api/v1/agents/:id/execute` (via `executeAgent`), `POST /api/proxy/api/v1/bcm/record-interaction` (via `recordInteraction`) | Executes an end-to-end workflow across stores; errors surfaced in UI. | 
| Refresh Systems | “Refresh Systems” button | No-op (client reload) | Uses `window.location.reload()` to rerun initialization. | 

## Performance Monitoring (`frontend/src/components/PerformanceMonitoring.tsx`)
| UI Action | Trigger | Backend Mapping | Notes | 
| --- | --- | --- | --- |
| Auto Refresh toggle | “Auto Refresh” button | `GET /api/monitoring/system`, `/agents`, `/workflows`, `/alerts`, `/health` | Toggles polling of monitoring endpoints. | 
| Export | “Export” button | No-op (client-only download) | Exports current in-memory dataset to JSON; no backend export endpoint wired. | 
| Settings | “Settings” button | No-op (client-only notice) | Displays a temporary notice; no backend settings endpoint wired. | 
| Retry Load | “Retry Load” button | `GET /api/monitoring/*` endpoints | Retries monitoring fetches after errors. | 

## Persona Brief Modal (`frontend/src/components/muse/PersonaBriefModal.tsx`)
| UI Action | Trigger | Backend Mapping | Notes | 
| --- | --- | --- | --- |
| Close | “X” button | No-op (client callback) | Calls `onClose`. | 
| Add Goal | “Add” button | No-op (client state) | Adds a goal to in-memory form state. | 
| Remove Goal | “X” on a goal pill | No-op (client state) | Removes the goal from in-memory form state. | 
| Cancel | “Cancel” button | No-op (client callback) | Calls `onClose`. | 
| Save Brief | “Save Brief” button | No-op (client store) | Persists to local persona store; no backend endpoint wired in this module. | 

## Muse Vertex AI Chat (`frontend/src/components/muse/MuseVertexAIChat.tsx`)
| UI Action | Trigger | Backend Mapping | Notes | 
| --- | --- | --- | --- |
| Blog quick action | “Blog” button | `POST http://localhost:8000/api/v1/muse/generate` | Sends a content generation request to the Muse API. | 
| Email quick action | “Email” button | `POST http://localhost:8000/api/v1/muse/generate` | Sends a content generation request to the Muse API. | 
| Prompt shortcut buttons | Suggested prompt buttons | No-op (client state) | Pre-fills the input field. | 
| Send message | Submit button | `POST http://localhost:8000/api/v1/muse/chat` | Sends a chat request to the Muse API. | 
