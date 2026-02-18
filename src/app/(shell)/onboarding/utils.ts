import { OnboardingStepKind } from "@/services/workspaces.service";

export type FieldValue = string | string[];

export function serializeValue(kind: OnboardingStepKind, value: unknown): FieldValue {
  if (kind === "list") {
    if (Array.isArray(value)) return value.filter((v): v is string => typeof v === "string");
    if (typeof value === "string") {
      return value
        .split(/[\n,;]+/)
        .map((part) => part.trim())
        .filter(Boolean);
    }
    return [];
  }

  return typeof value === "string" ? value : "";
}

export function isRequiredValuePresent(value: FieldValue): boolean {
  return Array.isArray(value) ? value.length > 0 : value.trim().length > 0;
}
