import posthog from 'posthog-js';

const posthogKey = import.meta.env.VITE_POSTHOG_KEY;
const posthogHost = import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com';
const environment = import.meta.env.VITE_ENVIRONMENT || 'development';

// Track initialization state
let isInitialized = false;

// Helper function to check if PostHog is ready
const isPostHogReady = (): boolean => {
  return isInitialized && typeof window !== 'undefined' && posthogKey && typeof posthog !== 'undefined';
};

// Initialize PostHog
export const initPostHog = () => {
  if (!posthogKey) {
    console.warn('PostHog key not found. Analytics will be disabled.');
    return null;
  }

  // Only initialize in browser environment
  if (typeof window !== 'undefined') {
    try {
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
          isInitialized = true;
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
    } catch (error) {
      console.error('Failed to initialize PostHog:', error);
    }
  }

  return posthog;
};

// Analytics helper functions
export const analytics = {
  // Track page views
  trackPageView: (pageName: string, properties?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.capture('$pageview', {
          page_name: pageName,
          ...properties,
        });
      } catch (error) {
        console.error('PostHog trackPageView error:', error);
      }
    }
  },

  // Track custom events
  trackEvent: (eventName: string, properties?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.capture(eventName, properties);
      } catch (error) {
        console.error('PostHog trackEvent error:', error);
      }
    }
  },

  // Track campaign actions
  trackCampaignAction: (action: string, campaignId: string, properties?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.capture('campaign_action', {
          action,
          campaign_id: campaignId,
          ...properties,
        });
      } catch (error) {
        console.error('PostHog trackCampaignAction error:', error);
      }
    }
  },

  // Track OODA loop iterations
  trackOODAIteration: (loopId: string, phase: 'observe' | 'orient' | 'decide' | 'act', properties?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.capture('ooda_iteration', {
          loop_id: loopId,
          phase,
          ...properties,
        });
      } catch (error) {
        console.error('PostHog trackOODAIteration error:', error);
      }
    }
  },

  // Track maneuver selection
  trackManeuverSelection: (maneuverId: string, maneuverName: string, properties?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.capture('maneuver_selected', {
          maneuver_id: maneuverId,
          maneuver_name: maneuverName,
          ...properties,
        });
      } catch (error) {
        console.error('PostHog trackManeuverSelection error:', error);
      }
    }
  },

  // Track capability unlock
  trackCapabilityUnlock: (capabilityId: string, capabilityName: string, properties?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.capture('capability_unlocked', {
          capability_id: capabilityId,
          capability_name: capabilityName,
          ...properties,
        });
      } catch (error) {
        console.error('PostHog trackCapabilityUnlock error:', error);
      }
    }
  },

  // Identify user
  identify: (userId: string, properties?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.identify(userId, properties);
      } catch (error) {
        console.error('PostHog identify error:', error);
      }
    }
  },

  // Reset identity (on logout)
  reset: () => {
    if (isPostHogReady()) {
      try {
        posthog.reset();
      } catch (error) {
        console.error('PostHog reset error:', error);
      }
    }
  },

  // Set user properties
  setUserProperties: (properties: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.people.set(properties);
      } catch (error) {
        console.error('PostHog setUserProperties error:', error);
      }
    }
  },

  // Track feature flags
  isFeatureEnabled: (flagKey: string): boolean => {
    if (isPostHogReady()) {
      try {
        return posthog.isFeatureEnabled(flagKey) || false;
      } catch (error) {
        console.error('PostHog isFeatureEnabled error:', error);
        return false;
      }
    }
    return false;
  },

  // Track errors
  trackError: (error: Error, context?: Record<string, any>) => {
    if (isPostHogReady()) {
      try {
        posthog.capture('error', {
          error_message: error.message,
          error_stack: error.stack,
          ...context,
        });
      } catch (err) {
        console.error('PostHog trackError error:', err);
      }
    }
  },
};

export default posthog;
