import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { getInferenceConfig, isInferenceReady } from "../inference-config";

describe("Inference Configuration", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it("should return ready=false when INFERENCE_SIMPLE is missing", () => {
    delete process.env.INFERENCE_SIMPLE;
    delete process.env.NEXT_PUBLIC_INFERENCE_SIMPLE;

    expect(isInferenceReady()).toBe(false);
  });

  it("should load configuration from INFERENCE_SIMPLE", () => {
    process.env.INFERENCE_SIMPLE = "test-api-key";

    const config = getInferenceConfig();
    expect(config.apiKey).toBe("test-api-key");
    expect(isInferenceReady()).toBe(true);
  });

  it("should load configuration from NEXT_PUBLIC_INFERENCE_SIMPLE as fallback", () => {
    delete process.env.INFERENCE_SIMPLE;
    process.env.NEXT_PUBLIC_INFERENCE_SIMPLE = "public-test-key";

    const config = getInferenceConfig();
    expect(config.apiKey).toBe("public-test-key");
    expect(isInferenceReady()).toBe(true);
  });
});
