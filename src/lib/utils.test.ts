import { describe, expect, it } from "vitest";

import { cn } from "./utils";

describe("cn", () => {
  it("merges classnames and resolves tailwind conflicts", () => {
    const shouldHide = false;
    expect(cn("px-2", "text-sm", "px-4")).toContain("px-4");
    expect(cn("px-2", "text-sm", "px-4")).not.toContain("px-2");
    expect(cn("font-bold", shouldHide ? "hidden" : "")).toContain("font-bold");
  });
});
