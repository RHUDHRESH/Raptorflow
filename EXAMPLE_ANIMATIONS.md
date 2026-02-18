# RaptorFlow Subtle Animation Examples

## Philosophy
Complex animations that feel invisible. Sophisticated easing, thoughtful timing, restrained motion.

## Examples

### 1. Text Reveal by Words
```tsx
import { AnimatedText } from "@/components/landing";

<AnimatedText
  as="h1"
  type="words"
  stagger={0.03}
  className="rf-h1"
>
  Marketing is not a funnel. It's a truth machine.
</AnimatedText>
```
Each word fades up with 30ms delay. Creates a wave you feel more than see.

### 2. Magnetic Button
```tsx
import { Button } from "@/components/raptor";

<Button magnetic variant="primary">
  Start Building
</Button>
```
Button subtly pulls toward cursor. Elastic release on mouse leave.

### 3. Parallax Depth
```tsx
import { ParallaxLayer } from "@/components/landing";

<ParallaxLayer speed={0.2}>
  <div className="bg-[var(--border-1)]" />
</ParallaxLayer>
```
Element moves 20% slower than scroll. Creates subtle depth.

### 4. SVG Line Draw
```tsx
import { drawPath } from "@/components/raptor";

useEffect(() => {
  drawPath("#myPath", { duration: 1.5, ease: "power2.inOut" });
}, []);

<svg>
  <path id="myPath" d="M0,0 L100,0" stroke="var(--ink-1)" fill="none" />
</svg>
```
Line draws itself. Elegant, architectural feel.

### 5. Staggered Cards
```tsx
import { StaggerContainer } from "@/components/landing";

<StaggerContainer stagger={0.08}>
  {cards.map(card => (
    <Card key={card.id} className="stagger-child">
      {card.content}
    </Card>
  ))}
</StaggerContainer>
```
Cards reveal in sequence with 80ms delay.

### 6. Blur Reveal
```tsx
import { AnimatedText } from "@/components/landing";

<AnimatedText blur type="lines" className="rf-h2">
  Build your foundation.
</AnimatedText>
```
Text starts blurry, sharpens into focus.

### 7. Counter Animation
```tsx
import { animateCounter } from "@/components/raptor";

useEffect(() => {
  animateCounter(ref.current, 100, { 
    duration: 2, 
    suffix: "%" 
  });
}, []);
```
Numbers count up with proper easing. Not linear - feels physical.

### 8. Underline Draw
```tsx
import { underlineDraw } from "@/components/raptor";

useEffect(() => {
  const cleanup = underlineDraw(linkRef.current);
  return cleanup;
}, []);

<a ref={linkRef} className="relative">
  Hover me
</a>
```
Underline draws from left on hover.

## Timing Reference

| Animation | Duration | Stagger | Easing |
|-----------|----------|---------|--------|
| Text words | 0.6s | 0.03s | power2.out |
| Text chars | 0.4s | 0.01s | power2.out |
| Cards | 0.6s | 0.08s | power2.out |
| SVG draw | 1.5s | - | power2.inOut |
| Counter | 2s | - | power2.out |
| Magnetic | 0.2s | - | power2.out |
| Elastic return | 0.5s | - | elastic.out |

## Principles

1. **Felt, not seen** - Animation should be noticed subconsciously
2. **Purposeful motion** - Every animation serves UX
3. **Consistent easing** - Power2.out for reveals, elastic for playful
4. **Restrained timing** - Fast enough to not bore, slow enough to register
5. **Performance** - will-change, transforms only, no layout thrash
