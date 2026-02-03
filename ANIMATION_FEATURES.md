# RaptorFlow Landing Page - Animation & Effects Guide

## 🎨 Custom Animation Components

### 1. **Custom Cursor** (`src/components/effects/CustomCursor.tsx`)
- **What**: Replaces default cursor with custom circular cursor
- **Features**:
  - Outer ring that follows mouse with lag (smooth feel)
  - Inner dot that follows precisely
  - Expands on hover over interactive elements
  - Mix-blend-mode for visibility on all backgrounds
  - Disabled on touch devices
- **Usage**: Automatically applied to all pages via layout

### 2. **Magnetic Button** (`src/components/effects/MagneticButton.tsx`)
- **What**: Buttons that magnetically attract to cursor
- **Features**:
  - Configurable strength (0.1 - 1.0)
  - Elastic snap-back on mouse leave
  - Content moves slightly less than button for depth
- **Usage**: 
  ```tsx
  <MagneticButton strength={0.3} onClick={handleClick} className="...">
    Click Me
  </MagneticButton>
  ```

### 3. **Text Reveal Animations** (`src/components/effects/TextReveal.tsx`)
- **Components**:
  - `TextReveal`: Character-by-character animation with 3D rotation
  - `WordReveal`: Word-by-word fade up
- **Features**:
  - ScrollTrigger activation
  - Configurable stagger delay
  - 3D perspective transforms
- **Usage**:
  ```tsx
  <TextReveal delay={0.2} stagger={0.02}>
    Your text here
  </TextReveal>
  ```

### 4. **Lottie-Style Compass** (`src/components/effects/LottieCompass.tsx`)
- **What**: Animated SVG compass using GSAP (no Lottie JSON needed)
- **Features**:
  - Rotating dashed outer ring
  - Counter-rotating inner markers
  - Gentle swaying needle
  - Floating animation
  - Loading spinner variant
- **Animations**:
  - Continuous rotation (outer)
  - Counter-rotation (inner markers)
  - Sine wave sway (needle)
  - Bobbing motion (entire compass)

### 5. **Animated Grain** (`src/components/effects/GrainEffect.tsx`)
- **What**: Real-time generated noise texture
- **Features**:
  - Canvas-based noise generation
  - 60fps animation
  - Very subtle opacity (8/255 alpha)
  - Mix-blend-mode overlay
- **Purpose**: Adds film/texture feel to the artisanal aesthetic

### 6. **Parallax Images** (`src/components/effects/ParallaxImage.tsx`)
- **What**: Images that move slower than scroll
- **Features**:
  - Configurable speed
  - Scale up to prevent edges showing
  - ScrollTrigger integration
- **Usage**:
  ```tsx
  <ParallaxImage src="..." speed={0.5} className="h-64" />
  ```

### 7. **Reveal on Scroll** (`src/components/effects/RevealOnScroll.tsx`)
- **What**: Generic scroll-triggered reveal wrapper
- **Animation Types**:
  - `fadeUp`: Slide up + fade
  - `fadeDown`: Slide down + fade
  - `fadeLeft`: Slide right + fade
  - `fadeRight`: Slide left + fade
  - `scale`: Scale up + fade
  - `rotate`: Rotate + scale + fade
- **Usage**:
  ```tsx
  <RevealOnScroll animation="fadeUp" delay={0.2}>
    <YourComponent />
  </RevealOnScroll>
  ```

### 8. **Floating Elements** (`src/components/effects/FloatingElements.tsx`)
- **What**: Elements that gently bob up and down
- **Features**:
  - Configurable amplitude and duration
  - Sine wave easing
  - Infinite loop
- **Usage**:
  ```tsx
  <FloatingElement amplitude={20} duration={3} delay={0}>
    <DecorativeDot />
  </FloatingElement>
  ```

### 9. **Animated Counter** (`src/components/effects/AnimatedCounter.tsx`)
- **What**: Numbers that count up when scrolled into view
- **Features**:
  - ScrollTrigger activation
  - Configurable duration
  - Prefix/suffix support
  - Locale formatting
- **Usage**:
  ```tsx
  <AnimatedCounter end={1000} prefix="₹" suffix="+" duration={2} />
  ```

### 10. **Smooth Scroll** (`src/components/effects/SmoothScroll.tsx`)
- **What**: Global smooth scrolling behavior
- **Features**:
  - CSS scroll-behavior: smooth
  - RequestAnimationFrame optimization
  - Passive event listeners

## 🎬 Section-Specific Animations

### Hero Section (`EnhancedHero.tsx`)
1. **Steam/Smoke Particles**: Canvas-based rising particles
   - Soft radial gradients
   - Fade in/out lifecycle
   - Slow upward drift
   - 25 particles max

2. **Entrance Timeline**:
   - Badge fades in first
   - Compass scales in with elastic bounce
   - Title words flip in from below (3D rotation)
   - Subtitle fades up
   - CTAs stagger in
   - Stats fade up last

3. **Floating Decorations**:
   - 3 small dots floating at different speeds
   - Adds life to the background

### Features Section (`EnhancedFeatures.tsx`)
1. **Card Reveal**: Staggered fade-up on scroll
2. **Image Parallax**: Images move slower than scroll
3. **Hover Effects**:
   - Border color transition to accent
   - Image scale on hover
   - Badge border highlight

### How It Works (`HowItWorks.tsx`)
1. **Timeline Animation**:
   - Vertical line grows from top
   - Compass markers pop in with rotation
   - Cards slide in from alternating sides

### Pricing Section (`Pricing.tsx`)
1. **Card Reveal**: Staggered fade-up
2. **Popular Card**: 
   - Scaled up slightly
   - Accent border
   - Badge bounces in
3. **Toggle Animation**: Smooth switch between monthly/yearly

## 🎯 GSAP Plugins Used

1. **ScrollTrigger**: All scroll-based animations
2. **Core GSAP**: Timelines, tweens, easings

## 📦 Files Created

```
src/components/effects/
├── SmoothScroll.tsx          # Global smooth scroll
├── CustomCursor.tsx          # Custom cursor component
├── MagneticButton.tsx        # Magnetic hover effect
├── TextReveal.tsx            # Text animation components
├── ParallaxImage.tsx         # Parallax scroll images
├── AnimatedCounter.tsx       # Counting animation
├── FloatingElements.tsx      # Bobbing animations
├── RevealOnScroll.tsx        # Scroll reveal wrapper
├── LottieCompass.tsx         # Animated compass SVG
├── GrainEffect.tsx           # Noise texture overlay
└── index.ts                  # Exports

src/components/landing/
├── EnhancedHero.tsx          # Hero with all effects
├── EnhancedFeatures.tsx      # Features with parallax
└── [existing components updated]
```

## 🚀 Performance Optimizations

1. **will-change**: Applied to animated elements
2. **Passive listeners**: Scroll events use passive mode
3. **RAF**: Canvas animations use requestAnimationFrame
4. **Cleanup**: All GSAP contexts properly reverted
5. **Touch detection**: Cursor/magnetic effects disabled on touch
6. **Reduced motion**: Respects prefers-reduced-motion

## 🎨 Visual Effects Summary

| Effect | Location | Tech |
|--------|----------|------|
| Custom Cursor | Global | GSAP + CSS |
| Magnetic Buttons | CTAs, Links | GSAP |
| Steam Particles | Hero | Canvas 2D |
| Animated Grain | Global | Canvas 2D |
| Text Reveal | Headlines | GSAP ScrollTrigger |
| Parallax Images | Feature Cards | GSAP ScrollTrigger |
| Lottie Compass | Hero | GSAP SVG |
| Floating Dots | Hero | GSAP Sine |
| Card Hover | Features | CSS Transitions |
| Timeline | How It Works | GSAP ScrollTrigger |

## 📝 Notes

- All animations use the coffeehouse color palette
- Animations are subtle and elegant, not flashy
- Custom cursor hides on mobile automatically
- Grain effect adds artisanal texture
- No external Lottie JSON files needed (custom SVG animations)
