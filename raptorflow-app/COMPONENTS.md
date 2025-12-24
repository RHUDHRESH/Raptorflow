# RaptorFlow — Component Specifications

These are **frozen**. Do not deviate.

---

## Button

### Primary
```
Background:    var(--color-ink) → #171717
Text:          #FFFFFF
Height:        var(--height-button-md) → 44px
Padding:       0 24px
Border:        none
Radius:        var(--radius-md) → 12px
Font:          var(--font-sans), var(--font-medium), var(--text-base)

Hover:         background #2a2a2a
Active:        transform scale(0.98)
Disabled:      opacity 0.5, cursor not-allowed
```

### Secondary
```
Background:    transparent
Text:          var(--color-ink)
Border:        1px solid var(--color-border)
Height:        44px
Radius:        12px

Hover:         border-color var(--color-muted)
Active:        transform scale(0.98)
```

### Ghost (Text Button)
```
Background:    transparent
Text:          var(--color-muted)
Border:        none
Padding:       0 8px
Height:        auto

Hover:         text-decoration underline, color var(--color-ink)
```

---

## Card

### Default
```
Background:    var(--color-surface) → #FFFFFF
Border:        1px solid var(--color-border-subtle)
Radius:        var(--radius-lg) → 14px
Padding:       var(--space-6) → 24px
Shadow:        none

Hover:         (optional) shadow var(--shadow-sm)
```

### Elevated
```
Background:    var(--color-surface)
Border:        none
Shadow:        var(--shadow-md)
Radius:        14px
Padding:       24px
```

**Rules:**
- No colored backgrounds, ever
- No colored borders, ever
- Pick border OR shadow, not both

---

## Input

### Text Input
```
Background:    var(--color-surface)
Border:        1px solid var(--color-border)
Height:        var(--height-input) → 48px
Padding:       0 16px
Radius:        var(--radius-md) → 12px
Font:          var(--text-base)

Focus:         border-color var(--color-ink), outline none
Placeholder:   color var(--color-ghost)
```

### Minimal (Bottom border only)
```
Background:    transparent
Border:        none
Border-bottom: 1px solid var(--color-border)
Height:        48px
Padding:       0 0 8px 0
Radius:        0

Focus:         border-color var(--color-ink)
```

---

## Tabs

### Underline Style (ONLY)
```
Container:
  Border-bottom: 1px solid var(--color-border)
  Gap: 32px

Tab:
  Padding: 12px 0
  Font: var(--text-base), var(--font-medium)
  Color: var(--color-muted)
  Border-bottom: 2px solid transparent

Tab Active:
  Color: var(--color-ink)
  Border-bottom: 2px solid var(--color-ink)

Tab Hover:
  Color: var(--color-ink)
```

**No pill tabs. No backgrounds. Underline only.**

---

## Badge (Use Sparingly)

### Neutral
```
Background:    var(--color-border-subtle)
Text:          var(--color-muted)
Font:          var(--text-xs), var(--font-medium)
Padding:       4px 8px
Radius:        var(--radius-full)
```

**Rules:**
- Maximum 1-2 per card
- No colored badges
- Prefer status dots over badges

---

## Status Dot

```
Size:          8px
Border-radius: var(--radius-full)
Colors:
  Green:  var(--color-green)
  Amber:  var(--color-amber)
  Red:    var(--color-red)
```

**Rules:**
- Dots only, never pill backgrounds
- 8px diameter maximum
- Used inline with text

---

## Modal / Dialog

### Slide-in
```
Position:      fixed right, full height
Width:         480px max
Background:    var(--color-surface)
Shadow:        -8px 0 24px rgba(0,0,0,0.1)
Padding:       32px

Animation:
  Enter: translateX(100%) → translateX(0), 220ms ease-out
  Exit:  translateX(0) → translateX(100%), 180ms ease-in

Backdrop:      rgba(0,0,0,0.4)
```

**No pop-in modals. Slide-in only.**

---

## Empty State

### Template
```
[Icon - 48px, muted, optional]

[Headline - text-heading]
Nothing here yet.

[Body - text-body, muted]
One sentence explaining what this is for.

[CTA - Primary Button, single action]
Create your first ___
```

**Rules:**
- No sad illustrations
- No jokes/emojis
- One action only

---

## Avatar

```
Size:          32px (default), 24px (small), 40px (large)
Radius:        var(--radius-full)
Border:        2px solid var(--color-surface) (for stacks)
Background:    gradient (if no image)
Font:          var(--text-xs), var(--font-semibold), white
```

---

## Skeleton Loader

```
Background:    var(--color-border-subtle)
Radius:        var(--radius-md)
Animation:     shimmer, 1.5s ease-in-out infinite

Shimmer gradient:
  linear-gradient(90deg,
    transparent,
    rgba(255,255,255,0.4),
    transparent)
```

**Rules:**
- Subtle shimmer, not aggressive
- Match exact shape of content

---

## Sidebar

```
Width:         var(--sidebar-width) → 220px
Background:    var(--color-surface)
Border-right:  1px solid var(--color-border-subtle)
Padding:       20px 12px

Nav Item:
  Height: 40px
  Padding: 0 12px
  Radius: var(--radius-md)
  Font: var(--text-sm), var(--font-medium)
  Color: var(--color-muted)

Nav Item Active:
  Background: var(--color-ink)
  Color: #FFFFFF

Nav Item Hover:
  Background: var(--color-border-subtle)
```

**Rules:**
- ≤10 items
- No colored icons
- No notification badges (except Help)

---

## Page Header

```
Layout:
  display: flex
  justify-content: space-between
  align-items: flex-start
  margin-bottom: var(--section-gap)

Title:
  font: var(--font-display)
  size: var(--text-4xl)
  weight: var(--font-semibold)
  color: var(--color-ink)

Subtitle:
  font: var(--font-sans)
  size: var(--text-base)
  color: var(--color-muted)
  margin-top: 4px

CTA:
  Primary button, aligned right
```

---

## Frozen Component Checklist

Before adding ANY new component:

- [ ] Does an existing component solve this?
- [ ] Is this component used in 3+ places?
- [ ] Does it follow token values exactly?
- [ ] Has it been added to this spec?

**If not frozen here, it doesn't ship.**
