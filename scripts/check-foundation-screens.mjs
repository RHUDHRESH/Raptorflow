import { access, readFile } from "node:fs/promises";
import { constants } from "node:fs";
import { join } from "node:path";

const pageFile = join(
  process.cwd(),
  "apps",
  "web",
  "src",
  "app",
  "(app)",
  "foundation",
  "page.tsx",
);
const routeFile = join(
  process.cwd(),
  "apps",
  "web",
  "src",
  "app",
  "(app)",
  "foundation",
  "[step]",
  "page.tsx",
);

const expectedScreens = [
  { slug: "url", title: "URL" },
  { slug: "identity-confirmation", title: "Identity Confirmation" },
  { slug: "business-stage-and-team", title: "Business Stage and Team" },
  { slug: "what-you-actually-sell", title: "What You Actually Sell" },
  { slug: "the-problem-you-solve", title: "The Problem You Solve" },
  { slug: "primary-icp", title: "Primary ICP" },
  { slug: "secondary-icps", title: "Secondary ICPs" },
  { slug: "competitive-landscape", title: "Competitive Landscape" },
  { slug: "competitive-differentiation", title: "Competitive Differentiation" },
  { slug: "positioning-statement", title: "Positioning Statement" },
  { slug: "brand-personality", title: "Brand Personality" },
  { slug: "voice-in-practice", title: "Voice in Practice" },
  { slug: "content-territories", title: "Content Territories" },
  { slug: "marketing-channels", title: "Marketing Channels" },
  { slug: "goals-and-kpis", title: "Goals and KPIs" },
  { slug: "keywords-and-seo", title: "Keywords and SEO" },
  { slug: "existing-assets", title: "Existing Assets" },
  { slug: "current-frustrations", title: "Current Frustrations" },
  { slug: "existing-tools", title: "Existing Tools" },
  { slug: "reference-brands", title: "Reference Brands" },
  { slug: "campaign-strategist", title: "Campaign Strategist" },
];

function extractScreenEntries(source) {
  const block = source.match(/const screens = \[(?<items>[\s\S]*?)\];/);
  if (!block?.groups?.items) {
    throw new Error("Foundation screens array missing.");
  }

  return [
    ...block.groups.items.matchAll(/\{\s*slug:\s*"([^"]+)"\s*,\s*title:\s*"([^"]+)"\s*\}/g),
  ].map((match) => ({ slug: match[1], title: match[2] }));
}

function assertExactList(label, actual, expected) {
  const actualJson = JSON.stringify(actual);
  const expectedJson = JSON.stringify(expected);
  if (actualJson !== expectedJson) {
    throw new Error(`${label} mismatch.\nexpected: ${expectedJson}\nactual:   ${actualJson}`);
  }
}

async function main() {
  await access(routeFile, constants.F_OK);
  const content = await readFile(pageFile, "utf8");

  if (!content.includes("Twenty-one screen scaffold")) {
    throw new Error("Foundation scaffold title missing.");
  }

  if (
    !content.includes(
      "Reserved route content, form contract, websocket hooks, and autosave behavior.",
    )
  ) {
    throw new Error("Foundation scaffold body text missing.");
  }

  const declaredScreens = extractScreenEntries(content);
  assertExactList("foundation screen coverage", declaredScreens, expectedScreens);

  console.log(`foundation scaffold check passed (${declaredScreens.length} screens)`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
