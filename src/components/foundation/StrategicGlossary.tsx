"use client";

import React from "react";
import { BlueprintTooltip } from "@/components/ui/BlueprintTooltip";
import { Info } from "lucide-react";

export const GLOSSARY = {
  RICP: {
    term: "Rich ICP",
    code: "RICP-01",
    definition: "Rich Ideal Customer Profile: A multi-dimensional view of your target buyer including behaviors, mindset, and market sophistication.",
  },
  SOPHISTICATION: {
    term: "Market Sophistication",
    code: "MKT-SO",
    definition: "A framework by Eugene Schwartz that determines how many similar claims your market has already heard.",
  },
  STORYBRAND: {
    term: "StoryBrand",
    code: "MSG-SB",
    definition: "A messaging framework that positions the customer as the hero and the brand as the guide.",
  },
  JTBD: {
    term: "Jobs To Be Done",
    code: "JTBD",
    definition: "A framework for understanding why customers 'hire' a product to do a specific job.",
  },
  ONE_LINER: {
    term: "One-Liner",
    code: "MSG-OL",
    definition: "A concise, 3-part statement that explains what you do, who you help, and the result you deliver.",
  }
};

interface GlossaryTermProps {
  termKey: keyof typeof GLOSSARY;
  children?: React.ReactNode;
  showIcon?: boolean;
}

export function GlossaryTerm({ termKey, children, showIcon = false }: GlossaryTermProps) {
  const item = GLOSSARY[termKey];
  
  return (
    <BlueprintTooltip 
      content={item.definition} 
      code={item.code}
      className="cursor-help"
    >
      <span className="flex items-center gap-1 group">
        <span className="border-b border-dotted border-[var(--blueprint)] group-hover:text-[var(--blueprint)] transition-colors">
          {children || item.term}
        </span>
        {showIcon && <Info size={12} className="text-[var(--ink-muted)] group-hover:text-[var(--blueprint)]" />}
      </span>
    </BlueprintTooltip>
  );
}
