import posthog from 'posthog-js';

const posthogKey = import.meta.env.VITE_POSTHOG_KEY;
const posthogHost = import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com';
const environment = import.meta.env.VITE_ENVIRONMENT || 'development';

// Initialize PostHog
export const initPostHog = () => {
  if (!posthogKey) {
    console.warn('PostHog key not found. Analytics will be disabled.');
    return null;
  }

  // Only initialize in browser environment
  if (typeof window !== 'undefined') {
    posthog.init(posthogKey, {
      api_host: posthogHost,

      // Privacy and compliance
      opt_out_capturing_by_default: false,
      respect_dnt: true,

      // Session recording
      disable_session_recording: environment === 'development',

      // Autocapture
      autocapture: true,
      capture_pageview: true,
      capture_pageleave: true,

      // Performance
      loaded: (posthog) => {
        if (environment === 'development') {
          posthog.debug();
        }
      },

      // Cookie configuration
      persistence: 'localStorage+cookie',
      cookie_expiration: 365,

      // Custom properties
      property_blacklist: ['password', 'token', 'api_key'],
    });

    // Set environment as a super property
    posthog.register({
      environment,
      app_version: '1.0.0',
    });
  }

  return posthog;
};

// Analytics helper functions
export const analytics = {
  // Track page views
  trackPageView: (pageName: string, properties?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.capture('$pageview', {
        page_name: pageName,
        ...properties,
      });
    }
  },

  // Track custom events
  trackEvent: (eventName: string, properties?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.capture(eventName, properties);
    }
  },

  // Track campaign actions
  trackCampaignAction: (action: string, campaignId: string, properties?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.capture('campaign_action', {
        action,
        campaign_id: campaignId,
        ...properties,
      });
    }
  },

  // Track OODA loop iterations
  trackOODAIteration: (loopId: string, phase: 'observe' | 'orient' | 'decide' | 'act', properties?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.capture('ooda_iteration', {
        loop_id: loopId,
        phase,
        ...properties,
      });
    }
  },

  // Track maneuver selection
  trackManeuverSelection: (maneuverId: string, maneuverName: string, properties?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.capture('maneuver_selected', {
        maneuver_id: maneuverId,
        maneuver_name: maneuverName,
        ...properties,
      });
    }
  },

  // Track capability unlock
  trackCapabilityUnlock: (capabilityId: string, capabilityName: string, properties?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.capture('capability_unlocked', {
        capability_id: capabilityId,
        capability_name: capabilityName,
        ...properties,
      });
    }
  },

  // Identify user
  identify: (userId: string, properties?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.identify(userId, properties);
    }
  },

  // Reset identity (on logout)
  reset: () => {
    if (posthog.__loaded) {
      posthog.reset();
    }
  },

  // Set user properties
  setUserProperties: (properties: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.people.set(properties);
    }
  },

  // Track feature flags
  isFeatureEnabled: (flagKey: string): boolean => {
    if (posthog.__loaded) {
      return posthog.isFeatureEnabled(flagKey) || false;
    }
    return false;
  },

  // Track errors
  trackError: (error: Error, context?: Record<string, any>) => {
    if (posthog.__loaded) {
      posthog.capture('error', {
        error_message: error.message,
        error_stack: error.stack,
        ...context,
      });
    }
  },
};

export default posthog;
