# Raptorflow Design System

## Philosophy
Clean, minimalist, and functional. Every element serves a purpose. We believe in:
- **Clarity over decoration**
- **Consistency over variety**
- **Purpose over trends**

## Core Principles

### 1. 8px Grid System
All spacing follows multiples of 8px (4px for half increments). This creates visual rhythm and consistency.

```
0px   4px   8px   12px   16px   20px   24px   32px   40px   48px   64px   80px   96px
```

### 2. Ultra-subtle Borders
Borders should be barely visible - 1px with 5% opacity black.

### 3. Pure White Canvas
The background is pure white (#FFFFFF). All depth comes from:
- Subtle shadows
- Minimal borders
- Content hierarchy

### 4. Restrained Color
Color is used only for:
- Status indicators (done, in-progress, blocked, attention, idea)
- Primary actions
- Destructive actions

### 5. Typography Hierarchy
Clear, predictable hierarchy with tight weight/size ratios:
- Display: 32px / 700 weight
- Title: 20px / 600 weight
- Title SM: 18px / 600 weight
- Body: 15px / 400 weight
- Body SM: 14px / 400 weight
- Meta: 13px / 500 weight
- Label: 11px / 600 weight / UPPERCASE

### 6. Sophisticated Micro-interactions
All transitions use:
- 150ms cubic-bezier for base interactions
- 200ms cubic-bezier for smooth animations
- 300ms cubic-bezier for bounce effects

## Component Guidelines

### Buttons
- Height: 40px (default), 36px (sm), 48px (lg)
- Radius: 8px (rounded-lg)
- Padding: 16px horizontal
- Focus: 2px ring with 2px offset

### Cards
- Background: White
- Border: 1px, 5% opacity
- Shadow: Multi-layered for depth
- Padding: 24px vertical
- Radius: 8px

### Inputs
- Height: 40px
- Padding: 16px horizontal, 8px vertical
- Radius: 8px
- Border: 1px, 5% opacity
- Focus: 2px ring with 2px offset

## Usage Examples

### Spacing
```tsx
// Use spacing utilities from @/lib/spacing
<div className={cn(spacingPatterns.cardPadding)}>
  <div className={gap(4)}>
    {/* Content */}
  </div>
</div>
```

### Typography
```tsx
<h1 className="text-display">Page Title</h1>
<h2 className="text-title">Section Title</h2>
<p className="text-body">Body text</p>
<span className="text-meta">Meta information</span>
```

### Interactions
```tsx
<button className="transition-base hover-lift focus-ring">
  Interactive Element
</button>
```

## Enforcement

### Linting Rules
1. No arbitrary values in Tailwind classes
2. Use spacing utilities, not raw values
3. Follow component patterns strictly

### Code Review Checklist
- [ ] Spacing follows 8px grid
- [ ] No unnecessary colors
- [ ] Typography uses defined classes
- [ ] Transitions are consistent
- [ ] Focus states are accessible

## Inspiration
Study these implementations:
- Linear.app - Clean workspace UI
- Notion.so - Content hierarchy
- Vercel.com - Subtle interactions
- Stripe.com - Form design
- Loom.com - Onboarding flow
