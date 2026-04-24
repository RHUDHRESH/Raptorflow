const { readFileSync } = require("fs");

const genPos = readFileSync("apps/web/src/lib/council/generatePositions.ts", "utf8");
const synth = readFileSync("apps/web/src/lib/council/synthesize.ts", "utf8");
const seed = readFileSync("src/lib/avatars/seed.ts", "utf8");
const schema = readFileSync("packages/database/prisma/schema.prisma", "utf8");
const sessionPage = readFileSync("apps/web/src/app/(app)/council/[sessionId]/page.tsx", "utf8");
const quickScan = readFileSync("apps/web/src/app/api/foundation/scan/quick/route.ts", "utf8");

const checks = [];

const avatarCount = (seed.match(/key:/g) || []).length;
checks.push({
  name: "21 avatars in seed script",
  pass: avatarCount === 21,
  detail: avatarCount + " avatars",
});

checks.push({
  name: "CouncilSession.errorMessage field",
  pass: schema.includes("errorMessage") && schema.includes('@map("error_message")'),
});

checks.push({
  name: "CouncilSession.lastScanResult field",
  pass: schema.includes("lastScanResult") && schema.includes('@map("last_scan_result")'),
});

checks.push({
  name: "Foundation completeness guard",
  pass: genPos.includes("REQUIRED_FIELDS") && genPos.includes("Foundation incomplete"),
});

checks.push({
  name: "All foundation fields in avatar prompt",
  pass:
    genPos.includes("companyStage") &&
    genPos.includes("primaryGoal") &&
    genPos.includes("budget") &&
    genPos.includes("goalStr"),
});

checks.push({
  name: "lastScanResult in synthesis prompt",
  pass: synth.includes("lastScanResult") && synth.includes("STRATEGIC SCAN ANALYSIS"),
});

checks.push({
  name: "generatePositions chains synthesis",
  pass: genPos.includes("synthesizeSession") && genPos.includes("setTimeout"),
});

const councilKeys = [
  "brand-guardian",
  "growth-hacker",
  "customer-champion",
  "data-analyst",
  "creative-director",
  "contrarian",
  "market-watcher",
  "operator",
  "revenue-lead",
  "risk-officer",
  "innovator",
  "storyteller",
];
checks.push({
  name: "All 12 council avatar keys",
  pass: councilKeys.every((k) => genPos.includes(k)),
});

checks.push({
  name: "Session page shows foundation error + link",
  pass:
    sessionPage.includes("Foundation Required") &&
    sessionPage.includes("/foundation") &&
    sessionPage.includes("Complete Foundation"),
});

checks.push({
  name: "Quick scan saves to CouncilSession",
  pass: quickScan.includes("CouncilSession.updateMany") && quickScan.includes("lastScanResult"),
});

console.log("\n=== Stage 4 Sign-off Checklist ===\n");
let allPass = true;
for (const c of checks) {
  const icon = c.pass ? "✅" : "❌";
  console.log(icon + " " + c.name + (c.detail ? " (" + c.detail + ")" : ""));
  if (!c.pass) allPass = false;
}
console.log("\n" + (allPass ? "✅ ALL 10 CHECKS PASS" : "❌ SOME CHECKS FAIL"));
process.exit(allPass ? 0 : 1);
