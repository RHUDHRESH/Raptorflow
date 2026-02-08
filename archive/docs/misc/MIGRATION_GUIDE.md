# Frontend Migration Guide

## Overview
This guide outlines the steps to migrate the existing Raptorflow frontend to the new minimalist design system.

## Phase 1: Foundation ✅
- [x] Updated color system to pure white background
- [x] Implemented 8px grid spacing system
- [x] Refined typography hierarchy
- [x] Added sophisticated transitions
- [x] Updated core components (Button, Card, Input, Badge)

## Phase 2: Component Updates
### Priority Components to Update

1. **Navigation Components**
   - `src/components/shell/NavRail.tsx`
   - `src/components/shell/IconRail.tsx`
   - `src/components/shell/ContentHeader.tsx`

   Changes needed:
   - Apply new spacing utilities
   - Update hover states with new transitions
   - Ensure typography consistency

2. **Form Components**
   - All form inputs in `/components/ui/`
   - Form layouts in feature components

   Changes needed:
   - Standardize input heights (40px)
   - Apply consistent spacing
   - Update focus states

3. **Data Display**
   - Tables
   - Lists
   - Status indicators

   Changes needed:
   - Apply status color system
   - Ensure proper spacing
   - Add hover interactions

## Phase 3: Layout Updates

### 1. Main Layout (`src/app/layout.tsx`)
- Ensure proper container padding
- Apply consistent spacing patterns

### 2. Page Templates
- Update all page layouts to use:
  - `container mx-auto px-6` for content
  - `py-12` for section spacing
  - Consistent header patterns

## Phase 4: Feature Components

### ICP/Cohort Components
Based on the memory analysis, update these key files:

1. **`src/components/icp/ICPWizard.tsx`**
   - Apply new card styles
   - Update button hierarchy
   - Ensure proper spacing between steps

2. **`src/components/onboarding/steps/StepCohorts.tsx`**
   - Use new form components
   - Apply consistent spacing
   - Update status indicators

3. **`src/lib/icp-store.ts`**
   - No UI changes, but ensure any toast notifications use new styles

## Migration Checklist for Each Component

### Before Updating
1. Identify all spacing values
2. Note all colors used
3. Check typography classes
4. List interactive elements

### During Update
1. Replace arbitrary spacing with 8px grid values
2. Update colors to use design tokens
3. Apply typography classes from the system
4. Add transition classes
5. Ensure focus states are accessible

### After Update
1. Test hover states
2. Check responsive behavior
3. Verify accessibility
4. Ensure visual consistency

## Common Patterns

### Card Pattern
```tsx
<Card className="transition-base hover-lift">
  <CardHeader>
    <CardTitle className="text-title">Title</CardTitle>
    <CardDescription className="text-body">Description</CardDescription>
  </CardHeader>
  <CardContent className="space-y-4">
    {/* Content */}
  </CardContent>
</Card>
```

### Form Pattern
```tsx
<div className="space-y-6">
  <div className="space-y-2">
    <label className="text-label">LABEL</label>
    <Input placeholder="..." />
  </div>
  <div className="flex gap-2 pt-4">
    <Button>Primary</Button>
    <Button variant="outline">Secondary</Button>
  </div>
</div>
```

### Status Badge Pattern
```tsx
<Badge variant={status === 'done' ? 'success' : 'info'}>
  {status}
</Badge>
```

## Testing Strategy

1. **Visual Regression Testing**
   - Capture screenshots of all pages
   - Compare with updated versions

2. **Interaction Testing**
   - Test all hover states
   - Verify transitions are smooth
   - Check focus management

3. **Accessibility Testing**
   - Ensure color contrast ratios
   - Test keyboard navigation
   - Verify screen reader compatibility

## Rollout Plan

1. **Week 1**: Update core components and design system
2. **Week 2**: Migrate navigation and layout components
3. **Week 3**: Update feature components (ICP, onboarding)
4. **Week 4**: Polish, testing, and bug fixes

## Resources

- Design System Documentation: `/DESIGN_SYSTEM.md`
- Live Preview: `/design-system` route
- Spacing Utilities: `/lib/spacing.ts`
- Component Examples: Check individual component files

## Gotchas

1. **Dark Mode**: Ensure all components work in both light and dark modes
2. **Responsive**: Test on mobile, tablet, and desktop
3. **Performance**: Don't over-animate - keep transitions subtle
4. **Consistency**: Always use design tokens, never arbitrary values
