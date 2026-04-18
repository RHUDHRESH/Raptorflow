// ─── RaptorFlow Landing Copy ──────────────────────────────────────────────────

export const navLinks = [
  { label: "Problem", href: "#problem" },
  { label: "System", href: "#system" },
  { label: "Campaigns", href: "#campaigns" },
  { label: "Pricing", href: "#pricing" },
] as const;

export const problemCards = [
  {
    title: "Agencies are expensive",
    body: "Good strategy often starts at retainers most SMBs cannot justify.",
  },
  {
    title: "Freelancers lose context",
    body: "When people change, your marketing memory disappears with them.",
  },
  {
    title: "DIY marketing is scattered",
    body: "Content, ads, competitors, analytics, and positioning live in different tabs.",
  },
  {
    title: "Generic AI is not enough",
    body: "A chatbot can write a caption. It cannot run a campaign system.",
  },
] as const;

export const systemPillars = [
  {
    title: "Foundation",
    body: "RaptorFlow learns your ICP, positioning, competitors, goals, voice, and constraints before it gives advice.",
    glyph: "◈",
    number: "01",
  },
  {
    title: "Campaigns",
    body: "Goals become moves, tasks, content actions, performance checks, and replanning signals.",
    glyph: "◆",
    number: "02",
  },
  {
    title: "Muse",
    body: "Ask strategic or tactical questions with full business context already attached.",
    glyph: "◉",
    number: "03",
  },
  {
    title: "Intel",
    body: "Competitor signals turn into usable response paths instead of vague alerts.",
    glyph: "▲",
    number: "04",
  },
  {
    title: "Daily Wins",
    body: "Every morning, one clear action tells you what matters today.",
    glyph: "◎",
    number: "05",
  },
] as const;

export const foundationCards = [
  "ICP",
  "Pricing",
  "Competitors",
  "Goals",
  "Voice",
  "Channels",
  "Budget",
  "Assets",
  "Positioning",
  "Frustrations",
  "Product",
  "Stage",
  "Tracking",
  "References",
  "Transformation",
  "Keywords",
  "History",
  "Customer",
  "Problem",
  "Strategy",
  "Constraints",
] as const;

export const campaignSteps = [
  {
    step: "01",
    title: "Plan the move",
    body: "A goal becomes a structured move with a clear timeframe and intent.",
  },
  {
    step: "02",
    title: "Execute the task",
    body: "Moves break into daily tasks with assigned agents and content briefs.",
  },
  {
    step: "03",
    title: "Review the signal",
    body: "Performance data surfaces as contextual signals, not raw numbers.",
  },
  {
    step: "04",
    title: "Adjust the path",
    body: "RaptorFlow replans the campaign when signals diverge from expectations.",
  },
] as const;

export const museContextLayers = [
  { label: "Foundation", desc: "Your ICP, tone, constraints, goals" },
  { label: "Active campaign", desc: "Current move, progress, intent" },
  { label: "Competitor signal", desc: "Recent market movement" },
  { label: "Past result", desc: "What worked, what did not" },
  { label: "Daily priority", desc: "Today's single focus" },
] as const;

export const intelSignals = [
  { label: "Pricing shift", color: "#ef4444" },
  { label: "Message change", color: "#f59e0b" },
  { label: "Ad movement", color: "#f59e0b" },
  { label: "SEO movement", color: "#22c55e" },
] as const;

export const councilPerspectives = [
  "Positioning",
  "Copywriting",
  "Distribution",
  "Growth",
  "Analytics",
  "Content",
  "SEO",
  "Paid Ads",
  "Brand",
  "Product",
  "Retention",
  "Memory",
] as const;

export const memorySignals = [
  { label: "Q1 Campaign Result", type: "past" },
  { label: "Brand Voice Pattern", type: "past" },
  { label: "Competitor Response", type: "past" },
  { label: "Channel Performance", type: "past" },
  { label: "Customer Segment", type: "past" },
  { label: "Budget Efficiency", type: "past" },
  { label: "Q3 Prediction", type: "future" },
  { label: "Next Recommendation", type: "future" },
] as const;

export const pricingPlans = [
  {
    name: "Ascend",
    referralCode: "LOKI",
    price: "₹5,000",
    cadence: "/month",
    line: "For founders and small teams starting disciplined marketing execution.",
    features: [
      "Foundation",
      "Daily Wins",
      "Muse",
      "Campaign planning basics",
      "Core task management",
      "Basic Intel",
    ],
    cta: "Start with Ascend",
    featured: false,
  },
  {
    name: "Glide",
    referralCode: "R2005",
    price: "₹7,000",
    cadence: "/month",
    line: "For growing SMBs that need stronger campaign rhythm and deeper visibility.",
    features: [
      "Everything in Ascend",
      "Deeper campaign planning",
      "Stronger Intel",
      "More active execution support",
      "Better performance review flow",
    ],
    cta: "Choose Glide",
    featured: true,
  },
  {
    name: "Soar",
    referralCode: "DUNE",
    price: "₹10,000",
    cadence: "/month",
    line: "For serious operators who want a full marketing operating rhythm.",
    features: [
      "Everything in Glide",
      "Advanced campaigns",
      "More strategic reviews",
      "Priority intelligence",
      "Deeper memory and execution loops",
    ],
    cta: "Go with Soar",
    featured: false,
  },
] as const;
