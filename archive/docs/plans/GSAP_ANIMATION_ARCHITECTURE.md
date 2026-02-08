# RAPTORFLOW LANDING PAGE — GSAP ANIMATION ARCHITECTURE
## Award-Winning Motion Design System

---

# TABLE OF CONTENTS
1. [Animation Philosophy](#animation-philosophy)
2. [GSAP Setup & Configuration](#gsap-setup--configuration)
3. [Global Animation Controller](#global-animation-controller)
4. [Section-Specific Animation Specs](#section-specific-animation-specs)
5. [Micro-Interaction Library](#micro-interaction-library)
6. [Performance Optimization](#performance-optimization)
7. [Accessibility Considerations](#accessibility-considerations)

---

# ANIMATION PHILOSOPHY

## Core Principles
> **Mechanical Motion** — Linear easing, precise landings, no bounce
> **Visible Structure** — Animations reveal the underlying system
> **Editorial Authority** — Purposeful, confident motion

## Timing Standards
| Animation Type | Duration | Easing |
|---------------|----------|--------|
| Micro-interactions | 150-200ms | `power2.out` |
| Element entrances | 400-600ms | `power3.out` |
| Section transitions | 800-1000ms | `power2.inOut` |
| Stagger delays | 50-100ms | - |
| Scroll parallax | Continuous | Linear |

## Movement Language
- **Entrances**: Elements arrive from bottom (y: 30-60px) or fade in place
- **Exits**: Elements exit to top or fade out (quick 200ms)
- **Scaling**: Subtle 0.95x to 1x for emphasis
- **Rotation**: Maximum 5° for playful moments only
- **Parallax**: Maximum 150px range for dramatic effect

---

# GSAP SETUP & CONFIGURATION

## Required Plugins
```typescript
// lib/gsap-config.ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText"; // Club GreenSock
import { MotionPathPlugin } from "gsap/MotionPathPlugin";

gsap.registerPlugin(ScrollTrigger, SplitText, MotionPathPlugin);

// Global defaults
gsap.defaults({
  ease: "power2.out",
  duration: 0.6,
});

// Reduced motion preference
const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
).matches;

gsap.globalTimeline.timeScale(prefersReducedMotion ? 0 : 1);
```

## Custom Easing Functions
```typescript
// Architectural precision easing
export const customEase = {
  // Sharp, mechanical arrival
  precise: "power3.out",

  // Smooth, confident landing
  confident: "power2.out",

  // Dramatic section reveals
  dramatic: "power2.inOut",

  // Subtle hover feedback
  subtle: "power1.out",

  // Elastic for playful moments (use sparingly)
  playful: "back.out(1.2)",
};
```

---

# GLOBAL ANIMATION CONTROLLER

## Master Timeline Architecture
```typescript
// hooks/useLandingPageAnimations.ts
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function useLandingPageAnimations() {
  const mainRef = useRef<HTMLElement>(null);
  const triggersRef = useRef<ScrollTrigger[]>([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initialize all section animations
      initPreloaderAnimation();
      initHeroAnimation();
      initProblemAnimation();
      initSolutionAnimation();
      initProductDemoAnimation();
      initFeaturesAnimation();
      initSocialProofAnimation();
      initPricingAnimation();
      initFAQAnimation();
      initFinalCTAAnimation();
    }, mainRef);

    return () => {
      // Clean up only this component's triggers
      triggersRef.current.forEach(st => st.kill());
      triggersRef.current = [];
      ctx.revert();
    };
  }, []);

  return mainRef;
}
```

## ScrollTrigger Configuration
```typescript
// Standard scroll trigger settings
const scrollTriggerDefaults = {
  start: "top 80%",
  end: "bottom 20%",
  toggleActions: "play none none reverse",
  // markers: process.env.NODE_ENV === "development",
};

// Parallax scroll trigger
const parallaxDefaults = {
  start: "top bottom",
  end: "bottom top",
  scrub: 1, // Smooth scrubbing
};
```

---

# SECTION-SPECIFIC ANIMATION SPECS

## 1. PRELOADER SEQUENCE

### Animation Flow
```
0ms     - Black screen
200ms   - Logo mark line drawing begins (SVG stroke animation)
800ms   - Logo fill completes
1000ms  - "RaptorFlow" text types in (character stagger)
1400ms  - Loading bar completes
1500ms  - Screen splits vertically, reveals content
1600ms  - Preloader destroyed
```

### GSAP Implementation
```typescript
const initPreloaderAnimation = () => {
  const tl = gsap.timeline();

  // Logo stroke draw
  tl.fromTo(".preloader-logo path",
    { strokeDashoffset: 1000 },
    { strokeDashoffset: 0, duration: 0.8, ease: "power2.inOut" }
  );

  // Logo fill
  tl.to(".preloader-logo",
    { fillOpacity: 1, duration: 0.3 },
    "-=0.2"
  );

  // Text reveal
  tl.fromTo(".preloader-text .char",
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.4, stagger: 0.03 },
    "-=0.1"
  );

  // Exit
  tl.to(".preloader", {
    clipPath: "inset(50% 0% 50% 0%)",
    duration: 0.6,
    ease: "power3.inOut"
  });
};
```

---

## 2. HERO SECTION — Cinematic Entrance

### Initial Load Sequence
```
0ms     - Background gradient orbs fade in (scale 0.8 → 1)
200ms   - Grid pattern draws in (SVG line animation)
400ms   - Badge slides up + fades in
600ms   - Headline words stagger in (y: 40 → 0, clip reveal)
900ms   - Subheadline fades in
1100ms  - CTA buttons slide up
1300ms  - Dashboard mockup 3D rotates in (rotateX: 15° → 0°)
1500ms  - Floating elements orbit in
```

### Scroll Effects
- **Dashboard mockup**: Parallax y: -50px to +100px
- **Floating elements**: Independent parallax at different speeds
- **Headline**: Fade out + slight blur on scroll
- **Background orbs**: Drift based on scroll position

### GSAP Implementation
```typescript
const initHeroAnimation = () => {
  const heroTl = gsap.timeline({ delay: 1.6 }); // After preloader

  // Background orbs
  heroTl.fromTo(".hero-orb",
    { scale: 0.8, opacity: 0 },
    { scale: 1, opacity: 1, duration: 1, stagger: 0.2 },
    0
  );

  // Badge
  heroTl.fromTo(".hero-badge",
    { y: 30, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.6 },
    0.4
  );

  // Headline word stagger
  heroTl.fromTo(".hero-headline .word",
    { y: 60, opacity: 0, rotateX: 20 },
    {
      y: 0,
      opacity: 1,
      rotateX: 0,
      duration: 0.8,
      stagger: 0.1,
      ease: "power3.out"
    },
    0.6
  );

  // Dashboard 3D entrance
  heroTl.fromTo(".hero-dashboard",
    {
      y: 100,
      opacity: 0,
      rotateX: 15,
      transformPerspective: 1000
    },
    {
      y: 0,
      opacity: 1,
      rotateX: 0,
      duration: 1.2,
      ease: "power2.out"
    },
    1.0
  );

  // ScrollTrigger for parallax
  const dashboardTrigger = ScrollTrigger.create({
    trigger: ".hero-section",
    start: "top top",
    end: "bottom top",
    scrub: 1,
    onUpdate: (self) => {
      gsap.set(".hero-dashboard", { y: self.progress * 100 });
      gsap.set(".hero-headline", {
        opacity: 1 - self.progress * 1.5,
        filter: `blur(${self.progress * 10}px)`
      });
    }
  });
  triggersRef.current.push(dashboardTrigger);
};
```

---

## 3. PROBLEM SECTION — Tension Build

### Entrance Sequence
```
0ms     - Section label slides in from left
200ms   - Problem statement words reveal (mask wipe)
500ms   - Pain point cards stagger in from bottom
800ms   - "Sound familiar?" text pulses
```

### Scroll Effects
- **Cards**: Slight rotation on scroll (±2°)
- **Icons**: Draw in on scroll (SVG stroke)

### GSAP Implementation
```typescript
const initProblemAnimation = () => {
  const trigger = ScrollTrigger.create({
    trigger: ".problem-section",
    start: "top 70%",
    onEnter: () => {
      const tl = gsap.timeline();

      // Label
      tl.fromTo(".problem-label",
        { x: -50, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.5 }
      );

      // Headline mask reveal
      tl.fromTo(".problem-headline .line",
        { clipPath: "inset(0 100% 0 0)" },
        {
          clipPath: "inset(0 0% 0 0)",
          duration: 0.8,
          stagger: 0.1,
          ease: "power3.inOut"
        },
        "-=0.2"
      );

      // Cards stagger
      tl.fromTo(".pain-card",
        { y: 60, opacity: 0, rotateY: -5 },
        {
          y: 0,
          opacity: 1,
          rotateY: 0,
          duration: 0.6,
          stagger: 0.15,
          ease: "power2.out"
        },
        "-=0.4"
      );
    },
    once: true
  });
  triggersRef.current.push(trigger);
};
```

---

## 4. SOLUTION SECTION — Reveal & Transform

### Entrance Sequence
```
0ms     - Transition gradient wipe from Problem section
300ms   - Solution headline splits and reassembles
600ms   - Feature list items cascade in
900ms   - Solution illustration morphs in
1200ms  - "Here's how it works" indicator pulses
```

### GSAP Implementation
```typescript
const initSolutionAnimation = () => {
  const trigger = ScrollTrigger.create({
    trigger: ".solution-section",
    start: "top 60%",
    onEnter: () => {
      const tl = gsap.timeline();

      // Split text animation
      tl.fromTo(".solution-headline .char",
        { opacity: 0, y: 50 },
        {
          opacity: 1,
          y: 0,
          duration: 0.5,
          stagger: 0.02,
          ease: "power3.out"
        }
      );

      // Feature cascade
      tl.fromTo(".solution-feature",
        { x: -30, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.5,
          stagger: 0.1
        },
        "-=0.3"
      );
    },
    once: true
  });
  triggersRef.current.push(trigger);
};
```

---

## 5. PRODUCT DEMO SECTION — Interactive Showcase

### Entrance Sequence
```
0ms     - Section header fades in
200ms   - Main product image slides in from right
500ms   - Feature hotspots pulse sequentially
800ms   - Interactive elements become clickable
```

### Interactive Behaviors
- **Hotspot hover**: Scale 1.2, tooltip fades in
- **Image hover**: Subtle 3D tilt (CSS perspective)
- **Scroll**: Product image parallax + zoom

### GSAP Implementation
```typescript
const initProductDemoAnimation = () => {
  // Main entrance
  const trigger = ScrollTrigger.create({
    trigger: ".product-demo-section",
    start: "top 70%",
    onEnter: () => {
      gsap.fromTo(".product-image",
        { x: 100, opacity: 0, scale: 0.95 },
        { x: 0, opacity: 1, scale: 1, duration: 1, ease: "power2.out" }
      );

      gsap.fromTo(".hotspot",
        { scale: 0 },
        { scale: 1, duration: 0.4, stagger: 0.2, ease: "back.out(1.5)", delay: 0.5 }
      );
    },
    once: true
  });
  triggersRef.current.push(trigger);

  // Parallax zoom
  const zoomTrigger = ScrollTrigger.create({
    trigger: ".product-demo-section",
    start: "top bottom",
    end: "bottom top",
    scrub: 1,
    onUpdate: (self) => {
      const scale = 1 + self.progress * 0.1;
      gsap.set(".product-image", { scale });
    }
  });
  triggersRef.current.push(zoomTrigger);
};
```

---

## 6. FEATURES GRID — Staggered Reveal

### Entrance Sequence
```
0ms     - Section header
200ms   - Grid items stagger in (diagonal wave pattern)
600ms   - Icons draw in (SVG stroke)
900ms   - Hover states activate
```

### Hover Effects
- **Card hover**: y: -8px, shadow increase, border color change
- **Icon**: Subtle rotation (5°)
- **Duration**: 200ms, ease: power1.out

### GSAP Implementation
```typescript
const initFeaturesAnimation = () => {
  const trigger = ScrollTrigger.create({
    trigger: ".features-section",
    start: "top 75%",
    onEnter: () => {
      // Diagonal stagger calculation
      const cards = gsap.utils.toArray<HTMLElement>(".feature-card");

      cards.forEach((card, i) => {
        const row = Math.floor(i / 3);
        const col = i % 3;
        const delay = (row + col) * 0.1;

        gsap.fromTo(card,
          { y: 60, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 0.6,
            delay,
            ease: "power2.out"
          }
        );
      });

      // Icon draw
      gsap.fromTo(".feature-icon path",
        { strokeDashoffset: 100 },
        {
          strokeDashoffset: 0,
          duration: 0.8,
          stagger: 0.1,
          delay: 0.4,
          ease: "power2.inOut"
        }
      );
    },
    once: true
  });
  triggersRef.current.push(trigger);
};
```

---

## 7. HOW IT WORKS — Step-by-Step Journey

### Entrance Sequence
```
0ms     - Timeline line draws down
300ms   - Step 1 node pulses, content fades in
800ms   - Connector line to step 2
1000ms  - Step 2 node pulses, content fades in
1500ms  - Connector line to step 3
1700ms  - Step 3 node pulses, content fades in
```

### Scroll Behavior
- **Pinned section**: Sticky timeline with content scrolling
- **Progress indicator**: Fill based on scroll position
- **Active step**: Scale up, opacity 1, others dimmed

### GSAP Implementation
```typescript
const initHowItWorksAnimation = () => {
  // Pinned timeline
  const trigger = ScrollTrigger.create({
    trigger: ".how-it-works-section",
    start: "top top",
    end: "+=200%",
    pin: true,
    scrub: 1,
    onUpdate: (self) => {
      const progress = self.progress;

      // Timeline draw
      gsap.set(".timeline-line", {
        scaleY: progress
      });

      // Step activation
      const steps = gsap.utils.toArray<HTMLElement>(".step");
      steps.forEach((step, i) => {
        const stepProgress = (progress - i * 0.3) / 0.3;
        const isActive = stepProgress > 0 && stepProgress <= 1;
        const isPast = stepProgress > 1;

        gsap.set(step, {
          opacity: isPast ? 0.3 : isActive ? 1 : 0.3,
          scale: isActive ? 1.05 : 1,
          filter: isActive ? "blur(0px)" : "blur(2px)"
        });
      });
    }
  });
  triggersRef.current.push(trigger);
};
```

---

## 8. TESTIMONIALS — Carousel Flow

### Entrance Sequence
```
0ms     - Section fades in
300ms   - Active testimonial slides in from right
500ms   - Quote marks animate (scale + opacity)
700ms   - Author info fades up
900ms   - Navigation appears
```

### Transition Effects
- **Slide change**: Current exits left (x: -50, opacity: 0), new enters from right
- **Duration**: 600ms with overlap
- **Quote marks**: Rotate 10° during transition

### GSAP Implementation
```typescript
const initTestimonialsAnimation = () => {
  const trigger = ScrollTrigger.create({
    trigger: ".testimonials-section",
    start: "top 70%",
    onEnter: () => {
      gsap.fromTo(".testimonial-card",
        { x: 100, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.8, ease: "power2.out" }
      );

      gsap.fromTo(".quote-mark",
        { scale: 0, rotation: -20 },
        { scale: 1, rotation: 0, duration: 0.5, delay: 0.3, ease: "back.out(2)" }
      );
    },
    once: true
  });
  triggersRef.current.push(trigger);
};

// Transition function
export const transitionTestimonial = (current: HTMLElement, next: HTMLElement) => {
  const tl = gsap.timeline();

  tl.to(current, {
    x: -100,
    opacity: 0,
    duration: 0.4,
    ease: "power2.in"
  });

  tl.fromTo(next,
    { x: 100, opacity: 0 },
    { x: 0, opacity: 1, duration: 0.4, ease: "power2.out" },
    "-=0.2"
  );
};
```

---

## 9. PRICING — Card Reveal

### Entrance Sequence
```
0ms     - Section header
200ms   - Toggle switch slides in
400ms   - Cards stagger in from bottom (center card first)
800ms   - Feature lists fade in
1000ms  - CTA buttons pulse once
```

### Toggle Animation
- **Switch**: 200ms slide with background color morph
- **Cards**: Cross-fade between monthly/annual prices
- **Badge**: Scale pop on recommended plan

### GSAP Implementation
```typescript
const initPricingAnimation = () => {
  const trigger = ScrollTrigger.create({
    trigger: ".pricing-section",
    start: "top 70%",
    onEnter: () => {
      const cards = gsap.utils.toArray<HTMLElement>(".pricing-card");
      const centerIndex = Math.floor(cards.length / 2);

      // Center card first, then outward
      const staggerOrder = cards.map((_, i) => {
        return Math.abs(i - centerIndex);
      });

      gsap.fromTo(cards,
        { y: 80, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.7,
          stagger: {
            each: 0.1,
            from: "center"
          },
          ease: "power2.out"
        }
      );
    },
    once: true
  });
  triggersRef.current.push(trigger);
};
```

---

## 10. FAQ — Accordion Dynamics

### Entrance Sequence
```
0ms     - Section header
200ms   - FAQ items stagger in
500ms   - First item hint (subtle bounce)
```

### Accordion Animation
- **Open**: Height 0 → auto (using gsap.to with height: "auto")
- **Icon**: Rotate 45° (plus to X)
- **Content**: Fade in + slide down 10px
- **Duration**: 300ms

### GSAP Implementation
```typescript
const initFAQAnimation = () => {
  const trigger = ScrollTrigger.create({
    trigger: ".faq-section",
    start: "top 75%",
    onEnter: () => {
      gsap.fromTo(".faq-item",
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          stagger: 0.08,
          ease: "power2.out"
        }
      );
    },
    once: true
  });
  triggersRef.current.push(trigger);
};

// Accordion toggle
export const toggleFAQ = (item: HTMLElement, isOpen: boolean) => {
  const content = item.querySelector(".faq-content");
  const icon = item.querySelector(".faq-icon");

  if (isOpen) {
    gsap.to(content, {
      height: "auto",
      opacity: 1,
      duration: 0.3,
      ease: "power2.out"
    });
    gsap.to(icon, { rotation: 45, duration: 0.3 });
  } else {
    gsap.to(content, {
      height: 0,
      opacity: 0,
      duration: 0.3,
      ease: "power2.in"
    });
    gsap.to(icon, { rotation: 0, duration: 0.3 });
  }
};
```

---

## 11. FINAL CTA — Crescendo

### Entrance Sequence
```
0ms     - Background gradient intensifies
300ms   - Headline words fly in from scattered positions
600ms   - Subtext fades up
800ms  - CTA button scales up with glow
1000ms  - Secondary elements (trust badges) cascade
```

### Persistent Effects
- **Background**: Animated gradient shift (subtle, continuous)
- **CTA button**: Gentle pulse glow every 4 seconds
- **Particles**: Floating elements drift slowly

### GSAP Implementation
```typescript
const initFinalCTAAnimation = () => {
  const trigger = ScrollTrigger.create({
    trigger: ".final-cta-section",
    start: "top 70%",
    onEnter: () => {
      const tl = gsap.timeline();

      // Scattered word assembly
      tl.fromTo(".cta-word",
        {
          x: () => gsap.utils.random(-200, 200),
          y: () => gsap.utils.random(-100, 100),
          opacity: 0,
          rotation: () => gsap.utils.random(-10, 10)
        },
        {
          x: 0,
          y: 0,
          opacity: 1,
          rotation: 0,
          duration: 0.8,
          stagger: 0.1,
          ease: "power3.out"
        }
      );

      // CTA emergence
      tl.fromTo(".cta-button",
        { scale: 0.8, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.5)" },
        "-=0.3"
      );

      // Continuous pulse
      gsap.to(".cta-button", {
        boxShadow: "0 0 40px rgba(58, 90, 124, 0.4)",
        duration: 1,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 2
      });
    },
    once: true
  });
  triggersRef.current.push(trigger);
};
```

---

# MICRO-INTERACTION LIBRARY

## Magnetic Button Effect
```typescript
export const useMagneticEffect = (ref: React.RefObject<HTMLElement>) => {
  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleMove = (e: MouseEvent) => {
      const rect = element.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      gsap.to(element, {
        x: x * 0.3,
        y: y * 0.3,
        duration: 0.3,
        ease: "power2.out"
      });
    };

    const handleLeave = () => {
      gsap.to(element, {
        x: 0,
        y: 0,
        duration: 0.5,
        ease: "elastic.out(1, 0.5)"
      });
    };

    element.addEventListener("mousemove", handleMove);
    element.addEventListener("mouseleave", handleLeave);

    return () => {
      element.removeEventListener("mousemove", handleMove);
      element.removeEventListener("mouseleave", handleLeave);
    };
  }, [ref]);
};
```

## Text Scramble Effect
```typescript
export const scrambleText = (element: HTMLElement, finalText: string) => {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  let iteration = 0;

  const interval = setInterval(() => {
    element.innerText = finalText
      .split("")
      .map((char, i) => {
        if (i < iteration) return finalText[i];
        return chars[Math.floor(Math.random() * chars.length)];
      })
      .join("");

    if (iteration >= finalText.length) clearInterval(interval);
    iteration += 1 / 3;
  }, 30);
};
```

## Scroll Velocity Skew
```typescript
export const useVelocitySkew = () => {
  let lastScroll = 0;
  let velocity = 0;

  useEffect(() => {
    const handleScroll = () => {
      const currentScroll = window.scrollY;
      velocity = (currentScroll - lastScroll) * 0.1;
      lastScroll = currentScroll;

      // Clamp velocity
      velocity = Math.max(-5, Math.min(5, velocity));

      gsap.to(".velocity-skew", {
        skewY: velocity,
        duration: 0.3,
        ease: "power2.out"
      });
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);
};
```

---

# PERFORMANCE OPTIMIZATION

## 1. Will-Change Strategy
```css
/* Apply only during animation */
.animating {
  will-change: transform, opacity;
}

/* Remove after animation completes */
.animation-complete {
  will-change: auto;
}
```

## 2. GPU Acceleration
```typescript
// Force GPU layer for animated elements
gsap.set(".animated-element", {
  force3D: true
});
```

## 3. Intersection Observer for Triggers
```typescript
// Only create ScrollTriggers when visible
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      createScrollTrigger(entry.target);
      observer.unobserve(entry.target);
    }
  });
}, { rootMargin: "100px" });
```

## 4. Debounced Resize
```typescript
import { debounce } from "lodash";

const handleResize = debounce(() => {
  ScrollTrigger.refresh();
}, 200);

window.addEventListener("resize", handleResize);
```

## 5. Cleanup on Unmount
```typescript
useEffect(() => {
  const ctx = gsap.context(() => {
    // All animations
  });

  return () => {
    ctx.revert(); // Kills all animations and ScrollTriggers in this context
  };
}, []);
```

---

# ACCESSIBILITY CONSIDERATIONS

## Reduced Motion Support
```typescript
const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
).matches;

if (prefersReducedMotion) {
  // Disable complex animations
  gsap.globalTimeline.timeScale(0);

  // Or use simple fades only
  document.querySelectorAll(".animated").forEach(el => {
    el.style.opacity = "1";
    el.style.transform = "none";
  });
}
```

## Focus States
```typescript
// Ensure focusable elements remain accessible
gsap.set(".focusable", {
  visibility: "visible"
});
```

## Screen Reader Announcements
```typescript
// Announce section changes
const announceSection = (sectionName: string) => {
  const announcer = document.getElementById("sr-announcer");
  if (announcer) {
    announcer.textContent = `Now viewing ${sectionName} section`;
  }
};
```

---

# ANIMATION TIMING CHEAT SHEET

| Element | Duration | Delay | Easing |
|---------|----------|-------|--------|
| Button hover | 150ms | 0 | power1.out |
| Card hover | 200ms | 0 | power2.out |
| Page section entrance | 600ms | stagger 100ms | power3.out |
| Hero elements | 800ms | stagger 200ms | power3.out |
| Modal open | 300ms | 0 | power2.out |
| Modal close | 200ms | 0 | power2.in |
| Accordion open | 300ms | 0 | power2.out |
| Accordion close | 250ms | 0 | power2.in |
| Tooltip show | 150ms | 0 | power1.out |
| Toast notification | 400ms | 0 | power2.out |
| Loading spinner | Continuous | - | Linear |
| Scroll parallax | Continuous | - | Linear |
| Background drift | 20s loop | - | Sine |

---

*Document Version: 1.0*
*Motion System: Mechanical Precision + Editorial Authority*
*Primary Library: GSAP 3.x with ScrollTrigger*
