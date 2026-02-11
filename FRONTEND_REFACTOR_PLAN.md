# Frontend Architecture Refactor Plan

## Current Structure Analysis

### Existing Organization
```
src/
├── app/                    # Next.js App Router (good)
├── components/             # Mixed organization (needs refactor)
│   ├── analytics/
│   ├── bcm/
│   ├── campaigns/
│   ├── compass/
│   ├── dashboard/
│   ├── effects/
│   ├── foundation/
│   ├── landing/
│   ├── moves/
│   ├── notifications/
│   ├── positioning/
│   ├── providers/
│   ├── shell/
│   ├── ui/                # Design system components
│   └── workspace/
├── lib/                   # Utilities (good)
├── services/              # API clients (good)
├── stores/                # Zustand stores (good)
└── types/                 # TypeScript types (good)
```

### Issues Identified
1. **Mixed organization**: Some feature-based, some type-based
2. **Large components directory**: 178+ component files
3. **No clear separation**: Shared vs feature-specific components
4. **Missing code splitting**: Large initial bundle
5. **Inconsistent imports**: Long import paths

---

## Target Structure

### Feature-Based Organization
```
src/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth routes
│   ├── (shell)/           # Main app shell
│   └── api/               # API routes
├── features/              # Feature modules (NEW)
│   ├── campaigns/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   └── types/
│   ├── dashboard/
│   ├── foundation/
│   ├── moves/
│   ├── positioning/
│   └── workspace/
├── shared/                # Shared components (NEW)
│   ├── ui/               # Design system (Blueprint)
│   ├── layouts/
│   ├── providers/
│   └── effects/
├── lib/                   # Utilities
├── services/              # Global API clients
└── types/                 # Global types
```

---

## Migration Strategy

### Phase 1: Create New Structure
1. Create `src/features/` directory
2. Create `src/shared/` directory
3. Move design system to `src/shared/ui/`

### Phase 2: Migrate Features
1. **Campaigns** - Move to `features/campaigns/`
2. **Dashboard** - Move to `features/dashboard/`
3. **Foundation** - Move to `features/foundation/`
4. **Moves** - Move to `features/moves/`
5. **Positioning** - Move to `features/positioning/`
6. **Workspace** - Move to `features/workspace/`

### Phase 3: Migrate Shared
1. **UI Components** - Already in good location
2. **Providers** - Move to `shared/providers/`
3. **Effects** - Move to `shared/effects/`
4. **Layouts** - Move to `shared/layouts/`

### Phase 4: Code Splitting
1. Add dynamic imports for heavy features
2. Implement route-based code splitting
3. Lazy load non-critical components

---

## Implementation Steps

### Step 1: Create Directory Structure
```bash
mkdir -p src/features/{campaigns,dashboard,foundation,moves,positioning,workspace}/{components,hooks,services,stores,types}
mkdir -p src/shared/{ui,layouts,providers,effects}
```

### Step 2: Move Components (Example: Campaigns)
```bash
# Move campaign components
mv src/components/campaigns/* src/features/campaigns/components/

# Update imports in moved files
# @/components/campaigns/... → @/features/campaigns/components/...
```

### Step 3: Update Path Aliases
```json
// tsconfig.json
{
  "paths": {
    "@/*": ["./src/*"],
    "@/features/*": ["./src/features/*"],
    "@/shared/*": ["./src/shared/*"]
  }
}
```

### Step 4: Add Code Splitting
```typescript
// Example: Lazy load campaign feature
const CampaignPage = dynamic(() => import('@/features/campaigns/components/CampaignPage'), {
  loading: () => <LoadingSpinner />,
  ssr: false
})
```

---

## Benefits

### Organization
- Clear feature boundaries
- Easier to navigate
- Better code ownership
- Scalable structure

### Performance
- Smaller initial bundle
- Faster page loads
- Better caching
- Reduced memory usage

### Developer Experience
- Shorter import paths
- Clear component location
- Easier refactoring
- Better IDE support

---

## Risks & Mitigation

### Risk 1: Breaking Changes
**Mitigation**: 
- Update imports incrementally
- Test after each feature migration
- Use TypeScript to catch errors

### Risk 2: Import Path Updates
**Mitigation**:
- Use find/replace with regex
- Update tsconfig.json paths
- Verify with type-check

### Risk 3: Build Failures
**Mitigation**:
- Test build after each migration
- Keep old structure until verified
- Rollback plan ready

---

## Success Criteria

- [ ] All features in `features/` directory
- [ ] All shared components in `shared/` directory
- [ ] Path aliases configured
- [ ] Code splitting implemented
- [ ] Bundle size reduced by 30%+
- [ ] All imports updated
- [ ] Type-check passes
- [ ] Build succeeds
- [ ] Tests pass

---

**Status**: Ready to Execute  
**Estimated Time**: 4 days  
**Impact**: High
