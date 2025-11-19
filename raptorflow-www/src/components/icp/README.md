# ICP Dashboard Components

Premium black-and-white dashboard components for the ICP Maker / ICP Reveal screen.

## Components

### `DarkBackground`
Replaces the colorful aurora background with a subtle dark gradient (black/white/grey only). Includes gentle radial highlights that respect `prefers-reduced-motion`.

### `ICPGrid` & `ICPGridItem`
Refactored grid components with:
- Black/white/grey gradients only (`from-slate-950 via-slate-900 to-zinc-900`)
- Premium card styling with subtle borders and shadows
- Hover effects with white/grey shine
- Responsive column spanning (1-6 columns)

### `ICPDashboardShell`
Main shell component that combines:
- Dark background
- Grid layout with placeholder areas for:
  - **Left**: ICP Cards stack
  - **Right**: ICP Details panel

## Usage

```tsx
import { ICPDashboardShell } from "@/components/icp";

export default function ICPRevealPage() {
  return <ICPDashboardShell />;
}
```

Or use individual components:

```tsx
import { DarkBackground, ICPGrid, ICPGridItem } from "@/components/icp";

export default function CustomPage() {
  return (
    <div className="relative min-h-screen">
      <DarkBackground />
      <ICPGrid>
        <ICPGridItem colSpan={3}>
          {/* Your content */}
        </ICPGridItem>
        <ICPGridItem colSpan={3}>
          {/* Your content */}
        </ICPGridItem>
      </ICPGrid>
    </div>
  );
}
```

## Design Principles

- **Black + White Only**: No colorful gradients, premium minimal aesthetic
- **OpenAI/Linear/Vercel Vibe**: Clean, spacious, professional
- **Subtle Animations**: Respects `prefers-reduced-motion`
- **Premium Feel**: Rounded corners, soft shadows, elegant hover effects

## Next Steps

1. Build the actual ICP card component (with silver glow border)
2. Build the ICP detail panel component
3. Implement the reveal flow (thinking state → unlock animations → split layout)
4. Connect to backend API for ICP data

