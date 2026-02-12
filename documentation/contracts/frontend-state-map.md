# Frontend State Map

- Generated: `2026-02-12T14:35:03.471496+00:00`
- Zustand Stores: `5`

## `useBCMStore`

- File: `src/stores/bcmStore.ts`
- State Fields: `manifest, version, checksum, createdAt, completionPct, synthesized, isLoading, isRebuilding, isSeeding, isReflecting, error, versions`
- Action Fields: `fetchBCM, rebuildBCM, fetchVersions, seedBCM, reflectBCM`
- Service Dependencies: `bcm.service`
- Consumer Files: `6`

## `useCampaignStore`

- File: `src/stores/campaignStore.ts`
- State Fields: `campaigns, isLoading, error`
- Action Fields: `clearError, fetchCampaigns, createCampaign, updateCampaign, deleteCampaign, getCampaignById`
- Service Dependencies: `campaigns.service`
- Consumer Files: `3`

## `useFoundationStore`

- File: `src/stores/foundationStore.ts`
- State Fields: `positioningConfidence, isLoading, error`
- Action Fields: `fetchFoundation, saveFoundation, addRICP, updateRICP, deleteRICP, getRICPById, updateMessaging, addChannel, updateChannel, deleteChannel, reset`
- Service Dependencies: `foundation.service`
- Consumer Files: `2`

## `useMovesStore`

- File: `src/stores/movesStore.ts`
- State Fields: `moves, pendingMove, isLoading, error`
- Action Fields: `fetchMoves, addMove, updateMove, deleteMove, cloneMove, setPendingMove, getMoveById, getActiveMoves, getCompletedMoves, getDraftMoves`
- Service Dependencies: `moves.service`
- Consumer Files: `7`

## `useNotificationStore`

- File: `src/stores/notificationStore.ts`
- State Fields: `notifications`
- Action Fields: `addNotification, removeNotification, markAsRead, clearNotifications`
- Service Dependencies: `-`
- Consumer Files: `1`

## `useWorkspace`

- File: `src/components/workspace/WorkspaceProvider.tsx`
- State Fields: `workspaceId, workspace, onboardingStatus, isOnboardingComplete, isLoading, error`
- Action Fields: `refresh, refreshOnboarding, reset`
- Storage Key: `raptorflow.workspace_id`
- Consumer Files: `14`
