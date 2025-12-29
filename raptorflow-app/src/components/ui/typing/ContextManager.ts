'use client';

// Intelligent Context Manager for 10x Typing Experience
export interface TypingContext {
  inputType:
    | 'text'
    | 'password'
    | 'email'
    | 'textarea'
    | 'search'
    | 'number'
    | 'rich-text';
  application:
    | 'coding'
    | 'writing'
    | 'messaging'
    | 'form'
    | 'search'
    | 'creative';
  environment: 'office' | 'home' | 'mobile' | 'public';
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
  userState: 'focused' | 'distracted' | 'tired' | 'energetic';
  taskComplexity: 'simple' | 'moderate' | 'complex';
}

export interface ContextualSettings {
  soundProfile: string;
  animationProfile: string;
  volume: number;
  intensity: 'subtle' | 'normal' | 'pronounced';
  features: {
    completionSounds: boolean;
    particleEffects: boolean;
    rippleEffects: boolean;
    adaptiveVolume: boolean;
  };
}

export class ContextManager {
  private currentContext: TypingContext;
  private contextHistory: TypingContext[] = [];
  private adaptationRules: Map<string, Partial<ContextualSettings>> = new Map();
  private userPreferences: ContextualSettings;
  private typingMetrics: TypingMetrics;

  constructor(initialPreferences: ContextualSettings) {
    this.userPreferences = initialPreferences;
    this.typingMetrics = new TypingMetrics();
    this.currentContext = this.detectInitialContext();
    this.initializeAdaptationRules();
  }

  private detectInitialContext(): TypingContext {
    const hour = new Date().getHours();
    const timeOfDay =
      hour < 12
        ? 'morning'
        : hour < 17
          ? 'afternoon'
          : hour < 21
            ? 'evening'
            : 'night';

    return {
      inputType: 'text',
      application: 'writing',
      environment: 'home',
      timeOfDay,
      userState: 'focused',
      taskComplexity: 'moderate',
    };
  }

  private initializeAdaptationRules(): void {
    // Time-based adaptations
    this.adaptationRules.set('morning', {
      soundProfile: 'luxury',
      intensity: 'subtle',
      volume: 0.2,
    });

    this.adaptationRules.set('night', {
      soundProfile: 'luxury',
      intensity: 'subtle',
      volume: 0.05,
      features: {
        completionSounds: false,
        particleEffects: false,
        rippleEffects: false,
        adaptiveVolume: false,
      },
    });

    // Environment-based adaptations
    this.adaptationRules.set('office', {
      soundProfile: 'luxury',
      intensity: 'subtle',
      volume: 0.15,
      features: {
        completionSounds: true,
        particleEffects: false,
        rippleEffects: false,
        adaptiveVolume: true,
      },
    });

    this.adaptationRules.set('public', {
      soundProfile: 'luxury',
      intensity: 'subtle',
      volume: 0.05,
      features: {
        completionSounds: false,
        particleEffects: false,
        rippleEffects: false,
        adaptiveVolume: false,
      },
    });

    // Application-based adaptations
    this.adaptationRules.set('coding', {
      soundProfile: 'gaming',
      intensity: 'normal',
      features: {
        completionSounds: true,
        particleEffects: false,
        rippleEffects: false,
        adaptiveVolume: true,
      },
    });

    this.adaptationRules.set('creative', {
      soundProfile: 'creative',
      intensity: 'pronounced',
      features: {
        completionSounds: true,
        particleEffects: true,
        rippleEffects: true,
        adaptiveVolume: true,
      },
    });

    // User state adaptations
    this.adaptationRules.set('tired', {
      soundProfile: 'minimalist',
      intensity: 'subtle',
      volume: 0.2,
    });

    this.adaptationRules.set('energetic', {
      soundProfile: 'gaming',
      intensity: 'pronounced',
      volume: 0.5,
    });
  }

  updateContext(
    element: HTMLElement,
    event: KeyboardEvent | MouseEvent
  ): TypingContext {
    const newContext = this.analyzeContext(element, event);

    // Detect user state from typing patterns
    if (event instanceof KeyboardEvent) {
      this.typingMetrics.recordKeystroke(event);
      newContext.userState = this.typingMetrics.detectUserState();
    }

    this.contextHistory.push(this.currentContext);
    if (this.contextHistory.length > 100) {
      this.contextHistory.shift();
    }

    this.currentContext = newContext;
    return newContext;
  }

  private analyzeContext(
    element: HTMLElement,
    event: KeyboardEvent | MouseEvent
  ): TypingContext {
    const context = { ...this.currentContext };

    // Detect input type
    if (element instanceof HTMLInputElement) {
      context.inputType = this.mapInputType(element.type);
    } else if (element instanceof HTMLTextAreaElement) {
      context.inputType = 'textarea';
    } else if (element.isContentEditable) {
      context.inputType = 'rich-text';
    }

    // Detect application context
    context.application = this.detectApplication(element);

    // Detect environment
    context.environment = this.detectEnvironment();

    // Update time of day
    const hour = new Date().getHours();
    context.timeOfDay =
      hour < 12
        ? 'morning'
        : hour < 17
          ? 'afternoon'
          : hour < 21
            ? 'evening'
            : 'night';

    // Detect task complexity
    context.taskComplexity = this.detectTaskComplexity(element);

    return context;
  }

  private mapInputType(type: string): TypingContext['inputType'] {
    const typeMap: Record<string, TypingContext['inputType']> = {
      text: 'text',
      password: 'password',
      email: 'email',
      search: 'search',
      number: 'number',
    };
    return typeMap[type] || 'text';
  }

  private detectApplication(
    element: HTMLElement
  ): TypingContext['application'] {
    // Check for coding environments
    if (
      element.closest(
        '.code-editor, .monaco-editor, .ace_editor, [data-language]'
      )
    ) {
      return 'coding';
    }

    // Check for creative applications
    if (element.closest('.design-tool, .canvas, .creative-editor')) {
      return 'creative';
    }

    // Check for messaging
    if (element.closest('.chat, .messenger, .slack, .teams')) {
      return 'messaging';
    }

    // Check for forms
    if (element.closest('form, .form, .signup, .login')) {
      return 'form';
    }

    // Check for search
    if (element.closest('.search, [role="search"], input[type="search"]')) {
      return 'search';
    }

    return 'writing';
  }

  private detectEnvironment(): TypingContext['environment'] {
    // Mobile detection
    if (/Mobi|Android/i.test(navigator.userAgent)) {
      return 'mobile';
    }

    // Public space detection (based on time and browser patterns)
    const hour = new Date().getHours();
    if (
      hour >= 9 &&
      hour <= 17 &&
      !window.location.hostname.includes('localhost')
    ) {
      return 'office';
    }

    return 'home';
  }

  private detectTaskComplexity(
    element: HTMLElement
  ): TypingContext['taskComplexity'] {
    // Complex tasks
    if (element.closest('.complex-form, .wizard, .multi-step')) {
      return 'complex';
    }

    // Simple tasks
    if (element.closest('.quick-action, .simple-input, .shortcut')) {
      return 'simple';
    }

    return 'moderate';
  }

  getAdaptedSettings(): ContextualSettings {
    const settings = { ...this.userPreferences };

    // Apply adaptation rules based on current context
    const contextKeys = [
      this.currentContext.timeOfDay,
      this.currentContext.environment,
      this.currentContext.application,
      this.currentContext.userState,
    ];

    contextKeys.forEach((key) => {
      const adaptations = this.adaptationRules.get(key);
      if (adaptations) {
        Object.assign(settings, adaptations);
        if (adaptations.features) {
          settings.features = { ...settings.features, ...adaptations.features };
        }
      }
    });

    return settings;
  }

  recordUserFeedback(feedback: {
    soundSatisfaction: number; // 1-10
    animationSatisfaction: number; // 1-10
    overallExperience: number; // 1-10
  }): void {
    // Learn from user feedback and adjust preferences
    if (feedback.soundSatisfaction < 5) {
      this.userPreferences.volume *= 0.9;
      this.userPreferences.intensity = 'subtle';
    } else if (feedback.soundSatisfaction > 8) {
      this.userPreferences.intensity = 'normal';
    }

    // Store feedback for learning algorithms
    this.storeFeedbackData(feedback);
  }

  private storeFeedbackData(feedback: any): void {
    // In a real implementation, this would store to a database
    // For now, store in localStorage
    const feedbackHistory = JSON.parse(
      localStorage.getItem('typing-feedback') || '[]'
    );
    feedbackHistory.push({
      ...feedback,
      context: this.currentContext,
      timestamp: Date.now(),
    });
    localStorage.setItem(
      'typing-feedback',
      JSON.stringify(feedbackHistory.slice(-100))
    );
  }

  getContextInsights(): {
    dominantContexts: Record<string, number>;
    peakProductivityTimes: string[];
    preferredProfiles: Record<string, string>;
  } {
    const insights = {
      dominantContexts: {} as Record<string, number>,
      peakProductivityTimes: [] as string[],
      preferredProfiles: {} as Record<string, string>,
    };

    // Analyze context history
    this.contextHistory.forEach((context) => {
      const key = `${context.application}-${context.environment}`;
      insights.dominantContexts[key] =
        (insights.dominantContexts[key] || 0) + 1;
    });

    return insights;
  }

  getCurrentContext(): TypingContext {
    return this.currentContext;
  }

  getTypingMetrics(): { speed: number; accuracy: number; consistency: number } {
    return this.typingMetrics.getMetrics();
  }

  updateUserPreferences(preferences: Partial<ContextualSettings>): void {
    this.userPreferences = { ...this.userPreferences, ...preferences };
  }
}

// Typing metrics for user state detection
class TypingMetrics {
  private keystrokes: Array<{
    timestamp: number;
    key: string;
    velocity: number;
  }> = [];
  private typingSpeeds: number[] = [];
  private errorRate = 0;

  recordKeystroke(event: KeyboardEvent): void {
    const now = Date.now();
    const velocity = this.calculateVelocity(event);

    this.keystrokes.push({ timestamp: now, key: event.key, velocity });

    // Keep only recent keystrokes
    if (this.keystrokes.length > 1000) {
      this.keystrokes.shift();
    }

    // Calculate typing speed
    this.updateTypingSpeed();
  }

  private calculateVelocity(event: KeyboardEvent): number {
    // Simple velocity calculation based on key characteristics
    if (event.key === 'Backspace' || event.key === 'Delete') return 0.5;
    if (event.key.length === 1) return 1;
    return 0.8;
  }

  private updateTypingSpeed(): void {
    if (this.keystrokes.length < 10) return;

    const recent = this.keystrokes.slice(-50);
    const timeSpan = recent[recent.length - 1].timestamp - recent[0].timestamp;

    if (timeSpan > 0) {
      const speed = (recent.length / timeSpan) * 1000 * 60; // keystrokes per minute
      this.typingSpeeds.push(speed);

      if (this.typingSpeeds.length > 20) {
        this.typingSpeeds.shift();
      }
    }
  }

  detectUserState(): TypingContext['userState'] {
    if (this.typingSpeeds.length < 5) return 'focused';

    const avgSpeed =
      this.typingSpeeds.reduce((a, b) => a + b, 0) / this.typingSpeeds.length;

    if (avgSpeed > 80) return 'energetic';
    if (avgSpeed < 30) return 'tired';
    if (this.errorRate > 0.1) return 'distracted';

    return 'focused';
  }

  getMetrics(): { speed: number; accuracy: number; consistency: number } {
    const speed =
      this.typingSpeeds.length > 0
        ? this.typingSpeeds.reduce((a, b) => a + b, 0) /
          this.typingSpeeds.length
        : 0;

    return {
      speed,
      accuracy: 1 - this.errorRate,
      consistency: this.calculateConsistency(),
    };
  }

  private calculateConsistency(): number {
    if (this.typingSpeeds.length < 10) return 1;

    const mean =
      this.typingSpeeds.reduce((a, b) => a + b, 0) / this.typingSpeeds.length;
    const variance =
      this.typingSpeeds.reduce(
        (sum, speed) => sum + Math.pow(speed - mean, 2),
        0
      ) / this.typingSpeeds.length;
    const standardDeviation = Math.sqrt(variance);

    // Consistency is inverse of coefficient of variation
    return mean > 0 ? 1 - standardDeviation / mean : 0;
  }
}
