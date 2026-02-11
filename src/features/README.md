# Features Directory

This directory contains feature modules organized by domain. Each feature is self-contained with its own components, hooks, services, stores, and types.

## Structure

```
features/
├── campaigns/          # Campaign management
│   ├── components/    # Campaign-specific components
│   ├── hooks/         # Campaign-specific hooks
│   ├── services/      # Campaign API clients
│   ├── stores/        # Campaign state management
│   └── types/         # Campaign TypeScript types
├── dashboard/         # Dashboard and analytics
├── foundation/        # Brand foundation (positioning, voice, etc.)
├── moves/             # Marketing moves and tasks
├── positioning/       # Competitive positioning
└── workspace/         # Workspace management
```

## Guidelines

### Component Organization
- **components/**: React components specific to this feature
- **hooks/**: Custom hooks for this feature's logic
- **services/**: API clients and data fetching
- **stores/**: Zustand stores for feature state
- **types/**: TypeScript interfaces and types

### Import Patterns

```typescript
// Import from same feature
import { CampaignCard } from './components/CampaignCard'
import { useCampaigns } from './hooks/useCampaigns'

// Import from other features
import { WorkspaceSelector } from '@/features/workspace/components/WorkspaceSelector'

// Import shared components
import { Button } from '@/shared/ui/button'
import { PageLayout } from '@/shared/layouts/PageLayout'
```

### Best Practices

1. **Keep features independent**: Minimize cross-feature dependencies
2. **Share through exports**: Export public API from index files
3. **Use shared components**: Don't duplicate UI components
4. **Colocate related code**: Keep related files together
5. **Type everything**: Use TypeScript for all feature code

### Code Splitting

Features are automatically code-split by Next.js App Router. For additional optimization:

```typescript
// Lazy load heavy components
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('./components/HeavyChart'), {
  loading: () => <Skeleton />,
  ssr: false
})
```

## Migration Status

- [ ] Campaigns - In Progress
- [ ] Dashboard - Pending
- [ ] Foundation - Pending
- [ ] Moves - Pending
- [ ] Positioning - Pending
- [ ] Workspace - Pending
