# RaptorFlow Brand System

## Visual Identity

RaptorFlow uses a **Paper / Amber / Editorial SaaS** identity.

The product should feel like:

- Premium founder operating desk
- Paper ledger
- Strategic command journal
- Warm B2B SaaS
- Sharp, editorial, senior, operational
- Calm but powerful

## Asset Drop Locations

Place final assets here:

| Asset                  | Path                                         | Status      |
| ---------------------- | -------------------------------------------- | ----------- |
| Full logo              | `public/brand/logo-full.svg`                 | Placeholder |
| Logo mark              | `public/brand/logo-mark.svg`                 | Placeholder |
| Favicon                | `public/brand/favicon.svg`                   | Placeholder |
| Apple touch icon       | `public/brand/apple-touch-icon.png`          | TBD         |
| OG image               | `public/brand/og-image.png`                  | TBD         |
| Paper grain (standard) | `public/brand/textures/paper-grain.svg`      | TBD         |
| Paper grain (soft)     | `public/brand/textures/paper-grain-soft.svg` | TBD         |

## How to Use `RaptorFlowLogo`

```tsx
import { RaptorFlowLogo } from "@/components/brand";

// Full logo with asset fallback
<RaptorFlowLogo size="md" variant="full" />

// Mark only
<RaptorFlowLogo size="sm" variant="mark" />

// Wordmark only
<RaptorFlowLogo size="lg" variant="wordmark" />
```

- `size`: `"sm" | "md" | "lg"`
- `variant`: `"full" | "mark" | "wordmark"`
- Falls back gracefully if `public/brand/logo-full.svg` is missing.

## How to Use `RfWindow`

```tsx
import { RfWindow, RfWindowGrid } from "@/components/windows";

<RfWindow
  eyebrow="Section"
  title="Window Title"
  description="Optional description."
  variant="default"
  density="comfortable"
>
  Content here
</RfWindow>;
```

Variants: `default` | `highlight` | `quiet` | `danger`
Density: `comfortable` | `compact`

Grid wrapper:

```tsx
<RfWindowGrid columns={3}>
  <RfWindow>...</RfWindow>
  <RfWindow>...</RfWindow>
</RfWindowGrid>
```

## Color Usage Rules

| Color                     | Usage                                     |
| ------------------------- | ----------------------------------------- |
| **Amber**                 | Strategic action, highlight, primary CTAs |
| **Ink**                   | Primary text, headings, body              |
| **Paper**                 | Surfaces, backgrounds, cards              |
| **Crimson / Destructive** | Errors, risk, deletion, danger ONLY       |
| **Leaf**                  | Success, confirmed, completed             |
| **Indigo**                | Reserved for Muse                         |

## Typography Rules

| Token                  | Use                                       |
| ---------------------- | ----------------------------------------- |
| `font-display` (Serif) | Headlines, display text, hero lines       |
| `font-sans`            | UI text, body, labels                     |
| `font-mono`            | Metadata, status, system labels, eyebrows |

## Motion Rules

| Duration | Use                              |
| -------- | -------------------------------- |
| 150ms    | Hover states, micro-interactions |
| 240ms    | Card lifts, transitions          |
| 700ms    | Page enters, reveals             |

Respect `prefers-reduced-motion`. Do not add heavy animation libraries.

## Accessibility Rules

- All interactive elements have visible focus rings (`outline-color: var(--ring)`).
- Images have alt text.
- SignalDot accepts an optional `label` for screen readers.
- Color is never the sole indicator of state (pair with text/icons).

## Responsive Design Rules

- Mobile-first.
- `RfWindowGrid` stacks gracefully: 1 col mobile, expands at `sm`/`lg` breakpoints.
- Sidebar is fixed on desktop, slide-over on mobile.

## App Shell Usage

### AppPageFrame

Standard page wrapper. Use on every page.

```tsx
import { AppPageFrame } from "@/components/layout";

<AppPageFrame
  eyebrow="Section"
  title="Page Title"
  description="Optional description."
  actions={<button className="btn-primary">Action</button>}
  maxWidth="wide"
>
  Content here
</AppPageFrame>;
```

### AppPageSection

Use for content sections within a page.

```tsx
import { AppPageSection } from "@/components/layout";

<AppPageSection title="Section" variant="quiet">
  Section content
</AppPageSection>;
```

### Loading / Empty / Error States

```tsx
import { AppLoadingState, AppEmptyState, AppErrorState } from "@/components/layout";

// While loading
<AppLoadingState label="Loading..." />

// When empty
<AppEmptyState
  icon={<FileText className="w-6 h-6" />}
  title="Nothing here"
  description="Get started by creating something."
  action={<button className="btn-primary">Create</button>}
/>

// On error
<AppErrorState
  title="Failed to load"
  description={error.message}
  action={<button onClick={refetch}>Retry</button>}
/>
```

## What NOT to Do

- Do NOT use dark glass as the default product UI.
- Do NOT use neon overload.
- Do NOT use fake hologram vibes.
- Do NOT use random gradients everywhere.
- Do NOT use random inline colours.
- Do NOT use one-off page-specific styling.
- Do NOT scatter logo usage — use `RaptorFlowLogo` everywhere.
- Do NOT use a literal bird, mascot, or claw scratches in the mark.
