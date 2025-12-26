"use client";

// Advanced Animation Engine for 10x Typing Experience
export interface AnimationProfile {
  name: string;
  keyframes: Keyframe[];
  duration: number;
  easing: string;
  properties: string[];
}

export interface AnimationConfig {
  enabled: boolean;
  profile: string;
  speed: number;
  intensity: 'subtle' | 'normal' | 'pronounced';
  accessibilityMode: boolean;
}

export class AnimationEngine {
  private config: AnimationConfig;
  private animationProfiles: Map<string, AnimationProfile> = new Map();
  private activeAnimations: Set<Animation> = new Set();
  private performanceMonitor: PerformanceMonitor;

  constructor(config: AnimationConfig) {
    this.config = config;
    this.performanceMonitor = new PerformanceMonitor();
    this.initializeProfiles();
  }

  private initializeProfiles(): void {
    // Subtle Profile - Minimal, elegant animations
    this.animationProfiles.set('subtle', {
      name: 'subtle',
      keyframes: [
        { transform: 'scale(1)', boxShadow: 'none' },
        { transform: 'scale(1.01)', boxShadow: '0 0 0 1px rgba(0,0,0,0.05)' },
        { transform: 'scale(1)', boxShadow: 'none' }
      ],
      duration: 60,
      easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      properties: ['transform', 'box-shadow']
    });
    // Luxury Profile - Microscopic, elegant transitions (NO SCALE)
    this.animationProfiles.set('luxury', {
      name: 'luxury',
      keyframes: [
        { borderColor: 'var(--border)', boxShadow: 'none' },
        { borderColor: 'var(--accent)', boxShadow: '0 0 0 2px rgba(215, 201, 174, 0.1)' },
        { borderColor: 'var(--border)', boxShadow: 'none' }
      ],
      duration: 80,
      easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
      properties: ['border-color', 'box-shadow']
    });

    // Professional Profile - Clean, purposeful animations
    this.animationProfiles.set('professional', {
      name: 'professional',
      keyframes: [
        { transform: 'scale(1)', borderColor: 'rgba(0,0,0,0.08)' },
        { transform: 'scale(1.02)', borderColor: 'rgba(0,0,0,0.12)' },
        { transform: 'scale(1)', borderColor: 'rgba(0,0,0,0.08)' }
      ],
      duration: 80,
      easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
      properties: ['transform', 'border-color']
    });

    // Creative Profile - Expressive, fluid animations
    this.animationProfiles.set('creative', {
      name: 'creative',
      keyframes: [
        { transform: 'scale(1) rotate(0deg)', filter: 'brightness(1)' },
        { transform: 'scale(1.03) rotate(1deg)', filter: 'brightness(1.1)' },
        { transform: 'scale(1) rotate(0deg)', filter: 'brightness(1)' }
      ],
      duration: 120,
      easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      properties: ['transform', 'filter']
    });

    // Gaming Profile - Responsive, dynamic animations
    this.animationProfiles.set('gaming', {
      name: 'gaming',
      keyframes: [
        { transform: 'scale(1)', boxShadow: '0 0 0 rgba(59, 130, 246, 0)' },
        { transform: 'scale(1.05)', boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)' },
        { transform: 'scale(1)', boxShadow: '0 0 0 rgba(59, 130, 246, 0)' }
      ],
      duration: 100,
      easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      properties: ['transform', 'box-shadow']
    });
  }

  animateElement(element: HTMLElement, context: {
    type: 'typing' | 'click' | 'focus' | 'completion';
    velocity?: number;
    position?: { x: number; y: number };
  }): void {
    if (!this.config.enabled || this.config.accessibilityMode) return;

    const profile = this.animationProfiles.get(this.config.profile);
    if (!profile) return;

    // Cancel existing animation on this element
    this.cancelAnimation(element);

    // Apply context-specific modifications
    const modifiedProfile = this.modifyProfileForContext(profile, context);

    // Create and run animation
    const animation = element.animate(modifiedProfile.keyframes, {
      duration: modifiedProfile.duration * (this.config.speed / 100),
      easing: modifiedProfile.easing,
      fill: 'forwards'
    });

    this.activeAnimations.add(animation);

    // Cleanup
    animation.onfinish = () => {
      this.activeAnimations.delete(animation);
    };

    // Performance monitoring
    this.performanceMonitor.recordAnimation(context.type, modifiedProfile.duration);
  }

  private modifyProfileForContext(profile: AnimationProfile, context: {
    type: 'typing' | 'click' | 'focus' | 'completion';
    velocity?: number;
    position?: { x: number; y: number };
  }): AnimationProfile {
    const modified = { ...profile };

    // Adjust based on velocity
    if (context.velocity) {
      modified.duration = profile.duration * (2 - context.velocity);
    }

    // Adjust based on intensity
    switch (this.config.intensity) {
      case 'subtle':
        modified.duration *= 0.7;
        break;
      case 'pronounced':
        modified.duration *= 1.3;
        break;
    }

    // Special handling for different contexts
    switch (context.type) {
      case 'completion':
        modified.duration *= 1.5; // Longer animation for completion
        break;
      case 'click':
        modified.duration *= 0.8; // Quicker for clicks
        break;
    }

    return modified;
  }

  createRippleEffect(element: HTMLElement, x: number, y: number): void {
    if (!this.config.enabled) return;

    const ripple = document.createElement('div');
    ripple.style.position = 'absolute';
    ripple.style.width = '20px';
    ripple.style.height = '20px';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(0, 0, 0, 0.1)';
    ripple.style.transform = 'translate(-50%, -50%)';
    ripple.style.pointerEvents = 'none';
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;

    element.style.position = 'relative';
    element.appendChild(ripple);

    const animation = ripple.animate([
      { transform: 'translate(-50%, -50%) scale(0)', opacity: 1 },
      { transform: 'translate(-50%, -50%) scale(4)', opacity: 0 }
    ], {
      duration: 600,
      easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    });

    animation.onfinish = () => {
      ripple.remove();
    };
  }

  createParticleEffect(element: HTMLElement, count: number = 5): void {
    if (!this.config.enabled || this.config.intensity === 'subtle') return;

    const rect = element.getBoundingClientRect();

    for (let i = 0; i < count; i++) {
      const particle = document.createElement('div');
      particle.style.position = 'fixed';
      particle.style.width = '4px';
      particle.style.height = '4px';
      particle.style.borderRadius = '50%';
      particle.style.background = 'rgba(59, 130, 246, 0.6)';
      particle.style.pointerEvents = 'none';
      particle.style.left = `${rect.left + rect.width / 2}px`;
      particle.style.top = `${rect.top + rect.height / 2}px`;
      particle.style.zIndex = '9999';

      document.body.appendChild(particle);

      const angle = (Math.PI * 2 * i) / count;
      const distance = 30 + Math.random() * 20;
      const endX = Math.cos(angle) * distance;
      const endY = Math.sin(angle) * distance;

      const animation = particle.animate([
        {
          transform: 'translate(0, 0) scale(1)',
          opacity: 1
        },
        {
          transform: `translate(${endX}px, ${endY}px) scale(0)`,
          opacity: 0
        }
      ], {
        duration: 400,
        easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
      });

      animation.onfinish = () => {
        particle.remove();
      };
    }
  }

  cancelAnimation(element: HTMLElement): void {
    const animations = element.getAnimations();
    animations.forEach(animation => {
      animation.cancel();
      this.activeAnimations.delete(animation);
    });
  }

  updateConfig(newConfig: Partial<AnimationConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  getAvailableProfiles(): string[] {
    return Array.from(this.animationProfiles.keys());
  }

  getPerformanceMetrics(): PerformanceMetrics {
    return this.performanceMonitor.getMetrics();
  }

  cleanup(): void {
    this.activeAnimations.forEach(animation => animation.cancel());
    this.activeAnimations.clear();
  }
}

// Performance monitoring for animations
class PerformanceMonitor {
  private animationCounts: Map<string, number> = new Map();
  private totalDurations: Map<string, number> = new Map();

  recordAnimation(type: string, duration: number): void {
    const current = this.animationCounts.get(type) || 0;
    this.animationCounts.set(type, current + 1);

    const totalDuration = this.totalDurations.get(type) || 0;
    this.totalDurations.set(type, totalDuration + duration);
  }

  getMetrics(): PerformanceMetrics {
    return {
      animationCounts: Object.fromEntries(this.animationCounts),
      averageDurations: Object.fromEntries(
        Array.from(this.totalDurations.entries()).map(([type, total]) => [
          type,
          total / (this.animationCounts.get(type) || 1)
        ])
      )
    };
  }
}

interface PerformanceMetrics {
  animationCounts: Record<string, number>;
  averageDurations: Record<string, number>;
}
