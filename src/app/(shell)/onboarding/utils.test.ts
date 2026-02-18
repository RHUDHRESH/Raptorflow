import { describe, expect, it } from "vitest";

import { isRequiredValuePresent, serializeValue } from "./utils";

describe("onboarding utils", () => {
  it("parses list values from multi-line and comma text", () => {
    expect(serializeValue("list", "alpha, beta\ngamma")).toEqual([
      "alpha",
      "beta",
      "gamma",
    ]);
  });

  it("preserves text values for text-like kinds", () => {
    expect(serializeValue("short_text", "Acme")).toBe("Acme");
    expect(serializeValue("long_text", "About us")).toBe("About us");
    expect(serializeValue("url", "https://acme.test")).toBe("https://acme.test");
  });

  it("checks required field completeness", () => {
    expect(isRequiredValuePresent("hello")).toBe(true);
    expect(isRequiredValuePresent("   ")).toBe(false);
    expect(isRequiredValuePresent(["x"])).toBe(true);
    expect(isRequiredValuePresent([])).toBe(false);
  });
});
