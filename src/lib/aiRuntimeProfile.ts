export type AIIntensity = "low" | "medium" | "high";
export type AIExecutionMode = "single" | "council" | "swarm";

export type AIRuntimeProfile = {
  intensity: AIIntensity;
  executionMode: AIExecutionMode;
};

const STORAGE_KEY = "raptorflow.ai_runtime_profile";

const DEFAULT_PROFILE: AIRuntimeProfile = {
  intensity: "medium",
  executionMode: "council",
};

function normalizeIntensity(value: unknown): AIIntensity {
  if (value === "low" || value === "medium" || value === "high") {
    return value;
  }
  return DEFAULT_PROFILE.intensity;
}

function normalizeExecutionMode(value: unknown): AIExecutionMode {
  if (value === "single" || value === "council" || value === "swarm") {
    return value;
  }
  return DEFAULT_PROFILE.executionMode;
}

export function getDefaultRuntimeProfile(): AIRuntimeProfile {
  return { ...DEFAULT_PROFILE };
}

export function readRuntimeProfile(): AIRuntimeProfile {
  if (typeof window === "undefined") return getDefaultRuntimeProfile();
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return getDefaultRuntimeProfile();
    const parsed = JSON.parse(raw) as Partial<AIRuntimeProfile>;
    return {
      intensity: normalizeIntensity(parsed.intensity),
      executionMode: normalizeExecutionMode(parsed.executionMode),
    };
  } catch {
    return getDefaultRuntimeProfile();
  }
}

export function writeRuntimeProfile(profile: Partial<AIRuntimeProfile>): AIRuntimeProfile {
  const next: AIRuntimeProfile = {
    intensity: normalizeIntensity(profile.intensity),
    executionMode: normalizeExecutionMode(profile.executionMode),
  };
  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // noop
    }
  }
  return next;
}
