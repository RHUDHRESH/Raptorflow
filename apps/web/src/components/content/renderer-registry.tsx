import type { ReactNode } from "react";
import { CouncilSynthesisRenderer } from "./CouncilSynthesisRenderer";
import { HookSetRenderer } from "./HookSetRenderer";
import { PositioningRenderer } from "./PositioningRenderer";
import { IcpRefinedRenderer } from "./IcpRefinedRenderer";
import { OfferDesignRenderer } from "./OfferDesignRenderer";
import { CalendarPlanRenderer } from "./CalendarPlanRenderer";
import { UnknownContentRenderer } from "./UnknownContentRenderer";

const KNOWN_TYPES = [
  "council-synthesis",
  "hook-set",
  "positioning",
  "icp-refined",
  "offer-design",
  "calendar-plan",
] as const;

export type KnownContentType = (typeof KNOWN_TYPES)[number];

export function renderGeneratedContent(
  contentType: string,
  body: unknown,
): ReactNode {
  switch (contentType) {
    case "council-synthesis":
      return <CouncilSynthesisRenderer body={body} />;
    case "hook-set":
      return <HookSetRenderer body={body} />;
    case "positioning":
      return <PositioningRenderer body={body} />;
    case "icp-refined":
      return <IcpRefinedRenderer body={body} />;
    case "offer-design":
      return <OfferDesignRenderer body={body} />;
    case "calendar-plan":
      return <CalendarPlanRenderer body={body} />;
    default:
      return <UnknownContentRenderer body={body} contentType={contentType} />;
  }
}
