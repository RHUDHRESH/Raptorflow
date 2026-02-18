# RaptorFlow Landing Page v2.0

## Overview
A 10x more ambitious landing page with intricate GSAP animations, complex scroll-driven interactions, and rich artwork.

## What's New

### 1. Hero Section Enhancements
- **3D perspective transforms** on headline text
- **Staggered reveal animation** with rotation
- **Blur-to-sharp effect** on "truth machine" text
- **Animated underline** with SVG path
- **Floating orbs** with sine wave motion
- **Grid pattern background** with subtle opacity
- **Parallax scroll effect** (content moves slower than scroll)
- **Animated scroll indicator** (mouse-style with bounce)

### 2. Problem Section (Pinned Scroll)
- **Sticky visual element** that pins while cards scroll
- **3D card entrances** with rotateY
- **Chaos visual** with scattered boxes
- **Broken connection lines** (SVG dashed lines)
- **Progressive reveal** of each problem card

### 3. Cockpit + Autopilot Section
- **Complex SVG diagram** with 4 connected nodes
- **Line draw animation** (strokeDashoffset)
- **Node scale animation** with bounce
- **Orbiting particle** rotating around center
- **Gradient glow effects** on hover
- **Interactive SVG** that builds on scroll

### 4. Features Grid
- **3D perspective cards** with rotateX
- **Hover parallax** (lift + scale effect)
- **Radial gradient glow** on hover
- **Tag pills** for each feature
- **Staggered 3D reveal** with transformPerspective

### 5. Demo Section (Interactive)
- **Tab-based navigation** (4 demo states)
- **Autoplay functionality** with pause/resume
- **Progress indicator** for each demo
- **Mock UI representations** (4 different states)
- **Play button overlay** on hover
- **State-driven content** switching

### 6. Stats Section (Dark Interlude)
- **Inverted color scheme** (ink-1 bg, inverse text)
- **Animated counters** with snap
- **Dot pattern background**
- **Subtitle text** under each stat

### 7. Principles Section
- **Alternating layout** (left/right)
- **Horizontal scroll reveals**
- **Large number indicators** (01, 02, 03, 04)
- **Icon hover color transition**

### 8. Testimonials (Infinite Marquee)
- **Infinite horizontal scroll**
- **Duplicated track** for seamless loop
- **Card-based layout** with avatars
- **Auto-scrolling animation** (30s duration)

### 9. CTA Section
- **Giant background glow**
- **Underlined text** with SVG underline
- **Checkmark list** with flex layout

### 10. Footer
- **5-column layout**
- **Social icons** with hover states
- **Multi-link columns**

## GSAP Animations Implemented

### Plugins Used
```javascript
gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);
```

### Animation Types

#### 1. Entrance Animations
```javascript
// Hero timeline with nested animations
heroTl
  .fromTo(".hero-badge", { scale: 0 }, { scale: 1, ease: "back.out" })
  .fromTo(".hero-line1", { y: 120, rotateX: 45 }, { y: 0, rotateX: 0 }, "-=0.3")
  .fromTo(".hero-truth", { filter: "blur(20px)" }, { filter: "blur(0px)" }, "-=0.6");
```

#### 2. Scroll-Triggered
```javascript
// Sticky pin
ScrollTrigger.create({
  trigger: ".problem-section",
  pin: ".problem-visual",
  start: "top 20%",
  end: "+=800",
});

// Reveal on scroll
scrollTrigger: {
  trigger: element,
  start: "top 80%",
  toggleActions: "play none none reverse",
}
```

#### 3. Parallax Effects
```javascript
// Hero parallax
gsap.to(".hero-content", {
  yPercent: 50,
  scrollTrigger: {
    scrub: true,
  },
});
```

#### 4. Continuous Animations
```javascript
// Floating orbs
gsap.to(orb, {
  y: "-30",
  duration: 3,
  repeat: -1,
  yoyo: true,
  ease: "sine.inOut",
});

// Testimonial marquee
gsap.to(".testimonial-track", {
  xPercent: -50,
  duration: 30,
  repeat: -1,
});

// Orbit rotation
gsap.to(".orbit-ring", {
  rotation: 360,
  duration: 60,
  repeat: -1,
});
```

#### 5. SVG Line Draw
```javascript
// Cockpit diagram
cockpitTl
  .fromTo(".cockpit-line", 
    { strokeDashoffset: 300 }, 
    { strokeDashoffset: 0, stagger: 0.1 }
  )
  .fromTo(".cockpit-node", 
    { scale: 0 }, 
    { scale: 1, ease: "back.out(2)" }
  );
```

#### 6. Counter Animation
```javascript
// Stats counting
scrollTrigger: {
  onEnter: () => {
    gsap.to(stat, {
      innerText: value,
      duration: 2.5,
      snap: { innerText: 1 },
    });
  },
}
```

## Component Architecture

### Page Structure
```
LandingPage (65KB)
├── PageLoader (SVG draw animation)
├── FloatingNav (scroll-aware, mobile menu)
├── Hero Section (parallax, 3D text)
├── Problem Section (pinned scroll)
├── Cockpit Section (SVG diagram)
├── Features Section (3D cards)
├── Demo Section (interactive tabs)
├── Stats Section (dark, counters)
├── Principles Section (alternating)
├── Testimonials (infinite marquee)
├── CTA Section (giant glow)
└── Footer (5-column)
```

## Interactive Elements

### 1. Demo Player
- 4 demo states (Foundation, Moves, Muse, Campaigns)
- Autoplay with progress indicator
- Manual tab switching
- Pause/resume controls

### 2. Feature Cards
- 3D hover lift effect
- Radial gradient glow
- Content reveal on scroll

### 3. Navigation
- Scroll-aware visibility
- Active section highlighting
- Smooth scroll to sections
- Mobile menu overlay

### 4. Testimonials
- Infinite auto-scroll
- Hover to pause (optional)
- Card-based layout

## Responsive Breakpoints

```css
Mobile:  < 640px  (Single column, stacked)
Tablet:  640-1024px (2 columns)
Desktop: > 1024px   (Full layout)
```

## Performance Optimizations

1. **will-change** on animated elements
2. **Passive scroll listeners**
3. **GSAP context cleanup** on unmount
4. **Lazy loading** of below-fold content
5. **CSS transforms** instead of layout properties
6. **will-change: transform** for GPU acceleration

## File Sizes

| File | Size |
|------|------|
| page.tsx | 65KB |
| FloatingNav.tsx | 5KB |
| PageLoader.tsx | 5KB |

## Dependencies

```json
{
  "gsap": "^3.14.2",
  "@gsap/react": "^2.1.2",
  "lucide-react": "latest"
}
```

## Animation Timing Reference

| Animation | Duration | Easing |
|-----------|----------|--------|
| Hero reveal | 1.2s | power4.out |
| Card entrance | 0.8s | power2.out |
| SVG line draw | 2s | power2.inOut |
| Counter | 2.5s | power2.out |
| Marquee | 30s | none (linear) |
| Hover effects | 0.3s | power2.out |
| Page load | 2.5s total | mixed |

## Copy Strategy

### Headlines
- "Marketing is not a funnel. It's a truth machine."
- "Cockpit + Autopilot"
- "Four systems. One truth."

### Philosophy
- Truth over trends
- Lock, don't lose  
- Pull, not push
- One decision per screen

### CTAs
- "Start Building Free"
- "See It In Action"
- "Ready to build your truth machine?"

## Visual Design

### Color Usage
- **Ink-1**: Primary text, CTAs, emphasis
- **Ink-2**: Secondary text, descriptions
- **Ink-3**: Muted text, labels
- **Status colors**: Accents for features/stats
- **Surface**: Card backgrounds
- **Canvas**: Page background

### Typography Scale
- H1: 48-120px (responsive)
- H2: 32-72px
- H3: 24px
- H4: 20px
- Body: 16px
- Mono-xs: 10px (labels)

## Future Enhancements

1. **Three.js globe** with live data points
2. **WebGL particle system** for hero background
3. **Video backgrounds** for demo section
4. **Sound design** for interactions
5. **Reduced motion** preferences support
6. **Prefers-color-scheme** dark mode
