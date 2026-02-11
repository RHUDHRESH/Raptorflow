# Shared Directory

This directory contains components, utilities, and providers shared across all features.

## Structure

```
shared/
├── ui/              # Design system components (Blueprint)
├── layouts/         # Page layouts and shells
├── providers/       # React context providers
└── effects/         # Visual effects and animations
```

## UI Components (Design System)

The `ui/` directory contains the Blueprint design system components:

- **Buttons**: BlueprintButton, ModernButton, MagneticButton
- **Cards**: BlueprintCard, ModernCard
- **Forms**: BlueprintInput, BlueprintSelect
- **Feedback**: BlueprintLoader, BlueprintToast, BlueprintSkeleton
- **Data Display**: BlueprintTable, BlueprintBadge, BlueprintKPI
- **Navigation**: BlueprintTabs
- **Modals**: BlueprintModal

### Usage

```typescript
import { Button } from '@/shared/ui/button'
import { Card } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'

function MyComponent() {
  return (
    <Card>
      <Input placeholder="Enter text" />
      <Button>Submit</Button>
    </Card>
  )
}
```

## Layouts

Common page layouts and shells:

```typescript
import { PageLayout } from '@/shared/layouts/PageLayout'
import { DashboardShell } from '@/shared/layouts/DashboardShell'

function MyPage() {
  return (
    <PageLayout title="My Page">
      <DashboardShell>
        {/* Page content */}
      </DashboardShell>
    </PageLayout>
  )
}
```

## Providers

React context providers for global state:

```typescript
import { AnimationProvider } from '@/shared/providers/AnimationProvider'
import { WorkspaceProvider } from '@/shared/providers/WorkspaceProvider'

function App({ children }) {
  return (
    <WorkspaceProvider>
      <AnimationProvider>
        {children}
      </AnimationProvider>
    </WorkspaceProvider>
  )
}
```

## Effects

Visual effects and animations:

```typescript
import { FloatingElements } from '@/shared/effects/FloatingElements'
import { TextReveal } from '@/shared/effects/TextReveal'
import { GrainEffect } from '@/shared/effects/GrainEffect'
```

## Guidelines

1. **Reusability**: Only add truly shared components
2. **Documentation**: Document all exported components
3. **Types**: Provide full TypeScript types
4. **Testing**: Test shared components thoroughly
5. **Performance**: Optimize for bundle size

## Adding New Shared Components

1. Create component in appropriate subdirectory
2. Export from index file
3. Add to this README
4. Write tests
5. Document usage examples
